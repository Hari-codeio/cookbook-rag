"""Grounded answerer with a FORCED refusal.

Requirement 5 wants cited answers for what the corpus contains and refusals for
what it does not. The common way to fail that is a grounding prompt that says
"if the context is insufficient, use your best judgement" — which is exactly how
an invented gram weight ends up in a reader's dough. That sentence does not
appear here. Instead there are two independent gates:

Gate 1 (prompt + schema).  The system prompt forbids outside knowledge and
forbids stating any quantity not written verbatim in context. The response is
additionally constrained by ``output_config.format`` to a JSON schema whose
``can_answer`` boolean is a required field — the model cannot dodge the question
of whether it actually had the facts.

Gate 2 (code).  Every chunk_id the model cites is checked against the set of
chunk_ids actually retrieved for this question, and then resolved against the
store. A citation that was not retrieved, or that does not resolve, discards the
answer and emits the refusal instead. Citation fabrication is therefore
structurally detectable rather than merely discouraged.

Either gate alone produces a refusal; ``--no-code-gate`` exists so the write-up
can demonstrate that the prompt gate still refuses on its own.

    python -m rag.generate "how much salt is in the 2kg sourdough?" --strategy structure
    python -m rag.generate "what is the sodium content per slice?" --show-context
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field
from typing import Any

from .config import (
    GEN_EFFORT,
    GEN_MAX_TOKENS,
    GEN_MODEL,
    REFUSAL_TOKEN,
    STRATEGIES,
    TOP_K,
    api_key,
)
from .store import SearchHit, get_chunk, get_collection, search

# ---------------------------------------------------------------------------
# Gate 1a — the grounding prompt.
#
# Read rule 4 and rule 5 carefully: refusal is the REQUIRED output for anything
# not fully present in context. There is no discretion clause anywhere in this
# prompt, and the words "judgement", "best guess", "reasonable", and "estimate"
# appear only as prohibitions.
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """\
You answer questions about a recipe archive using ONLY the CONTEXT blocks supplied \
in the user turn.

RULES

1. The CONTEXT blocks are the entire world. Nothing you know about cooking, baking, \
fermentation, food science, nutrition, or ingredients may enter your answer. If a \
fact is not in a CONTEXT block, it does not exist.

2. Every claim in `answer` must be supported by a chunk you cite in `claims`. Each \
`chunk_id` you cite must be copied character-for-character from a CONTEXT block \
header in THIS request. Never invent, guess, shorten, reformat, or construct a \
chunk_id.

3. Never state a weight, percentage, temperature, duration, hydration figure, or any \
other quantity unless it appears verbatim in a CONTEXT block. Do not convert units, \
do not do arithmetic, do not scale a recipe up or down, do not interpolate between \
two values, and do not estimate.

4. If the CONTEXT does not contain the answer, set `can_answer` to false, set \
`answer` to an empty string, leave `claims` empty, and write in `missing` the \
specific fact that is absent. This applies even when the context is close, \
related, about a similar recipe, or about the right recipe but the wrong detail.

5. A partially answerable question is not answerable. If any part of the requested \
fact is missing from CONTEXT, set `can_answer` to false.

