"""Generate the week's traces by running the shipped app over the traffic pool.

This is the data-collection step for Week 5, and it is deliberately dumb: it
reads a query, calls ``rag.generate.answer`` with the SHIPPED configuration, and
lets ``rag.trace`` append whatever came back. It does not score anything, it
does not know what a correct answer looks like, and it never skips a query
because the output looked bad. Filtering here would put a thumb on the scale of
every frequency in taxonomy.md.

The shipped configuration is dense retrieval, ``strategy=structure``, ``k=5``,
both gates on. That is what Week 4 concluded with: the cross-encoder reranker
won one question out of twelve for 3.4x the latency and was not shipped, so the
app that ran this week is the Week 3 retriever.

    python eval/run_traffic.py --set random          # 150 queries -> out/traces.jsonl
    python eval/run_traffic.py --set demo            # the 12 curated demo questions
    python eval/run_traffic.py --set random --limit 5 --dry-run

The pool file's sha256 is printed on every run and written into out/traffic.lock.json
on the first run, so the traffic cannot quietly be re-mixed after the fact.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rag import trace as trc  # noqa: E402
from rag.config import OUT_DIR, TOP_K  # noqa: E402
from rag.generate import answer, build_client  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
RANDOM_POOL = ROOT / "eval" / "traffic_queries.jsonl"
DEMO_POOL = ROOT / "eval" / "golden_set.jsonl"
TRAFFIC_LOCK = OUT_DIR / "traffic.lock.json"

# The shipped configuration. Held constant for every trace in the log, so a
# difference between two traces is a difference in the question, not in the app.
SHIPPED = {"strategy": "structure", "retriever": "dense", "k": TOP_K, "code_gate": True}


def load_pool(path: Path, source: str) -> list[dict]:
    """One dict per query. Lines whose object has a ``_note`` key are comments."""
    rows: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        obj = json.loads(line)
        if "_note" in obj:
            continue
        if source == "demo":
            # The golden set carries expected_chunk_id / known_answer. They are
            # deliberately NOT copied into the trace: open-coding is supposed to
            # describe what the app produced, and a trace carrying its own answer
            # key invites reading the key instead of the output.
            rows.append({"id": obj["id"], "intent": "curated-demo", "query": obj["question"]})
        else:
            rows.append({"id": obj["id"], "intent": obj["intent"], "query": obj["query"]})
    return rows


def lock_pool(path: Path, label: str) -> str:
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    locks = {}
    if TRAFFIC_LOCK.exists():
        locks = json.loads(TRAFFIC_LOCK.read_text(encoding="utf-8"))
    prior = locks.get(label)
    if prior and prior != digest:
        print(
            f"WARNING: {path.name} has changed since the locked run "
            f"({prior[:12]} -> {digest[:12]}). Traces from before and after are "
            f"not from the same pool.",
            file=sys.stderr,
        )
    locks[label] = digest
    TRAFFIC_LOCK.write_text(json.dumps(locks, indent=2) + "\n", encoding="utf-8")
    return digest


def main() -> None:
    ap = argparse.ArgumentParser(description="Run the traffic pool and log traces.")
    ap.add_argument("--set", dest="which", default="random", choices=["random", "demo"])
    ap.add_argument("--limit", type=int, default=0, help="0 = the whole pool")
    ap.add_argument("--sleep", type=float, default=0.6, help="seconds between calls")
    ap.add_argument("--dry-run", action="store_true", help="print the plan, call nothing")
    args = ap.parse_args()

    pool_path = RANDOM_POOL if args.which == "random" else DEMO_POOL
    source = "random-traffic" if args.which == "random" else "curated-demo"
    rows = load_pool(pool_path, args.which)
    if args.limit:
        rows = rows[: args.limit]

    digest = lock_pool(pool_path, args.which)
    print(f"pool        : {pool_path.name}  ({len(rows)} queries)")
    print(f"pool sha256 : {digest}")
    print(f"source tag  : {source}")
    print(f"config      : {SHIPPED}")
    print(f"trace file  : {trc.TRACE_PATH}")
    print()

    if args.dry_run:
        for r in rows:
            print(f"  {r['id']}  [{r['intent']}]  {r['query']}")
        return

    client = build_client()
    ok = failed = 0
    started = time.time()

    for i, row in enumerate(rows, start=1):
        try:
            result = answer(
                row["query"],
                SHIPPED["strategy"],
                k=SHIPPED["k"],
                code_gate=SHIPPED["code_gate"],
                client=client,
                retriever=SHIPPED["retriever"],
                trace=True,
                trace_meta={
                    "source": source,
                    "query_id": row["id"],
                    "intent": row["intent"],
                    "pool_sha256": digest,
                },
            )
            ok += 1
            flag = "REFUSED" if result.refused else "answered"
            print(f"[{i:>3}/{len(rows)}] {row['id']}  {result.trace_id}  {flag:<8}  {row['query'][:56]}")
        except Exception as exc:  # noqa: BLE001 - one bad query must not end the run
            failed += 1
            print(f"[{i:>3}/{len(rows)}] {row['id']}  ERROR  {type(exc).__name__}: {exc}", file=sys.stderr)
            # An error is itself part of the week's behaviour, so it is logged
            # rather than silently dropped.
            trc.write(
                {
                    "trace_schema": trc.TRACE_SCHEMA,
                    "trace_id": trc.new_trace_id(),
                    "ts": trc.utc_now(),
                    "app": {"git_sha": trc.git_sha(), "entrypoint": "eval/run_traffic.py"},
                    "meta": {
                        "source": source,
                        "query_id": row["id"],
                        "intent": row["intent"],
                        "pool_sha256": digest,
                    },
                    "request": {"query": row["query"], **SHIPPED},
                    "error": {"type": type(exc).__name__, "message": str(exc)},
                }
            )
        if args.sleep:
            time.sleep(args.sleep)

    elapsed = time.time() - started
    print()
    print(f"done: {ok} logged, {failed} errored, {elapsed / 60:.1f} min")
    print(json.dumps(trc.file_fingerprint(), indent=2))


if __name__ == "__main__":
    main()
