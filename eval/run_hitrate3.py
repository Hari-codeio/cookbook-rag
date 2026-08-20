"""hit-rate@3 and p50 latency over the 12-question golden set.

Week 4 requirements 2 and 5. One script measures both the before and the after,
selected by --retriever, so the ONLY thing that differs between the two runs is
the retriever. Everything else (the 12 questions, the embedding model, the
collection, k) is held fixed by construction.

A hit means: the chunk_id declared in golden_set.jsonl is inside the top 3. Not
the right recipe, not a chunk that looks close - that exact chunk. Whole-
collection rank is recorded for every question too, so a miss can be diagnosed
as mis-ordered (inside the candidate window) or unreachable (outside it).

Latency is the retrieval call only, which is the thing the change actually
affects. The embedder is warmed up first so the one-off ONNX model load does not
land inside the measurement.

    python eval/run_hitrate3.py --retriever dense  --label before
    python eval/run_hitrate3.py --retriever rerank --label after
"""

from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rag.config import EMBED_MODEL, OUT_DIR, ROOT  # noqa: E402
from rag.store import get_collection, search  # noqa: E402

GOLDEN_PATH = ROOT / "eval" / "golden_set.jsonl"
WARMUP_QUERIES = ["warm up the embedder", "another warm up call", "third warm up"]


def load_golden() -> tuple[list[dict], str]:
    raw = GOLDEN_PATH.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    rows = [json.loads(l) for l in raw.decode("utf-8").splitlines() if l.strip()]
    if len(rows) != 12:
        print(
            f"[warn] golden set has {len(rows)} questions, the brief asks for 12",
            file=sys.stderr,
        )
    return rows, digest


