"""Race the agent against the fixed workflow over the same 10 requests.

    python eval/run_race.py                    # agent_v2 vs workflow
    python eval/run_race.py --systems all      # adds agent_v1, the overlapping-description build

Four numbers per system, over identical inputs:

    pass rate        graded by rag/contract.check, which neither system owns
    p50 latency      median, not mean, so one 429 retry does not set the number
    total tokens     SUMMED OVER EVERY LAP. The loop re-sends the whole message
                     list each time, so counting only the final call understates
                     a 4-lap run several times over.
    cost per request total cost / 10, at the gemini-3.1-flash-lite rates in
                     rag/llm.py

Results are cached in out/race_cache.json keyed on system + case id, so a
re-run costs nothing and cannot quietly produce different numbers. Delete the
file to race again for real.
"""

from __future__ import annotations

import argparse
import csv
import json
import statistics
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from rag.agent import Budgets, run_agent  # noqa: E402
from rag.contract import check  # noqa: E402
from rag.generate import build_client  # noqa: E402
from rag.tools import (  # noqa: E402
    REGISTRY_V1,
    REGISTRY_V2,
    TOOL_SCHEMAS_V1,
    TOOL_SCHEMAS_V2,
)
from rag.workflow import run_workflow  # noqa: E402

CASES = ROOT / "eval" / "race_cases.jsonl"
OUT_DIR = ROOT / "out"
CACHE = OUT_DIR / "race_cache.json"
CSV_PATH = OUT_DIR / "race.csv"
MD_PATH = OUT_DIR / "race.md"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def load_cases() -> list[dict[str, Any]]:
    rows = [
        json.loads(line)
        for line in CASES.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    return [r for r in rows if "id" in r]


SYSTEMS = {
    "agent_v2": "agent, 3 tools, sharpened descriptions",
    "workflow": "fixed workflow, no loop",
    "agent_v1": "agent, 2 tools, overlapping descriptions",
}


def run_one(client, system: str, case: dict[str, Any]) -> dict[str, Any]:
    request = case["request"]
    if system == "workflow":
        result = run_workflow(client, request)
    elif system == "agent_v1":
        result = run_agent(
            client, request, Budgets(), TOOL_SCHEMAS_V1, REGISTRY_V1
        )
    else:
        result = run_agent(
            client, request, Budgets(), TOOL_SCHEMAS_V2, REGISTRY_V2
        )

    passed, problems = check(result.answer, case)
    return {
        "system": system,
        "case_id": case["id"],
        # Kept so a grader fix can be re-applied to a finished race without
        # spending the API again. The first race failed three cascade cases on
        # a bug in the allergen matcher, and re-running to find that out cost a
        # full set of calls that this field would have saved.
        "answer": result.answer,
        "cascade": bool(case.get("cascade")),
        "ran_ok": result.ok,
        "passed": bool(passed),
        "problems": problems,
        "laps": result.laps,
        "input_tokens": result.input_tokens,
        "output_tokens": result.output_tokens,
        "total_tokens": result.total_tokens,
        "cost_usd": round(result.cost_usd, 6),
        "latency_ms": round(result.latency_ms, 1),
        "terminated_by": result.terminated_by,
        "error": result.error,
        "tools_called": [e.get("tool") for e in result.log if e.get("event") == "tool_result"]
        or [e.get("tool") for e in result.log if e.get("event") == "tool"],
        # The FULL log, arguments included. Week 8 scores the path, not just the
        # destination, and argument validity ("were the recipe ids real or
        # fluent fiction?") cannot be checked from tool names alone. Storing it
        # here means the trajectory eval is a pure re-read of a finished race
        # rather than another 150 API calls.
        "log": result.log,
    }


def summarise(rows: list[dict[str, Any]]) -> dict[str, Any]:
    n = len(rows)
    passes = sum(1 for r in rows if r["passed"])
    latencies = sorted(r["latency_ms"] for r in rows)
    tokens = sum(r["total_tokens"] for r in rows)
    cost = sum(r["cost_usd"] for r in rows)
    casc = [r for r in rows if r["cascade"]]
    plain = [r for r in rows if not r["cascade"]]
    return {
        "n": n,
        "pass_rate": passes / n if n else 0.0,
        "passes": passes,
        "p50_latency_ms": statistics.median(latencies) if latencies else 0.0,
        "total_tokens": tokens,
        "cost_per_request_usd": cost / n if n else 0.0,
        "total_cost_usd": cost,
        "mean_laps": statistics.fmean([r["laps"] for r in rows]) if rows else 0.0,
        "cascade_pass": f"{sum(1 for r in casc if r['passed'])}/{len(casc)}",
        "plain_pass": f"{sum(1 for r in plain if r['passed'])}/{len(plain)}",
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="Race agent vs workflow.")
    ap.add_argument("--systems", default="main", choices=["main", "all"])
    ap.add_argument("--no-cache", action="store_true")
    ap.add_argument("--sleep", type=float, default=0.5)
    args = ap.parse_args()

    order = ["agent_v2", "workflow"] + (["agent_v1"] if args.systems == "all" else [])
    cases = load_cases()
    cache: dict[str, Any] = {}
    if not args.no_cache and CACHE.exists():
        cache = json.loads(CACHE.read_text(encoding="utf-8"))

    client = build_client()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []

    for system in order:
        for case in cases:
            key = f"{system}::{case['id']}"
            if key in cache:
                row = cache[key]
                cached = True
            else:
                row = run_one(client, system, case)
                cache[key] = row
                CACHE.write_text(
                    json.dumps(cache, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
                )
                cached = False
                if args.sleep:
                    time.sleep(args.sleep)
            rows.append(row)
            mark = "PASS" if row["passed"] else "fail"
            tag = "C" if row["cascade"] else " "
            print(
                f"{system:<9} {case['id']:<4} {tag} {mark}  "
                f"laps={row['laps']:<2} tok={row['total_tokens']:<6} "
                f"${row['cost_usd']:.6f} {row['latency_ms']:>7.0f}ms"
                f"{'  (cached)' if cached else ''}"
                + ("" if row["passed"] else f"  <- {'; '.join(row['problems'][:2])}")
            )
        print()

    # ---- the table -------------------------------------------------------
    summaries = {s: summarise([r for r in rows if r["system"] == s]) for s in order}

    with CSV_PATH.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(
            ["system", "description", "n", "pass_rate", "p50_latency_ms",
             "total_tokens", "cost_per_request_usd", "cascade_pass", "plain_pass", "mean_laps"]
        )
        for s in order:
            m = summaries[s]
            w.writerow([
                s, SYSTEMS[s], m["n"], f"{m['pass_rate']:.2f}",
                f"{m['p50_latency_ms']:.0f}", m["total_tokens"],
                f"{m['cost_per_request_usd']:.6f}", m["cascade_pass"],
                m["plain_pass"], f"{m['mean_laps']:.1f}",
            ])

    lines = ["# Week 7 race: agent vs fixed workflow\n"]
    lines.append(f"Same {len(cases)} requests, same tools, same pinned model, same output contract.\n")
    lines.append("| system | pass rate | p50 latency | total tokens | cost / request |")
    lines.append("|---|---|---|---|---|")
    for s in order:
        m = summaries[s]
        lines.append(
            f"| `{s}` | {m['passes']}/{m['n']} ({m['pass_rate']*100:.0f}%) "
            f"| {m['p50_latency_ms']:.0f} ms | {m['total_tokens']:,} | ${m['cost_per_request_usd']:.6f} |"
        )
    lines.append("")
    lines.append("Split by case type, which is where the average hides the answer:\n")
    lines.append("| system | 6 straightforward | 4 cascade | mean laps |")
    lines.append("|---|---|---|---|")
    for s in order:
        m = summaries[s]
        lines.append(f"| `{s}` | {m['plain_pass']} | {m['cascade_pass']} | {m['mean_laps']:.1f} |")
    lines.append("")
    lines.append("## Per case\n")
    lines.append("| system | case | cascade | result | laps | tokens | cost | latency |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for r in rows:
        lines.append(
            f"| `{r['system']}` | `{r['case_id']}` | {'yes' if r['cascade'] else 'no'} "
            f"| {'PASS' if r['passed'] else 'fail'} | {r['laps']} | {r['total_tokens']} "
            f"| ${r['cost_usd']:.6f} | {r['latency_ms']:.0f} ms |"
        )
    lines.append("")
    lines.append("## Failures, with the reason\n")
    for r in rows:
        if not r["passed"]:
            lines.append(f"- `{r['system']}` `{r['case_id']}`: {'; '.join(r['problems']) or r['error']}")
    md = "\n".join(lines) + "\n"
    MD_PATH.write_text(md, encoding="utf-8")

    print(md)
    print(f"written: {CSV_PATH.relative_to(ROOT)}")
    print(f"written: {MD_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
