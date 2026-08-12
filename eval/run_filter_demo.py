"""Requirement 4 — show one query where a dietary_tags filter changes top-1.

Rather than hand-picking a query that flatters the filter, this sweeps the 8
eval questions plus a set of probe queries across every dietary tag present in
the corpus, and reports the cases where the filtered top-1 differs from the
unfiltered top-1. Both full result lists are printed with scores.

The filter is a real Chroma ``where`` clause applied BEFORE ranking, so the
filtered run re-ranks the surviving subset — it is not an unfiltered top-5 with
rows crossed out afterwards.

    python eval/run_filter_demo.py
    python eval/run_filter_demo.py --query "..." --tag vegan
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rag.chunkers.base import tag_key  # noqa: E402
from rag.config import EMBED_MODEL, OUT_DIR, QUESTIONS_PATH, ROOT, TOP_K  # noqa: E402
from rag.store import SearchHit, get_collection, search  # noqa: E402

PROBE_QUERIES = [
    "a creamy spiced dish with tomatoes and onion",
    "which recipe uses butter and eggs",
    "a rich braise cooked slowly in liquid",
    "something with a sweet and sour glaze",
    "a dish finished with fresh herbs",
    "what should I serve for a warming breakfast",
    "a recipe with a long overnight rest",
    "which dish uses toasted sesame",
]


def corpus_tags(collection) -> list[str]:
    got = collection.get(include=["metadatas"])
    tags: set[str] = set()
    for meta in got.get("metadatas") or []:
        for tag in str((meta or {}).get("dietary_tags", "")).split("|"):
            if tag.strip():
                tags.add(tag.strip())
    return sorted(tags)


def render(hits: list[SearchHit], indent: str = "  ") -> str:
    if not hits:
        return f"{indent}(no results)"
    out = []
    for h in hits:
        out.append(
            f"{indent}{h.rank}. score={h.score:.4f}  {h.chunk_id}\n"
            f"{indent}   recipe_id={h.recipe_id}  section={h.section}  "
            f"dietary_tags=[{h.dietary_tags}]"
        )
    return "\n".join(out)


def block(query: str, tag: str, unfiltered: list[SearchHit], filtered: list[SearchHit]) -> str:
    changed = (
        bool(unfiltered) and bool(filtered) and unfiltered[0].chunk_id != filtered[0].chunk_id
    )
    lines = [
        f"**Query:** `{query}`",
        f"**Filter:** `where={{'{tag_key(tag)}': True}}`  (dietary_tags contains `{tag}`)",
        "",
        "```text",
        f"UNFILTERED  (top-{len(unfiltered)})",
        render(unfiltered),
        "",
        f"FILTERED    (top-{len(filtered)})  where={{'{tag_key(tag)}': True}}",
        render(filtered),
        "",
        f"top-1 unfiltered : {unfiltered[0].chunk_id if unfiltered else '-'} "
        f"(recipe_id={unfiltered[0].recipe_id if unfiltered else '-'}, "
        f"score={unfiltered[0].score:.4f})" if unfiltered else "top-1 unfiltered : -",
        f"top-1 filtered   : {filtered[0].chunk_id if filtered else '-'} "
        f"(recipe_id={filtered[0].recipe_id if filtered else '-'}, "
        f"score={filtered[0].score:.4f})" if filtered else "top-1 filtered   : -",
        f"TOP-1 CHANGED    : {'YES' if changed else 'no'}",
        "```",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--strategy", default="structure")
    parser.add_argument("--k", type=int, default=TOP_K)
    parser.add_argument("--query", default=None, help="run one specific query")
    parser.add_argument("--tag", default=None, help="run one specific dietary tag")
    args = parser.parse_args()

    collection = get_collection(args.strategy)
    tags = [args.tag] if args.tag else corpus_tags(collection)

    queries = [args.query] if args.query else list(PROBE_QUERIES)
    if not args.query and QUESTIONS_PATH.exists():
        payload = json.loads(QUESTIONS_PATH.read_text(encoding="utf-8"))
        queries = [q["question"] for q in payload.get("questions", [])] + queries

    header = [
        f"strategy        : {args.strategy}",
        f"embedding model : {EMBED_MODEL}",
        f"top-k           : {args.k}",
        f"dietary tags    : {tags}",
        f"generated       : {datetime.now(timezone.utc).isoformat(timespec='seconds')}",
    ]

    scored_changes: list[tuple[float, str]] = []
    all_blocks: list[str] = []

    for query in queries:
        unfiltered = search(collection, query, k=args.k)
        for tag in tags:
            filtered = search(collection, query, k=args.k, where={tag_key(tag): True})
            b = block(query, tag, unfiltered, filtered)
            all_blocks.append(b)
            if unfiltered and filtered and unfiltered[0].chunk_id != filtered[0].chunk_id:
                # Rank candidates by how strong the FILTERED top-1 still is.
                # A filter that swaps a 0.69 hit for a 0.32 one has "changed
                # top-1", but only because it excluded the whole relevant
                # recipe — that is a nonsense pairing, not a demo. The most
                # defensible case is the one where the surviving top-1 is still
                # a genuinely good answer under the constraint.
                scored_changes.append((filtered[0].score, b))

    scored_changes.sort(key=lambda pair: pair[0], reverse=True)
    changed_blocks = [b for _, b in scored_changes]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    body = [
        "# Metadata filter on dietary_tags — unfiltered vs filtered",
        "",
        "```",
        *header,
        "```",
        "",
        f"Swept {len(queries)} quer(y/ies) x {len(tags)} tag(s) = {len(all_blocks)} comparisons; "
        f"**{len(changed_blocks)}** of them changed the top-1 result.",
        "",
    ]
    if changed_blocks:
        body += ["## Cases where the filter changed top-1", ""]
        for b in changed_blocks[:6]:
            body += [b, ""]
    else:
        body += [
            "## No top-1 change found",
            "",
            "Every filtered query returned the same top-1 as unfiltered — the highest-scoring "
            "chunk already satisfied every filter. Widen the probe queries or add a card whose "
            "tags differ from the current top scorer.",
            "",
        ]
    (OUT_DIR / "filter_demo.md").write_text("\n".join(body), encoding="utf-8")

    print("\n".join(header))
    print()
    print(f"{len(changed_blocks)} of {len(all_blocks)} comparisons changed top-1.")
    print()
    for b in changed_blocks[:2]:
        print(b)
        print()
    print(f"[written] {(OUT_DIR / 'filter_demo.md').relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
