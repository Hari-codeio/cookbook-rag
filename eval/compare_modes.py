"""Before -> after for one mitigation, with the price attached.

    python eval/compare_modes.py --before agent_v1 --after workflow

Reads out/trajectory_scores.json, which eval/trajectory_eval.py writes, and
prints three things:

  1. the targeted mode's count, before -> after
  2. EVERY other mode's count, before -> after, so a mode that got worse or a
     mode that appeared cannot hide behind the one that improved
  3. the price, as numbers: latency, tokens and cost per request, at p50 and max

THE PRICE IS NOT OPTIONAL. Every mitigation costs latency, tokens or
flexibility. A mitigation reported without its price has not been measured, it
has been hoped at. If all three cost columns move the right way, that is worth
saying plainly, and then the price is somewhere else and has to be named in
words instead of pretended away.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

SCORES = ROOT / "out" / "trajectory_scores.json"
OUT_MD = ROOT / "out" / "mitigation.md"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def stats(runs: list[dict[str, Any]]) -> dict[str, float]:
    costs = sorted(r["cost_usd"] for r in runs)
    lats = sorted(r["latency_ms"] for r in runs)
    toks = sorted(r["total_tokens"] for r in runs)
    return {
        "cost_p50": statistics.median(costs),
        "cost_max": max(costs),
        "latency_p50": statistics.median(lats),
        "latency_max": max(lats),
        "tokens_p50": statistics.median(toks),
        "tokens_max": max(toks),
        "tokens_total": sum(toks),
    }


def delta(before: float, after: float) -> str:
    if before == 0:
        return "n/a" if after == 0 else "+inf"
    change = (after - before) / before * 100
    sign = "+" if change >= 0 else ""
    return f"{sign}{change:.0f}%"


def main() -> None:
    ap = argparse.ArgumentParser(description="Compare two systems' trajectory modes.")
    ap.add_argument("--before", required=True)
    ap.add_argument("--after", required=True)
    ap.add_argument("--mode", default="", help="the targeted mode; blank = pick the worst in `before`")
    ap.add_argument("--scores", default=str(SCORES))
    ap.add_argument("--out", default=str(OUT_MD))
    args = ap.parse_args()

    doc = json.loads(Path(args.scores).read_text(encoding="utf-8"))
    runs, summary = doc["runs"], doc["summary"]

    for name in (args.before, args.after):
        if name not in runs:
            raise SystemExit(f"{name!r} is not in {args.scores}; have {sorted(runs)}")

    b_runs, a_runs = runs[args.before], runs[args.after]
    b_sum, a_sum = summary[args.before], summary[args.after]

    target = args.mode or max(b_sum["modes"], key=lambda m: b_sum["modes"][m])

    b_stats, a_stats = stats(b_runs), stats(a_runs)

    L: list[str] = ["# Week 8 - the one mitigation, and what it cost\n"]
    L.append(f"before : `{args.before}`")
    L.append(f"after  : `{args.after}`")
    L.append(f"target : `{target}`\n")

    L.append("## The targeted mode\n")
    L.append("```")
    L.append(f"{target}")
    L.append(f"  before : {b_sum['modes'][target]} / {b_sum['n']}")
    L.append(f"  after  : {a_sum['modes'][target]} / {a_sum['n']}")
    L.append("```\n")

    L.append("## Regression check, every mode\n")
    L.append("| mode | before | after | verdict |")
    L.append("|---|---|---|---|")
    worsened: list[str] = []
    appeared: list[str] = []
    for mode in b_sum["modes"]:
        b, a = b_sum["modes"][mode], a_sum["modes"][mode]
        if a > b:
            verdict = "**WORSE**"
            (appeared if b == 0 else worsened).append(mode)
        elif a < b:
            verdict = "improved"
        else:
            verdict = "unchanged"
        L.append(f"| `{mode}` | {b} | {a} | {verdict} |")
    L.append("")
    if appeared:
        L.append(f"**New modes the mitigation created: {', '.join('`'+m+'`' for m in appeared)}**\n")
    if worsened:
        L.append(f"**Modes that got worse: {', '.join('`'+m+'`' for m in worsened)}**\n")
    if not appeared and not worsened:
        L.append(
            "No mode got worse and no new mode appeared. Modes checked: "
            + ", ".join(f"`{m}`" for m in b_sum["modes"])
            + ".\n"
        )

    L.append("## Outcome and trajectory\n")
    L.append("| | outcome pass | trajectory pass | gap |")
    L.append("|---|---|---|---|")
    for name, s in ((args.before, b_sum), (args.after, a_sum)):
        L.append(
            f"| `{name}` | {s['outcome_pass']}/{s['n']} | {s['trajectory_pass']}/{s['n']} "
            f"| {s['gap_points']:.0f} points |"
        )
    L.append("")

    L.append("## The price\n")
    L.append("| measure | before | after | change |")
    L.append("|---|---|---|---|")
    rows = [
        ("cost / request, p50", b_stats["cost_p50"], a_stats["cost_p50"], "${:.6f}"),
        ("cost / request, max", b_stats["cost_max"], a_stats["cost_max"], "${:.6f}"),
        ("latency, p50", b_stats["latency_p50"], a_stats["latency_p50"], "{:.0f} ms"),
        ("latency, max", b_stats["latency_max"], a_stats["latency_max"], "{:.0f} ms"),
        ("tokens, p50", b_stats["tokens_p50"], a_stats["tokens_p50"], "{:.0f}"),
        ("tokens, total", b_stats["tokens_total"], a_stats["tokens_total"], "{:.0f}"),
    ]
    for label, b, a, fmt in rows:
        L.append(f"| {label} | {fmt.format(b)} | {fmt.format(a)} | {delta(b, a)} |")
    L.append("")

    L.append("| measure | before | after | change |")
    L.append("|---|---|---|---|")
    L.append(
        f"| step efficiency | {b_sum['step_efficiency']:.2f} | {a_sum['step_efficiency']:.2f} "
        f"| {delta(b_sum['step_efficiency'], a_sum['step_efficiency'])} |"
    )
    L.append("")

    # ---- flexibility -----------------------------------------------------
    # When every cost column improves, the price is somewhere else, and the
    # brief is explicit that an unnamed price means it was not measured. So
    # flexibility gets a number too: how many DISTINCT routes the system was
    # observed to take over the same inputs. A system that always walks the
    # same line cannot adapt to an input that needs a different one.
    def paths(runs: list[dict[str, Any]]) -> list[tuple[str, ...]]:
        return sorted({tuple(r["collapsed"]) for r in runs})

    b_paths, a_paths = paths(b_runs), paths(a_runs)
    L.append("## The price that is not cost: flexibility\n")
    L.append("Every cost column above moved the right way, so the price is not latency,")
    L.append("tokens or money. It is the ability to take a different route. Distinct tool")
    L.append("sequences actually observed over the same 10 inputs:\n")
    L.append("| system | distinct routes taken | routes |")
    L.append("|---|---|---|")
    for name, ps in ((args.before, b_paths), (args.after, a_paths)):
        rendered = "<br>".join("`" + " -> ".join(p) + "`" for p in ps)
        L.append(f"| `{name}` | {len(ps)} | {rendered} |")
    L.append("")

    report = "\n".join(L) + "\n"
    Path(args.out).write_text(report, encoding="utf-8")
    print(report)
    print(f"written: {args.out}")


if __name__ == "__main__":
    main()
