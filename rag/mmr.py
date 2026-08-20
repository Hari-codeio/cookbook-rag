"""BONUS — Maximal Marginal Relevance over the reranked candidate list.

The bonus premise, checked against this corpus before building anything:

    query "gluten free brioche", reranked top-5
      1. +9.028  gf-brioche        title
      2. +8.512  gf-brioche        allergens
      3. +8.413  gf-brioche        method
      4. +7.877  gf-brioche        ingredients     <- the chunk with the xanthan weight
      5. +3.879  classic-brioche   allergens

It holds, and in a sharper form than the brief describes. The brief expects three
near-copies of the same base dough crowding each other out. What actually happens
here is four sections of the SAME recipe filling the window, and the one section
carrying the number lands at rank 4, just outside the top 3.

That is a redundancy problem MMR is built for. It is also exactly where MMR's
danger lives: the four gf-brioche chunks are mutually similar partly because the
structure-aware chunker deliberately stamps the same "Recipe: ... (cuisine: ...)"
prefix on every one of them. So a diversity penalty computed on embeddings will
see them as near-duplicates and start pushing them apart, and the chunk it
demotes might be the one holding the answer.

MMR picks documents one at a time, each time maximising

    lambda * relevance(d)  -  (1 - lambda) * max similarity(d, already picked)

lambda = 1.0 is pure relevance and reduces exactly to the reranked order.
lambda = 0.0 is pure novelty and ignores the query.

Relevance here is the cross-encoder score. Those are unbounded logits, so they are
min-max normalised across the candidate window before being mixed with a cosine
similarity that lives in [-1, 1]. Without that, lambda would not mean anything
consistent from query to query.

Similarity uses the SAME embeddings already stored in Chroma, so no second model
and no extra inference. It is read straight out of the collection.
"""

from __future__ import annotations

from dataclasses import replace
from typing import Any

from .config import MMR_LAMBDA, RERANK_CANDIDATES, TOP_K
from .rerank import rerank_search
from .store import SearchHit


def _cosine(a, b) -> float:
    import numpy as np

    na = float(np.linalg.norm(a))
    nb = float(np.linalg.norm(b))
    if na == 0.0 or nb == 0.0:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def build_pool(
    collection,
    query: str,
    candidates: int = RERANK_CANDIDATES,
    where: dict[str, Any] | None = None,
):
    """The expensive half: rerank the window and fetch its embeddings once.

    Split out from selection so a lambda sweep can reuse one pool per question
    instead of paying for 25 cross-encoder pairs again at every lambda.
    """
    import numpy as np

    pool = rerank_search(
        collection, query, k=candidates, candidates=candidates, where=where
    )
    if not pool:
        return [], {}
    ids = [h.chunk_id for h in pool]
    got = collection.get(ids=ids, include=["embeddings"])
    # Chroma returns embeddings as a numpy array, so `x or []` raises
    # "truth value of an array is ambiguous". Check for None explicitly.
    got_ids = got.get("ids")
    got_embs = got.get("embeddings")
    got_ids = [] if got_ids is None else list(got_ids)
    got_embs = [] if got_embs is None else list(got_embs)
    emb_by_id = {
        cid: np.asarray(vec, dtype=float) for cid, vec in zip(got_ids, got_embs)
    }
    return pool, emb_by_id


def mmr_select(pool, emb_by_id, k: int = TOP_K, lam: float = MMR_LAMBDA):
    """The cheap half: pick k from an already-scored pool."""
    import numpy as np

    if not pool:
        return []
    if lam >= 1.0:
        return pool[:k]

    ids = [h.chunk_id for h in pool]
    # If embeddings are unavailable for any reason, degrade to plain reranking
    # rather than silently scoring diversity as zero.
    if len(emb_by_id) != len(ids):
        return pool[:k]

    raw = np.array([h.score for h in pool], dtype=float)
    spread = float(raw.max() - raw.min())
    rel = (raw - raw.min()) / spread if spread > 1e-9 else np.ones_like(raw)

    selected: list[int] = []
    remaining = list(range(len(pool)))

    while len(selected) < min(k, len(pool)) and remaining:
        best_i = remaining[0]
        best_val = float("-inf")
        for i in remaining:
            if not selected:
                val = float(rel[i])
            else:
                sim = max(
                    _cosine(emb_by_id[ids[i]], emb_by_id[ids[j]]) for j in selected
                )
                val = lam * float(rel[i]) - (1.0 - lam) * sim
            if val > best_val:
                best_val = val
                best_i = i
        selected.append(best_i)
        remaining.remove(best_i)

    return [replace(pool[i], rank=n + 1) for n, i in enumerate(selected)]


def mmr_search(
    collection,
    query: str,
    k: int = TOP_K,
    candidates: int = RERANK_CANDIDATES,
    lam: float = MMR_LAMBDA,
    where: dict[str, Any] | None = None,
) -> list[SearchHit]:
    """Rerank the candidate window, then re-select k of them with MMR."""
    pool, emb_by_id = build_pool(collection, query, candidates=candidates, where=where)
    return mmr_select(pool, emb_by_id, k=k, lam=lam)


def top_k_diversity(hits: list[SearchHit]) -> int:
    """How many distinct recipes the top-k covers. 1 means total redundancy."""
    return len({h.recipe_id for h in hits})
