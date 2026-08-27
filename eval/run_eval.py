"""THE one command. Assertions + judge over all cases, pass rate BY MODE.

    python eval/run_eval.py                        # judge v2, cached if unchanged
    python eval/run_eval.py --judge eval/judge_v1.txt
    python eval/run_eval.py --no-judge             # assertions only, no API calls

A case passes when every assertion passes AND the judge calls it SOUND. The
table is broken out by Week-5 taxonomy mode and there is deliberately no single
headline number at the top: one overall pass rate will happily sit still while
the allergen-safety mode regresses and the flavour-plausibility mode carries it.
The overall figure is printed last, under the table, where it belongs.

Judge verdicts are cached in out/ and keyed by the sha256 of BOTH the judge
prompt and the substitutions file. Change either and the cache misses and the
judge re-runs, so a stale verdict cannot survive an edit to the thing it judged.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from eval import assertions as A  # noqa: E402
from eval.judge import load_prompt  # noqa: E402
from rag.config import GEN_PIN, GEN_PINNED_MODEL, OUT_DIR  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SUBSTITUTIONS = OUT_DIR / "substitutions_v1.jsonl"
LABELS = ROOT / "labels_25.json"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_substitutions(path: Path) -> list[dict]:
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]


def verdicts_for(judge_path: Path, subs_path: Path, sleep: float) -> dict[str, Any]:
    """Cached judge verdicts, re-run when the prompt or the substitutions change."""
    version = judge_path.stem
    cache = OUT_DIR / f"{version}_verdicts.json"
    _, prompt_sha = load_prompt(judge_path)
    subs_sha = sha(subs_path)

    if cache.exists():
        prior = json.loads(cache.read_text(encoding="utf-8"))
        if prior.get("judge_prompt_sha256") == prompt_sha and prior.get("substitutions_sha256") == subs_sha:
            print(f"judge {version}: using cached verdicts ({cache.name})")
            return prior
        print(f"judge {version}: cache is stale (prompt or substitutions changed), re-running")

    print(f"judge {version}: running")
    subprocess.run(
        [sys.executable, str(ROOT / "eval" / "judge.py"),
         "--prompt", str(judge_path), "--substitutions", str(subs_path),
         "--out", str(cache), "--sleep", str(sleep)],
        check=True,
    )
    return json.loads(cache.read_text(encoding="utf-8"))


def agreement(labels: dict[str, Any], verdicts: dict[str, Any]) -> dict[str, Any]:
    """Raw agreement on the binary criterion, plus the 2x2 that explains it."""
    shared = [c for c in labels if c in verdicts]
    tt = tf = ft = ff = 0
    disagreements = []
    for cid in shared:
        h = bool(labels[cid]["sound"])
        j = bool(verdicts[cid]["sound"])
        if h and j:
            tt += 1
        elif h and not j:
            tf += 1
            disagreements.append((cid, "human SOUND / judge UNSOUND"))
        elif not h and j:
            ft += 1
            disagreements.append((cid, "human UNSOUND / judge SOUND"))
        else:
            ff += 1
    n = len(shared)
    agree = tt + ff
    return {
        "n": n,
        "agree": agree,
        "pct": round(100.0 * agree / n, 1) if n else 0.0,
        "both_sound": tt,
        "both_unsound": ff,
        "human_sound_judge_unsound": tf,
        "human_unsound_judge_sound": ft,
        "disagreements": disagreements,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="Run the substitution eval.")
    ap.add_argument("--judge", default=str(ROOT / "eval" / "judge_v2.txt"))
    ap.add_argument("--substitutions", default=str(SUBSTITUTIONS))
    ap.add_argument("--labels", default=str(LABELS))
    ap.add_argument("--no-judge", action="store_true", help="assertions only, no API calls")
    ap.add_argument("--sleep", type=float, default=1.0)
    ap.add_argument("--out", default=None, help="also write the report to a markdown file")
    args = ap.parse_args()

    subs_path = Path(args.substitutions)
    recs = load_substitutions(subs_path)
    judge_path = Path(args.judge)

    L: list[str] = []

    def out(s: str = "") -> None:
        print(s)
        L.append(s)

    out("# Substitution eval")
    out()
    out("```")
    out(f"cases             : {len(recs)}   ({subs_path.name})")
    out(f"substitutions sha : {sha(subs_path)}")
    out(f"model pinned      : {GEN_PIN}  ({GEN_PINNED_MODEL})")
    out(f"assertions        : {len(A.ASSERTIONS) + 1}   (A1-A6)")
    out(f"judged criteria   : 1   (soundness, one binary field)")
    out("```")
    out()

    # ---- assertions -------------------------------------------------------
    asserted = {r["case_id"]: A.run_all(r["output"], model=r.get("model")) for r in recs}

    # ---- judge ------------------------------------------------------------
    verdicts: dict[str, Any] = {}
    judge_version = "(not run)"
    if not args.no_judge:
        if not judge_path.exists():
            raise SystemExit(f"{judge_path} does not exist; pass --judge or --no-judge")
        rec = verdicts_for(judge_path, subs_path, args.sleep)
        verdicts = rec["verdicts"]
        judge_version = rec["judge_version"]
        out()
        out(f"judge: `{judge_version}`  prompt sha `{rec['judge_prompt_sha256'][:16]}`")
        out()

    # ---- pass rate by mode ------------------------------------------------
    by_mode: dict[str, list[dict]] = defaultdict(list)
    for r in recs:
        by_mode[r["mode"]].append(r)

    out("## Pass rate by Week-5 mode")
    out()
    out("| mode | n | assertions pass | judged SOUND | case PASS | pass % |")
    out("|---|---|---|---|---|---|")
    tot_a = tot_j = tot_p = 0
    for mode in sorted(by_mode):
        rows = by_mode[mode]
        a_ok = sum(1 for r in rows if asserted[r["case_id"]]["passed"])
        j_ok = sum(1 for r in rows if verdicts.get(r["case_id"], {}).get("sound")) if verdicts else 0
        p_ok = sum(
            1
            for r in rows
            if asserted[r["case_id"]]["passed"]
            and (not verdicts or verdicts.get(r["case_id"], {}).get("sound"))
        )
        tot_a += a_ok
        tot_j += j_ok
        tot_p += p_ok
        jcell = f"{j_ok}/{len(rows)}" if verdicts else "-"
        out(f"| `{mode}` | {len(rows)} | {a_ok}/{len(rows)} | {jcell} | {p_ok}/{len(rows)} | {100 * p_ok // len(rows)}% |")
    n = len(recs)
    out(f"| **all** | {n} | {tot_a}/{n} | {f'{tot_j}/{n}' if verdicts else '-'} | {tot_p}/{n} | **{100 * tot_p // n}%** |")
    out()
    out("The overall row is last on purpose. It is the number most likely to sit still")
    out("while one mode regresses and another carries it.")
    out()

    # ---- which assertions bite -------------------------------------------
    out("## Assertion failures")
    out()
    fails: dict[str, list[str]] = defaultdict(list)
    for cid, res in asserted.items():
        for c in res["checks"]:
            if not c["passed"]:
                fails[f"{c['code']} {c['name']}"].append(cid)
    if not fails:
        out("None. All six assertions pass on all cases.")
    else:
        out("| assertion | failed on |")
        out("|---|---|")
        for k in sorted(fails):
            out(f"| `{k}` | {len(fails[k])}: {', '.join(sorted(fails[k]))} |")
    out()

    # ---- agreement with the hand labels -----------------------------------
    labels_path = Path(args.labels)
    if verdicts and labels_path.exists():
        labels = json.loads(labels_path.read_text(encoding="utf-8"))["labels"]
        labels = {k: v for k, v in labels.items() if v.get("sound") is not None}
        ag = agreement(labels, verdicts)
        out(f"## Agreement, hand labels vs `{judge_version}`")
        out()
        out("```")
        out(f"n compared                 : {ag['n']}")
        out(f"agree                      : {ag['agree']}")
        out(f"AGREEMENT                  : {ag['pct']}%")
        out("")
        out(f"both SOUND                 : {ag['both_sound']}")
        out(f"both UNSOUND               : {ag['both_unsound']}")
        out(f"human SOUND, judge UNSOUND : {ag['human_sound_judge_unsound']}")
        out(f"human UNSOUND, judge SOUND : {ag['human_unsound_judge_sound']}")
        out("```")
        out()
        if ag["disagreements"]:
            out("| case | disagreement | judge's reason |")
            out("|---|---|---|")
            for cid, kind in ag["disagreements"]:
                out(f"| `{cid}` | {kind} | {verdicts[cid]['reason'][:88]} |")
            out()
    elif verdicts:
        out(f"## Agreement")
        out()
        out(f"No labels at `{labels_path}`, so no agreement figure. Label first, then judge.")
        out()

    if args.out:
        Path(args.out).write_text("\n".join(L) + "\n", encoding="utf-8")
        print(f"\nwritten: {args.out}")


if __name__ == "__main__":
    main()
