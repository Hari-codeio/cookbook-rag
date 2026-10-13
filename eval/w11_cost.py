"""Week 11: cost per query, attributed by stage BEFORE anything is optimised, and the 10x numbers.

    python eval/w11_cost.py                                  # whole production log
    python eval/w11_cost.py --trace tr_xxxxxxxxxxxx          # one request, by stage
    python eval/w11_cost.py --log out/w11/suite_traces.jsonl --label green --release squad-v2

Every figure is summed from spans in the trace log, never estimated. Leaf
spans only, so a worker's cost is its laps' cost and is not counted twice.

PRICES. gemini-3.1-flash-lite list price, $0.25 / 1M input and $1.50 / 1M
output (ai.google.dev/pricing, checked 2026-10-13), stamped into every trace.
The free tier invoices $0, so this is what the same traffic costs once it
outgrows the free tier. Retrieval and tools are local (an MCP server reading
21 recipe cards, deterministic Python), so their dollar cost is $0 and their
cost is latency, reported next to it.

LIMITS for the 10x line. The free tier's per-model quotas for this model are
not on an official page we could find; the figure used is 15 requests/minute
and 500 requests/day, from a third-party table, and is overridden by the quota
a real 429 names if any span recorded one.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from rag import obs  # noqa: E402

RPM_LIMIT = 15
RPD_LIMIT = 500
LIMIT_SOURCE = "third-party free-tier table (tilnote.io), not confirmed on an official page; check AI Studio"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def step_of(span: dict[str, Any]) -> str:
    """'allergen_worker.lap2' -> 'allergen_worker'; tool calls keep their tool name."""
    name = span["name"]
    if span["stage"] == "tool":
        return name.split(".")[-1]
    return name.split(".")[0]


def pct(xs: list[float], q: float) -> float:
    xs = sorted(xs)
    return xs[max(0, math.ceil(q * len(xs)) - 1)] if xs else 0.0


def one_request(rec: dict[str, Any]) -> list[str]:
    L = [f"### `{rec['trace_id']}`: {rec['request']['text']!r}", "",
         f"release `{rec['prompt_version']}`, user `{rec['user']['user_id']}`, {rec['ts']}", "",
         "| stage | spans | model calls | latency ms | input tok | output tok | cost $ | share |",
         "|---|---|---|---|---|---|---|---|"]
    tot = rec["totals"]["cost_usd"] or 1e-12
    for st, v in rec["cost_by_stage"].items():
        L.append(f"| {st} | {v['spans']} | {v['model_calls']} | {v['latency_ms']:.0f} | {v['input_tokens']} | "
                 f"{v['output_tokens']} | {v['cost_usd']:.6f} | {100 * v['cost_usd'] / tot:.0f}% |")
    t = rec["totals"]
    L.append(f"| **request** | {len([s for s in rec['spans'] if s['stage'] != obs.CONTAINER])} | {t['model_calls']} | "
             f"{t['latency_ms']:.0f} (wall) | {t['input_tokens']} | {t['output_tokens']} | **{t['cost_usd']:.6f}** | 100% |")
    L += ["", "By step (leaf spans grouped):", "",
          "| step | stage | calls | latency ms | input tok | output tok | cost $ | share |", "|---|---|---|---|---|---|---|---|"]
    by: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for s in rec["spans"]:
        if s["stage"] != obs.CONTAINER:
            by[(step_of(s), s["stage"])].append(s)
    for (step, st), ss in by.items():
        c = sum(x["cost_usd"] for x in ss)
        L.append(f"| {step} | {st} | {len(ss)} | {sum(x['latency_ms'] for x in ss):.0f} | "
                 f"{sum(x['input_tokens'] for x in ss)} | {sum(x['output_tokens'] for x in ss)} | "
                 f"{c:.6f} | {100 * c / tot:.0f}% |")
    return L


def aggregate(rows: list[dict[str, Any]]) -> tuple[list[str], dict[str, Any]]:
    n = len(rows)
    costs = [r["totals"]["cost_usd"] for r in rows]
    lat = [r["totals"]["latency_ms"] for r in rows]
    calls = [r["totals"]["model_calls"] for r in rows]
    L = [f"{n} requests.  mean cost/request **${statistics.mean(costs):.6f}**  "
         f"median ${statistics.median(costs):.6f}  max ${max(costs):.6f}  "
         f"mean model calls {statistics.mean(calls):.2f}  p50 {pct(lat, .5) / 1000:.1f} s  "
         f"p95 {pct(lat, .95) / 1000:.1f} s", ""]

    L += ["| stage | mean cost $/request | share of $ | mean latency ms | share of summed span time |",
          "|---|---|---|---|---|"]
    st_cost: Counter = Counter()
    st_lat: Counter = Counter()
    for r in rows:
        for st, v in r["cost_by_stage"].items():
            st_cost[st] += v["cost_usd"]
            st_lat[st] += v["latency_ms"]
    tc, tl = sum(st_cost.values()) or 1e-12, sum(st_lat.values()) or 1e-12
    for st in obs.STAGES:
        L.append(f"| {st} | {st_cost[st] / n:.6f} | {100 * st_cost[st] / tc:.1f}% | "
                 f"{st_lat[st] / n:.0f} | {100 * st_lat[st] / tl:.1f}% |")
    L.append("")

    L += ["| step | stage | calls/request | in tok/request | out tok/request | $/request | share of $ |",
          "|---|---|---|---|---|---|---|"]
    acc: dict[tuple[str, str], Counter] = defaultdict(Counter)
    for r in rows:
        for s in r["spans"]:
            if s["stage"] == obs.CONTAINER:
                continue
            a = acc[(step_of(s), s["stage"])]
            a["calls"] += 1
            a["in"] += s["input_tokens"]
            a["out"] += s["output_tokens"]
            a["cost"] += s["cost_usd"]
    for (step, st), a in sorted(acc.items(), key=lambda kv: -kv[1]["cost"]):
        L.append(f"| {step} | {st} | {a['calls'] / n:.2f} | {a['in'] / n:.0f} | {a['out'] / n:.0f} | "
                 f"{a['cost'] / n:.6f} | {100 * a['cost'] / tc:.1f}% |")
    ins = sum(r["totals"]["input_tokens"] for r in rows)
    outs = sum(r["totals"]["output_tokens"] for r in rows)
    in_cost = ins / 1e6 * obs.USD_PER_1M_INPUT
    out_cost = outs / 1e6 * obs.USD_PER_1M_OUTPUT
    L += ["", f"Input tokens {ins} (${in_cost:.6f}, {100 * in_cost / (in_cost + out_cost):.0f}% of $) vs output "
              f"tokens {outs} (${out_cost:.6f}, {100 * out_cost / (in_cost + out_cost):.0f}% of $). Output is "
              f"{ins / max(outs, 1):.1f}x fewer tokens and costs 6x more per token."]
    stats = {"n": n, "mean_cost": statistics.mean(costs), "mean_calls": statistics.mean(calls),
             "p50_s": pct(lat, .5) / 1000, "p95_s": pct(lat, .95) / 1000, "stage_cost": dict(st_cost),
             "steps": {f"{k[0]}|{k[1]}": dict(v) for k, v in acc.items()}}
    return L, stats


def tenx(rows: list[dict[str, Any]]) -> tuple[list[str], str]:
    quotas = {s["attrs"].get("quota") for r in rows for s in r["spans"] if s["attrs"].get("quota")}
    rpd, src = RPD_LIMIT, LIMIT_SOURCE
    for q in quotas:
        if "PerDay" in q:
            rpd, src = int(q.split("=")[1]), f"from a real 429 in the log: {q}"
    limited = sum(r["totals"].get("rate_limited", 0) for r in rows)

    by_day: Counter = Counter()
    calls_by_day: Counter = Counter()
    per_minute: Counter = Counter()
    for r in rows:
        t0 = datetime.fromisoformat(r["ts"])
        by_day[r["ts"][:10]] += 1
        for s in r["spans"]:
            if s["stage"] == "generation":
                calls_by_day[r["ts"][:10]] += 1
                per_minute[(t0 + timedelta(milliseconds=s["start_ms"])).strftime("%Y-%m-%d %H:%M")] += 1
    day = max(by_day, key=lambda d: by_day[d])
    req_day, calls_day = by_day[day], calls_by_day[day]
    peak_min = max(per_minute.values()) if per_minute else 0
    mean_cost = statistics.mean(r["totals"]["cost_usd"] for r in rows)
    lat = [r["totals"]["latency_ms"] for r in rows]

    breaks_at_rpd = rpd / calls_day if calls_day else float("inf")
    # A published per-minute cap that our own log has already exceeded WITHOUT
    # a 429 is wrong for this key. Say so, and do not use it as the answer.
    rpm_contradicted = peak_min > RPM_LIMIT and limited == 0
    breaks_at_rpm = float("inf") if rpm_contradicted else (RPM_LIMIT / peak_min if peak_min else float("inf"))
    rpm_cell = f"~~{RPM_LIMIT}/min~~ (>= {peak_min} seen, no 429)" if rpm_contradicted else f"**{RPM_LIMIT}/min**"
    L = ["| at | requests/day | model calls/day | peak calls/min | $/day (list price) | p50 latency |",
         "|---|---|---|---|---|---|",
         f"| 1x (busiest day, {day}) | {req_day} | {calls_day} | {peak_min} | {req_day * mean_cost:.4f} | {pct(lat, .5) / 1000:.1f} s |",
         f"| 10x | {10 * req_day} | {10 * calls_day} | {10 * peak_min} | {10 * req_day * mean_cost:.4f} | "
         f"{pct(lat, .5) / 1000:.1f} s if nothing queues |",
         f"| limit | | **{rpd}/day** | {rpm_cell} | none | |", "",
         f"Daily cap is reached at **{breaks_at_rpd:.1f}x** today's volume. "
         + (f"The published {RPM_LIMIT}/min cap is contradicted by this log: the busiest minute made "
            f"{peak_min} model calls and drew no 429, so the real per-minute cap is at least {peak_min} "
            f"and cannot be the answer until a 429 names it. "
            if rpm_contradicted else
            f"The per-minute cap is reached at **{breaks_at_rpm:.1f}x** today's busiest minute. ")
         + f"429s seen at 1x: {limited}. Limits: {src}."]
    first = min(("rate limit (requests per day)", breaks_at_rpd), ("rate limit (requests per minute)", breaks_at_rpm),
                key=lambda kv: kv[1])
    line = (f"At 10x, the {first[0]} breaks first: 10x is {10 * calls_day} model calls/day against a "
            f"{rpd}/day cap, hit at {breaks_at_rpd:.1f}x, while cost is only ${10 * req_day * mean_cost:.2f}/day "
            f"and latency does not move until requests start queuing behind the cap.")
    return L, line


def main() -> None:
    ap = argparse.ArgumentParser(description="Cost per query by stage, and the 10x numbers.")
    ap.add_argument("--log", default=str(obs.trace_path()))
    ap.add_argument("--trace", help="one request, broken down by stage")
    ap.add_argument("--release", help="only traces from this release")
    ap.add_argument("--source", default="w11-traffic", help="meta.source to include ('' = all)")
    ap.add_argument("--label", default="traffic")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    log = Path(args.log)
    if args.trace:
        print("\n".join(one_request(obs.load(args.trace, log))))
        return

    rows = [r for r in obs.iter_traces(log)
            if (not args.source or (r.get("meta") or {}).get("source") == args.source)
            and (not args.release or r.get("prompt_version") == args.release)]
    L = [f"# Cost per query, `{args.label}`", "", f"log `{log.name}`, source `{args.source or 'all'}`"
         f"{', release ' + args.release if args.release else ''}. Prices: ${obs.USD_PER_1M_INPUT}/1M in, "
         f"${obs.USD_PER_1M_OUTPUT}/1M out.", "", "## By stage, then by step", ""]
    agg, stats = aggregate(rows)
    L += agg
    for kind in ("allergen-swap", "scale-only"):
        sub = [r for r in rows if r["request"]["input_type"] == kind]
        if sub:
            L += ["", f"### only `{kind}` ({len(sub)} requests)", ""]
            L += aggregate(sub)[0][:1]
    t_lines, line = tenx(rows)
    L += ["", "## 10x", ""] + t_lines + ["", f"**{line}**"]
    text = "\n".join(L) + "\n"
    print(text)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
        Path(args.out).with_suffix(".json").write_text(json.dumps(stats, indent=1), encoding="utf-8")
        print(f"written: {args.out}")


if __name__ == "__main__":
    main()
