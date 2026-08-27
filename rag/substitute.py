"""Grounded substitution generator.

Week 5 found that the app refused all 12 substitution questions in the traffic
pool (mode 5, "refuses a swap question instead of quoting the ingredient the
card does name"). There was no substitution path to refuse WITH - the answerer
in rag/generate.py only extracts facts. This module adds one.

The design constraint that makes it evaluable
---------------------------------------------
A substitution is only allowed when ANOTHER CARD IN THE CORPUS demonstrates it.
The archive is built out of near-duplicate families on purpose:

    brioche      classic-brioche / gf-brioche / chocolate-brioche
    sourdough    sourdough-2kg / wholemeal-sourdough / rye-sourdough
    gluten-free  gf-brioche / gf-sandwich-loaf

so "make the classic brioche gluten free" has a real donor card and
"make the tikka masala dairy free" does not. Both requests look identical to a
user. Only one of them can be answered honestly, and telling them apart is
exactly the judgement this week's eval has to measure.

The model may therefore do one of two things and nothing else: propose swaps
each backed by a cited chunk, or say plainly what it cannot ground. There is no
"use your best judgement" clause, for the same reason there is not one in
rag/generate.py: an invented dairy-free swap on an allergy request is not a
rounding error.

Retrieval is two searches, not one. A single query for "make the classic
brioche gluten free" ranks the brioche cards highly and the gluten-free donor
cards barely at all, because the base recipe dominates the embedding. Searching
the base and the constraint separately and merging keeps both in context.

    python -m rag.substitute --recipe "classic brioche" --constraint "gluten free"
    python -m rag.substitute --request "make the chocolate brioche dairy free"
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from dataclasses import dataclass, field
from typing import Any

from . import trace as trc
from .config import (
    COLLECTION_NAMES,
    EMBED_MODEL,
    GEN_MAX_TOKENS,
    GEN_PROVIDER,
    HNSW_SPACE,
    TOP_K,
)
from .generate import _schema_sha, build_client, call_model
from .store import SearchHit, get_collection, search

# ---------------------------------------------------------------------------
# The substitution prompt. Version-stamped like the answerer's, because the
# eval has to be able to say which prompt produced which output.
#
# Note what is NOT in here: nothing about allergen-warning wording, nothing
# about unit formatting, nothing about whether quantities parse. Those are
# checked by eval/assertions.py, deterministically and for free. A prompt rule
# the code can enforce is a rule the model can have an off day about.
# ---------------------------------------------------------------------------
SUBSTITUTE_PROMPT = """\
You rewrite recipes from a fixed archive to meet a dietary constraint, using ONLY \
the CONTEXT blocks supplied in the user turn.

RULES

1. The CONTEXT blocks are the entire world. Nothing you know about cooking, baking, \
food science, allergies or ingredients may enter your answer. If a fact is not in a \
CONTEXT block, it does not exist.

2. You may propose a swap ONLY when a CONTEXT block shows that swap being made, or \
shows an ingredient serving the same role in a comparable recipe. Cite the chunk_id \
that shows it in `evidence_chunk_id`. A swap you cannot cite is not a swap you may \
make.

3. Copy every quantity character-for-character from a CONTEXT block. Do not convert \
units, do not scale, do not interpolate between two recipes' amounts, and do not \
estimate. If the donor recipe states a different total flour weight from the base \
recipe, say so in `unsupported` rather than rescaling it yourself.

4. `ingredients` must be the COMPLETE list for the rewritten recipe, not only the \
changed rows. Every ingredient your `method` mentions by name must appear in it.

5. If the archive contains no card that grounds the requested change, set \
`can_substitute` to false, leave `swaps` and `ingredients` empty, and name in \
`unsupported` the specific thing you could not ground. A partially groundable \
request is not groundable. This applies even when the constraint seems obvious.

