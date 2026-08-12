"""Show exactly what the parser and both chunkers made of each card.

Run this BEFORE ingesting a new drop. If the test kitchen's cards use a shape
the parser mis-reads, it shows up here as a missing table or an "unspecified"
cuisine — cheaply, before anything is embedded.

    python -m rag.inspect_cards --dir data/new_drop
    python -m rag.inspect_cards --dir data/new_drop --show-chunks structure
"""

from __future__ import annotations

import argparse
from pathlib import Path

from .chunkers import chunk_card
from .config import ROOT, STRATEGIES
from .parse import load_cards


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect parsed recipe cards.")
    parser.add_argument("--dir", required=True)
    parser.add_argument("--show-chunks", choices=list(STRATEGIES), default=None)
    parser.add_argument("--full", action="store_true", help="print whole chunk text")
    args = parser.parse_args()

    directory = Path(args.dir)
    if not directory.is_absolute():
        directory = (ROOT / directory).resolve()

    cards = load_cards(directory)
    print(f"Parsed {len(cards)} card(s) from {directory}\n")

    problems = 0
    for card in cards:
        print("=" * 78)
        print(f"{card.source_file}")
        print(f"  recipe_id    : {card.recipe_id}")
        print(f"  title        : {card.title}")
        print(f"  cuisine      : {card.cuisine}")
        print(f"  dietary_tags : {card.dietary_tags}")
        print(f"  sections     : {[(s.kind, s.heading) for s in card.sections]}")
        if card.table:
            t = card.table
            print(f"  table        : kind={t.kind}  header={t.header}  rows={len(t.rows)}")
            for row in t.rows[:3]:
                print(f"                 {row.cells}")
            if len(t.rows) > 3:
                print(f"                 ... {len(t.rows) - 3} more row(s)")
        else:
            print("  table        : NONE")
        for warning in card.warnings:
            problems += 1
            print(f"  [warn] {warning}")

        counts = {s: len(chunk_card(card, s)) for s in STRATEGIES}
        print(f"  chunk counts : {counts}")

        if args.show_chunks:
            print(f"\n  --- chunks ({args.show_chunks}) ---")
            for c in chunk_card(card, args.show_chunks):
                body = c.text if args.full else (c.text[:220] + ("..." if len(c.text) > 220 else ""))
                indented = "\n".join("      " + line for line in body.splitlines())
                print(f"  [{c.chunk_id}] section={c.section} chars={c.char_start}-{c.char_end}")
                print(indented)
                print()
        print()

    print("=" * 78)
    print(f"{len(cards)} card(s), {problems} warning(s).")
    if problems:
        print("Warnings above are the parser telling you what it could not find.")


if __name__ == "__main__":
    main()
