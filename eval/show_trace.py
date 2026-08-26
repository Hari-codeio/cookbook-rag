"""Render traces for reading by a human. No scoring, no labelling, no judgement.

This is the tool used for the open-coding pass. It shows what the app did and
stops there: the query, what came back from retrieval with scores, what the
model said, and what the gates did with it. It does not compare against an
answer key, does not mark anything pass or fail, and has no notion of a failure
mode. Anything of that sort here would leak a category into the reading step,
which is the one step that has to stay category-free.

    python eval/show_trace.py --from-sample out/sample_random-traffic_20.json
    python eval/show_trace.py --trace-id tr_61660ebdd78d --full-context
    python eval/show_trace.py --from-sample ... --out out/sample_render.md
"""

from __future__ import annotations

import argparse
import json
import sys
import textwrap
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rag import trace as trc  # noqa: E402

# The Windows console is cp1252 and the corpus is not; renderer output must not
# die on an ingredient name.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def render(rec: dict[str, Any], full_context: bool = False, preview: int = 150) -> str:
    L: list[str] = []
    meta = rec.get("meta") or {}
    L.append(f"### {rec['trace_id']}")
    L.append("")
    L.append(f"- **query**: `{rec['request']['query']}`")
    L.append(
        f"- query_id `{meta.get('query_id')}` · intent `{meta.get('intent')}` · "
        f"source `{meta.get('source')}` · logged `{rec['ts']}`"
    )

    if "error" in rec:
        L.append(f"- **the run raised**: `{rec['error']['type']}: {rec['error']['message']}`")
        L.append("")
        return "\n".join(L)

    req, retr = rec["request"], rec["retrieval"]
    L.append(
        f"- retriever `{req['retriever']}` · strategy `{req['strategy']}` · k={req['k']} · "
        f"collection `{retr['collection']}` · prompt `{rec['prompt']['version']}`"
    )
    L.append(
        f"- model `{rec['model']['name']}` · temp {rec['model']['params'].get('temperature')} · "
        f"tokens {rec['usage']['input_tokens']}/{rec['usage']['output_tokens']} · "
        f"{rec['usage']['model_latency_ms']:.0f} ms"
    )
    L.append("")
    L.append("retrieved:")
    L.append("")
    L.append("| rank | score | recipe_id | section | chunk_id |")
    L.append("|---|---|---|---|---|")
    for h in retr["hits"]:
        L.append(
            f"| {h['rank']} | {h['score']:.4f} | {h['recipe_id']} | {h['section']} | "
            f"`{h['chunk_id']}` |"
        )
    L.append("")

    if full_context:
        L.append("context supplied to the model:")
        L.append("")
        L.append("```text")
        for h in retr["hits"]:
            L.append(f"--- {h['chunk_id']} ---")
            L.extend(h["text"].splitlines())
        L.append("```")
    else:
        L.append("first line of each retrieved chunk:")
        L.append("")
        for h in retr["hits"]:
            first = " / ".join(x.strip() for x in h["text"].splitlines() if x.strip())
            L.append(f"  {h['rank']}. {textwrap.shorten(first, width=preview, placeholder=' ...')}")
    L.append("")

    parsed = rec["output"].get("parsed")
    L.append("model output (raw):")
    L.append("")
    L.append("```json")
    L.append(rec["output"]["raw_text"])
    L.append("```")
    L.append("")
    if parsed:
        L.append(f"- can_answer: `{parsed.get('can_answer')}`")
        if parsed.get("missing"):
            L.append(f"- missing: `{parsed['missing']}`")
        for c in parsed.get("claims") or []:
            L.append(f"- claim: {c.get('claim')}  ->  `{c.get('chunk_id')}`")
    L.append("")
    L.append(f"- **refused**: `{rec['gates']['refused']}`")
    if rec["gates"]["refusal_reason"]:
        L.append(f"- refusal reason: {rec['gates']['refusal_reason']}")
    for n in rec["gates"]["notes"]:
        L.append(f"- gate note: {n}")
    L.append("")
    L.append("what the user saw:")
    L.append("")
    L.append("```text")
    L.extend(rec["gates"]["rendered"].splitlines())
    L.append("```")
    L.append("")
    return "\n".join(L)


def main() -> None:
    ap = argparse.ArgumentParser(description="Render traces for human reading.")
    ap.add_argument("--trace-id", action="append", default=[])
    ap.add_argument("--from-sample", default=None, help="a sample json written by sample_traces.py")
    ap.add_argument("--full-context", action="store_true")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    ids = list(args.trace_id)
    if args.from_sample:
        ids += json.loads(Path(args.from_sample).read_text(encoding="utf-8"))["trace_ids"]
    if not ids:
        raise SystemExit("pass --trace-id or --from-sample")

    by_id = {r["trace_id"]: r for r in trc.iter_traces()}
    missing = [i for i in ids if i not in by_id]
    if missing:
        raise SystemExit(f"not in the log: {missing}")

    blocks = [render(by_id[i], full_context=args.full_context) for i in ids]
    text = "\n---\n\n".join(blocks)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
        print(f"written: {args.out}  ({len(ids)} traces)")
    else:
        print(text)


if __name__ == "__main__":
    main()
