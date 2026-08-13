"""Requirement 5 — 3 cited answers, 3 forced refusals, plus the bonus comparison.

Everything here is written to out/generation.md verbatim, including the gate
notes and the citation-resolution block, so the transcripts pasted into
results.md are the real output rather than a retyped summary.

Also runs two honesty checks the write-up depends on:

  * every out-of-corpus question MUST refuse — a single answered one is reported
    as a FAILURE, not quietly dropped;
  * one out-of-corpus question is re-run with the code gate disabled, to show
    the prompt gate refuses on its own rather than the refusal being an artefact
    of post-processing.

    python eval/run_generation.py
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rag.config import (  # noqa: E402
    GEN_EFFORT,
    GEN_MODEL,
    GEN_PROVIDER,
    OUT_DIR,
    QUESTIONS_PATH,
    ROOT,
    STRATEGIES,
    TOP_K,
    api_key,
)
from rag.generate import SYSTEM_PROMPT, answer, render_transcript  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--strategy", default="structure", choices=list(STRATEGIES))
    parser.add_argument("--k", type=int, default=TOP_K)
    parser.add_argument("--show-context", action="store_true")
    args = parser.parse_args()

    if not api_key():
        wanted = "ANTHROPIC_API_KEY" if GEN_PROVIDER == "anthropic" else "GEMINI_API_KEY"
        raise SystemExit(
            f"{wanted} is not set — generation cannot run (GEN_PROVIDER={GEN_PROVIDER}).\n"
            "Copy .env.example to .env and put your key in it, or export the variable.\n"
            "A free Gemini key: https://aistudio.google.com/apikey\n"
            "Everything else (hit-rate, filter demo, chunk invariants) runs without a key."
        )

    if not QUESTIONS_PATH.exists():
        raise SystemExit(f"{QUESTIONS_PATH} does not exist — write the 8 questions first.")

    payload = json.loads(QUESTIONS_PATH.read_text(encoding="utf-8"))
    questions = {q["id"]: q for q in payload.get("questions", [])}

    answerable_ids = payload.get("generation_answerable_ids") or list(questions)[:3]
    unanswerable = payload.get("generation_unanswerable") or []
    bonus = payload.get("bonus") or {}

    if len(unanswerable) < 3:
        raise SystemExit(
            "questions.json needs at least 3 entries in 'generation_unanswerable' — "
            "questions whose answers appear on no card."
        )

    out: list[str] = [
        "# Generation — cited answers and forced refusals",
        "",
        "```",
        f"model      : {GEN_MODEL}",
        f"effort     : {GEN_EFFORT}",
        f"strategy   : {args.strategy}",
        f"top-k      : {args.k}",
        f"generated  : {datetime.now(timezone.utc).isoformat(timespec='seconds')}",
        "```",
        "",
        "## The grounding prompt (gate 1), verbatim",
        "",
        "Note what is absent: there is no 'if the context is insufficient, use your best",
        "judgement' clause. Refusal is the required output, not a suggested one.",
        "",
        "```text",
        SYSTEM_PROMPT,
        "```",
        "",
        "## 3 answerable questions — cited",
        "",
    ]

    cited_ok = 0
    for qid in answerable_ids[:3]:
        q = questions.get(qid)
        if q is None:
            print(f"[warn] unknown question id {qid!r}", file=sys.stderr)
            continue
        print(f"[generate] {qid}: {q['question']}")
        result = answer(q["question"], args.strategy, k=args.k)
        if not result.refused and result.claims:
            cited_ok += 1
        out += [
            f"### {qid} — {q['question']}",
            f"*Known-correct source: {q['expected_recipe_id']} / {q.get('expected_section','')}*",
            "",
            render_transcript(result, show_context=args.show_context),
            "",
        ]

    out += ["## 3 out-of-corpus questions — must refuse", ""]
    refused_ok = 0
    for i, question in enumerate(unanswerable[:3], start=1):
        print(f"[generate] refusal {i}: {question}")
        result = answer(question, args.strategy, k=args.k)
        if result.refused:
            refused_ok += 1
        out += [
            f"### R{i} — {question}",
            "",
            render_transcript(result, show_context=args.show_context),
            f"\n**Refused: {'YES' if result.refused else 'NO — THIS IS A FAILURE'}**",
            "",
        ]

    # ---- prompt gate alone ---------------------------------------------
    probe = unanswerable[0]
    print(f"[generate] prompt-gate-only probe: {probe}")
    ungated = answer(probe, args.strategy, k=args.k, code_gate=False)
    out += [
        "## Is the refusal an artefact of the code gate?",
        "",
        "The same out-of-corpus question, re-run with gate 2 (the code gate) disabled.",
        "If it still refuses, the refusal came from the prompt and schema alone.",
        "",
        render_transcript(ungated, show_context=False),
        f"\n**Refused with code gate OFF: {'YES — the prompt gate is doing the work' if ungated.refused else 'NO — the refusal depended on the code gate'}**",
        "",
    ]

    # ---- bonus ----------------------------------------------------------
    if bonus.get("question"):
        print(f"[generate] bonus: {bonus['question']}")
        out += [
            "## Bonus — precision vs completeness",
            "",
            f"**Question:** {bonus['question']}",
            "",
        ]
        if bonus.get("note"):
            out += [bonus["note"], ""]
        for strategy in STRATEGIES:
            result = answer(bonus["question"], strategy, k=args.k)
            out += [
                f"### strategy = {strategy}",
                "",
                render_transcript(result, show_context=True),
                "",
            ]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "generation.md").write_text("\n".join(out), encoding="utf-8")

    print()
    print(f"cited answers produced : {cited_ok}/3")
    print(f"out-of-corpus refused  : {refused_ok}/3")
    print(f"prompt gate alone      : {'refused' if ungated.refused else 'DID NOT REFUSE'}")
    print(f"[written] {(OUT_DIR / 'generation.md').relative_to(ROOT)}")
    if refused_ok < 3:
        print("\nFAILURE: not every out-of-corpus question was refused.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
