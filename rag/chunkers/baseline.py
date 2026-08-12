"""Strategy A — the chunker the app already had.

A fixed-size sliding character window with overlap. It has no model of the
document: no headings, no tables, no rows. It snaps cut points back to the
nearest whitespace so it does not slice words in half, which is about as much
sophistication as a naive splitter ever has.

Deliberate fairness note: this runs over the FULL raw card text, frontmatter
included. Stripping the frontmatter would have hidden the recipe title and
cuisine from the baseline's first chunk and made the structure-aware chunker
look better for a reason that has nothing to do with chunking. Baseline gets
every character the other strategy gets.
"""

from __future__ import annotations

from ..config import BASELINE_CHUNK_CHARS, BASELINE_OVERLAP_CHARS
from ..parse import Card
from .base import Chunk

STRATEGY = "baseline"


def _label_section(card: Card, char_mid: int) -> str:
    """Best-effort section label for the dump only.

    The baseline chunker does not know about sections — this label is derived
    afterwards, purely so the search dumps are readable and the failure
    diagnosis can say which part of the card a chunk landed in. It is never
    used for retrieval or for scoring.
    """
    for section in card.sections:
        if section.char_start <= char_mid < section.char_end:
            return f"~{section.kind}"
    return "~unknown"


def chunk_card(card: Card) -> list[Chunk]:
    text = card.raw
    n = len(text)
    if n == 0:
        return []

    step = max(1, BASELINE_CHUNK_CHARS - BASELINE_OVERLAP_CHARS)
    chunks: list[Chunk] = []
    start = 0
    index = 0

    while start < n:
        end = min(start + BASELINE_CHUNK_CHARS, n)

        # Snap the cut back to the last whitespace so words survive. This is
        # the only structural courtesy the baseline extends — it knows nothing
        # about table rows, so it will still cut straight through one.
        if end < n:
            snap = text.rfind(" ", start, end)
            snap_nl = text.rfind("\n", start, end)
            snap = max(snap, snap_nl)
            if snap > start + step // 2:
                end = snap

        body = text[start:end].strip()
        if body:
            chunks.append(
                Chunk(
                    chunk_id=f"{card.recipe_id}::{STRATEGY}::c{index:03d}",
                    text=body,
                    strategy=STRATEGY,
                    section=_label_section(card, (start + end) // 2),
                    recipe_id=card.recipe_id,
                    source_file=card.source_file,
                    cuisine=card.cuisine,
                    dietary_tags=list(card.dietary_tags),
                    title=card.title,
                    char_start=start,
                    char_end=end,
                )
            )
            index += 1

        if end >= n:
            break
        start += step

    return chunks
