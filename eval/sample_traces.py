"""Draw a seeded random sample of trace_ids from the trace log.

The whole value of this week's exercise rests on the sample being random, so
this script is built to make the draw checkable by someone who does not trust
me:

* The population is every trace in the log with the requested ``source`` tag,
  sorted by ``trace_id``. Sorting first makes the draw independent of the order
  lines happen to sit in the file, so re-running after an append cannot silently
  reshuffle a previous sample.
* The population is fingerprinted (sha256 over the sorted id list). Seed plus
  population fingerprint plus n determines the output completely. Publish those
  three and anyone can reproduce the exact 20 without my machine.
* The seed is a constant in this file, not a command-line habit, and the file is
  committed BEFORE the draw is run. A seed chosen after seeing the results is
  the easiest way to fake a random sample, and the commit order is the only
  thing that rules it out.
* ``random.Random(seed).sample`` is used rather than the global ``random``
  module state, so nothing else importing this module can move the draw.

    python eval/sample_traces.py --source random-traffic --n 20
    python eval/sample_traces.py --source curated-demo --n 10
    python eval/sample_traces.py --source random-traffic --n 20 --verify
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rag import trace as trc  # noqa: E402
from rag.config import OUT_DIR  # noqa: E402

# Today's date, fixed in the file and committed before the draw. Not tuned, not
# retried: this file's git history is the evidence that no other seed was tried.
SEED = 20260826


def population(source: str) -> list[str]:
    ids = [
        rec["trace_id"]
        for rec in trc.iter_traces()
        if (rec.get("meta") or {}).get("source") == source
    ]
    if len(set(ids)) != len(ids):
        raise RuntimeError("duplicate trace_ids in the log; the draw would not be well defined")
    return sorted(ids)


def fingerprint(ids: list[str]) -> str:
    return hashlib.sha256("\n".join(ids).encode("utf-8")).hexdigest()


def draw(ids: list[str], n: int, seed: int) -> list[str]:
    if n > len(ids):
        raise SystemExit(f"asked for {n} traces but the population has only {len(ids)}")
    return sorted(random.Random(seed).sample(ids, n))


def main() -> None:
    ap = argparse.ArgumentParser(description="Seeded random sample of trace_ids.")
    ap.add_argument("--source", default="random-traffic")
    ap.add_argument("--n", type=int, default=20)
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--out", default=None, help="where to write the sample json")
    ap.add_argument(
        "--verify",
        action="store_true",
        help="re-draw and compare against the saved sample instead of writing one",
    )
    args = ap.parse_args()

    ids = population(args.source)
    fp = fingerprint(ids)
    picked = draw(ids, args.n, args.seed)

    out_path = Path(args.out) if args.out else OUT_DIR / f"sample_{args.source}_{args.n}.json"
    record = {
        "seed": args.seed,
        "n": args.n,
        "source": args.source,
        "population_size": len(ids),
        "population_sha256": fp,
        "sampler": "python random.Random(seed).sample(sorted(population), n), python "
        + ".".join(str(v) for v in sys.version_info[:3]),
        "trace_file_sha256": trc.file_fingerprint()["sha256"],
        "trace_ids": picked,
    }

    print(f"source              : {args.source}")
    print(f"population          : {len(ids)} traces")
    print(f"population sha256   : {fp}")
    print(f"seed                : {args.seed}")
    print(f"n                   : {args.n}")
    print()

    if args.verify:
        if not out_path.exists():
            raise SystemExit(f"nothing to verify: {out_path} does not exist")
        saved = json.loads(out_path.read_text(encoding="utf-8"))
        same_pop = saved["population_sha256"] == fp
        same_ids = saved["trace_ids"] == picked
        print(f"saved population matches : {same_pop}")
        print(f"saved sample matches     : {same_ids}")
        if not (same_pop and same_ids):
            raise SystemExit("VERIFY FAILED - the saved sample is not reproducible")
        print("VERIFY OK")
        return

    if out_path.exists():
        # Re-running with a different seed and overwriting is exactly the fraud
        # this exercise is about, so it takes an explicit deletion.
        raise SystemExit(
            f"{out_path} already exists. The draw has been made. Delete the file by "
            f"hand if you genuinely mean to redraw, and say so in the write-up."
        )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    for i, tid in enumerate(picked, start=1):
        print(f"  {i:>2}. {tid}")
    print()
    print(f"written: {out_path}")


if __name__ == "__main__":
    main()
