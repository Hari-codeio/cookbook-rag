"""Search-only CLI. No LLM is imported or called on this path.

    python -m rag.search "how much salt in the 2kg sourdough" --strategy structure
    python -m rag.search "which loaf is vegan" --filter-tag vegan
    python -m rag.search "..." --strategy both --k 5
"""

from __future__ import annotations

import argparse
import textwrap

from .chunkers.base import tag_key
from .config import EMBED_MODEL, STRATEGIES, TOP_K
from .store import SearchHit, get_collection, search


def build_where(tag: str | None, cuisine: str | None) -> dict | None:
    clauses: list[dict] = []
    if tag:
        clauses.append({tag_key(tag): True})
    if cuisine:
        clauses.append({"cuisine": cuisine})
    if not clauses:
        return None
    if len(clauses) == 1:
        return clauses[0]
    return {"$and": clauses}


def format_hits(hits: list[SearchHit], preview: int = 200, indent: str = "  ") -> str:
    if not hits:
        return f"{indent}(no results)"
    lines: list[str] = []
    for h in hits:
        first = h.text.strip().splitlines()
        snippet = " / ".join(line.strip() for line in first if line.strip())[:preview]
        lines.append(
            f"{indent}{h.rank}. score={h.score:.4f}  chunk_id={h.chunk_id}\n"
            f"{indent}   recipe_id={h.recipe_id}  section={h.section}  "
            f"source_file={h.source_file}  dietary_tags=[{h.dietary_tags}]\n"
            f"{indent}   {textwrap.shorten(snippet, width=preview, placeholder=' ...')}"
        )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Search the recipe index (no generation).")
    parser.add_argument("query", help="the search query")
    parser.add_argument("--strategy", default="both", choices=[*STRATEGIES, "both"])
    parser.add_argument("--k", type=int, default=TOP_K)
    parser.add_argument("--filter-tag", default=None, help="dietary_tags value, e.g. vegan")
    parser.add_argument("--filter-cuisine", default=None)
    parser.add_argument("--preview", type=int, default=200)
    args = parser.parse_args()

    where = build_where(args.filter_tag, args.filter_cuisine)
    strategies = list(STRATEGIES) if args.strategy == "both" else [args.strategy]

    print(f"query        : {args.query!r}")
    print(f"top-k        : {args.k}")
    print(f"embed model  : {EMBED_MODEL}")
    print(f"where filter : {where if where else 'none (unfiltered)'}")
    print()

    for strategy in strategies:
        collection = get_collection(strategy)
        hits = search(collection, args.query, k=args.k, where=where)
        print(f"--- strategy={strategy} (collection has {collection.count()} chunks) ---")
        print(format_hits(hits, preview=args.preview))
        print()


if __name__ == "__main__":
    main()
