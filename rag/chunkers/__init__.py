"""The two chunking strategies under test."""

from __future__ import annotations

from ..parse import Card
from . import baseline, structure_aware
from .base import Chunk, tag_key

CHUNKERS = {
    "baseline": baseline.chunk_card,
    "structure": structure_aware.chunk_card,
}


def chunk_card(card: Card, strategy: str) -> list[Chunk]:
    if strategy not in CHUNKERS:
        raise ValueError(f"unknown chunking strategy: {strategy!r}")
    return CHUNKERS[strategy](card)


__all__ = ["CHUNKERS", "Chunk", "chunk_card", "tag_key"]
