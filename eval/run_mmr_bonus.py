"""BONUS — sweep MMR lambda once, report hit-rate@3 AND top-3 diversity.

The bonus asks two questions and they pull in opposite directions:

  * what does MMR do to hit-rate@3?
  * what does it do to the diversity of the top 3?

and then: would you ship it, given that MMR can push the correct chunk out of the
top 3 in the name of variety?

One tuning pass, all lambdas reported, including the ones that made things worse.
Reporting only the best lambda would turn a sweep into a search for a flattering
number.

lambda = 1.0 is pure relevance, which reduces exactly to plain reranking, so that
row IS the after-run from the main experiment and acts as the control.

Diversity is measured as the number of distinct recipe_ids in the top 3. 1 means
all three chunks came from one recipe; 3 means three different recipes.

    python eval/run_mmr_bonus.py
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rag.config import EMBED_MODEL, OUT_DIR, RERANK_CANDIDATES, RERANK_MODEL, ROOT  # noqa: E402
from rag.mmr import build_pool, mmr_select, top_k_diversity  # noqa: E402
from rag.store import get_collection  # noqa: E402

GOLDEN_PATH = ROOT / "eval" / "golden_set.jsonl"
LAMBDAS = [1.0, 0.9, 0.8, 0.7, 0.5, 0.3, 0.0]
SHOWCASE = "gluten free brioche"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", type=int, default=3)
    ap.add_argument("--strategy", default="structure")
    args = ap.parse_args()

    golden = [
        json.loads(l)
        for l in GOLDEN_PATH.read_text(encoding="utf-8").splitlines()
        if l.strip()
    ]
    collection = get_collection(args.strategy)

    # Build each question's reranked pool once. This is the expensive part.
    print("building reranked pools for " + str(len(golden)) + " questions...", file=sys.stderr)
    pools = {}
    for g in golden:
        pools[g["id"]] = build_pool(collection, g["question"], candidates=RERANK_CANDIDATES)

    showcase_pool = build_pool(collection, SHOWCASE, candidates=RERANK_CANDIDATES)

    rows = []
    per_q = {}
    for lam in LAMBDAS:
        hits = 0
        divs = []
        flips = []
        started = time.perf_counter()
        for g in golden:
            pool, emb = pools[g["id"]]
            top = mmr_select(pool, emb, k=args.k, lam=lam)
            ids = [h.chunk_id for h in top]
            got = g["expected_chunk_id"] in ids
            hits += 1 if got else 0
            divs.append(top_k_diversity(top))
            per_q.setdefault(g["id"], {})[lam] = got
            if not got:
                flips.append(g["id"])
        elapsed = (time.perf_counter() - started) * 1000.0 / len(golden)
        rows.append(
            {
                "lam": lam,
                "hits": hits,
                "mean_div": statistics.mean(divs),
                "misses": flips,
                "select_ms": elapsed,
            }
        )
        print(
            "  lambda=" + format(lam, ".1f")
            + "  hit@" + str(args.k) + "=" + str(hits) + "/" + str(len(golden))
            + "  mean top-3 recipes=" + format(statistics.mean(divs), ".2f")
            + "  misses=" + str(flips),
            file=sys.stderr,
        )

    out = [
        "# Bonus - MMR over the reranked candidate list",
        "",
        "```",
        "strategy         : " + args.strategy,
        "embedding model  : " + EMBED_MODEL,
        "reranker         : " + RERANK_MODEL,
        "candidate window : " + str(RERANK_CANDIDATES),
        "k                : " + str(args.k),
        "questions        : " + str(len(golden)) + " (the same golden set)",
        "generated        : " + datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "```",
        "",
        "`lambda = 1.0` is pure relevance and reduces exactly to plain reranking, so that",
        "row is the control and should match the after-run in the main experiment.",
        "",
        "## The lambda sweep, all values reported",
        "",
        "| lambda | hit-rate@" + str(args.k) + " | mean distinct recipes in top-3 | questions missed |",
        "|---|---|---|---|",
    ]
    for r in rows:
        out.append(
            "| " + format(r["lam"], ".1f")
            + " | " + str(r["hits"]) + "/" + str(len(golden))
            + " | " + format(r["mean_div"], ".2f")
            + " | " + (", ".join(r["misses"]) if r["misses"] else "none")
            + " |"
        )

    out += [
        "",
        "## Per-question, hit or miss at each lambda",
        "",
        "| id | " + " | ".join(format(l, ".1f") for l in LAMBDAS) + " |",
        "|---|" + "---|" * len(LAMBDAS),
    ]
    for g in golden:
        marks = ["Y" if per_q[g["id"]][l] else "**n**" for l in LAMBDAS]
        out.append("| " + g["id"] + " | " + " | ".join(marks) + " |")

    out += [
        "",
        "## The showcase query: `" + SHOWCASE + "`",
        "",
        "This is the case the bonus describes. Watch the ingredients chunk, which is the",
        "one carrying the xanthan gum weight.",
        "",
    ]
    for lam in LAMBDAS:
        pool, emb = showcase_pool
        top = mmr_select(pool, emb, k=5, lam=lam)
        out += [
            "**lambda = " + format(lam, ".1f") + "**  (distinct recipes in top-3: "
            + str(top_k_diversity(top[:3])) + ")",
            "",
            "```text",
        ]
        for h in top:
            out.append(
                "  " + str(h.rank) + ". " + format(h.score, "+8.3f") + "  "
                + h.recipe_id.ljust(22) + " " + h.section
            )
        out += ["```", ""]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / "mmr_bonus.md"
    path.write_text("\n".join(out) + "\n", encoding="utf-8")
    print()
    print("[written] out/" + path.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
