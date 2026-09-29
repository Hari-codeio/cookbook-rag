"""Race the kitchen squad against the single agent on the same 10 cases.

    python eval/run_squad_race.py                 # the race (cached per arm + case)
    python eval/run_squad_race.py --inject s01    # the squad again on one case, allergen worker -> HTTP 500

THE RULER DOES NOT MOVE. Both arms get eval/race_cases.jsonl, the 10 requests
the single agent has been measured on since Week 7, unchanged, and both are
graded by rag/contract.check, which neither arm owns. No case was added,
removed or reworded for the orchestrator.

SAME EVERYTHING ELSE. One MCPHost (mcp_config.json, the Week 9 servers) serves
both arms, so both reach the same tools the same way. Same pinned model, same
token accounting (summed over every model call), same price constants. Arms are
INTERLEAVED per case (single, then squad), so a slow minute on the API lands on
both arms rather than on whichever happened to be running.

Four numbers per arm: pass rate, p50 and p99 latency, total tokens, cost per
question. p99 over 10 samples is the nearest-rank value, rank ceil(0.99 * 10) =
10, which is the slowest run. It is reported anyway, because it is the number a
client screenshots.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from rag.contract import check  # noqa: E402
from rag.generate import build_client  # noqa: E402
from rag.mcp_host import MCPHost  # noqa: E402
from rag.squad import run_squad  # noqa: E402

CASES = ROOT / "eval" / "race_cases.jsonl"
OUT = ROOT / "out"
CACHE = OUT / "squad_race_cache.json"
FAILURE = OUT / "failure_run.json"
TABLE = ROOT / "race_table.md"
HANDOFFS = ROOT / "handoffs.log"
ARMS = ("single", "squad")
# CONTROL arm, not one of the two the brief asks for: the same single agent on
# the Week 9 SERVER-ONE config (3 tools, commit f499c39). It answers "does the
# squad beat the pattern, or only a single agent bloated by 6 tools?"
CONTROL = "single_3tools"
CONTROL_CONFIG = ROOT / "eval" / "mcp_config.server_one.json"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def load_cases() -> list[dict[str, Any]]:
    rows = [json.loads(l) for l in CASES.read_text(encoding="utf-8").splitlines() if l.strip()]
    return [r for r in rows if "id" in r]


def run_one(client, host: MCPHost, arm: str, case: dict[str, Any], inject_500: bool = False) -> dict[str, Any]:
    if arm in ("single", CONTROL):
        result = host.run(client, case["request"])
        hops = [
            {"name": f"single_agent lap {e['lap']} (whole conversation re-sent)",
             "model_calls": 1, "input_tokens": e["input_tokens"], "output_tokens": e["output_tokens"],
             "total_tokens": e["input_tokens"] + e["output_tokens"],
             "detail": {"tool_calls": e["tool_calls"]}}
            for e in result.log if e.get("event") == "model_turn"
        ]
    else:
        result = run_squad(client, host, case["request"], inject_500=inject_500)
        hops = [{**asdict(h), "total_tokens": h.total_tokens} for h in result.handoffs]
    passed, problems = check(result.answer, case)
    return {
        "arm": arm, "case_id": case["id"], "cascade": bool(case.get("cascade")),
        "passed": bool(passed), "problems": problems, "ran_ok": result.ok,
        "error": result.error, "terminated_by": result.terminated_by,
        "model_calls": result.laps, "input_tokens": result.input_tokens,
        "output_tokens": result.output_tokens, "total_tokens": result.total_tokens,
        "cost_usd": round(result.cost_usd, 6), "latency_ms": round(result.latency_ms, 1),
        "handoffs": hops, "answer": result.answer, "log": result.log,
    }


def p99(values: list[float]) -> float:
    ordered = sorted(values)
    return ordered[max(0, math.ceil(0.99 * len(ordered)) - 1)]


def summarise(rows: list[dict[str, Any]]) -> dict[str, Any]:
    lat = [r["latency_ms"] for r in rows]
    return {
        "passes": sum(r["passed"] for r in rows), "n": len(rows),
        "p50": statistics.median(lat), "p99": p99(lat),
        "tokens": sum(r["total_tokens"] for r in rows),
        "cost_per_q": sum(r["cost_usd"] for r in rows) / len(rows),
        "calls": statistics.fmean(r["model_calls"] for r in rows),
    }


def write_outputs(cases: list[dict[str, Any]], rows: list[dict[str, Any]]) -> None:
    s = {a: summarise([r for r in rows if r["arm"] == a]) for a in ARMS}
    mult = s["squad"]["tokens"] / s["single"]["tokens"]

    shares: dict[str, int] = {}
    for r in rows:
        if r["arm"] == "squad":
            for h in r["handoffs"]:
                shares[h["name"]] = shares.get(h["name"], 0) + h["total_tokens"]
    top_name, top_tokens = max(shares.items(), key=lambda kv: kv[1])
    top_share = top_tokens / s["squad"]["tokens"]

    # ---- handoffs.log -----------------------------------------------------
    lines = ["# handoffs.log: every hand-off in the race, with the tokens it consumed",
             "# tokens = input + output summed over every model call inside the hop",
             "# (a worker hop contains that worker's whole agent loop).",
             "# single-agent rows are its laps: it has no hand-offs, but every lap re-sends the whole conversation.",
             "#",
             f"# {'case':<4} {'arm':<6} {'hand-off':<58} {'calls':>5} {'in':>6} {'out':>5} {'total':>6}  status"]
    for case in cases:
        for arm in ARMS:
            r = next(x for x in rows if x["arm"] == arm and x["case_id"] == case["id"])
            for h in r["handoffs"]:
                lines.append(f"  {case['id']:<4} {arm:<6} {h['name']:<58} {h['model_calls']:>5} "
                             f"{h['input_tokens']:>6} {h['output_tokens']:>5} {h['total_tokens']:>6}  "
                             f"{h.get('status', 'ok')}")
            lines.append(f"  {case['id']:<4} {arm:<6} {'= case total':<58} {r['model_calls']:>5} "
                         f"{r['input_tokens']:>6} {r['output_tokens']:>5} {r['total_tokens']:>6}")
    lines += ["", "# squad tokens by hand-off, all 10 cases"]
    for name, tok in sorted(shares.items(), key=lambda kv: -kv[1]):
        lines.append(f"  {name:<58} {tok:>7}  {tok / s['squad']['tokens'] * 100:5.1f}%")
    lines.append(f"  {'TOTAL squad':<58} {s['squad']['tokens']:>7}")
    lines.append(f"  {'TOTAL single':<58} {s['single']['tokens']:>7}")
    HANDOFFS.write_text("\n".join(lines) + "\n", encoding="utf-8")

    # ---- race_table.md ----------------------------------------------------
    t = ["# Race: kitchen squad vs single agent", "",
         f"Same {len(cases)} cases ({', '.join(c['id'] for c in cases)}) from `eval/race_cases.jsonl`,",
         "graded by `rag/contract.check`, same pinned model, same MCP servers, arms interleaved per case.", "",
         "| arm | pass rate | p50 latency | p99 latency | total tokens | cost / question |",
         "|---|---|---|---|---|---|"]
    for a, label in (("single", "single agent (6 MCP tools)"), ("squad", "squad (orchestrator + 2 workers)")):
        m = s[a]
        t.append(f"| {label} | {m['passes']}/{m['n']} | {m['p50'] / 1000:.1f} s | {m['p99'] / 1000:.1f} s "
                 f"| {m['tokens']:,} | ${m['cost_per_q']:.6f} |")
    ctrl = [r for r in rows if r["arm"] == CONTROL]
    if ctrl:
        m = summarise(ctrl)
        t.append(f"| *control:* single agent, 3 tools (server one only) | {m['passes']}/{m['n']} | {m['p50'] / 1000:.1f} s "
                 f"| {m['p99'] / 1000:.1f} s | {m['tokens']:,} | ${m['cost_per_q']:.6f} |")
        t.append("")
        t.append(f"Control multiplier, squad / 3-tool single: {s['squad']['tokens']:,} / {m['tokens']:,} "
                 f"= {s['squad']['tokens'] / m['tokens']:.1f}x. The control ran after the race, not interleaved with it.")
    t += ["", f"Mean model calls per question: single {s['single']['calls']:.1f}, squad {s['squad']['calls']:.1f}.",
          "p99 over 10 runs is nearest-rank, i.e. the slowest run.", "",
          f"**Context re-send multiplier: {s['squad']['tokens']:,} / {s['single']['tokens']:,} = {mult:.1f}x.**",
          f"Largest squad token share: `{top_name}`, {top_share * 100:.0f}% of all squad tokens.", "",
          "## Per case", "",
          "| case | cascade | single | squad | single tokens | squad tokens | single s | squad s |",
          "|---|---|---|---|---|---|---|---|"]
    for case in cases:
        a = next(x for x in rows if x["arm"] == "single" and x["case_id"] == case["id"])
        b = next(x for x in rows if x["arm"] == "squad" and x["case_id"] == case["id"])
        t.append(f"| `{case['id']}` | {'yes' if case.get('cascade') else 'no'} "
                 f"| {'PASS' if a['passed'] else 'fail'} | {'PASS' if b['passed'] else 'fail'} "
                 f"| {a['total_tokens']:,} | {b['total_tokens']:,} "
                 f"| {a['latency_ms'] / 1000:.1f} | {b['latency_ms'] / 1000:.1f} |")
    fails = [r for r in rows if not r["passed"]]
    t += ["", "## Failures, with the grader's reason", ""]
    t += [f"- {r['arm']} `{r['case_id']}`: {'; '.join(r['problems']) or r['error']}"
          + (f" (terminated_by {r['terminated_by']})" if r["terminated_by"] else "") for r in fails] or ["- none"]
    TABLE.write_text("\n".join(t) + "\n", encoding="utf-8")
    print("\n".join(t))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--inject", metavar="CASE_ID", help="run the squad on one case with the allergen worker failing")
    ap.add_argument("--sleep", type=float, default=1.0)
    ap.add_argument("--control", action="store_true", help="also run the 3-tool single agent (control arm)")
    args = ap.parse_args()

    cases = load_cases()
    client = build_client()
    with MCPHost() as host:
        if args.inject:
            case = next(c for c in cases if c["id"] == args.inject)
            row = run_one(client, host, "squad", case, inject_500=True)
            FAILURE.write_text(json.dumps(row, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            print(json.dumps({k: row[k] for k in ("case_id", "passed", "problems", "total_tokens")}, indent=2))
            print(json.dumps(row["answer"], indent=2, ensure_ascii=False))
            return

        cache = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}
        rows = []
        for case in cases:
            for arm in ARMS:
                key = f"{arm}::{case['id']}"
                if key not in cache:
                    cache[key] = run_one(client, host, arm, case)
                    CACHE.write_text(json.dumps(cache, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
                    time.sleep(args.sleep)
                r = cache[key]
                rows.append(r)
                print(f"{case['id']:<4} {arm:<13} {'PASS' if r['passed'] else 'fail'} calls={r['model_calls']:<2} "
                      f"tok={r['total_tokens']:<6} {r['latency_ms'] / 1000:6.1f}s"
                      + ("" if r["passed"] else f"  <- {'; '.join(r['problems'][:2])}"), flush=True)
        if args.control:
            with MCPHost(CONTROL_CONFIG) as control_host:
                for case in cases:
                    key = f"{CONTROL}::{case['id']}"
                    if key not in cache:
                        cache[key] = run_one(client, control_host, CONTROL, case)
                        CACHE.write_text(json.dumps(cache, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
                        time.sleep(args.sleep)
                    r = cache[key]
                    rows.append(r)
                    print(f"{case['id']:<4} {CONTROL:<13} {'PASS' if r['passed'] else 'fail'} calls={r['model_calls']:<2} "
                          f"tok={r['total_tokens']:<6} {r['latency_ms'] / 1000:6.1f}s"
                          + ("" if r["passed"] else f"  <- {'; '.join(r['problems'][:2])}"), flush=True)
    write_outputs(cases, rows)


if __name__ == "__main__":
    main()
