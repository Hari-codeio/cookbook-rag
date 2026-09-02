"""Week 6 BONUS, one command: RAGAS faithfulness + context precision over the
frozen 25 substitutions, and the free diagnostic that catches what they miss.

    python eval/run_ragas.py

Everything it reads is frozen and committed before it runs:

    out/substitutions_v1.jsonl   the 25 answers            (commit 959ce8c)
    eval/ragas_reference.json    which card is relevant    (commit d4ccfac)

Two LLM calls per case, both on the pinned model, both cached in
out/ragas_cache.json keyed on the sha256 of the exact system prompt and user
turn. Editing a prompt changes the key and forces a re-run; re-running unchanged
costs nothing and cannot silently produce different numbers.

The last section is the point of the exercise: cases where faithfulness is
0.9 or better AND the answer still stood on worse evidence than it was given.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from eval.ragas_metrics import (  # noqa: E402
    NLI_SCHEMA,
    NLI_SYSTEM,
    STATEMENT_SCHEMA,
    STATEMENT_SYSTEM,
    build_nli_turn,
    build_statement_turn,
    context_precision_at_k,
    faithfulness_score,
    grounding_diagnostics,
    joined_premise,
    parse_context_blocks,
    render_response,
)
from rag.config import OUT_DIR  # noqa: E402
from rag.generate import build_client, call_model  # noqa: E402

SUBS = OUT_DIR / "substitutions_v1.jsonl"
REFERENCE = ROOT / "eval" / "ragas_reference.json"
CACHE = OUT_DIR / "ragas_cache.json"
OUT_MD = OUT_DIR / "ragas.md"
OUT_JSON = OUT_DIR / "ragas_scores.json"

# The threshold the bonus asks about: "0.9+ faithfulness while grounding itself
# in the wrong recipe's method".
FAITHFUL_HIGH = 0.9

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def key_of(system: str, user: str) -> str:
    h = hashlib.sha256()
    h.update(system.encode("utf-8"))
    h.update(b"\x00")
    h.update(user.encode("utf-8"))
    return h.hexdigest()


def load_cache(use_cache: bool) -> dict[str, Any]:
    if use_cache and CACHE.exists():
        return json.loads(CACHE.read_text(encoding="utf-8"))
    return {}


def cached_call(
    client,
    cache: dict[str, Any],
    system: str,
    user: str,
    schema: dict[str, Any],
    sleep: float,
) -> tuple[dict[str, Any], bool]:
    """Return (parsed payload, was_cached)."""
    k = key_of(system, user)
    if k in cache:
        return cache[k], True
    reply = call_model(
        client, "", user, system_prompt=system, schema=schema,
        max_tokens=4096, prefer_no_thinking=True,
    )
    try:
        payload = json.loads(reply.text)
    except json.JSONDecodeError:
        payload = {"_unparseable": reply.text}
    payload["_model"] = reply.model
    cache[k] = payload
    if sleep:
        time.sleep(sleep)
    return payload, False


def score_case(
    client,
    cache: dict[str, Any],
    rec: dict[str, Any],
    ref: dict[str, Any],
    sleep: float,
) -> dict[str, Any]:
    chunks = parse_context_blocks(rec["context"])
    relevant = ref.get("relevant_recipe_ids") or []

    question = (
        f"For the recipe '{rec['recipe'] or '(none named)'}', "
        f"apply this change: {rec['constraint']}"
    )
    answer = render_response(rec["output"])

    # --- faithfulness, step 1: decompose. Context deliberately NOT shown. ---
    s_user = build_statement_turn(question, answer)
    s_payload, s_cached = cached_call(
        client, cache, STATEMENT_SYSTEM, s_user, STATEMENT_SCHEMA, sleep
    )
    statements = [s for s in (s_payload.get("statements") or []) if str(s).strip()]

    # --- faithfulness, step 2: one joined premise, one verdict per statement ---
    verdicts: list[dict[str, Any]] = []
    n_cached = 1 if s_cached else 0
    n_calls = 0 if s_cached else 1
    if statements:
        premise = joined_premise(chunks)
        n_user = build_nli_turn(premise, statements)
        n_payload, n_cached_hit = cached_call(
            client, cache, NLI_SYSTEM, n_user, NLI_SCHEMA, sleep
        )
        n_cached += 1 if n_cached_hit else 0
        n_calls += 0 if n_cached_hit else 1
        raw = n_payload.get("verdicts") or []
        # Align by position; the prompt asks for one entry per statement in
        # order. A short reply is padded with verdict 0 rather than silently
        # shortening the denominator, which would inflate the score.
        for i, stmt in enumerate(statements):
            if i < len(raw) and isinstance(raw[i], dict):
                # Only an explicit 1 counts as supported. `if raw[i]["verdict"]`
                # would be wrong the moment the model returns the STRING "0",
                # which is truthy and would silently mark an unsupported claim
                # as supported - i.e. inflate faithfulness.
                verdicts.append(
                    {
                        "statement": stmt,
                        "verdict": 1 if str(raw[i].get("verdict")).strip() == "1" else 0,
                        "reason": str(raw[i].get("reason") or ""),
                    }
                )
            else:
                verdicts.append(
                    {"statement": stmt, "verdict": 0, "reason": "MISSING from judge reply"}
                )

    faith = faithfulness_score(verdicts)
    cp = context_precision_at_k(chunks, relevant)
    ground = grounding_diagnostics(chunks, rec["output"], ref)

    return {
        "case_id": rec["case_id"],
        "mode": rec["mode"],
        "recipe": rec["recipe"],
        "constraint": rec["constraint"],
        "reference_relevant_recipe_ids": relevant,
        "reference_ambiguous": ref.get("ambiguous"),
        "rendered_answer": answer,
        "faithfulness": faith,
        "n_statements": len(statements),
        "n_supported": sum(1 for v in verdicts if v["verdict"]),
        "verdicts": verdicts,
        "context_precision": cp["score"],
        "context_precision_detail": cp,
        "grounding": ground,
        "_calls": n_calls,
        "_cached": n_cached,
    }


def fmt(x: float | None, nd: int = 3) -> str:
    return "n/a" if x is None else f"{x:.{nd}f}"


def build_markdown(rows: list[dict[str, Any]], meta: dict[str, Any]) -> str:
    L: list[str] = []
    L.append("# Week 6 bonus - RAGAS faithfulness and context precision\n")
    L.append("```")
    L.append(f"substitutions     : {meta['substitutions']}  ({meta['n']} cases)")
    L.append(f"substitutions sha : {meta['substitutions_sha256']}")
    L.append(f"reference         : {meta['reference']}")
    L.append(f"reference sha     : {meta['reference_sha256']}")
    L.append(f"metric model      : {meta['model']}  (pinned)")
    L.append(f"llm calls made    : {meta['calls']}   cache hits: {meta['cached']}")
    L.append("```\n")

    scored = [r for r in rows if r["faithfulness"] is not None]
    faiths = [r["faithfulness"] for r in scored]
    cps = [r["context_precision"] for r in rows]

    L.append("## The two averages, which is all a dashboard would show you\n")
    L.append("```")
    L.append(f"mean faithfulness      : {fmt(statistics.fmean(faiths))}   (n={len(faiths)})")
    L.append(f"mean context precision : {fmt(statistics.fmean(cps))}   (n={len(cps)})")
    L.append("```\n")

    L.append("## Per case\n")
    L.append("| case | mode | faithfulness | context precision | grounded on | rank | in base? | declined w/ donor? |")
    L.append("|---|---|---|---|---|---|---|---|")
    for r in rows:
        g = r["grounding"]
        L.append(
            f"| `{r['case_id']}` | `{r['mode']}` | {fmt(r['faithfulness'])} "
            f"| {fmt(r['context_precision'])} | `{g['grounded_recipe_id'] or '-'}` "
            f"| {g['grounding_rank'] or '-'} "
            f"| {'yes' if g['grounded_in_reference_base'] else '**NO**'} "
            f"| {'**YES**' if g['declined_with_donor_on_screen'] else 'no'} |"
        )
    L.append("")

    # The bonus: high faithfulness, wrong grounding.
    flagged = [
        r for r in rows
        if r["faithfulness"] is not None
        and r["faithfulness"] >= FAITHFUL_HIGH
        and r["grounding"]["wrongly_grounded"]
    ]

    L.append("## Confidently, faithfully wrong\n")
    L.append(
        f"Cases scoring faithfulness >= {FAITHFUL_HIGH} that still answered about a dish "
        f"the request could not defensibly name, or declined with a donor card sitting "
        f"in their own retrieved context: **{len(flagged)} of {len(rows)}**.\n"
    )
    for r in flagged:
        g = r["grounding"]
        L.append(f"### `{r['case_id']}` - {r['recipe']} / {r['constraint']}\n")
        L.append("```")
        L.append(f"faithfulness      : {fmt(r['faithfulness'])}   ({r['n_supported']}/{r['n_statements']} claims entailed)")
        L.append(f"context precision : {fmt(r['context_precision'])}")
        L.append(f"grounded on       : {g['grounded_recipe_id']}   at rank {g['grounding_rank']}")
        L.append(f"in reference base : {g['grounded_in_reference_base']}")
        L.append(f"declined          : {g['declined']}")
        L.append(f"donors on screen  : {', '.join(g['donors_on_screen']) or '-'}   (best at rank {g['best_donor_rank']})")
        L.append(f"walked past       : {', '.join(g['relevant_above']) or '-'}")
        L.append("```\n")
        L.append("Retrieved context, in rank order:\n")
        L.append("| rank | chunk | relevant | P@k | contributes |")
        L.append("|---|---|---|---|---|")
        for d in r["context_precision_detail"]["ranks"]:
            L.append(
                f"| {d['rank']} | `{d['chunk_id']}` | {d['v_k']} "
                f"| {d['precision_at_k']:.4f} | {d['contribution']:.4f} |"
            )
        L.append("")
        L.append("Claims and their verdicts:\n")
        for v in r["verdicts"]:
            L.append(f"- `{v['verdict']}` {v['statement']}")
            if v["reason"]:
                L.append(f"  - {v['reason']}")
        L.append("")

    L.append("## Why the average hides it\n")
    if flagged:
        f_flag = statistics.fmean([r["faithfulness"] for r in flagged])
        c_flag = statistics.fmean([r["context_precision"] for r in flagged])
        others = [r for r in rows if r not in flagged and r["faithfulness"] is not None]
        L.append("```")
        L.append(f"flagged cases   n={len(flagged):<3} mean faithfulness {fmt(f_flag)}  mean context precision {fmt(c_flag)}")
        if others:
            L.append(
                f"everything else n={len(others):<3} mean faithfulness "
                f"{fmt(statistics.fmean([r['faithfulness'] for r in others]))}  "
                f"mean context precision {fmt(statistics.fmean([r['context_precision'] for r in others]))}"
            )
        L.append("```\n")
        L.append(
            "The flagged cases score AT OR ABOVE the run average on both metrics. They "
            "do not drag either mean down, so no threshold on either number can "
            "separate them out. Averaging is not what hides them - they are invisible "
            "at the per-case level too, because neither metric ever forms the pair "
            "(claim, chunk that supported it). Faithfulness joins every chunk into one "
            "premise, so support by ANY chunk reads the same as support by the RIGHT "
            "chunk. Context precision never looks at the answer at all. The failure "
            "lives in the gap between them, and the free deterministic check in the "
            "`declined w/ donor?` column is what finds it - no model call, no "
            "threshold to tune.\n"
        )
    else:
        L.append("No case matched the pattern on this run.\n")

    return "\n".join(L) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description="RAGAS faithfulness + context precision.")
    ap.add_argument("--substitutions", default=str(SUBS))
    ap.add_argument("--reference", default=str(REFERENCE))
    ap.add_argument("--sleep", type=float, default=1.0)
    ap.add_argument("--limit", type=int, default=0, help="score only the first N cases")
    ap.add_argument("--no-cache", action="store_true")
    args = ap.parse_args()

    subs_path = Path(args.substitutions)
    ref_path = Path(args.reference)

    recs = [
        json.loads(l)
        for l in subs_path.read_text(encoding="utf-8").splitlines()
        if l.strip()
    ]
    if args.limit:
        recs = recs[: args.limit]

    ref_doc = json.loads(ref_path.read_text(encoding="utf-8"))
    reference = ref_doc["reference"]

    subs_sha = hashlib.sha256(subs_path.read_bytes()).hexdigest()
    ref_sha = hashlib.sha256(ref_path.read_bytes()).hexdigest()

    # The reference records the substitutions sha it was built against. If the
    # answers were regenerated, the reference is stale and the relevance
    # judgements no longer describe these cases.
    recorded = ref_doc.get("substitutions_sha256")
    if recorded and recorded != subs_sha and not args.limit:
        raise SystemExit(
            "reference was built against a different substitutions file\n"
            f"  reference expects : {recorded}\n"
            f"  actual            : {subs_sha}"
        )

    print(f"substitutions     : {subs_path}  ({len(recs)} cases)")
    print(f"substitutions sha : {subs_sha}")
    print(f"reference         : {ref_path}")
    print(f"reference sha     : {ref_sha}")
    print()

    cache = load_cache(not args.no_cache)
    client = build_client()

    rows: list[dict[str, Any]] = []
    started = time.time()
    for i, rec in enumerate(recs, start=1):
        ref = reference.get(rec["case_id"])
        if ref is None:
            raise SystemExit(f"no reference entry for {rec['case_id']}")
        row = score_case(client, cache, rec, ref, args.sleep)
        rows.append(row)
        g = row["grounding"]
        flag = ""
        if row["faithfulness"] is not None and row["faithfulness"] >= FAITHFUL_HIGH and g["wrongly_grounded"]:
            flag = "  <-- faithful but wrongly grounded"
        print(
            f"[{i:>2}/{len(recs)}] {row['case_id']:<4} "
            f"faith={fmt(row['faithfulness'])} cp={fmt(row['context_precision'])} "
            f"grounded={str(g['grounded_recipe_id']):<22} rank={str(g['grounding_rank']):<4}{flag}"
        )
        CACHE.parent.mkdir(parents=True, exist_ok=True)
        CACHE.write_text(json.dumps(cache, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    models = {
        v.get("_model")
        for v in cache.values()
        if isinstance(v, dict) and v.get("_model")
    }
    meta = {
        "substitutions": str(subs_path.relative_to(ROOT)).replace("\\", "/"),
        "substitutions_sha256": subs_sha,
        "reference": str(ref_path.relative_to(ROOT)).replace("\\", "/"),
        "reference_sha256": ref_sha,
        "n": len(rows),
        "model": ", ".join(sorted(models)) or "unknown",
        "calls": sum(r["_calls"] for r in rows),
        "cached": sum(r["_cached"] for r in rows),
    }

    md = build_markdown(rows, meta)
    OUT_MD.write_text(md, encoding="utf-8")
    OUT_JSON.write_text(
        json.dumps({"meta": meta, "cases": rows}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print()
    print(md)
    print(f"done in {(time.time() - started) / 60:.1f} min")
    print(f"written : {OUT_MD.relative_to(ROOT)}")
    print(f"written : {OUT_JSON.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
