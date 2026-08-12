"""Strategy B — structure-aware.

The contract from requirement 3: *never separate an ingredient row from its
table header or its parent recipe title*. That is enforced structurally, not by
tuning a size:

  * Ingredient rows are grouped as whole ``TableRow`` objects, so a cut can
    never land inside a row.
  * Every ingredient chunk re-prepends the recipe title AND the table's column
    header row. A chunk holding rows 9-12 of a table carries the same title and
    the same ``| Ingredient | Weight | Baker's % |`` line as the chunk holding
    rows 1-8.
  * The row budget is applied before the prefix is added, so the repeated
    prefix can never push rows out of a chunk.
  * Method prose and the allergen note become their own title-prefixed chunks,
    split on paragraph boundaries.

Deliberate omission: ``dietary_tags`` are NOT written into the chunk text, only
into metadata. If the tags were in the text they would move the embedding too,
and the requirement-4 filter demo could no longer show that the *metadata
filter* is what changed the ranking.
"""

from __future__ import annotations

import re

from ..config import STRUCTURE_PROSE_CHARS, STRUCTURE_TABLE_ROWS_PER_CHUNK
from ..parse import Card, Section
from .base import Chunk, line_offsets

STRATEGY = "structure"


def _recipe_prefix(card: Card) -> str:
    return f"Recipe: {card.title} (cuisine: {card.cuisine})"


def _split_paragraphs(text: str) -> list[str]:
    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    return paras


def _pack_paragraphs(paras: list[str], budget: int) -> list[str]:
    """Pack whole paragraphs up to the budget; only split a paragraph that
    exceeds the budget on its own, and then only on sentence boundaries."""
    packed: list[str] = []
    current: list[str] = []
    size = 0

    def flush() -> None:
        nonlocal current, size
        if current:
            packed.append("\n\n".join(current))
            current = []
            size = 0

    for para in paras:
        if len(para) > budget:
            flush()
            sentences = re.split(r"(?<=[.!?])\s+", para)
            buf: list[str] = []
            buf_len = 0
            for sentence in sentences:
                if buf and buf_len + len(sentence) + 1 > budget:
                    packed.append(" ".join(buf))
                    buf, buf_len = [], 0
                buf.append(sentence)
                buf_len += len(sentence) + 1
            if buf:
                packed.append(" ".join(buf))
            continue
        if size + len(para) + 2 > budget and current:
            flush()
        current.append(para)
        size += len(para) + 2

    flush()
    return packed


def chunk_card(card: Card) -> list[Chunk]:
    offsets = line_offsets(card.raw)
    prefix = _recipe_prefix(card)
    chunks: list[Chunk] = []
    counter = 0

    def emit(text: str, section: str, char_start: int, char_end: int) -> None:
        nonlocal counter
        if not text.strip():
            return
        chunks.append(
            Chunk(
                chunk_id=f"{card.recipe_id}::{STRATEGY}::c{counter:03d}",
                text=text.strip(),
                strategy=STRATEGY,
                section=section,
                recipe_id=card.recipe_id,
                source_file=card.source_file,
                cuisine=card.cuisine,
                dietary_tags=list(card.dietary_tags),
                title=card.title,
                char_start=char_start,
                char_end=char_end,
            )
        )
        counter += 1

    # ---- 1. title / header block ---------------------------------------
    header_sections = card.sections_of("header")
    header_body = "\n\n".join(s.text for s in header_sections if s.text.strip())
    header_start = header_sections[0].char_start if header_sections else 0
    header_end = header_sections[-1].char_end if header_sections else 0
    emit(
        f"{prefix}\nSection: Title\n{header_body}".strip(),
        "title",
        header_start,
        header_end,
    )

    # ---- 2. ingredient table -------------------------------------------
    table = card.table
    if table is not None:
        rows = table.rows
        total = len(rows)
        header_line = table.header_line()
        separator = "| " + " | ".join("---" for _ in table.header) + " |"

        for start in range(0, total, STRUCTURE_TABLE_ROWS_PER_CHUNK):
            group = rows[start : start + STRUCTURE_TABLE_ROWS_PER_CHUNK]
            first, last = group[0], group[-1]
            row_lines = "\n".join(
                "| " + " | ".join(r.cells) + " |" if table.kind == "aligned" else r.raw.strip()
                for r in group
            )
            body = (
                f"{prefix}\n"
                f"Section: Ingredients (rows {start + 1}-{start + len(group)} of {total})\n"
                f"{header_line}\n{separator}\n{row_lines}"
            )
            emit(
                body,
                "ingredients",
                offsets[first.line_no],
                offsets[min(last.line_no + 1, len(offsets) - 1)],
            )

    # ---- 3. every other section, as prose ------------------------------
    table_lines: set[int] = set()
    if table is not None:
        table_lines = set(range(table.line_start, table.line_end + 1))

    def section_prose(section: Section) -> str:
        """Section text with the table's own lines removed."""
        if not table_lines:
            return section.text
        kept = [
            line
            for i, line in enumerate(
                card.raw.splitlines()[section.line_start : section.line_end + 1],
                start=section.line_start,
            )
            if i not in table_lines
        ]
        return "\n".join(kept)

    for section in card.sections:
        if section.kind == "header":
            continue
        body = section_prose(section)
        # Drop the heading line itself from the body; it is restated in the prefix.
        body = re.sub(r"^#{1,6}\s+.*\n?", "", body, count=1)
        paras = _split_paragraphs(body)
        if not paras:
            continue

        label = section.heading or section.kind.title()
        for part in _pack_paragraphs(paras, STRUCTURE_PROSE_CHARS):
            emit(
                f"{prefix}\nSection: {label}\n{part}",
                section.kind if section.kind != "other" else "notes",
                section.char_start,
                section.char_end,
            )

    return chunks
