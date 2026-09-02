"""Reconcile three independent reference-recipe maps into one ground truth file.

WHY THIS EXISTS AT ALL, AND WHY IT IS A SEPARATE COMMITTED STEP

RAGAS context precision needs a per-case notion of "which retrieved chunk was
relevant". Relevance has to come from a REFERENCE - a statement, made
independently of the app's answers, of which recipe card(s) a correct answer
would have to stand on. If that reference is written after reading the app's
outputs it is not a reference, it is a rationalisation, and the resulting
precision number means nothing. Same failure the hand labels were designed to
avoid in section 2 of results_week6.md.

So the reference is built under the same blind discipline as labels_25.json:

  * three readers, each given ONLY eval/substitution_cases.jsonl and the 21
    cards under data/. They were explicitly forbidden from opening
    out/substitutions_v1.jsonl, out/judge_*_verdicts.json, labels_25.json,
    results_week6.md or anything else under out/.
  * the three were deliberately DECORRELATED - same question, three different
    reading strategies (case-first, card-first, adversarial) - so that a shared
    mistake has to survive three different routes to the answer.
  * this file is committed BEFORE eval/run_ragas.py is ever run, so the commit
    order proves the reference did not move to fit the scores.

THE RECONCILIATION RULE, STATED BEFORE IT IS APPLIED

Per recipe_id majority. A recipe_id enters base_recipe_ids (or
donor_recipe_ids) iff at least 2 of the 3 readers listed it there. `ambiguous`
is likewise a majority vote. Nothing is hand-adjusted: run this script and you
get the file byte for byte.

Every id the readers split on is recorded in `split_on`, so a disagreement is
visible in the artefact rather than smoothed away. The three raw maps are kept
at out/ragas_raw/reference_maps.json for audit.

    python eval/build_ragas_reference.py
"""

from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

RAW = ROOT / "out" / "ragas_raw" / "reference_maps.json"
CASES = ROOT / "eval" / "substitution_cases.jsonl"
SUBS = ROOT / "out" / "substitutions_v1.jsonl"
OUT = ROOT / "eval" / "ragas_reference.json"

READERS = ("case-first", "card-first", "adversarial")
MAJORITY = 2  # of 3

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    raw = json.loads(RAW.read_text(encoding="utf-8"))
    if len(raw) != len(READERS):
        raise SystemExit(f"expected {len(READERS)} reference maps, got {len(raw)}")

    # reader name -> case id -> that reader's entry
    per_reader = {
        name: {c["id"]: c for c in payload["cases"]}
        for name, payload in zip(READERS, raw)
    }

    case_ids = [
        json.loads(line)["id"]
        for line in CASES.read_text(encoding="utf-8").splitlines()
        if line.strip() and "id" in json.loads(line)
    ]

    reconciled: dict[str, dict] = {}
    n_split = 0

    for cid in case_ids:
        entries = {n: per_reader[n][cid] for n in READERS if cid in per_reader[n]}
        if len(entries) != len(READERS):
            raise SystemExit(f"{cid}: only {len(entries)} readers covered it")

        merged: dict[str, list[str]] = {}
        split_on: dict[str, dict[str, int]] = {}

        for field in ("base_recipe_ids", "donor_recipe_ids"):
            votes: Counter[str] = Counter()
            for name in READERS:
                for rid in set(entries[name].get(field) or []):
                    votes[rid] += 1
            merged[field] = sorted(r for r, n in votes.items() if n >= MAJORITY)
            split = {r: n for r, n in votes.items() if 0 < n < len(READERS)}
            if split:
                split_on[field] = dict(sorted(split.items()))

        ambiguous_votes = sum(1 for n in READERS if entries[n].get("ambiguous"))
        conf = Counter(entries[n].get("confidence") for n in READERS)

        relevant = sorted(set(merged["base_recipe_ids"]) | set(merged["donor_recipe_ids"]))

        if split_on:
            n_split += 1

        reconciled[cid] = {
            "base_recipe_ids": merged["base_recipe_ids"],
            "donor_recipe_ids": merged["donor_recipe_ids"],
            # base UNION donor. This is the set context precision treats as
            # relevant: a correct answer has to stand on the dish's own card,
            # and on whichever card demonstrates the requested change.
            "relevant_recipe_ids": relevant,
            "ambiguous": ambiguous_votes >= MAJORITY,
            "ambiguous_votes": f"{ambiguous_votes}/{len(READERS)}",
            "confidence": conf.most_common(1)[0][0],
            "unanimous": not split_on,
            "split_on": split_on,
            "why": {n: entries[n].get("why", "") for n in READERS},
        }

    record = {
        "_note": (
            "GROUND TRUTH for RAGAS context precision. Which recipe card(s) a correct "
            "answer to each case would have to ground itself in. Built 2026-09-03 by "
            "three independent readers who saw ONLY eval/substitution_cases.jsonl and "
            "the 21 cards under data/ - never the app's answers, the hand labels or the "
            "judge verdicts. Reconciled by per-recipe_id majority (>=2 of 3); see "
            "eval/build_ragas_reference.py for the rule, stated before it was applied. "
            "Committed BEFORE eval/run_ragas.py was run so the order is provable. "
            "relevant_recipe_ids = base UNION donor and is the set the metric uses."
        ),
        "built": "2026-09-03",
        "readers": list(READERS),
        "reader_strategies": {
            "case-first": "walk the case list, then hunt the corpus for a donor per case",
            "card-first": "map the corpus's near-duplicate families first, assign cases after",
            "adversarial": "state the obvious pick, then actively try to break it; keep it only if unbroken",
        },
        "reconciliation_rule": f"per recipe_id majority, >={MAJORITY} of {len(READERS)} readers",
        "cases_file": str(CASES.relative_to(ROOT)).replace("\\", "/"),
        "cases_sha256": sha256(CASES),
        "substitutions_sha256": sha256(SUBS) if SUBS.exists() else None,
        "n": len(reconciled),
        "n_cases_with_a_split": n_split,
        "raw_maps": "out/ragas_raw/reference_maps.json",
        "reference": reconciled,
    }

    OUT.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    n_unan = sum(1 for v in reconciled.values() if v["unanimous"])
    n_amb = sum(1 for v in reconciled.values() if v["ambiguous"])
    n_nodonor = sum(1 for v in reconciled.values() if not v["donor_recipe_ids"])
    print(f"cases                     : {len(reconciled)}")
    print(f"unanimous across 3 readers: {n_unan}/{len(reconciled)}")
    print(f"had a split (recorded)    : {n_split}")
    print(f"flagged ambiguous         : {n_amb}")
    print(f"no donor in the archive   : {n_nodonor}")
    print(f"written                   : {OUT.relative_to(ROOT)}")
    print()
    for cid, v in reconciled.items():
        if v["split_on"]:
            print(f"  split {cid}: {v['split_on']}")


if __name__ == "__main__":
    main()
