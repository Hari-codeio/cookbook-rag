"""Assert the structural contract of each chunker, and quantify the baseline's failure.

This is the mechanism behind whatever the hit-rate numbers turn out to be. It is
measured, not eyeballed:

  * Requirement 3 says the structure-aware chunker must never separate an
    ingredient row from its table header or its parent recipe title. Checks 1-3
    assert exactly that, for every row of every card.
  * Check 4 counts how many ingredient rows the BASELINE chunker strands in a
    chunk that never names the recipe. That count is the concrete reason a
    question like "how much salt is in the 2kg sourdough" can retrieve a chunk
    holding "| Fine sea salt | 7 g | 0.7% |" that the embedder has no way to
    associate with the right loaf.

    python eval/test_chunk_invariants.py --dir data/baseline
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rag.chunkers import chunk_card  # noqa: E402
from rag.config import ROOT  # noqa: E402
from rag.parse import load_cards  # noqa: E402


def normalise(text: str) -> str:
    return " ".join(text.split()).lower()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", default="data/baseline")
    args = parser.parse_args()

    directory = Path(args.dir)
    if not directory.is_absolute():
        directory = (ROOT / directory).resolve()

    cards = load_cards(directory)
    failures: list[str] = []

    rows_total = 0
    rows_stranded_baseline = 0
    rows_split_baseline = 0
    stranded_examples: list[str] = []

    for card in cards:
        if card.table is None:
            print(f"[skip] {card.source_file}: no ingredient table")
            continue

        title_n = normalise(card.title)
        header_n = normalise(card.table.header_line())

        # ---- structure-aware -------------------------------------------
        s_chunks = chunk_card(card, "structure")
        ing_chunks = [c for c in s_chunks if c.section == "ingredients"]

        if not ing_chunks:
            failures.append(f"{card.source_file}: structure-aware produced no ingredients chunk")
            continue

        for c in ing_chunks:
            body = normalise(c.text)
            if title_n not in body:
                failures.append(f"{c.chunk_id}: CHECK 1 FAILED — ingredient chunk lacks the recipe title")
            if header_n not in body:
                failures.append(f"{c.chunk_id}: CHECK 2 FAILED — ingredient chunk lacks the table header row")

        # CHECK 3: every row appears intact in exactly one ingredients chunk.
        for row in card.table.rows:
            needle = normalise(" | ".join(row.cells))
            holders = [c.chunk_id for c in ing_chunks if needle in normalise(c.text)]
            if len(holders) != 1:
                failures.append(
                    f"{card.recipe_id}: CHECK 3 FAILED — row {row.cells!r} appears "
                    f"in {len(holders)} ingredient chunk(s), expected exactly 1"
                )

        # ---- baseline: quantify the damage -----------------------------
        b_chunks = chunk_card(card, "baseline")
        for row in card.table.rows:
            rows_total += 1
            needle = normalise(" | ".join(row.cells))
            holders = [c for c in b_chunks if needle in normalise(c.text)]
            if not holders:
                rows_split_baseline += 1
                continue
            if not any(title_n in normalise(c.text) for c in holders):
                rows_stranded_baseline += 1
                if len(stranded_examples) < 6:
                    stranded_examples.append(
                        f"{card.recipe_id}: row {' | '.join(row.cells)!r} -> {holders[0].chunk_id} (no recipe title in chunk)"
                    )

    print()
    print("=" * 78)
    print("STRUCTURE-AWARE CONTRACT (requirement 3)")
    print("=" * 78)
    if failures:
        for f in failures:
            print(f"  {f}")
        print(f"\n  {len(failures)} FAILURE(S)")
    else:
        print("  CHECK 1 PASS: every ingredient chunk carries its recipe title")
        print("  CHECK 2 PASS: every ingredient chunk carries its table header row")
        print("  CHECK 3 PASS: every ingredient row appears intact in exactly one chunk")

    print()
    print("=" * 78)
    print("BASELINE CHUNKER - MEASURED DAMAGE")
    print("=" * 78)
    pct_stranded = (100.0 * rows_stranded_baseline / rows_total) if rows_total else 0.0
    pct_split = (100.0 * rows_split_baseline / rows_total) if rows_total else 0.0
    print(f"  ingredient rows in corpus              : {rows_total}")
    print(f"  rows cut in half across a chunk edge   : {rows_split_baseline}  ({pct_split:.1f}%)")
    print(f"  rows landing in a chunk with NO title  : {rows_stranded_baseline}  ({pct_stranded:.1f}%)")
    if stranded_examples:
        print("  examples:")
        for ex in stranded_examples:
            print(f"    - {ex}")

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