def get_retriever(name: str):
    """Return fn(collection, question, k) -> list[chunk_id], best first."""
    if name == "dense":
        def dense(collection, question, k):
            return [h.chunk_id for h in search(collection, question, k=k)]
        return dense
    if name == "rerank":
        from rag.rerank import rerank_search

        def rerank(collection, question, k):
            return [h.chunk_id for h in rerank_search(collection, question, k=k)]
        return rerank
    raise SystemExit("unknown retriever " + repr(name))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--retriever", default="dense", choices=["dense", "rerank"])
    ap.add_argument("--label", default=None, help="file label, e.g. before / after")
    ap.add_argument("--k", type=int, default=3)
    ap.add_argument("--strategy", default="structure")
    ap.add_argument("--deep", type=int, default=25)
    ap.add_argument(
        "--repeats",
        type=int,
        default=7,
        help="timing samples per query; the median of ALL samples is the reported p50",
    )
    args = ap.parse_args()
    label = args.label or args.retriever

    golden, digest = load_golden()
    collection = get_collection(args.strategy)
    total_chunks = collection.count()
    retrieve = get_retriever(args.retriever)

    for w in WARMUP_QUERIES:
        retrieve(collection, w, args.k)

    rows = []
    latencies_ms = []
    for g in golden:
        # Time the top-k retrieval only, repeated, because a single sample on a
        # local ONNX embedder swings by a factor of seven. The reported p50 is
        # the median of every sample taken across every question.
        samples = []
        for _ in range(args.repeats):
            started = time.perf_counter()
            top = retrieve(collection, g["question"], args.k)
            samples.append((time.perf_counter() - started) * 1000.0)
        latencies_ms.extend(samples)
        elapsed_ms = statistics.median(samples)

        full = retrieve(collection, g["question"], total_chunks)
        expected = g["expected_chunk_id"]
        rank = full.index(expected) + 1 if expected in full else None
        rows.append(
            {
                "id": g["id"],
                "question": g["question"],
                "expected": expected,
                "exact_token": g.get("exact_token", False),
                "token_kind": g.get("token_kind", ""),
                "hit": expected in top,
                "rank": rank,
                "in_deep": rank is not None and rank <= args.deep,
                "top": top,
                "ms": elapsed_ms,
            }
        )

    hits = sum(1 for r in rows if r["hit"])
    hit1 = sum(1 for r in rows if r["rank"] == 1)
    mrr = sum((1.0 / r["rank"]) for r in rows if r["rank"]) / len(rows)
    exact_rows = [r for r in rows if r["exact_token"]]
    para_rows = [r for r in rows if not r["exact_token"]]
    exact_hits = sum(1 for r in exact_rows if r["hit"])
    para_hits = sum(1 for r in para_rows if r["hit"])
    p50 = statistics.median(latencies_ms)
    p95 = sorted(latencies_ms)[max(0, int(round(0.95 * len(latencies_ms))) - 1)]

    header = [
        "retriever        : " + args.retriever,
        "strategy         : " + args.strategy,
        "embedding model  : " + EMBED_MODEL + "   (held fixed)",
        "k                : " + str(args.k),
        "candidate window : " + str(args.deep),
        "chunks in index  : " + str(total_chunks),
        "golden set       : eval/golden_set.jsonl  (" + str(len(golden)) + " questions)",
        "golden sha256    : " + digest,
        "timing samples   : " + str(args.repeats) + " per query, " + str(args.repeats * len(golden)) + " total",
        "generated        : " + datetime.now(timezone.utc).isoformat(timespec="seconds"),
    ]

    out = [
        "# hit-rate@" + str(args.k) + " - retriever=" + args.retriever,
        "",
        "```",
        *header,
        "```",
        "",
        "## Per-question record",
        "",
        "| id | question | exact term? | expected chunk | hit@"
        + str(args.k)
        + " | rank of expected | in top-"
        + str(args.deep)
        + " | ms |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        rank_txt = (str(r["rank"]) + " of " + str(total_chunks)) if r["rank"] else "-"
        out.append(
            "| " + r["id"]
            + " | " + r["question"]
            + " | " + ("yes" if r["exact_token"] else "no")
            + " | `" + r["expected"] + "`"
            + " | " + ("HIT" if r["hit"] else "**MISS**")
            + " | " + rank_txt
            + " | " + ("yes" if r["in_deep"] else "NO")
            + " | " + format(r["ms"], ".1f")
            + " |"
        )

    out += [
        "",
        "## Result",
        "",
        "| metric | value |",
        "|---|---|",
        "| **hit-rate@" + str(args.k) + "** | **" + str(hits) + "/" + str(len(rows)) + "** |",
        "| hit@1 | " + str(hit1) + "/" + str(len(rows)) + " |",
        "| MRR | " + format(mrr, ".3f") + " |",
        "| hit-rate@" + str(args.k) + ", exact-term questions | " + str(exact_hits) + "/" + str(len(exact_rows)) + " |",
        "| hit-rate@" + str(args.k) + ", paraphrase questions | " + str(para_hits) + "/" + str(len(para_rows)) + " |",
        "| **p50 latency per query** | **" + format(p50, ".1f") + " ms** |",
        "| p95 latency per query | " + format(p95, ".1f") + " ms |",
        "",
        "## Misses",
        "",
    ]
    misses = [r for r in rows if not r["hit"]]
    if not misses:
        out.append("None.")
    for r in misses:
        if r["in_deep"]:
            reach = "retrieved but mis-ordered at rank " + str(r["rank"])
        else:
            reach = (
                "outside the top-" + str(args.deep) + " candidate window (rank "
                + str(r["rank"]) + " of " + str(total_chunks) + ")"
            )
        out.append("- **" + r["id"] + "** `" + r["question"] + "` - " + reach)
        out.append("  - top-" + str(args.k) + " was: " + str(r["top"]))

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / ("hitrate3_" + label + ".md")
    path.write_text("\n".join(out) + "\n", encoding="utf-8")

    print("\n".join(header))
    print()
    for r in rows:
        print(
            "  " + r["id"]
            + ("  HIT " if r["hit"] else "  MISS")
            + "  rank=" + str(r["rank"]).rjust(3) + "/" + str(total_chunks)
            + "  deep=" + ("y" if r["in_deep"] else "N")
            + "  " + format(r["ms"], "6.1f") + "ms  "
            + r["question"]
        )
    print()
    print("hit-rate@" + str(args.k) + "      : " + str(hits) + "/" + str(len(rows)))
    print("  exact-term    : " + str(exact_hits) + "/" + str(len(exact_rows)))
    print("  paraphrase    : " + str(para_hits) + "/" + str(len(para_rows)))
    print("hit@1           : " + str(hit1) + "/" + str(len(rows)))
    print("MRR             : " + format(mrr, ".3f"))
    print("p50 latency     : " + format(p50, ".1f") + " ms")
    print("p95 latency     : " + format(p95, ".1f") + " ms")
    print("[written] out/" + path.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
