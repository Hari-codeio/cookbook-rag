"""Week 11: THE suite. Every case the squad is measured on, live, graded, with pass counts.

    python eval/run_suite.py --label red                    # the release that is live now
    python eval/run_suite.py --label green --release squad-v2

The cases are the 10 the squad has been raced on since Week 7
(eval/race_cases.jsonl, unchanged) plus every regression case turned from a
real failure (eval/regression_cases.jsonl). Week 10 established that the
Week 6 file grades rag/substitute.py's output shape, which the squad does not
produce, so this is the squad's suite; see results_week11.md section 0.

Every case runs LIVE against the squad, every time. Grading a cached answer
would only prove the grader changed. The suite's job is to say what the app
does today, so a fix that quietly breaks another case shows up in the count.

Two grades per case, side by side:
    w10   rag/contract.check points 1-5 only, the grader Week 10 reported
    now   points 1-6, with the Week 11 residue test

Traces go to out/w11/suite_traces.jsonl, never into the production log, so a
suite run cannot pollute the haystack the drill searches.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ.setdefault("OBS_TRACE_PATH", str(ROOT / "out" / "w11" / "suite_traces.jsonl"))

from rag import obs  # noqa: E402
from rag.contract import check  # noqa: E402
from rag.generate import build_client  # noqa: E402
from rag.mcp_host import MCPHost  # noqa: E402
from rag.squad import RELEASE, run_squad  # noqa: E402

RACE = ROOT / "eval" / "race_cases.jsonl"
REGRESSION = ROOT / "eval" / "regression_cases.jsonl"
OUT = ROOT / "out" / "w11"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def load(path: Path, kind: str) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
    return [{**r, "_kind": kind} for r in rows if "id" in r]


def main() -> None:
    ap = argparse.ArgumentParser(description="Run the squad suite live.")
    ap.add_argument("--label", required=True, help="e.g. red, green; names the output files")
    ap.add_argument("--release", default=None, help=f"prompt release (default: {RELEASE})")
    ap.add_argument("--only", default="", help="comma-separated case ids")
    ap.add_argument("--gap", type=float, default=5.0)
    args = ap.parse_args()

    cases = load(RACE, "race") + load(REGRESSION, "regression")
    if args.only:
        keep = set(args.only.split(","))
        cases = [c for c in cases if c["id"] in keep]
    release = args.release or RELEASE

    lines: list[str] = []

    def out(s: str = "") -> None:
        print(s, flush=True)
        lines.append(s)

    out(f"# Suite run `{args.label}`")
    out()
    out("```")
    out(f"release   : {release}")
    out(f"cases     : {len(cases)}  ({sum(c['_kind'] == 'race' for c in cases)} race + "
        f"{sum(c['_kind'] == 'regression' for c in cases)} regression)")
    out(f"started   : {obs.utc_now()}")
    out(f"traces    : {obs.trace_path()}")
    out("```")
    out()

    results = []
    client = build_client()
    with MCPHost() as host:
        for i, case in enumerate(cases, start=1):
            r = run_squad(client, host, case["request"], user_id="suite", session_id=f"suite-{args.label}",
                          release=release, trace_meta={"source": "suite", "label": args.label,
                                                       "case_id": case["id"]})
            ok_w10, probs_w10 = check(r.answer, case, residue=False)
            ok_now, probs_now = check(r.answer, case)
            results.append({"case_id": case["id"], "kind": case["_kind"], "trace_id": r.trace_id,
                            "release": r.release, "w10_pass": ok_w10, "pass": ok_now,
                            "problems": probs_now, "ran_ok": r.ok, "error": r.error,
                            "calls": r.laps, "tokens": r.total_tokens, "cost_usd": round(r.cost_usd, 8),
                            "latency_ms": round(r.latency_ms, 1), "answer": r.answer})
            print(f"  [{i:>2}/{len(cases)}] {case['id']:<8} {'PASS' if ok_now else 'FAIL'}  "
                  f"(w10 grader {'PASS' if ok_w10 else 'FAIL'})  {r.trace_id}  {'; '.join(probs_now)[:110]}",
                  flush=True)
            if args.gap and i < len(cases):
                time.sleep(args.gap)

    n = len(results)
    p = sum(r["pass"] for r in results)
    p10 = sum(r["w10_pass"] for r in results)
    out("| case | kind | w10 grader (1-5) | **now (1-6)** | trace | why it failed |")
    out("|---|---|---|---|---|---|")
    for r in results:
        why = "; ".join(r["problems"]) or (r["error"] or "")
        out(f"| `{r['case_id']}` | {r['kind']} | {'PASS' if r['w10_pass'] else 'FAIL'} | "
            f"**{'PASS' if r['pass'] else 'FAIL'}** | `{r['trace_id']}` | {why[:160]} |")
    out()
    out("```")
    out(f"SUITE {args.label.upper()}: {p}/{n} pass   (release {release})")
    out(f"same answers, Week 10 grader: {p10}/{n}")
    out(f"tokens {sum(r['tokens'] for r in results)}   cost ${sum(r['cost_usd'] for r in results):.6f}   "
        f"model calls {sum(r['calls'] for r in results)}")
    out("```")

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"suite_{args.label}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (OUT / f"suite_{args.label}.json").write_text(json.dumps(results, indent=1, ensure_ascii=False),
                                                  encoding="utf-8")
    print(f"\nwritten: {OUT / f'suite_{args.label}.md'}")


if __name__ == "__main__":
    main()