6. Never claim the rewritten recipe is free of something unless a CONTEXT block \
states it. Reporting an allergen you removed is not the same as certifying the \
dish safe.\
"""

PROMPT_VERSION = "substitute-v1"
PROMPT_SHA256 = hashlib.sha256(SUBSTITUTE_PROMPT.encode("utf-8")).hexdigest()

RESPONSE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "can_substitute": {
            "type": "boolean",
            "description": "True only if every proposed swap is grounded in a cited CONTEXT block.",
        },
        "base_recipe_id": {"type": "string"},
        "title": {"type": "string"},
        "servings": {
            "type": "string",
            "description": "Yield, copied from context. Empty if the context does not state one.",
        },
        "swaps": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "removed": {"type": "string"},
                    "added": {"type": "string"},
                    "evidence_chunk_id": {"type": "string"},
                },
                "required": ["removed", "added", "evidence_chunk_id"],
            },
        },
        "ingredients": {
            "type": "array",
            "description": "The COMPLETE rewritten ingredient list, not only the changed rows.",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "amount": {"type": "string"},
                    "source_chunk_id": {"type": "string"},
                },
                "required": ["name", "amount", "source_chunk_id"],
            },
        },
        "method": {"type": "string"},
        "oven": {
            "type": "string",
            "description": "Oven setting copied from context, or empty if the dish is not baked.",
        },
        "allergen_warning": {"type": "string"},
        "unsupported": {
            "type": "string",
            "description": "What could not be grounded. Required when can_substitute is false.",
        },
    },
    "required": [
        "can_substitute",
        "base_recipe_id",
        "title",
        "servings",
        "swaps",
        "ingredients",
        "method",
        "oven",
        "allergen_warning",
        "unsupported",
    ],
}


def _strip_unsupported(node: Any) -> Any:
    if isinstance(node, dict):
        return {k: _strip_unsupported(v) for k, v in node.items() if k != "additionalProperties"}
    if isinstance(node, list):
        return [_strip_unsupported(v) for v in node]
    return node


GEMINI_SCHEMA: dict[str, Any] = _strip_unsupported(RESPONSE_SCHEMA)


@dataclass
class SubstitutionResult:
    request: str
    recipe: str
    constraint: str
    payload: dict[str, Any]
    hits: list[SearchHit]
    raw_text: str
    usage: dict[str, Any] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)
    trace_id: str | None = None

    @property
    def can_substitute(self) -> bool:
        return bool(self.payload.get("can_substitute"))


def build_context(hits: list[SearchHit]) -> str:
    blocks = []
    for h in hits:
        blocks.append(
            f'<context chunk_id="{h.chunk_id}" recipe_id="{h.recipe_id}" '
            f'source_file="{h.source_file}" section="{h.section}" '
            f'dietary_tags="{h.dietary_tags}">\n'
            f"{h.text}\n"
            f"</context>"
        )
    return "\n\n".join(blocks)


def build_user_turn(recipe: str, constraint: str, context: str) -> str:
    return (
        f"CONTEXT\n=======\n{context}\n\n"
        f"BASE RECIPE\n===========\n{recipe}\n\n"
        f"REQUESTED CHANGE\n================\n{constraint}\n\n"
        f"Rewrite the base recipe to meet the requested change, using only the "
        f"CONTEXT blocks above. If the archive does not ground the change, say so."
    )


def retrieve(
    recipe: str,
    constraint: str,
    strategy: str = "structure",
    k_base: int = 6,
    k_donor: int = 6,
) -> list[SearchHit]:
    """Two searches, merged and re-ranked by score, duplicates dropped.

    One search cannot serve this task. Embedding "make the classic brioche
    gluten free" puts all three brioches at the top and the gluten-free sandwich
    loaf nowhere, because the dish name dominates the vector. The donor card is
    the whole point of the request, so it gets its own query.
    """
    collection = get_collection(strategy)
    base_hits = search(collection, recipe, k=k_base)
    donor_hits = search(collection, f"{constraint} {recipe}", k=k_donor)

    merged: dict[str, SearchHit] = {}
    for h in base_hits + donor_hits:
        prior = merged.get(h.chunk_id)
        if prior is None or h.score > prior.score:
            merged[h.chunk_id] = h

    ordered = sorted(merged.values(), key=lambda h: h.score, reverse=True)
    from dataclasses import replace

    return [replace(h, rank=i) for i, h in enumerate(ordered, start=1)]


def substitute(
    recipe: str,
    constraint: str,
    request: str | None = None,
    strategy: str = "structure",
    client=None,
    trace: bool = True,
    trace_meta: dict[str, Any] | None = None,
) -> SubstitutionResult:
    t_retrieve = time.perf_counter()
    hits = retrieve(recipe, constraint, strategy=strategy)
    retrieve_ms = (time.perf_counter() - t_retrieve) * 1000.0
    context = build_context(hits)

    if client is None:
        client = build_client()

    t_model = time.perf_counter()
    reply = call_model_substitute(client, recipe, constraint, context)
    model_ms = (time.perf_counter() - t_model) * 1000.0

    try:
        payload = json.loads(reply.text)
    except json.JSONDecodeError:
        payload = {
            "can_substitute": False,
            "base_recipe_id": "",
            "title": "",
            "servings": "",
            "swaps": [],
            "ingredients": [],
            "method": "",
            "oven": "",
            "allergen_warning": "",
            "unsupported": "the model did not return parseable JSON",
        }

    result = SubstitutionResult(
        request=request or f"{recipe} / {constraint}",
        recipe=recipe,
        constraint=constraint,
        payload=payload,
        hits=hits,
        raw_text=reply.text,
        usage={
            "input_tokens": reply.input_tokens,
            "output_tokens": reply.output_tokens,
            "stop_reason": reply.stop_reason,
            "model": reply.model,
            "model_latency_ms": round(model_ms, 1),
        },
        notes=list(reply.notes),
    )

    if trace and trc.tracing_enabled():
        result.trace_id = trc.new_trace_id()
        trc.write(
            {
                "trace_schema": trc.TRACE_SCHEMA,
                "trace_id": result.trace_id,
                "ts": trc.utc_now(),
                "app": {"git_sha": trc.git_sha(), "entrypoint": "rag.substitute.substitute"},
                "meta": trace_meta or {},
                "request": {
                    "query": result.request,
                    "recipe": recipe,
                    "constraint": constraint,
                    "strategy": strategy,
                    "retriever": "dense-two-query",
                },
                "prompt": {
                    "version": PROMPT_VERSION,
                    "sha256": PROMPT_SHA256,
                    "system_text": SUBSTITUTE_PROMPT,
                    "user_turn_sha256": trc.sha256_text(
                        build_user_turn(recipe, constraint, context)
                    ),
                },
                "retrieval": {
                    "embed_model": EMBED_MODEL,
                    "space": HNSW_SPACE,
                    "collection": COLLECTION_NAMES[strategy],
                    "n_hits": len(hits),
                    "latency_ms": round(retrieve_ms, 1),
                    "hits": [
                        {
                            "rank": h.rank,
                            "chunk_id": h.chunk_id,
                            "score": round(float(h.score), 6),
                            "recipe_id": h.recipe_id,
                            "section": h.section,
                            "source_file": h.source_file,
                            "dietary_tags": h.dietary_tags,
                            "text": h.text,
                            "text_sha256": trc.sha256_text(h.text),
                        }
                        for h in hits
                    ],
                },
                "context": {"sha256": trc.sha256_text(context), "chars": len(context)},
                "model": {
                    "provider": GEN_PROVIDER,
                    "name": reply.model,
                    "params": {**reply.params, "response_schema": GEMINI_SCHEMA},
                },
                "output": {"raw_text": reply.text, "parsed": payload},
                "gates": {
                    "refused": not result.can_substitute,
                    "refusal_reason": str(payload.get("unsupported") or ""),
                    "notes": list(reply.notes),
                    "rendered": render(result),
                },
                "usage": {**result.usage, "model_latency_ms": round(model_ms, 1)},
            }
        )

    return result


def call_model_substitute(client, recipe: str, constraint: str, context: str):
    """Reuse the answerer's provider plumbing with this module's prompt and schema.

    Not by swapping rag.generate's globals: call_model takes them as arguments,
    so there is one retry-and-fallback ladder for both paths and the traces stay
    comparable. 12288 tokens because a full rewritten ingredient list plus method
    is several times longer than a Q&A answer, and thinking off first because
    Gemini 3.x counts reasoning tokens against the same budget - the first run of
    this module stopped at MAX_TOKENS having emitted 151 visible tokens.
    """
    return call_model(
        client,
        "",
        build_user_turn(recipe, constraint, context),
        system_prompt=SUBSTITUTE_PROMPT,
        schema=GEMINI_SCHEMA if GEN_PROVIDER != "anthropic" else RESPONSE_SCHEMA,
        max_tokens=12288,
        prefer_no_thinking=True,
    )


def render(result: SubstitutionResult) -> str:
    p = result.payload
    if not result.can_substitute:
        return f"CANNOT_SUBSTITUTE: {p.get('unsupported') or 'no reason given'}"
    lines = [p.get("title") or "(untitled)", ""]
    if p.get("servings"):
        lines.append(f"Servings: {p['servings']}")
    lines.append("")
    lines.append("Ingredients:")
    for ing in p.get("ingredients") or []:
        lines.append(f"  - {ing.get('name')}: {ing.get('amount')}  [{ing.get('source_chunk_id')}]")
    lines.append("")
    lines.append("Swaps:")
    for s in p.get("swaps") or []:
        lines.append(f"  - {s.get('removed')} -> {s.get('added')}  [{s.get('evidence_chunk_id')}]")
    lines.append("")
    if p.get("oven"):
        lines.append(f"Oven: {p['oven']}")
    lines.append("")
    lines.append("Method:")
    lines.append(f"  {p.get('method')}")
    lines.append("")
    lines.append(f"Allergens: {p.get('allergen_warning') or '(none stated)'}")
    if p.get("unsupported"):
        lines.append(f"Not grounded: {p['unsupported']}")
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser(description="Rewrite a recipe to meet a constraint.")
    ap.add_argument("--recipe", default=None)
    ap.add_argument("--constraint", default=None)
    ap.add_argument("--request", default=None, help="free text, split on ' to be ' if given")
    ap.add_argument("--strategy", default="structure")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    recipe, constraint = args.recipe, args.constraint
    if not (recipe and constraint):
        if not args.request:
            raise SystemExit("pass --recipe and --constraint, or --request")
        recipe, _, constraint = args.request.partition(" to be ")
        if not constraint:
            raise SystemExit("--request must contain ' to be ', e.g. 'classic brioche to be vegan'")

    result = substitute(recipe.strip(), constraint.strip(), request=args.request)
    if args.json:
        print(json.dumps(result.payload, indent=2))
    else:
        print(render(result))
        print()
        print(f"trace_id: {result.trace_id}  model: {result.usage.get('model')}")


if __name__ == "__main__":
    main()
