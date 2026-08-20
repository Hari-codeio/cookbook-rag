"""THE ONE RETRIEVAL CHANGE — cross-encoder rerank over the top 25.

Chosen from the failure tally in out/answer_eval_before.md, not from taste:

    PASS 9   R 2   G 1   Not-In-Corpus 0

Both R failures have the correct chunk sitting INSIDE the candidate window:

    g03  psyllium husk amount              correct chunk at rank 14 of 94
    g09  hydration of the wholemeal loaf   correct chunk at rank 13 of 94

Reordering the top 25 can reach both. That is the entire job of a reranker, so
the change is aimed exactly at the failures that exist.

Why NOT BM25 + RRF, the other option offered
--------------------------------------------
BM25 matches literal terms. It would very likely fix g03, because "psyllium
husk" appears verbatim in the target chunk. It structurally cannot fix g09: the
query's key term is "hydration", and the word hydration appears NOWHERE on the
wholemeal sourdough card. The card states the fact as

    | Water (28 C) | 800 g | 80% |

so there is no lexical bridge from "hydration" to "80%" for BM25 to cross. A
cross-encoder reads the query and the passage together and can make that jump.
One change has to cover both R failures, and only reranking does.

Why not swap the embedding model, as the team lead suggested
-----------------------------------------------------------
Honestly: it is not structurally ruled out here, and I am not going to pretend
otherwise just because the brief primes you to reject it. The brief's argument
against it holds when failures are exact-term misses, where the correct chunk is
unreachable. Mine are not that - both correct chunks were retrieved and merely
mis-ordered, and a stronger embedder could plausibly reorder them. It is still
the worse choice: it re-embeds all 94 chunks, invalidates every number measured
in Week 3, and changes the representation for the 9 questions that already pass.
Reranking leaves the index untouched and only reorders. Smaller blast radius for
the same target.

A cost the write-up states plainly: cross-encoder scores are relevance logits,
not cosine similarity. They are not comparable to the dense scores in the before
run, and they are not bounded to [0, 1]. Only the ORDER is comparable.

    python eval/run_hitrate3.py --retriever rerank --label after
"""

from __future__ import annotations

from dataclasses import replace
from typing import Any

from .config import RERANK_CANDIDATES, RERANK_MODEL, TOP_K
from .store import SearchHit, search

_encoder = None


def get_encoder():
    """Lazy, cached. The ONNX model is ~80 MB and loads once per process."""
    global _encoder
    if _encoder is None:
        from fastembed.rerank.cross_encoder import TextCrossEncoder

        _encoder = TextCrossEncoder(model_name=RERANK_MODEL)
    return _encoder


def rerank_search(
    collection,
    query: str,
    k: int = TOP_K,
    where: dict[str, Any] | None = None,
    candidates: int = RERANK_CANDIDATES,
) -> list[SearchHit]:
    """Dense retrieve a candidate window, then reorder it with a cross-encoder.

    The dense stage is unchanged - same collection, same embedder, same cosine
    space - so this is one variable, bolted on after retrieval.

    Anything beyond the candidate window keeps its dense order and is appended
    untouched. That matters for measurement: the hit-rate harness asks for the
    rank of the expected chunk across the WHOLE collection, and without the tail
    that rank would be undefined for chunks the reranker never saw.
    """
    pool_size = max(candidates, k)
    pool = search(collection, query, k=pool_size, where=where)
    if not pool:
        return []

    head = pool[:candidates]
    tail = pool[candidates:]

    scores = list(get_encoder().rerank(query, [h.text for h in head]))
    order = sorted(range(len(head)), key=lambda i: scores[i], reverse=True)

    out: list[SearchHit] = []
    for new_rank, i in enumerate(order, start=1):
        out.append(replace(head[i], rank=new_rank, score=float(scores[i])))
    for offset, h in enumerate(tail, start=len(out) + 1):
        out.append(replace(h, rank=offset))

    return out[:k]
