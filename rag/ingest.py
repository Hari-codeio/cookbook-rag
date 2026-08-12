"""Ingest CLI — append-only, with a paste-ready proof block.

Requirement 6 says: do NOT re-index the whole recipe corpus, index the 6 new
cards only, and say so in the write-up. So this command reads exactly one
directory, appends to whatever is already in the collection, and prints the
numbers that prove it did:

    files read / chunks before / chunks added / chunks after / wall clock.

Requirement 1 says a chunk with no ``source_file`` is a failed ingest. That is
enforced as a hard assertion below, not a lint.

Usage
-----
    python -m rag.ingest --dir data/baseline  --label baseline-corpus
    python -m rag.ingest --dir data/new_drop  --label new-drop
    python -m rag.ingest --dir data/new_drop  --label new-drop --strategy structure
"""

from __future__ import annotations

import argparse
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from .chunkers import chunk_card
from .config import EMBED_MODEL, OUT_DIR, ROOT, STRATEGIES
from .parse import Card, load_cards
from .store import add_chunks, get_collection

REQUIRED_METADATA = ("source_file", "recipe_id", "cuisine", "dietary_tags")


def assert_metadata(chunks, strict: bool) -> list[str]:
    """Requirement 1 enforcement. Returns the list of checks that passed."""
    if not chunks:
        raise SystemExit("FAILED INGEST: chunker produced zero chunks.")

    missing_source = [c.chunk_id for c in chunks if not str(c.source_file).strip()]
    if missing_source:
        raise SystemExit(
            "FAILED INGEST: "
            f"{len(missing_source)} chunk(s) have no source_file, e.g. {missing_source[:3]}. "
            "Requirement 1: a chunk with no source_file is a failed ingest."
        )

    missing_recipe = [c.chunk_id for c in chunks if not str(c.recipe_id).strip()]
    if missing_recipe:
        raise SystemExit(
            f"FAILED INGEST: {len(missing_recipe)} chunk(s) have no recipe_id, "
            f"e.g. {missing_recipe[:3]}. Citations could not resolve."
        )

    incomplete: list[str] = []
    for c in chunks:
        if c.cuisine in ("", "unspecified"):
            incomplete.append(f"{c.source_file}: cuisine is '{c.cuisine}'")
        if not c.dietary_tags:
            incomplete.append(f"{c.source_file}: dietary_tags is empty")
    incomplete = sorted(set(incomplete))

    if incomplete and strict:
        listing = "\n  ".join(incomplete[:12])
        raise SystemExit(
            "FAILED INGEST: requirement 1 asks for cuisine and dietary_tags on every "
            f"chunk, and these cards do not declare them:\n  {listing}\n"
            "Add frontmatter (cuisine: ..., dietary_tags: [...]) or an inline "
            "'Cuisine:' / 'Dietary:' line to those cards, or re-run with "
            "--allow-incomplete-metadata to proceed anyway."
        )

    checks = [
        f"source_file present on all {len(chunks)} chunks",
        f"recipe_id present on all {len(chunks)} chunks",
    ]
    checks.append(
        "cuisine + dietary_tags present on all chunks"
        if not incomplete
        else f"cuisine/dietary_tags INCOMPLETE on {len(incomplete)} card-field(s) (allowed by flag)"
    )
    return checks


def format_proof(
    *,
    label: str,
    directory: Path,
    strategy: str,
    cards: list[Card],
    added: int,
    before: int,
    after: int,
    elapsed_ms: float,
    checks: list[str],
) -> str:
    rel = directory.relative_to(ROOT) if directory.is_relative_to(ROOT) else directory
    lines = [
        f"### Ingest proof — {label} / strategy={strategy}",
        "",
        "```",
        f"timestamp            : {datetime.now(timezone.utc).isoformat(timespec='seconds')}",
        f"directory read       : {rel}   (ONLY this directory was read)",
        f"files read           : {len(cards)}",
        *[f"  - {c.source_file}  [recipe_id={c.recipe_id}]" for c in cards],
        f"embedding model      : {EMBED_MODEL}",
        f"chunks BEFORE        : {before}",
        f"chunks ADDED         : {added}",
        f"chunks AFTER         : {after}",
        f"delta check          : {before} + {added} = {before + added} "
        f"({'OK' if before + added == after else 'MISMATCH'})",
        f"pre-existing rewritten: 0 (append-only; ingest aborts on any id clash)",
        f"wall clock           : {elapsed_ms:.0f} ms",
        "assertions:",
        *[f"  - PASS  {c}" for c in checks],
        "```",
    ]
    return "\n".join(lines)


def ingest_dir(directory: Path, strategy: str, label: str, strict: bool) -> str:
    cards = load_cards(directory)
    if not cards:
        raise SystemExit(f"No .md/.txt cards found in {directory}")

    for card in cards:
        for warning in card.warnings:
            print(f"  [warn] {card.source_file}: {warning}", file=sys.stderr)

    started = time.perf_counter()
    chunks = []
    for card in cards:
        chunks.extend(chunk_card(card, strategy))

    checks = assert_metadata(chunks, strict)

    collection = get_collection(strategy, create=True)
    before = collection.count()
    added = add_chunks(collection, chunks)
    after = collection.count()
    elapsed_ms = (time.perf_counter() - started) * 1000.0

    proof = format_proof(
        label=label,
        directory=directory,
        strategy=strategy,
        cards=cards,
        added=added,
        before=before,
        after=after,
        elapsed_ms=elapsed_ms,
        checks=checks,
    )
    print(proof)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / f"ingest_{label}_{strategy}.md"
    out_path.write_text(proof + "\n", encoding="utf-8")
    return proof


def main() -> None:
    parser = argparse.ArgumentParser(description="Append a directory of recipe cards to the index.")
    parser.add_argument("--dir", required=True, help="directory of cards to read (ONLY this one)")
    parser.add_argument("--label", required=True, help="label for the proof block, e.g. new-drop")
    parser.add_argument(
        "--strategy",
        default="both",
        choices=[*STRATEGIES, "both"],
        help="which chunker to ingest under (default: both)",
    )
    parser.add_argument(
        "--allow-incomplete-metadata",
        action="store_true",
        help="proceed even if a card omits cuisine or dietary_tags",
    )
    args = parser.parse_args()

    directory = Path(args.dir)
    if not directory.is_absolute():
        directory = (ROOT / directory).resolve()

    strategies = list(STRATEGIES) if args.strategy == "both" else [args.strategy]
    proofs = []
    for strategy in strategies:
        proofs.append(ingest_dir(directory, strategy, args.label, not args.allow_incomplete_metadata))
        print()

    combined = OUT_DIR / f"ingest_{args.label}.md"
    combined.write_text("\n\n".join(proofs) + "\n", encoding="utf-8")
    print(f"[proof written] {combined.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
