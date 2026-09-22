"""Score the PATH, not just the destination.

    python eval/trajectory_eval.py                  # score every system in the cache
    python eval/trajectory_eval.py --system agent_v2

Weeks 6 and 7 scored outcomes: was the final answer right? An agent can reach a
right answer down a wrong path, and when it does, the outcome eval passes and
the bug ships. This scores the route.

It is a pure re-read of out/race_cache.json, which now carries the full per-lap
log including tool ARGUMENTS. No API calls, so the numbers cannot drift between
a run and the write-up that quotes them.

THE FOUR NUMBERS

  tool-choice accuracy   did the collapsed tool sequence match one of the
                         sequences eval/trajectory_cases.jsonl accepts
  argument validity      were the recipe ids and ingredient names real, or
                         fluent fiction the model produced confidently
  step efficiency        tool calls made / tool calls needed. 1.0 is ideal,
                         above 1.0 is wandering
  cost per request       reported at p50 AND max. The mean hides the one run
                         that looped chasing a substitute for a substitute,
                         and that run is what appears on the bill

THE FAILURE MODE ZOO

Every mode below is decided in code from the log. No model is asked, so the
counts cannot move because a judge had an off day.

  skipped-allergen-check   made substitutions, never called the allergen tool
  unverified-substitute    checked the original, never re-checked its own
                           replacement (one allergen call where two are needed)
  hallucinated-argument    passed a recipe_id or ingredient that is not in the
                           archive
  wrong-tool-order         collapsed sequence not in the accepted set
  redundant-call           identical (tool, arguments) pair issued twice
  unrequested-tool-use     called the allergen tool on a case that named no
                           allergen
  budget-terminated        stopped by a budget rather than by answering
  unparseable-final        final reply was not JSON the contract could read
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

from rag.tools import ALLERGENS, _corpus, _ingredient_rows  # noqa: E402

CACHE = ROOT / "out" / "race_cache.json"
TRAJ_CASES = ROOT / "eval" / "trajectory_cases.jsonl"
OUT_MD = ROOT / "out" / "trajectory.md"
OUT_JSON = ROOT / "out" / "trajectory_scores.json"

MODES = (
    "skipped-allergen-check",
    "unverified-substitute",
    "hallucinated-argument",
    "wrong-tool-order",
    "redundant-call",
    "unrequested-tool-use",
    "budget-terminated",
    "unparseable-final",
)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def load_traj_cases() -> dict[str, dict[str, Any]]:
    rows = [
        json.loads(line)
        for line in TRAJ_CASES.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    return {r["id"]: r for r in rows if "id" in r}


def collapse(seq: list[str]) -> list[str]:
    """Drop consecutive repeats.

    Two get_allergen_profile calls in a row are the correct behaviour (check the
    original, then check the replacement), not a different route. Asserting the
    exact repeat count would fail a correct three-substitution run for verifying
    three replacements instead of one.
    """
    out: list[str] = []
    for name in seq:
        if not out or out[-1] != name:
            out.append(name)
    return out


def tool_calls_from_log(log: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Every tool invocation, in order, with its arguments.

    The agent logs `tool_result` events carrying args. The workflow logs plain
    `tool` events with no args, because its arguments are written in the source
    rather than chosen, so they cannot be hallucinated.
    """
    calls = [e for e in log if e.get("event") == "tool_result"]
    if calls:
        return [{"tool": e.get("tool"), "args": e.get("args") or {}} for e in calls]
    return [
        {"tool": e.get("tool"), "args": {}}
        for e in log
        if e.get("event") == "tool" and e.get("tool")
    ]


def corpus_ingredient_names() -> set[str]:
    names: set[str] = set()
    for card in _corpus().values():
        for row in _ingredient_rows(card):
            names.add(row["ingredient"].strip().lower())
    return names


