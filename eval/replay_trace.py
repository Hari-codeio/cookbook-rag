"""Replay one logged trace FROM THE TRACE ALONE, and show it next to the original.

The claim being tested is narrow and worth stating precisely: given only a line
of ``out/traces.jsonl``, can the original model call be reconstructed and
re-issued without consulting the vector store, the corpus, or the index?

To stop that claim being sloppy, the store is booby-trapped before the replay
starts. ``rag.store.search``, ``rag.store.get_collection`` and
``rag.store.get_chunk`` are replaced with functions that raise, so if any part
of the replay path quietly reaches for the index the run dies instead of
producing a comfortable result.

Three reconstructions are checked against hashes recorded at the time:

    system prompt   trace.prompt.system_text      vs trace.prompt.sha256
    context blocks  rebuilt from trace.retrieval.hits vs trace.context.sha256
    user turn       rebuilt from both              vs trace.prompt.user_turn_sha256

The context string is deliberately NOT stored in the trace. Rebuilding it from
the stored hits and matching the hash is what proves the hits are sufficient;
storing the string would have proved only that a string was stored.

    python eval/replay_trace.py --pick-seeded --seed 20260826
    python eval/replay_trace.py --trace-id tr_61660ebdd78d --repeats 3
"""

from __future__ import annotations

import argparse
import difflib
import json
import random
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rag import trace as trc  # noqa: E402
from rag.config import OUT_DIR, gemini_api_key  # noqa: E402

SEED = 20260826


# ---------------------------------------------------------------------------
# Booby-trap the retrieval layer. Anything that reaches for the index during a
# replay is a bug in the claim, not a convenience.
# ---------------------------------------------------------------------------
def seal_the_store() -> None:
    from rag import store

    def _forbidden(*_a: Any, **_k: Any):
        raise AssertionError(
            "replay touched the vector store. A trace that needs the index to be "
            "replayed is not a replayable trace."
        )

    store.search = _forbidden  # type: ignore[assignment]
    store.get_collection = _forbidden  # type: ignore[assignment]
    store.get_chunk = _forbidden  # type: ignore[assignment]


# ---------------------------------------------------------------------------
# Reconstruction. These two functions are copies of the shapes in rag.generate,
# written out here on purpose: the replay must depend on the TRACE, not on the
# current state of the module that produced it.
# ---------------------------------------------------------------------------
def rebuild_context(hits: list[dict[str, Any]]) -> str:
    blocks = []
    for h in sorted(hits, key=lambda x: x["rank"]):
        blocks.append(
            f'<context chunk_id="{h["chunk_id"]}" recipe_id="{h["recipe_id"]}" '
            f'source_file="{h["source_file"]}" section="{h["section"]}">\n'
            f'{h["text"]}\n'
            f"</context>"
        )
    return "\n\n".join(blocks)


def rebuild_user_turn(question: str, context: str) -> str:
    return (
        f"CONTEXT\n=======\n{context}\n\n"
        f"QUESTION\n========\n{question}\n\n"
        f"Answer using only the CONTEXT blocks above."
    )


def check(label: str, rebuilt: str, recorded: str | None) -> bool:
    got = trc.sha256_text(rebuilt)
    if recorded is None:
        print(f"  {label:<16} NOT RECORDED IN TRACE  (rebuilt sha {got[:16]})")
        return False
    ok = got == recorded
    print(f"  {label:<16} {'MATCH  ' if ok else 'MISMATCH'} {got[:16]}  vs recorded {recorded[:16]}")
    return ok


def resolve_schema(rec: dict[str, Any]) -> tuple[dict[str, Any] | None, bool, str]:
    """The response schema, and whether the trace was self-sufficient for it.

    Traces written by schema 1.0 record only the schema's sha256, not the schema.
    That is a genuine hole: the sha proves which schema was used but cannot
    produce it. Where the trace carries the schema inline (1.1 and later) it is
    used directly and nothing outside the trace is read.
    """
    inline = (rec.get("model", {}).get("params") or {}).get("response_schema")
    recorded_sha = (rec.get("model", {}).get("params") or {}).get("response_schema_sha256")
    if inline is not None:
        return inline, True, "taken from the trace"

    from rag.generate import GEMINI_SCHEMA, RESPONSE_SCHEMA, _schema_sha

    provider = rec.get("model", {}).get("provider", "gemini")
    schema = GEMINI_SCHEMA if provider == "gemini" else RESPONSE_SCHEMA
    if recorded_sha and _schema_sha(schema) == recorded_sha:
        return schema, False, f"NOT in the trace; recovered from rag/generate.py, sha matches"
    return schema, False, "NOT in the trace; recovered from rag/generate.py, sha DOES NOT match"


