"""Week 11: send the traffic pool through the live squad, one trace per request.

    python eval/w11_traffic.py                 # all 36, 15 s apart, into out/w11/traces.jsonl
    python eval/w11_traffic.py --limit 3 --gap 0

This is the PRODUCTION log the support drill searches. Every line is a real run
of rag.squad on the pinned model, stamped with the test user and session it
came from. Nothing in it is edited afterwards. A planted record for the drill
goes into a COPY of this log (eval/w11_plant.py), never into this file.

The gap between requests is arrival pacing, not politeness. A burst of 36
requests at ~6 model calls each would be ~200 calls in a few minutes, and the
free tier's per-minute cap would turn the run into a rate-limit test. Any 429
that still happens is recorded on its span (rate_limited, quota), which is
evidence for the 10x plan rather than noise.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from rag import obs  # noqa: E402
from rag.generate import build_client  # noqa: E402
from rag.mcp_host import MCPHost  # noqa: E402
from rag.squad import RELEASE, run_squad  # noqa: E402

POOL = ROOT / "eval" / "w11_traffic_pool.jsonl"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def load_pool(path: Path = POOL) -> list[dict]:
    rows = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
    return [r for r in rows if "id" in r]


def main() -> None:
    ap = argparse.ArgumentParser(description="Run the Week 11 traffic pool through the squad.")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--start", type=int, default=0, help="skip the first N (resume after a stop)")
    ap.add_argument("--gap", type=float, default=15.0, help="seconds between requests")
    args = ap.parse_args()

    pool = load_pool()[args.start:]
    if args.limit:
        pool = pool[: args.limit]
    pool_sha = hashlib.sha256(POOL.read_bytes()).hexdigest()
    print(f"pool    : {len(pool)} requests from {POOL.name}  sha256 {pool_sha[:16]}")
    print(f"release : {RELEASE}")
    print(f"log     : {obs.trace_path()}")
    print()

    client = build_client()
    started = time.time()
    with MCPHost() as host:
        for i, row in enumerate(pool, start=1):
            r = run_squad(client, host, row["request"], user_id=row["user_id"],
                          session_id=row["session_id"],
                          trace_meta={"source": "w11-traffic", "pool_id": row["id"],
                                      "pool_sha256": pool_sha})
            print(f"[{i:>2}/{len(pool)}] {row['id']} {row['user_id']} {r.trace_id} "
                  f"ok={str(r.ok):<5} calls={r.laps} tok={r.total_tokens:<5} "
                  f"${r.cost_usd:.6f} {r.latency_ms / 1000:5.1f}s  {row['request'][:48]}", flush=True)
            if args.gap and i < len(pool):
                time.sleep(args.gap)
    print(f"\ndone in {(time.time() - started) / 60:.1f} min")


if __name__ == "__main__":
    main()