def check_arguments(
    calls: list[dict[str, Any]], all_ingredients: set[str]
) -> tuple[int, int, list[str]]:
    """Return (valid_calls, checked_calls, problems).

    Calls with no recorded arguments (the workflow's) are not counted either
    way: its arguments are hard-coded, so scoring them would flatter it against
    a system that genuinely chooses.
    """
    recipe_ids = set(_corpus().keys())
    valid = checked = 0
    problems: list[str] = []
    first_allergen_seen = False

    for call in calls:
        args = call.get("args") or {}
        if not args:
            continue
        checked += 1
        ok = True

        rid = args.get("recipe_id")
        if rid is not None and str(rid) not in recipe_ids:
            ok = False
            problems.append(f"{call['tool']}: recipe_id {rid!r} is not in the archive")

        allergen = args.get("allergen")
        if allergen is not None and str(allergen) not in ALLERGENS:
            ok = False
            problems.append(f"{call['tool']}: allergen {allergen!r} is not a known value")

        # Ingredient names: only the FIRST allergen call is checked against the
        # archive. Later calls legitimately carry proposed replacements, which
        # are new by design - "Coconut yoghurt" is not a corpus ingredient and
        # flagging it as fiction would punish the correct behaviour.
        ings = args.get("ingredients")
        if isinstance(ings, (list, tuple)) and ings and not first_allergen_seen:
            first_allergen_seen = True
            named = [str(i).strip().lower() for i in ings if str(i).strip()]
            if named:
                real = sum(1 for n in named if n in all_ingredients)
                if real / len(named) < 0.5:
                    ok = False
                    invented = [n for n in named if n not in all_ingredients][:3]
                    problems.append(
                        f"{call['tool']}: {len(named) - real}/{len(named)} ingredient names "
                        f"are not in the archive, e.g. {invented}"
                    )

        if ok:
            valid += 1

    return valid, checked, problems


def score_run(row: dict[str, Any], case: dict[str, Any], all_ingredients: set[str]) -> dict[str, Any]:
    log = row.get("log") or []
    calls = tool_calls_from_log(log)
    seq = [c["tool"] for c in calls if c["tool"]]
    collapsed = collapse(seq)

    n_allergen = sum(1 for t in seq if t == "get_allergen_profile")
    subs = [s for s in ((row.get("answer") or {}).get("substitutions") or []) if isinstance(s, dict)]
    real_subs = [
        s for s in subs
        if str(s.get("to") or "").strip().lower() not in {"", "none", "-", "n/a", "omit", "removed"}
    ]

    fired: list[str] = []

    # --- the zoo -----------------------------------------------------------
    if subs and n_allergen == 0:
        fired.append("skipped-allergen-check")
    elif real_subs and n_allergen == 1:
        fired.append("unverified-substitute")

    valid_args, checked_args, arg_problems = check_arguments(calls, all_ingredients)
    if arg_problems:
        fired.append("hallucinated-argument")

    if collapsed not in [list(s) for s in case["accepted_sequences"]]:
        fired.append("wrong-tool-order")

    seen: set[str] = set()
    for c in calls:
        key = f"{c['tool']}::{json.dumps(c.get('args') or {}, sort_keys=True)}"
        if key in seen and c.get("args"):
            fired.append("redundant-call")
            break
        seen.add(key)

    if not case["needs_substitution"] and n_allergen > 0:
        fired.append("unrequested-tool-use")

    if row.get("terminated_by"):
        fired.append("budget-terminated")

    if any(e.get("event") == "unparseable_final" for e in log):
        fired.append("unparseable-final")

    steps_taken = len(calls)

    # steps_needed is computed per RUN, not read as a constant, and this is a
    # correction to the first version of this file. It was fixed at 4 for every
    # substitution case, which scored a correct run at 0.75 efficiency whenever
    # the agent REMOVED an ingredient instead of replacing it: a removal has no
    # replacement to verify, so the fourth call is not work it skipped, it is
    # work that did not exist. A denominator that punishes correct behaviour
    # makes the metric worse than not having it.
    #
    #   2  search_recipes + scale_recipe, always
    #  +1  find which ingredients carry the allergen, if one was named
    #  +1  re-check the replacement, only if a real replacement was proposed
    steps_needed = 2
    if case["needs_substitution"]:
        steps_needed += 1
        if real_subs:
            steps_needed += 1

    return {
        "case_id": row["case_id"],
        "system": row["system"],
        "outcome_pass": bool(row.get("passed")),
        "trajectory_pass": not fired,
        "modes": fired,
        "sequence": seq,
        "collapsed": collapsed,
        "accepted": case["accepted_sequences"],
        "steps_taken": steps_taken,
        "steps_needed": steps_needed,
        "step_efficiency": (steps_taken / steps_needed) if steps_needed else 0.0,
        "args_valid": valid_args,
        "args_checked": checked_args,
        "arg_problems": arg_problems,
        "n_allergen_calls": n_allergen,
        "n_substitutions": len(subs),
        "cost_usd": float(row.get("cost_usd") or 0.0),
        "latency_ms": float(row.get("latency_ms") or 0.0),
        "total_tokens": int(row.get("total_tokens") or 0),
    }


