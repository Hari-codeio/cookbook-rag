"""Shared chunk record.

Both chunkers emit exactly this shape, so the only thing that varies between
the two indexes is where the text was cut — not what metadata rides along with
it.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


def line_offsets(text: str) -> list[int]:
    """Char offset of the start of each line, plus a final sentinel."""
    offsets: list[int] = []
    pos = 0
    for line in text.splitlines():
        offsets.append(pos)
        pos += len(line) + 1
    offsets.append(pos)
    return offsets


def tag_key(tag: str) -> str:
    """Chroma metadata keys must be plain identifiers."""
    return "tag_" + re.sub(r"[^a-z0-9]+", "_", tag.lower()).strip("_")


@dataclass
class Chunk:
    chunk_id: str
    text: str
    strategy: str
    section: str
    recipe_id: str
    source_file: str
    cuisine: str
    dietary_tags: list[str]
    title: str
    char_start: int
    char_end: int

    def metadata(self) -> dict[str, str | int | bool]:
        """Chroma metadata values must be scalars — no lists.

        ``dietary_tags`` is therefore stored twice: once as a pipe-delimited
        string for display and citation, and once exploded into one boolean per
        tag (``tag_vegan: True``) so that ``where={"tag_vegan": True}`` is a
        real, indexed metadata filter rather than a substring hack.
        """
        md: dict[str, str | int | bool] = {
            "chunk_id": self.chunk_id,
            "source_file": self.source_file,
            "recipe_id": self.recipe_id,
            "cuisine": self.cuisine,
            "title": self.title,
            "dietary_tags": "|".join(self.dietary_tags),
            "section": self.section,
            "strategy": self.strategy,
            "char_start": self.char_start,
            "char_end": self.char_end,
        }
        for tag in self.dietary_tags:
            md[tag_key(tag)] = True
        return md