6. Do not apologise, do not offer to help further, and do not suggest where the \
information might otherwise be found.\
"""

RESPONSE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "can_answer": {
            "type": "boolean",
            "description": "True only if every part of the answer is present verbatim in CONTEXT.",
        },
        "answer": {
            "type": "string",
            "description": "The answer, or an empty string when can_answer is false.",
        },
        "claims": {
            "type": "array",
            "description": "One entry per factual claim in `answer`. Empty when can_answer is false.",
            "items": {
                "type": "object",
                "properties": {
                    "claim": {"type": "string"},
                    "chunk_id": {
                        "type": "string",
                        "description": "Copied exactly from a CONTEXT block header.",
                    },
                },
                "required": ["claim", "chunk_id"],
                "additionalProperties": False,
            },
        },
        "missing": {
            "type": "string",
            "description": "When can_answer is false, the specific fact absent from CONTEXT.",
        },
    },
    "required": ["can_answer", "answer", "claims", "missing"],
    "additionalProperties": False,
}


@dataclass
class GenerationResult:
    question: str
    strategy: str
    refused: bool
    refusal_reason: str
    answer_text: str
    claims: list[dict[str, str]]
    hits: list[SearchHit]
    gate_notes: list[str] = field(default_factory=list)
    model_json: dict[str, Any] | None = None
    usage: dict[str, Any] = field(default_factory=dict)

    def rendered(self) -> str:
        if self.refused:
            return f"{REFUSAL_TOKEN}: {self.refusal_reason}"
        lines = [self.answer_text.strip()]
        if self.claims:
            lines.append("")
            for c in self.claims:
                lines.append(f"  - {c['claim']}  [{c['chunk_id']}]")
        return "\n".join(lines)


def build_context(hits: list[SearchHit]) -> str:
    blocks = []
    for h in hits:
        blocks.append(
            f"<context chunk_id=\"{h.chunk_id}\" recipe_id=\"{h.recipe_id}\" "
            f"source_file=\"{h.source_file}\" section=\"{h.section}\">\n"
            f"{h.text}\n"
            f"</context>"
        )
    return "\n\n".join(blocks)


def _call_model(client, question: str, context: str, use_fallbacks: bool):
    user_turn = (
        f"CONTEXT\n=======\n{context}\n\n"
        f"QUESTION\n========\n{question}\n\n"
        f"Answer using only the CONTEXT blocks above."
    )
    kwargs: dict[str, Any] = {
        "model": GEN_MODEL,
        "max_tokens": GEN_MAX_TOKENS,
        "system": SYSTEM_PROMPT,
        "output_config": {
            "effort": GEN_EFFORT,
            "format": {"type": "json_schema", "schema": RESPONSE_SCHEMA},
        },
        "messages": [{"role": "user", "content": user_turn}],
    }
    if use_fallbacks:
        # Recommended for claude-opus-5: a policy decline is re-served by the
        # fallback model inside the same call instead of stopping the run.
        return client.beta.messages.create(
            betas=["server-side-fallback-2026-07-01"], fallbacks="default", **kwargs
        )
    return client.messages.create(**kwargs)


def answer(
    question: str,
    strategy: str,
    k: int = TOP_K,
    where: dict[str, Any] | None = None,
    code_gate: bool = True,
    client=None,
) -> GenerationResult:
    import anthropic

    collection = get_collection(strategy)
    hits = search(collection, question, k=k, where=where)
    retrieved_ids = {h.chunk_id for h in hits}

    if client is None:
        key = api_key()
        if not key:
            raise SystemExit(
                "ANTHROPIC_API_KEY is not set. Put it in the environment or in a .env "
                "file at the project root (see .env.example). Search-only commands "
                "(python -m rag.search, eval/run_hitrate.py) do not need a key."
            )
        client = anthropic.Anthropic(api_key=key)

    gate_notes: list[str] = []

    try:
        response = _call_model(client, question, build_context(hits), use_fallbacks=True)
        gate_notes.append("server-side refusal fallbacks: enabled")
    except anthropic.BadRequestError as exc:  # beta unavailable on this account
        if "fallback" not in str(exc).lower() and "beta" not in str(exc).lower():
            raise
        response = _call_model(client, question, build_context(hits), use_fallbacks=False)
        gate_notes.append("server-side refusal fallbacks: unavailable on this account, disabled")

    usage = {
        "input_tokens": getattr(response.usage, "input_tokens", None),
        "output_tokens": getattr(response.usage, "output_tokens", None),
        "stop_reason": response.stop_reason,
        "model": response.model,
    }

    # Opus 5 safety classifiers can decline; that is a refusal, not an answer.
    if response.stop_reason == "refusal":
        return GenerationResult(
            question=question,
            strategy=strategy,
            refused=True,
            refusal_reason="the model's safety classifier declined this request",
            answer_text="",
            claims=[],
            hits=hits,
            gate_notes=gate_notes + ["gate: model returned stop_reason=refusal"],
            usage=usage,
        )

    text = next((b.text for b in response.content if b.type == "text"), "")
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return GenerationResult(
            question=question,
            strategy=strategy,
            refused=True,
            refusal_reason="the model did not return a parseable grounded answer",
            answer_text="",
            claims=[],
            hits=hits,
            gate_notes=gate_notes + ["gate: response was not valid JSON"],
            usage=usage,
        )

    can_answer = bool(payload.get("can_answer"))
    claims = [c for c in payload.get("claims") or [] if isinstance(c, dict)]
    missing = str(payload.get("missing") or "").strip()

    # ---- Gate 1b: the model's own verdict --------------------------------
    if not can_answer:
        gate_notes.append("gate 1 (prompt/schema): model set can_answer=false")
        return GenerationResult(
            question=question,
            strategy=strategy,
            refused=True,
            refusal_reason=missing or "the retrieved context does not contain this fact",
            answer_text="",
            claims=[],
            hits=hits,
            gate_notes=gate_notes,
            model_json=payload,
            usage=usage,
        )

    # ---- Gate 2: citations must be real ----------------------------------
    if code_gate:
        if not claims:
            gate_notes.append("gate 2 (code): can_answer=true but zero citations -> discarded")
            return GenerationResult(
                question=question,
                strategy=strategy,
                refused=True,
                refusal_reason="the model answered without citing any chunk",
                answer_text="",
                claims=[],
                hits=hits,
                gate_notes=gate_notes,
                model_json=payload,
                usage=usage,
            )

        not_retrieved = [c["chunk_id"] for c in claims if c.get("chunk_id") not in retrieved_ids]
        if not_retrieved:
            gate_notes.append(
                f"gate 2 (code): cited chunk_id(s) not in the retrieved set: {not_retrieved} -> discarded"
            )
            return GenerationResult(
                question=question,
                strategy=strategy,
                refused=True,
                refusal_reason=f"the model cited chunk_id(s) that were never retrieved: {not_retrieved}",
                answer_text="",
                claims=[],
                hits=hits,
                gate_notes=gate_notes,
                model_json=payload,
                usage=usage,
            )

        unresolvable = [
            c["chunk_id"] for c in claims if get_chunk(strategy, c["chunk_id"]) is None
        ]
        if unresolvable:
            gate_notes.append(
                f"gate 2 (code): cited chunk_id(s) do not resolve in the store: {unresolvable} -> discarded"
            )
            return GenerationResult(
                question=question,
                strategy=strategy,
                refused=True,
                refusal_reason=f"the model cited chunk_id(s) that do not exist: {unresolvable}",
                answer_text="",
                claims=[],
                hits=hits,
                gate_notes=gate_notes,
                model_json=payload,
                usage=usage,
            )

        gate_notes.append(
            f"gate 2 (code): all {len(claims)} citation(s) were retrieved for this question and resolve in the store"
        )
    else:
        gate_notes.append("gate 2 (code): DISABLED for this run (--no-code-gate)")

    return GenerationResult(
        question=question,
        strategy=strategy,
        refused=False,
        refusal_reason="",
        answer_text=str(payload.get("answer") or ""),
        claims=[{"claim": str(c.get("claim", "")), "chunk_id": str(c.get("chunk_id", ""))} for c in claims],
        hits=hits,
        gate_notes=gate_notes,
        model_json=payload,
        usage=usage,
    )


def render_transcript(result: GenerationResult, show_context: bool = False) -> str:
    lines = [
        "```text",
        f"Q ({result.strategy}): {result.question}",
        "",
        f"retrieved (top-{len(result.hits)}):",
    ]
    for h in result.hits:
        lines.append(f"  {h.rank}. {h.chunk_id}  score={h.score:.4f}  section={h.section}")
    if show_context:
        lines.append("")
        lines.append("context supplied to the model:")
        for h in result.hits:
            lines.append(f"  --- {h.chunk_id} ---")
            for line in h.text.splitlines():
                lines.append(f"  {line}")
    lines.append("")
    lines.append("A:")
    for line in result.rendered().splitlines():
        lines.append(f"  {line}")
    lines.append("")
    lines.append("gates:")
    for note in result.gate_notes:
        lines.append(f"  - {note}")

    if not result.refused and result.claims:
        lines.append("")
        lines.append("citation resolution (each cited chunk_id looked up in the store):")
        for c in result.claims:
            resolved = get_chunk(result.strategy, c["chunk_id"])
            if resolved is None:
                lines.append(f"  - {c['chunk_id']}: DOES NOT RESOLVE")
                continue
            meta = resolved["metadata"]
            snippet = " / ".join(
                s.strip() for s in resolved["text"].splitlines() if s.strip()
            )[:160]
            lines.append(
                f"  - {c['chunk_id']} -> recipe_id={meta.get('recipe_id')} "
                f"source_file={meta.get('source_file')} section={meta.get('section')}"
            )
            lines.append(f"      chunk text: {snippet}")
    lines.append(f"model: {result.usage.get('model')}  stop_reason={result.usage.get('stop_reason')}")
    lines.append("```")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Answer a question, grounded, or refuse.")
    parser.add_argument("question")
    parser.add_argument("--strategy", default="structure", choices=list(STRATEGIES))
    parser.add_argument("--k", type=int, default=TOP_K)
    parser.add_argument("--show-context", action="store_true")
    parser.add_argument(
        "--no-code-gate",
        action="store_true",
        help="disable gate 2 to demonstrate that the prompt gate refuses on its own",
    )
    args = parser.parse_args()

    result = answer(args.question, args.strategy, k=args.k, code_gate=not args.no_code_gate)
    print(render_transcript(result, show_context=args.show_context))


if __name__ == "__main__":
    main()