def call_gemini(model: str, system_text: str, user_turn: str, params: dict, schema: dict) -> dict:
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=gemini_api_key())
    cfg: dict[str, Any] = {
        "system_instruction": system_text,
        "response_mime_type": params.get("response_mime_type", "application/json"),
        "response_schema": schema,
        "max_output_tokens": params.get("max_output_tokens"),
        "temperature": params.get("temperature"),
    }
    if params.get("thinking_budget") is not None:
        cfg["thinking_config"] = types.ThinkingConfig(thinking_budget=params["thinking_budget"])

    response = client.models.generate_content(
        model=model, contents=user_turn, config=types.GenerateContentConfig(**cfg)
    )
    usage = getattr(response, "usage_metadata", None)
    candidates = getattr(response, "candidates", None) or []
    finish = str(getattr(candidates[0], "finish_reason", "stop") or "stop") if candidates else "stop"
    return {
        "raw_text": response.text or "",
        "stop_reason": finish,
        "input_tokens": getattr(usage, "prompt_token_count", None) if usage else None,
        "output_tokens": getattr(usage, "candidates_token_count", None) if usage else None,
    }


def pick_seeded(seed: int, source: str) -> str:
    ids = sorted(
        rec["trace_id"]
        for rec in trc.iter_traces()
        if (rec.get("meta") or {}).get("source") == source
    )
    if not ids:
        raise SystemExit(f"no traces with source={source!r}")
    return random.Random(seed).choice(ids)


def main() -> None:
    ap = argparse.ArgumentParser(description="Replay one trace from the trace alone.")
    ap.add_argument("--trace-id", default=None)
    ap.add_argument("--pick-seeded", action="store_true", help="choose the trace_id with --seed")
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--source", default="random-traffic")
    ap.add_argument("--repeats", type=int, default=1, help="re-issue N times to show drift")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    if args.pick_seeded:
        trace_id = pick_seeded(args.seed, args.source)
        picked_by = f"random.Random({args.seed}).choice(sorted(trace_ids where source={args.source}))"
    elif args.trace_id:
        trace_id = args.trace_id
        picked_by = "named on the command line"
    else:
        raise SystemExit("pass --trace-id or --pick-seeded")

    rec = trc.load_trace(trace_id)
    seal_the_store()

    lines: list[str] = []

    def out(s: str = "") -> None:
        print(s)
        lines.append(s)

    out(f"trace_id     : {trace_id}")
    out(f"picked by    : {picked_by}")
    out(f"logged at    : {rec['ts']}")
    out(f"query        : {rec['request']['query']!r}")
    out(f"query_id     : {(rec.get('meta') or {}).get('query_id')}")
    out(f"trace schema : {rec.get('trace_schema')}")
    out(f"code git sha : {rec['app']['git_sha']}")
    out()

    out("RECONSTRUCTION (nothing below reads the index - it is sealed shut)")
    system_text = rec["prompt"]["system_text"]
    context = rebuild_context(rec["retrieval"]["hits"])
    user_turn = rebuild_user_turn(rec["request"]["query"], context)

    ok_prompt = check("system prompt", system_text, rec["prompt"].get("sha256"))
    ok_ctx = check("context", context, rec.get("context", {}).get("sha256"))
    ok_turn = check("user turn", user_turn, rec["prompt"].get("user_turn_sha256"))

    schema, self_contained, schema_note = resolve_schema(rec)
    out(f"  {'response schema':<16} {'MATCH  ' if self_contained else 'GAP    '} {schema_note}")
    out()

    params = rec["model"]["params"]
    out("MODEL AND PARAMS, AS RECORDED")
    out(f"  provider          : {rec['model']['provider']}")
    out(f"  model             : {rec['model']['name']}")
    for key in ("temperature", "max_output_tokens", "response_mime_type", "thinking_budget"):
        out(f"  {key:<18}: {params.get(key)!r}")
    out(f"  prompt version    : {rec['prompt']['version']}")
    out()

    if not (ok_prompt and ok_ctx and ok_turn):
        raise SystemExit("reconstruction failed a hash check; refusing to replay")

    original = rec["output"]["raw_text"]
    out("ORIGINAL raw output (as logged)")
    out("```json")
    out(original)
    out("```")
    out()

    for attempt in range(1, args.repeats + 1):
        replayed = call_gemini(rec["model"]["name"], system_text, user_turn, params, schema)
        same = replayed["raw_text"] == original
        out(f"REPLAY {attempt} of {args.repeats} - byte-identical to the original: {same}")
        out("```json")
        out(replayed["raw_text"])
        out("```")
        if not same:
            diff = list(
                difflib.unified_diff(
                    original.splitlines(),
                    replayed["raw_text"].splitlines(),
                    fromfile="original",
                    tofile=f"replay-{attempt}",
                    lineterm="",
                )
            )
            out("diff:")
            out("```diff")
            for d in diff[:60]:
                out(d)
            out("```")
        try:
            a, b = json.loads(original), json.loads(replayed["raw_text"])
            out(f"  can_answer  original={a.get('can_answer')}  replay={b.get('can_answer')}")
            out(f"  answer same : {a.get('answer') == b.get('answer')}")
            out(f"  claims same : {a.get('claims') == b.get('claims')}")
        except json.JSONDecodeError:
            out("  (one side was not parseable JSON)")
        out(
            f"  tokens in/out original={rec['usage']['input_tokens']}/{rec['usage']['output_tokens']}"
            f"  replay={replayed['input_tokens']}/{replayed['output_tokens']}"
        )
        out()

    path = Path(args.out) if args.out else OUT_DIR / f"replay_{trace_id}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"written: {path}")


if __name__ == "__main__":
    main()