def summarise(rows: list[dict[str, Any]]) -> dict[str, Any]:
    n = len(rows)
    if not n:
        return {}
    costs = sorted(r["cost_usd"] for r in rows)
    outcome = sum(1 for r in rows if r["outcome_pass"])
    traj = sum(1 for r in rows if r["trajectory_pass"])
    checked = sum(r["args_checked"] for r in rows)
    valid = sum(r["args_valid"] for r in rows)
    mode_counts = {m: sum(1 for r in rows if m in r["modes"]) for m in MODES}
    return {
        "n": n,
        "outcome_pass": outcome,
        "outcome_rate": outcome / n,
        "trajectory_pass": traj,
        "trajectory_rate": traj / n,
        "gap_points": (outcome / n - traj / n) * 100,
        "tool_choice_accuracy": sum(
            1 for r in rows if "wrong-tool-order" not in r["modes"]
        ) / n,
        "argument_validity": (valid / checked) if checked else None,
        "args_checked": checked,
        "step_efficiency": statistics.fmean([r["step_efficiency"] for r in rows]),
        "cost_p50": statistics.median(costs),
        "cost_max": max(costs),
        "cost_mean": statistics.fmean(costs),
        "modes": mode_counts,
    }


def fmt_pct(x: float | None) -> str:
    return "n/a" if x is None else f"{x * 100:.0f}%"


