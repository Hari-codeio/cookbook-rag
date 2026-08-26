"""Descriptive statistics for the trace log. Deliberately has no opinions.

Counts, rates, latency percentiles, token totals. Nothing here decides whether a
trace was good or bad, because the whole point of this week is that the reading
comes before the categories. ``refused`` is reported because it is a fact the
app recorded about itself, not a verdict on the answer: a refusal can be exactly
right or badly wrong and this script cannot tell which.

    python eval/trace_summary.py
    python eval/trace_summary.py --out out/trace_summary.md
"""

from __future__ import annotations

import argparse
import statistics
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rag import trace as trc  # noqa: E402


def pct(part: int, whole: int) -> str:
    return f"{100.0 * part / whole:.0f}%" if whole else "-"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    recs = trc.read_all()
    fp = trc.file_fingerprint()

    L: list[str] = []

    def out(s: str = "") -> None:
        L.append(s)

    out("# Trace log - descriptive summary")
    out()
    out("```")
    out(f"file          : {fp['path']}")
    out(f"bytes         : {fp['bytes']:,}")
    out(f"lines         : {fp['lines']:,}   (one JSON object per line)")
    out(f"sha256        : {fp['sha256']}")
    out(f"traces        : {len(recs)}")
    out("```")
    out()

    by_source = Counter((r.get("meta") or {}).get("source", "untagged") for r in recs)
    out("| source | traces |")
    out("|---|---|")
    for k, v in sorted(by_source.items()):
        out(f"| `{k}` | {v} |")
    out()

    for source in sorted(by_source):
        sub = [r for r in recs if (r.get("meta") or {}).get("source") == source]
        errored = [r for r in sub if "error" in r]
        good = [r for r in sub if "error" not in r]
        refused = [r for r in good if r["gates"]["refused"]]
        out(f"## `{source}` - {len(sub)} traces")
        out()
        out("```")
        out(f"raised an exception : {len(errored)}")
        out(f"answered            : {len(good) - len(refused)}  ({pct(len(good) - len(refused), len(sub))})")
        out(f"refused             : {len(refused)}  ({pct(len(refused), len(sub))})")
        if good:
            lat = [r["usage"]["model_latency_ms"] for r in good]
            tin = [r["usage"]["input_tokens"] or 0 for r in good]
            tout = [r["usage"]["output_tokens"] or 0 for r in good]
            lat.sort()
            out(f"model latency ms    : p50 {statistics.median(lat):.0f}  p90 {lat[int(0.9 * (len(lat) - 1))]:.0f}  max {lat[-1]:.0f}")
            out(f"tokens in / out     : {sum(tin):,} / {sum(tout):,}")
            models = Counter(r["model"]["name"] for r in good)
            prompts = Counter(r["prompt"]["version"] for r in good)
            schemas = Counter(r.get("trace_schema") for r in good)
            out(f"models              : {dict(models)}")
            out(f"prompt versions     : {dict(prompts)}")
            out(f"trace schemas       : {dict(schemas)}")
        out("```")
        out()

        intents = Counter((r.get("meta") or {}).get("intent") for r in sub)
        if len(intents) > 1:
            out("| question shape | traces | refused |")
            out("|---|---|---|")
            for k, v in sorted(intents.items()):
                r_ = sum(
                    1
                    for r in sub
                    if (r.get("meta") or {}).get("intent") == k
                    and "error" not in r
                    and r["gates"]["refused"]
                )
                out(f"| {k} | {v} | {r_} ({pct(r_, v)}) |")
            out()

    text = "\n".join(L) + "\n"
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
        print(f"written: {args.out}")
    else:
        print(text)


if __name__ == "__main__":
    main()
