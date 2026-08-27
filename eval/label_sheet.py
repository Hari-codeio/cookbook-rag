"""Render the frozen substitutions for blind hand-labelling.

Blind means the sheet shows the labeller exactly what the judge will be shown
and nothing else: the request, the CONTEXT blocks, and the output. It does NOT
show the case's `groundable` field from substitution_cases.jsonl, which is my
own prior about what the archive supports, and it does not show any judge
verdict, because at the time this is used no judge has been run.

It also emits a labels skeleton with every verdict set to null, so the labelling
step is filling in a file rather than authoring one from scratch, and a
half-finished pass is visibly half-finished.

    python eval/label_sheet.py --out out/label_sheet.md --skeleton out/labels_skeleton.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rag.config import OUT_DIR  # noqa: E402

SUBSTITUTIONS = OUT_DIR / "substitutions_v1.jsonl"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Fields of the eval case that must never reach the sheet. `groundable` and
# `why` are my expectations, written before generation; showing them would turn
# a blind label into a check of whether the app agreed with me.
WITHHELD = ("groundable", "why", "week5_outcome")


def render(rec: dict) -> str:
    out = rec["output"]
    L = [f"## {rec['case_id']}", ""]
    L.append(f"**request**: `{rec['recipe'] or '(no recipe named)'}` -> `{rec['constraint']}`")
    L.append("")
    L.append(f"context blocks given ({len(rec['context_chunk_ids'])}):")
    L.append("")
    L.append("```")
    L.append(rec["context"])
    L.append("```")
    L.append("")
    L.append("**output**:")
    L.append("")
    L.append("```json")
    L.append(
        json.dumps(
            {
                "can_substitute": out.get("can_substitute"),
                "base_recipe_id": out.get("base_recipe_id"),
                "title": out.get("title"),
                "swaps": out.get("swaps"),
                "ingredients": out.get("ingredients"),
                "method": out.get("method"),
                "oven": out.get("oven"),
                "allergen_warning": out.get("allergen_warning"),
                "unsupported": out.get("unsupported"),
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    L.append("```")
    L.append("")
    L.append("`sound`: [ ] true   [ ] false")
    L.append("")
    return "\n".join(L)


def main() -> None:
    ap = argparse.ArgumentParser(description="Render substitutions for blind labelling.")
    ap.add_argument("--substitutions", default=str(SUBSTITUTIONS))
    ap.add_argument("--out", default=str(OUT_DIR / "label_sheet.md"))
    ap.add_argument("--skeleton", default=str(OUT_DIR / "labels_skeleton.json"))
    args = ap.parse_args()

    path = Path(args.substitutions)
    recs = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
    subs_sha = hashlib.sha256(path.read_bytes()).hexdigest()

    header = [
        "# Blind label sheet - substitution soundness",
        "",
        f"substitutions: `{path.name}`  sha256 `{subs_sha}`",
        f"cases: {len(recs)}",
        "",
        "One binary criterion, copied from eval/judge_v1.txt:",
        "",
        "> SOUND means BOTH: (a) every claim is supported by the CONTEXT blocks shown,",
        "> every quantity appears verbatim in one, and every cited chunk_id is one of the",
        "> blocks shown and does contain the claimed evidence; and (b) the output does not",
        "> overstate what the archive supports - declining is SOUND when the archive really",
        "> does not ground the change, and UNSOUND when the evidence was in the blocks given.",
        "",
        "The case's `groundable` field and every judge verdict are deliberately absent.",
        "",
        "---",
        "",
    ]
    blocks = [render(r) for r in recs]
    Path(args.out).write_text("\n".join(header) + "\n---\n\n".join(blocks) + "\n", encoding="utf-8")

    skeleton = {
        "_note": (
            "Blind hand labels on the single binary criterion in eval/judge_v1.txt. "
            "Filled in by reading out/label_sheet.md, which shows only what the judge "
            "is shown. No judge had been run when these were written; the commit that "
            "adds this file predates the commit that adds any judge verdict file, and "
            "out/judge_v1_verdicts.json did not exist on disk."
        ),
        "criterion": "sound: every claim supported by the CONTEXT blocks shown, and no overstatement of what the archive grounds",
        "labeller": "Hari (single labeller; see the limitation noted in results_week6.md)",
        "substitutions_sha256": subs_sha,
        "labels": {r["case_id"]: {"sound": None, "note": ""} for r in recs},
    }
    Path(args.skeleton).write_text(
        json.dumps(skeleton, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"written: {args.out}  ({len(recs)} cases)")
    print(f"written: {args.skeleton}")
    print(f"substitutions sha256: {subs_sha}")


if __name__ == "__main__":
    main()
