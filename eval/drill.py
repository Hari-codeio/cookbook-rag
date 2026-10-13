"""Week 11: the support drill. Find one bad answer from a vague complaint, on the clock.

The complaint, and everything you will ever get:

    "someone said it recommended a dairy-free substitution that wasn't
     dairy-free, sometime last week."

No trace id, no timestamp, no recipe. A squadmate has planted one bad answer in
a copy of the log (eval/w11_plant.py). You find it with this tool alone.

    python eval/drill.py start --finder Hari            # the clock starts
    python eval/drill.py slice --since 7d --type allergen-swap --allergen contains-dairy
    python eval/drill.py slice --text "ghee" --field answer
    python eval/drill.py slice --cost-outlier
    python eval/drill.py show tr_xxxxxxxxxxxx           # spans, prompt version, context ids, answer
    python eval/drill.py found tr_xxxxxxxxxxxx --slice "input type + answer text" --timer "Priya"
    python eval/drill.py export tr_xxxxxxxxxxxx --out trace.json

THE FIVE SLICES the brief names, and the flag for each:

    time            --since 7d | --day 2026-10-13
    user            --user u_0156
    prompt version  --prompt squad-v1
    input type      --type allergen-swap  [--allergen contains-dairy]
    cost outlier    --cost-outlier        (cost more than 2 sigma above the mean)

and, added after drill 1 as the bonus (derived columns, see rag/obs_index.py):

    residue         --residue swap|rows|method|any   the answer put the allergen back
    asked           --asked contains-dairy           what the user's own words asked to avoid
    plan mismatch   --plan-mismatch                  the user asked, the planner did not pick it

plus --text, full-text over the request (--field request), the answer
(--field answer) or both. The complaint describes the OUTPUT, so the answer has
to be searchable; a tool that only searched requests would fail this drill.

`found` stops the clock, checks the candidate against the planter's SEALED
answer (a salted sha256, so the finder cannot read the answer off the seal), and
appends the attempt to out/w11/drill/drill_log.jsonl.

Not allowed during a timed drill: diffing the drill copy against the
production log, or recognising a recipe you demoed. Both find the needle
without the tooling, and neither will be there at 3am.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from rag import obs  # noqa: E402
from rag.obs_index import connect  # noqa: E402

DRILL_DIR = obs.W11_DIR / "drill"
DRILL_LOG = DRILL_DIR / "traces.jsonl"
SEAL = DRILL_DIR / "plant.sealed.json"
CLOCK = DRILL_DIR / "clock.json"
ATTEMPTS = DRILL_DIR / "drill_log.jsonl"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def default_log() -> Path:
    """The drill copy if a plant exists, otherwise the production log."""
    return DRILL_LOG if DRILL_LOG.exists() else obs.trace_path()


def _now() -> datetime:
    return datetime.now(timezone.utc)


def mmss(seconds: float) -> str:
    s = int(round(seconds))
    return f"{s // 60:02d}:{s % 60:02d}"


# --------------------------------------------------------------------------
# start / found
# --------------------------------------------------------------------------

def cmd_start(args: argparse.Namespace) -> None:
    DRILL_DIR.mkdir(parents=True, exist_ok=True)
    CLOCK.write_text(json.dumps({"started_at": _now().isoformat(), "finder": args.finder,
                                 "log": str(default_log())}), encoding="utf-8")
    print(f"clock started for {args.finder} at {_now():%H:%M:%S} UTC on {default_log()}")
    print('complaint: "someone said it recommended a dairy-free substitution that '
          "wasn't dairy-free, sometime last week.\"")


def seal_matches(trace_id: str) -> bool | None:
    if not SEAL.exists():
        return None
    seal = json.loads(SEAL.read_text(encoding="utf-8"))
    digest = hashlib.sha256(f"{seal['salt']}:{trace_id}".encode()).hexdigest()
    return digest == seal["sealed"]


def cmd_found(args: argparse.Namespace) -> None:
    if not CLOCK.exists():
        raise SystemExit("no clock running; `drill.py start` first")
    clock = json.loads(CLOCK.read_text(encoding="utf-8"))
    elapsed = (_now() - datetime.fromisoformat(clock["started_at"])).total_seconds()
    match = seal_matches(args.trace_id)
    entry = {"finder": clock["finder"], "timer": args.timer, "trace_id": args.trace_id,
             "slice": args.slice, "elapsed_s": round(elapsed, 1), "mmss": mmss(elapsed),
             "matches_seal": match, "log": clock["log"], "found_at": _now().isoformat(),
             "note": args.note}
    with ATTEMPTS.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry) + "\n")
    verdict = {True: "MATCH: this is the planted answer", False: "NO MATCH: not the planted answer",
               None: "no seal on disk; cannot verify"}[match]
    print(f"{verdict}\ntime-to-find {mmss(elapsed)}  slice: {args.slice}  "
          f"finder: {clock['finder']}  timed by: {args.timer}")
    if match:
        CLOCK.unlink()


# --------------------------------------------------------------------------
# slice
# --------------------------------------------------------------------------

def _since(spec: str) -> str:
    n, unit = int(spec[:-1]), spec[-1]
    delta = {"d": timedelta(days=n), "h": timedelta(hours=n), "m": timedelta(minutes=n)}[unit]
    return (_now() - delta).isoformat(timespec="seconds")


def _fts_query(text: str, field: str) -> str:
    """Each word becomes a quoted FTS term, so 'dairy-free' is not read as
    'dairy NOT free'. Upper-case OR / AND / NOT stay operators."""
    terms = " ".join(w if w in {"OR", "AND", "NOT"} else '"' + w.replace('"', "") + '"'
                     for w in text.split())
    if field == "both":
        return terms
    return f"{field}_text : ({terms})"


def cmd_slice(args: argparse.Namespace) -> None:
    con = connect(Path(args.log))
    where, params = [], []
    if args.since:
        where.append("r.ts >= ?")
        params.append(_since(args.since))
    if args.day:
        where.append("r.day = ?")
        params.append(args.day)
    for col, val in (("user_id", args.user), ("prompt_version", args.prompt),
                     ("input_type", args.type), ("allergen", args.allergen),
                     ("recipe_id", args.recipe)):
        if val:
            where.append(f"r.{col} = ?")
            params.append(val)
    # Week 11 bonus: the derived columns (rag/obs_index.py) turn the drill
    # from reading answers into one query.
    if args.residue:
        col = {"any": "r.residue = 1", "swap": "r.residue_swaps != ''", "rows": "r.residue_rows != ''",
               "method": "r.residue_method != ''"}[args.residue]
        where.append(col)
    if args.asked:
        where.append("(',' || r.asked || ',') LIKE ?")
        params.append(f"%,{args.asked},%")
    if args.plan_mismatch:
        where.append("r.missed != ''")
    join = ""
    if args.text:
        join = "JOIN requests_fts ON requests_fts.trace_id = r.trace_id"
        where.append("requests_fts MATCH ?")
        params.append(_fts_query(args.text, args.field))
    if args.cost_outlier:
        costs = [r[0] for r in con.execute("SELECT cost_usd FROM requests")]
        if len(costs) >= 2:
            mu, sd = statistics.mean(costs), statistics.pstdev(costs)
            where.append("r.cost_usd > ?")
            params.append(mu + 2 * sd)
            print(f"cost outlier: > ${mu + 2 * sd:.6f}  (mean ${mu:.6f} + 2 x sd ${sd:.6f}, n={len(costs)})")
    sql = (f"SELECT r.* FROM requests r {join} "
           f"{'WHERE ' + ' AND '.join(where) if where else ''} ORDER BY r.ts LIMIT ?")
    params.append(args.limit)
    rows = con.execute(sql, params).fetchall()
    total = con.execute("SELECT COUNT(*) FROM requests").fetchone()[0]
    print(f"{len(rows)} of {total} requests\n")
    print(f"{'trace_id':<16} {'ts (UTC)':<19} {'user':<7} {'type':<13} {'allergen':<17} "
          f"{'recipe':<22} {'prompt':<9} {'cost $':>9} {'secs':>5}")
    for r in rows:
        print(f"{r['trace_id']:<16} {r['ts'][:19]:<19} {r['user_id']:<7} {r['input_type']:<13} "
              f"{r['allergen'] or '-':<17} {r['recipe_id'][:22]:<22} {r['prompt_version']:<9} "
              f"{r['cost_usd']:>9.6f} {r['latency_ms'] / 1000:>5.1f}")
        if args.residue or args.plan_mismatch:
            print(f"    request: {r['request_text']!r}   asked={r['asked'] or '-'}   "
                  f"planner dropped={r['missed'] or '-'}")
            for label, col in (("swap", "residue_swaps"), ("rows", "residue_rows"), ("method", "residue_method")):
                if r[col]:
                    print(f"    residue {label:<6} {r[col][:150]}")
        if args.show_answer:
            print(f"    request: {r['request_text']}")
            for line in (r["answer_text"] or "").splitlines():
                if args.grep and args.grep.lower() not in line.lower():
                    continue
                print(f"    | {line[:150]}")
            print()


# --------------------------------------------------------------------------
# show / export
# --------------------------------------------------------------------------

def cmd_show(args: argparse.Namespace) -> None:
    rec = obs.load(args.trace_id, Path(args.log))
    req, tot = rec["request"], rec["totals"]
    print(f"trace   {rec['trace_id']}   {rec['ts']}   status={rec['status']}")
    print(f"user    {rec['user']['user_id']}  session {rec['user']['session_id']}")
    print(f"request {req['text']!r}")
    print(f"type    {req['input_type']}  allergen={req['allergen'] or '-'}  scale={req['scale_factor']}")
    print(f"prompt  {rec['prompt_version']}   " +
          "  ".join(f"{k}={v['version']}" for k, v in rec["prompts"].items()))
    print(f"context {rec['retrieval']['context_ids']}  used={rec['retrieval']['used']}")
    print(f"model   {rec['model']['used']}   git {rec['app']['git_sha']}")
    print()
    print(f"{'span':<4} {'name':<42} {'stage':<10} {'start ms':>9} {'latency ms':>10} "
          f"{'in tok':>6} {'out tok':>7} {'cost $':>10}  status")
    for s in rec["spans"]:
        indent = "  " if s.get("parent_id") else ""
        print(f"{s['span_id']:<4} {(indent + s['name'])[:42]:<42} {s['stage']:<10} {s['start_ms']:>9.1f} "
              f"{s['latency_ms']:>10.1f} {s['input_tokens']:>6} {s['output_tokens']:>7} "
              f"{s['cost_usd']:>10.6f}  {s['status'][:30]}")
    print(f"{'':<4} {'TOTAL':<42} {'':<10} {'':>9} {tot['latency_ms']:>10.1f} "
          f"{tot['input_tokens']:>6} {tot['output_tokens']:>7} {tot['cost_usd']:>10.6f}")
    print()
    print("cost by stage: " + "   ".join(
        f"{st} ${v['cost_usd']:.6f} / {v['latency_ms']:.0f} ms" for st, v in rec["cost_by_stage"].items()))
    print()
    print(rec["output"]["answer_text"] or f"(no answer: {rec['output']['error']})")


def cmd_export(args: argparse.Namespace) -> None:
    rec = obs.load(args.trace_id, Path(args.log))
    Path(args.out).write_text(json.dumps(rec, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {args.out}")


def main() -> None:
    ap = argparse.ArgumentParser(description="Week 11 support drill.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("start")
    p.add_argument("--finder", required=True)
    p.set_defaults(fn=cmd_start)

    p = sub.add_parser("found")
    p.add_argument("trace_id")
    p.add_argument("--slice", required=True, help="which slice found it, in words")
    p.add_argument("--timer", required=True, help="the squadmate holding the stopwatch")
    p.add_argument("--note", default="")
    p.set_defaults(fn=cmd_found)

    p = sub.add_parser("slice")
    p.add_argument("--log", default=str(default_log()))
    p.add_argument("--since", help="e.g. 7d, 36h")
    p.add_argument("--day", help="YYYY-MM-DD (UTC)")
    p.add_argument("--user")
    p.add_argument("--prompt", help="prompt release, e.g. squad-v1")
    p.add_argument("--type", help="input type: allergen-swap | scale-only | unresolved | unparsed")
    p.add_argument("--allergen", help="e.g. contains-dairy")
    p.add_argument("--recipe")
    p.add_argument("--text", help="full-text search terms")
    p.add_argument("--field", choices=("request", "answer", "both"), default="both")
    p.add_argument("--cost-outlier", action="store_true")
    p.add_argument("--residue", choices=("any", "swap", "rows", "method"),
                   help="bonus: answers that put an avoided allergen back (derived column)")
    p.add_argument("--asked", help="bonus: allergen the user's own words ask to avoid, e.g. contains-dairy")
    p.add_argument("--plan-mismatch", action="store_true",
                   help="bonus: the user asked to avoid an allergen the planner did not pick")
    p.add_argument("--show-answer", action="store_true", help="print each answer under its row")
    p.add_argument("--grep", help="with --show-answer, only answer lines containing this")
    p.add_argument("--limit", type=int, default=200)
    p.set_defaults(fn=cmd_slice)

    p = sub.add_parser("show")
    p.add_argument("trace_id")
    p.add_argument("--log", default=str(default_log()))
    p.set_defaults(fn=cmd_show)

    p = sub.add_parser("export")
    p.add_argument("trace_id")
    p.add_argument("--out", required=True)
    p.add_argument("--log", default=str(default_log()))
    p.set_defaults(fn=cmd_export)

    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
