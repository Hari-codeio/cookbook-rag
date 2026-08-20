"""Inspection view — why did this query fail?

Week 4 requirement 3 needs every miss labelled R / G / Not-In-Corpus with one
line of real evidence. You cannot produce that evidence from a hit-rate table;
you need to see what was actually fetched and where the known-correct chunk
really landed. That is what this prints.

The single most important column is ``rank of expected chunk``, measured against
the WHOLE collection rather than the top-k. It separates the two failure shapes
that demand different fixes:

  * expected chunk is at rank 4-25  -> it was retrieved but mis-ordered.
    A reranker can fix this. BM25 might not be needed at all.
  * expected chunk is far down or last -> dense retrieval never saw it as
    relevant. No amount of reordering the top-25 helps, because it is not in
    the top-25. This is the exact-term failure BM25 exists for.

    python -m rag.inspect "how much saeujeot in the kimchi"
    python -m rag.inspect --golden g01
    python -m rag.inspect --all                 # -> out/inspection.md
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .config import OUT_DIR, ROOT, STRATEGIES
from .store import get_collection, search

GOLDEN_PATH = ROOT / "eval" / "golden_set.jsonl"


def load_golden() -> list[dict]:
    if not GOLDEN_PATH.exists():
        return []
    out = []
    for line in GOLDEN_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            out.append(json.loads(line))
    return out


def snippet(text: str, width: int = 96) -> str:
    return " / ".join(l.strip() for l in text.splitlines() if l.strip())[:width]


def full_ranking(collection, question: str) -> list[str]:
    """Every chunk_id ordered by relevance, so an absent chunk still gets a rank."""
    total = collection.count()
    hits = search(collection, question, k=total)
    return [h.chunk_id for h in hits]


def inspect_one(
    collection,
    question: str,
    expected_chunk_id: str | None = None,
    token: str | None = None,
    k: int = 3,
    deep: int = 25,
    qid: str = "",
) -> tuple[str, dict]:
    """Return (rendered block, facts dict)."""
    hits = search(collection, question, k=max(k, deep))
    ordering = full_ranking(collection, question)
    total = len(ordering)

    expected_rank = None
    if expected_chunk_id:
        if expected_chunk_id in ordering:
            expected_rank = ordering.index(expected_chunk_id) + 1

    hit_at_k = bool(
        expected_chunk_id and expected_rank is not None and expected_rank <= k
    )
    in_deep = bool(
        expected_chunk_id and expected_rank is not None and expected_rank <= deep
    )

    lines: list[str] = []
    head = f"=== {qid} {question}".strip()
    lines.append(head)
    if expected_chunk_id:
        lines.append(f"expected      : {expected_chunk_id}" + (f"   token={token!r}" if token else ""))
        lines.append(
            f"hit@{k}         : {'HIT' if hit_at_k else 'MISS'}"
            f"    expected chunk rank: {expected_rank} of {total}"
            f"    in top-{deep}: {'yes' if in_deep else 'NO'}"
        )
    lines.append(f"top-{k}:")
    for h in hits[:k]:
        mark = "  <== EXPECTED" if h.chunk_id == expected_chunk_id else ""
        tokflag = ""
        if token:
            tokflag = " [token:yes]" if token.lower() in h.text.lower() else " [token:no ]"
        lines.append(
            f"  {h.rank}. {h.score:.4f}  {h.chunk_id:44s} {h.section:12s}{tokflag}{mark}"
        )
        lines.append(f"      {snippet(h.text)}")

    if expected_chunk_id and not hit_at_k:
        lines.append("evidence:")
        if expected_rank is None:
            lines.append("  - expected chunk did not appear in the ranking at all")
        elif in_deep:
            lines.append(
                f"  - correct chunk WAS retrieved, at rank {expected_rank}, but ranked below "
                f"{k}. Mis-ordering, not absence -> a reranker could reach it."
            )
        else:
            lines.append(
                f"  - correct chunk sits at rank {expected_rank} of {total}, outside the "
                f"top-{deep} candidate window. Reordering the top-{deep} cannot reach it "
                f"-> exact-term retrieval failure."
            )
        if token:
            got = [h.chunk_id for h in hits[:k] if token.lower() in h.text.lower()]
            lines.append(
                f"  - token {token!r} present in {len(got)} of the top-{k} chunks"
                + (f": {got}" if got else "")
            )
    lines.append("")

    facts = {
        "qid": qid,
        "question": question,
        "expected_chunk_id": expected_chunk_id,
        "expected_rank": expected_rank,
        "total_chunks": total,
        "hit_at_k": hit_at_k,
        "in_deep": in_deep,
        "top_k_ids": [h.chunk_id for h in hits[:k]],
        "top_k_scores": [round(h.score, 4) for h in hits[:k]],
    }
    return "\n".join(lines), facts


def main() -> int:
    ap = argparse.ArgumentParser(description="Inspect what retrieval actually fetched.")
    ap.add_argument("question", nargs="?", default=None)
    ap.add_argument("--strategy", default="structure", choices=list(STRATEGIES))
    ap.add_argument("--k", type=int, default=3)
    ap.add_argument("--deep", type=int, default=25, help="candidate window a reranker would see")
    ap.add_argument("--golden", default=None, help="inspect one golden-set id, e.g. g01")
    ap.add_argument("--all", action="store_true", help="inspect the whole golden set")
    ap.add_argument("--out", default=None, help="also write to this file under out/")
    args = ap.parse_args()

    collection = get_collection(args.strategy)
    golden = {g["id"]: g for g in load_golden()}

    blocks: list[str] = []
    if args.all:
        header = [
            f"# Inspection view — golden set, strategy={args.strategy}, k={args.k}, deep={args.deep}",
            "",
            "```text",
        ]
        for g in load_golden():
            block, _ = inspect_one(
                collection, g["question"], g.get("expected_chunk_id"), g.get("token"),
                k=args.k, deep=args.deep, qid=g["id"],
            )
            blocks.append(block)
        body = "\n".join(header + blocks + ["```"])
        out_name = args.out or f"inspection_{args.strategy}.md"
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        (OUT_DIR / out_name).write_text(body, encoding="utf-8")
        print("\n".join(blocks))
        print(f"[written] out/{out_name}")
        return 0

    if args.golden:
        g = golden.get(args.golden)
        if g is None:
            raise SystemExit(f"unknown golden id {args.golden!r}")
        block, _ = inspect_one(
            collection, g["question"], g.get("expected_chunk_id"), g.get("token"),
            k=args.k, deep=args.deep, qid=g["id"],
        )
        print(block)
        return 0

    if not args.question:
        raise SystemExit("give a question, or --golden ID, or --all")
    block, _ = inspect_one(collection, args.question, None, None, k=args.k, deep=args.deep)
    print(block)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