def build_report(by_system: dict[str, list[dict[str, Any]]]) -> str:
    L: list[str] = ["# Week 8 - trajectory eval\n"]
    L.append("Scored from `out/race_cache.json`. No API calls, so these numbers")
    L.append("cannot drift from the run that produced them.\n")

    sums = {s: summarise(rows) for s, rows in by_system.items()}

    L.append("## The four trajectory numbers\n")
    L.append("| system | tool-choice accuracy | argument validity | step efficiency | cost p50 | cost max |")
    L.append("|---|---|---|---|---|---|")
    for s, m in sums.items():
        L.append(
            f"| `{s}` | {fmt_pct(m['tool_choice_accuracy'])} | {fmt_pct(m['argument_validity'])} "
            f"| {m['step_efficiency']:.2f} | ${m['cost_p50']:.6f} | ${m['cost_max']:.6f} |"
        )
    L.append("")
    L.append("Mean cost is shown only to make the point that it hides the tail:\n")
    L.append("| system | cost mean | cost p50 | cost max | max / p50 |")
    L.append("|---|---|---|---|---|")
    for s, m in sums.items():
        ratio = m["cost_max"] / m["cost_p50"] if m["cost_p50"] else 0
        L.append(
            f"| `{s}` | ${m['cost_mean']:.6f} | ${m['cost_p50']:.6f} | ${m['cost_max']:.6f} | {ratio:.2f}x |"
        )
    L.append("")

    L.append("## The gap\n")
    L.append("| system | outcome pass | trajectory pass | gap |")
    L.append("|---|---|---|---|")
    for s, m in sums.items():
        L.append(
            f"| `{s}` | {m['outcome_pass']}/{m['n']} ({fmt_pct(m['outcome_rate'])}) "
            f"| {m['trajectory_pass']}/{m['n']} ({fmt_pct(m['trajectory_rate'])}) "
            f"| **{m['gap_points']:.0f} points** |"
        )
    L.append("")

    L.append("## Failure modes, per system\n")
    header = "| mode | " + " | ".join(f"`{s}`" for s in by_system) + " |"
    L.append(header)
    L.append("|---" * (len(by_system) + 1) + "|")
    for mode in MODES:
        cells = " | ".join(str(sums[s]["modes"][mode]) for s in by_system)
        L.append(f"| `{mode}` | {cells} |")
    L.append("")

    L.append("## Right answer, wrong path\n")
    for s, rows in by_system.items():
        bad = [r for r in rows if r["outcome_pass"] and not r["trajectory_pass"]]
        if not bad:
            L.append(f"`{s}`: none.\n")
            continue
        L.append(f"`{s}`: **{len(bad)} of {len(rows)}** passed the outcome eval while failing the trajectory eval.\n")
        for r in bad:
            L.append(f"- `{r['case_id']}` modes={r['modes']} path={r['collapsed']}")
        L.append("")

    L.append("## Per case\n")
    L.append("| system | case | outcome | trajectory | steps | eff | modes |")
    L.append("|---|---|---|---|---|---|---|")
    for s, rows in by_system.items():
        for r in rows:
            L.append(
                f"| `{s}` | `{r['case_id']}` | {'PASS' if r['outcome_pass'] else 'fail'} "
                f"| {'PASS' if r['trajectory_pass'] else 'fail'} "
                f"| {r['steps_taken']}/{r['steps_needed']} | {r['step_efficiency']:.2f} "
                f"| {', '.join(r['modes']) or '-'} |"
            )
    L.append("")
    return "\n".join(L) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description="Score agent trajectories.")
    ap.add_argument("--cache", default=str(CACHE))
    ap.add_argument("--system", default="")
    ap.add_argument("--out-md", default=str(OUT_MD))
    ap.add_argument("--out-json", default=str(OUT_JSON))
    args = ap.parse_args()

    cache = json.loads(Path(args.cache).read_text(encoding="utf-8"))
    traj_cases = load_traj_cases()
    all_ingredients = corpus_ingredient_names()

    missing_logs = [k for k, v in cache.items() if "log" not in v]
    if missing_logs:
        raise SystemExit(
            f"{len(missing_logs)} cached runs have no `log` field, so the path cannot be scored.\n"
            "Delete out/race_cache.json and re-run eval/run_race.py --systems all."
        )

    by_system: dict[str, list[dict[str, Any]]] = {}
    for key in sorted(cache):
        row = cache[key]
        if args.system and row["system"] != args.system:
            continue
        case = traj_cases.get(row["case_id"])
        if case is None:
            continue
        by_system.setdefault(row["system"], []).append(
            score_run(row, case, all_ingredients)
        )

    if not by_system:
        raise SystemExit("nothing to score")

    report = build_report(by_system)
    Path(args.out_md).write_text(report, encoding="utf-8")
    Path(args.out_json).write_text(
        json.dumps(
            {"summary": {s: summarise(r) for s, r in by_system.items()}, "runs": by_system},
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    def shown(p: str) -> str:
        """Path relative to the repo root when it is inside it, else as given.

        `relative_to` raises on a path that is already relative, so the plain
        version of this line crashed the whole run after the report had been
        written, on any --out-md the caller passed by hand.
        """
        try:
            return str(Path(p).resolve().relative_to(ROOT)).replace("\\", "/")
        except ValueError:
            return p

    print(report)
    print(f"written: {shown(args.out_md)}")
    print(f"written: {shown(args.out_json)}")


if __name__ == "__main__":
    main()
