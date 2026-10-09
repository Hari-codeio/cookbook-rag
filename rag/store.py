"""Chroma-backed vector store.

Two collections live in one persistent client — ``recipes_baseline`` and
``recipes_structure`` — built from the same cards with the same embedding
function and differing only in how the text was cut.

The embedding function is pinned in :mod:`rag.config` and stamped into each
collection's metadata at creation. Opening a collection whose stamp disagrees
with the current config raises, because a chunker comparison across two
different embedders measures nothing.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from .chunkers.base import Chunk
from .config import CHROMA_DIR, COLLECTION_NAMES, EMBED_MODEL, HNSW_SPACE, TOP_K

if TYPE_CHECKING:
    import chromadb

# chromadb is imported inside the two functions that use it, not at module
# level. Importing this module (rag/generate.py does, for build_client) must
# not drag chromadb -> grpc in for callers that never touch the vector store:
# the agent, the squad and the race only need a Gemini client.


def build_embedding_function():
    """all-MiniLM-L6-v2 under onnxruntime. Identical for index and query."""
    from chromadb.utils import embedding_functions

    if hasattr(embedding_functions, "DefaultEmbeddingFunction"):
        return embedding_functions.DefaultEmbeddingFunction()
    return embedding_functions.ONNXMiniLM_L6_V2()  # pragma: no cover


def get_client() -> chromadb.ClientAPI:
    import chromadb

    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(CHROMA_DIR))


def get_collection(strategy: str, create: bool = False):
    if strategy not in COLLECTION_NAMES:
        raise ValueError(f"unknown strategy {strategy!r}")
    client = get_client()
    name = COLLECTION_NAMES[strategy]
    ef = build_embedding_function()

    if not create:
        collection = client.get_collection(name=name, embedding_function=ef)
    else:
        meta = {"hnsw:space": HNSW_SPACE, "embed_model": EMBED_MODEL, "strategy": strategy}
        try:
            collection = client.get_or_create_collection(
                name=name, embedding_function=ef, metadata=meta
            )
        except Exception:  # pragma: no cover - chroma API drift
            collection = client.get_or_create_collection(
                name=name,
                embedding_function=ef,
                configuration={"hnsw": {"space": HNSW_SPACE}},
                metadata={"embed_model": EMBED_MODEL, "strategy": strategy},
            )

    stamped = (collection.metadata or {}).get("embed_model")
    if stamped and stamped != EMBED_MODEL:
        raise RuntimeError(
            f"collection {name!r} was built with embed_model={stamped!r} but config "
            f"now says {EMBED_MODEL!r}. Comparing chunkers across two embedders "
            f"measures nothing — delete out/chroma and re-ingest."
        )
    return collection


def collection_exists(strategy: str) -> bool:
    client = get_client()
    names = {c if isinstance(c, str) else c.name for c in client.list_collections()}
    return COLLECTION_NAMES[strategy] in names


def existing_ids(collection, ids: list[str]) -> set[str]:
    """Which of these chunk_ids are already in the collection."""
    if not ids:
        return set()
    found: set[str] = set()
    for i in range(0, len(ids), 500):
        batch = ids[i : i + 500]
        got = collection.get(ids=batch, include=[])
        found.update(got.get("ids") or [])
    return found


def add_chunks(collection, chunks: list[Chunk], batch_size: int = 128) -> int:
    """Append chunks. Refuses to touch an id that is already present."""
    if not chunks:
        return 0

    ids = [c.chunk_id for c in chunks]
    duplicates_within = {i for i in ids if ids.count(i) > 1}
    if duplicates_within:
        raise RuntimeError(f"chunker produced duplicate chunk_ids: {sorted(duplicates_within)[:5]}")

    clashes = existing_ids(collection, ids)
    if clashes:
        raise RuntimeError(
            f"{len(clashes)} chunk_id(s) already exist in the collection, e.g. "
            f"{sorted(clashes)[:3]}. Ingest is append-only; it will not rewrite "
            f"an existing chunk. Delete out/chroma to rebuild from scratch."
        )

    for i in range(0, len(chunks), batch_size):
        batch = chunks[i : i + batch_size]
        collection.add(
            ids=[c.chunk_id for c in batch],
            documents=[c.text for c in batch],
            metadatas=[c.metadata() for c in batch],
        )
    return len(chunks)


@dataclass
class SearchHit:
    rank: int
    chunk_id: str
    score: float
    distance: float
    text: str
    metadata: dict[str, Any]

    @property
    def recipe_id(self) -> str:
        return str(self.metadata.get("recipe_id", ""))

    @property
    def section(self) -> str:
        return str(self.metadata.get("section", ""))

    @property
    def source_file(self) -> str:
        return str(self.metadata.get("source_file", ""))

    @property
    def dietary_tags(self) -> str:
        return str(self.metadata.get("dietary_tags", ""))


def search(
    collection,
    query: str,
    k: int = TOP_K,
    where: dict[str, Any] | None = None,
) -> list[SearchHit]:
    """Search-only. No LLM is involved on this path at all.

    ``where`` is applied by Chroma BEFORE ranking, so a filtered query re-ranks
    the surviving subset rather than trimming an unfiltered top-k.
    """
    kwargs: dict[str, Any] = {
        "query_texts": [query],
        "n_results": k,
        "include": ["documents", "metadatas", "distances"],
    }
    if where:
        kwargs["where"] = where

    res = collection.query(**kwargs)
    docs = (res.get("documents") or [[]])[0]
    metas = (res.get("metadatas") or [[]])[0]
    dists = (res.get("distances") or [[]])[0]
    ids = (res.get("ids") or [[]])[0]

    hits: list[SearchHit] = []
    for rank, (cid, doc, meta, dist) in enumerate(zip(ids, docs, metas, dists), start=1):
        meta = meta or {}
        hits.append(
            SearchHit(
                rank=rank,
                chunk_id=str(meta.get("chunk_id") or cid),
                score=1.0 - float(dist),
                distance=float(dist),
                text=doc or "",
                metadata=dict(meta),
            )
        )
    return hits


def get_chunk(strategy: str, chunk_id: str) -> dict[str, Any] | None:
    """Resolve a chunk_id back to its stored text — the citation check."""
    collection = get_collection(strategy)
    got = collection.get(ids=[chunk_id], include=["documents", "metadatas"])
    if not got.get("ids"):
        return None
    return {
        "chunk_id": chunk_id,
        "text": (got.get("documents") or [""])[0],
        "metadata": (got.get("metadatas") or [{}])[0] or {},
    }
