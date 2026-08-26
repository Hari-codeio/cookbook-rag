"""Live demo: show one question before and after the Week 4 change, side by side.

Built for a screen-share. Retrieval only, so there is no API key, no cost, and
nothing that can fail because a model is busy. One dense call and one rerank call
per question, so it returns in a few seconds.

    python demo.py g03            # the failure the change fixed
    python demo.py g09            # the failure it did not fix
    python demo.py g12            # retrieval was perfect, the model was the problem
    python demo.py "any question you like"
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from rag.rerank import rerank_search  # noqa: E402
from rag.store import get_collection, search  # noqa: E402

GOLDEN = ROOT / "eval" / "golden_set.jsonl"


def load_golden() -> dict:
    rows = [
        json.loads(l)
        for l in GOLDEN.read_text(encoding="utf-8").splitlines()
        if l.strip()
    ]
    return {r["id"]: r for r in rows}


def line(hits, expected, total):
    for h in hits:
        mark = "   <-- THE ANSWER" if h.chunk_id == expected else ""
        print(f"    {h.rank}. {h.chunk_id:<44}{mark}")


def rank_of(ids: list[str], expected: str) -> str:
    return str(ids.index(expected) + 1) if expected in ids else "not found"


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1

    arg = " ".join(sys.argv[1:])
    golden = load_golden()

    if arg in golden:
        g = golden[arg]
        question = g["question"]
        expected = g["expected_chunk_id"]
        known = g["known_answer"]
        qid = arg
    else:
        question = arg
        expected = None
        known = None
        qid = "ad-hoc"

    collection = get_collection("structure")
    total = collection.count()

    print()
    print("=" * 78)
    print(f"  {qid}:  {question}")
    if expected:
        print(f"  correct chunk : {expected}")
        print(f"  correct answer: {known}")
    print("=" * 78)

    dense_all = [h.chunk_id for h in search(collection, question, k=total)]
    dense_top = search(collection, question, k=3)

    print()
    print("  BEFORE  - dense only (what Week 3 shipped)")
    line(dense_top, expected, total)
    if expected:
        got = expected in [h.chunk_id for h in dense_top]
        print(f"    hit@3: {'YES' if got else 'NO'}"
              f"    correct chunk was at rank {rank_of(dense_all, expected)} of {total}")

    rerank_all = [h.chunk_id for h in rerank_search(collection, question, k=total)]
    rerank_top = rerank_search(collection, question, k=3)

    print()
    print("  AFTER   - cross-encoder rerank over the top 25")
    line(rerank_top, expected, total)
    if expected:
        got = expected in [h.chunk_id for h in rerank_top]
        print(f"    hit@3: {'YES' if got else 'NO'}"
              f"    correct chunk was at rank {rank_of(rerank_all, expected)} of {total}")

    if expected:
        before = expected in [h.chunk_id for h in dense_top]
        after = expected in [h.chunk_id for h in rerank_top]
        print()
        if not before and after:
            print("  VERDICT: FIXED by the change")
        elif before and after:
            print("  VERDICT: was already passing, retrieval was never the problem here")
        elif not before and not after:
            print("  VERDICT: STILL BROKEN - the change moved it closer but not far enough")
        else:
            print("  VERDICT: REGRESSED - the change broke a question that was passing")
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
