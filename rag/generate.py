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
import hashlib
import json
import time
from dataclasses import dataclass, field
from typing import Any

from .config import (
    ANTHROPIC_MODEL,
    COLLECTION_NAMES,
    EMBED_MODEL,
    GEMINI_MODELS,
    GEN_EFFORT,
    GEN_MAX_TOKENS,
    GEN_PROVIDER,
    GEN_RETRY_ATTEMPTS,
    GEN_RETRY_WAIT_SECONDS,
    HNSW_SPACE,
    REFUSAL_TOKEN,
    STRATEGIES,
    TOP_K,
    api_key,
)
from . import trace as trc
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

# Bumped by hand whenever SYSTEM_PROMPT changes. Every trace records this label
# AND the sha256 of the text above, so a trace cannot claim a prompt version it
# did not actually run — the replay harness recomputes the hash and compares.
PROMPT_VERSION = "grounded-recipe-v1"
PROMPT_SHA256 = hashlib.sha256(SYSTEM_PROMPT.encode("utf-8")).hexdigest()


def _schema_sha(schema: dict[str, Any]) -> str:
    """Fingerprint of the JSON schema sent as the structured-output contract."""
    return hashlib.sha256(
        json.dumps(schema, sort_keys=True, separators=(',', ':')).encode('utf-8')
    ).hexdigest()


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
    trace_id: str | None = None

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


def _strip_unsupported(node: Any) -> Any:
    """Gemini's response_schema is an OpenAPI 3.0 subset.

    It rejects ``additionalProperties``, which the Anthropic schema uses to lock
    the object shape. Everything the two gates actually depend on — the
    ``required`` list containing ``can_answer``, the types, and the nested
    ``claims`` items — is supported by both, so dropping this one keyword does
    not weaken either gate.
    """
    if isinstance(node, dict):
        return {k: _strip_unsupported(v) for k, v in node.items() if k != "additionalProperties"}
    if isinstance(node, list):
        return [_strip_unsupported(v) for v in node]
    return node


GEMINI_SCHEMA: dict[str, Any] = _strip_unsupported(RESPONSE_SCHEMA)


def build_user_turn(question: str, context: str) -> str:
    return (
        f"CONTEXT\n=======\n{context}\n\n"
        f"QUESTION\n========\n{question}\n\n"
        f"Answer using only the CONTEXT blocks above."
    )


@dataclass
class ModelReply:
    """Provider-neutral reply, so the gates below never see a vendor SDK type."""

    text: str
    model: str
    stop_reason: str
    input_tokens: int | None = None
    output_tokens: int | None = None
    notes: list[str] = field(default_factory=list)
    # Every knob actually sent on THIS call, recorded per call rather than read
    # back from config.py, because the answering model is picked at runtime from
    # a fallback list and the thinking config is dropped for models that reject it.
    params: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Gemini (default) — Google AI Studio, free tier.
# ---------------------------------------------------------------------------
def _call_gemini(client, question: str, context: str) -> ModelReply:
    from google.genai import types

    notes: list[str] = []
    last_error: Exception | None = None

    # Models that rejected the thinking config, so later passes stop offering it.
    reject_thinking: set[str] = set()

    # Outer loop = one full sweep of every model. A 503 means THIS model is busy,
    # not that the API is down, and models have independent capacity, so the
    # right move is to try the next model immediately and only sleep once every
    # model in the list has turned us away.
    for sweep in range(1, GEN_RETRY_ATTEMPTS + 1):
        saw_transient = False

        for model_name in GEMINI_MODELS:
            options: list[Any] = [None]
            if model_name not in reject_thinking:
                options.append(types.ThinkingConfig(thinking_budget=0))

            for thinking in options:
                cfg: dict[str, Any] = {
                    "system_instruction": SYSTEM_PROMPT,
                    "response_mime_type": "application/json",
                    "response_schema": GEMINI_SCHEMA,
                    "max_output_tokens": GEN_MAX_TOKENS,
                    # Deterministic: a grounded extractor should not sample.
                    "temperature": 0.0,
                }
                if thinking is not None:
                    cfg["thinking_config"] = thinking

                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=build_user_turn(question, context),
                        config=types.GenerateContentConfig(**cfg),
                    )
                except Exception as exc:  # noqa: BLE001 - provider taxonomy varies
                    message = str(exc)
                    lowered = message.lower()
                    last_error = exc

                    # Transient: free-tier per-minute limit (429) or the model
                    # temporarily overloaded (503). Move to the next model now.
                    if (
                        "429" in message
                        or "resource_exhausted" in lowered
                        or "quota" in lowered
                        or "503" in message
                        or "unavailable" in lowered
                        or "overloaded" in lowered
                        or "high demand" in lowered
                    ):
                        saw_transient = True
                        kind = "overloaded" if "503" in message else "rate limited"
                        notes.append(f"{kind} on {model_name}, trying the next model")
                        break

                    # This model rejects the thinking config. The newest flash
                    # models return a bare "invalid argument" with no mention of
                    # thinking, so match on that too rather than on the word.
                    if thinking is not None and (
                        "thinking" in lowered
                        or "invalid_argument" in lowered
                        or "invalid argument" in lowered
                    ):
                        reject_thinking.add(model_name)
                        continue

                    # Model not available to this key: try the next model.
                    if "404" in message or "not found" in lowered or "not supported" in lowered:
                        break

                    raise

                usage = getattr(response, "usage_metadata", None)
                finish = "stop"
                candidates = getattr(response, "candidates", None) or []
                if candidates:
                    finish = str(getattr(candidates[0], "finish_reason", "stop") or "stop")

                notes.append(f"provider: gemini, model={model_name}")
                if thinking is not None:
                    notes.append("thinking: disabled (thinking_budget=0)")
                params = {
                    "temperature": cfg["temperature"],
                    "max_output_tokens": cfg["max_output_tokens"],
                    "response_mime_type": cfg["response_mime_type"],
                    "response_schema_sha256": _schema_sha(GEMINI_SCHEMA),
                    "thinking_budget": 0 if thinking is not None else None,
                    "model_candidates": list(GEMINI_MODELS),
                    "sweep": sweep,
                }
                return ModelReply(
                    text=response.text or "",
                    model=model_name,
                    stop_reason=finish,
                    input_tokens=getattr(usage, "prompt_token_count", None) if usage else None,
                    output_tokens=getattr(usage, "candidates_token_count", None) if usage else None,
                    notes=notes,
                    params=params,
                )

        # Every model turned us away. Only worth sleeping if the reason was
        # temporary; a list of 404s will never clear.
        if not saw_transient:
            break
        if sweep < GEN_RETRY_ATTEMPTS:
            notes.append(
                f"all {len(GEMINI_MODELS)} models busy, waiting "
                f"{GEN_RETRY_WAIT_SECONDS}s (sweep {sweep})"
            )
            time.sleep(GEN_RETRY_WAIT_SECONDS)

    raise RuntimeError(
        f"no Gemini model from {list(GEMINI_MODELS)} could be reached. "
        f"Last error: {last_error}"
    )


# ---------------------------------------------------------------------------
# Anthropic — only when GEN_PROVIDER=anthropic. Needs paid API credit.
# ---------------------------------------------------------------------------
def _call_anthropic(client, question: str, context: str) -> ModelReply:
    import anthropic

    kwargs: dict[str, Any] = {
        "model": ANTHROPIC_MODEL,
        "max_tokens": GEN_MAX_TOKENS,
        "system": SYSTEM_PROMPT,
        "output_config": {
            "effort": GEN_EFFORT,
            "format": {"type": "json_schema", "schema": RESPONSE_SCHEMA},
        },
        "messages": [{"role": "user", "content": build_user_turn(question, context)}],
    }

    notes: list[str] = ["provider: anthropic"]
    try:
        # A policy decline is re-served by the fallback model inside the same
        # call instead of stopping the run.
        response = client.beta.messages.create(
            betas=["server-side-fallback-2026-07-01"], fallbacks="default", **kwargs
        )
        notes.append("server-side refusal fallbacks: enabled")
    except anthropic.BadRequestError as exc:
        if "fallback" not in str(exc).lower() and "beta" not in str(exc).lower():
            raise
        response = client.messages.create(**kwargs)
        notes.append("server-side refusal fallbacks: unavailable on this account, disabled")

    return ModelReply(
        text=next((b.text for b in response.content if b.type == "text"), ""),
        model=response.model,
        stop_reason=str(response.stop_reason),
        input_tokens=getattr(response.usage, "input_tokens", None),
        output_tokens=getattr(response.usage, "output_tokens", None),
        notes=notes,
        params={
            "max_tokens": GEN_MAX_TOKENS,
            "effort": GEN_EFFORT,
            "output_format": "json_schema",
            "response_schema_sha256": _schema_sha(RESPONSE_SCHEMA),
        },
    )


def build_client():
    """Construct the client for the configured provider."""
    key = api_key()
    if not key:
        wanted = "GEMINI_API_KEY" if GEN_PROVIDER != "anthropic" else "ANTHROPIC_API_KEY"
        raise SystemExit(
            f"{wanted} is not set. Put it in the environment or in a .env file at the "
            f"project root (see .env.example). Search-only commands "
            f"(python -m rag.search, eval/run_hitrate.py) do not need a key."
        )
    if GEN_PROVIDER == "anthropic":
        import anthropic

        return anthropic.Anthropic(api_key=key)

    from google import genai

    return genai.Client(api_key=key)


def call_model(client, question: str, context: str) -> ModelReply:
    if GEN_PROVIDER == "anthropic":
        return _call_anthropic(client, question, context)
    return _call_gemini(client, question, context)


def _trace_record(
    *,
    trace_id: str,
    question: str,
    strategy: str,
    retriever: str,
    k: int,
    where: dict[str, Any] | None,
    code_gate: bool,
    hits: list[SearchHit],
    context: str,
    reply: ModelReply,
    result: GenerationResult,
    retrieve_ms: float,
    model_ms: float,
    meta: dict[str, Any] | None,
) -> dict[str, Any]:
    """Everything needed to replay this call without touching the vector store.

    The context STRING is not stored, only its sha256. It is rebuilt from the
    stored hits at replay time and compared against that hash, which proves the
    stored hits are sufficient to reconstruct the call rather than just claiming
    it. Storing the string too would have hidden a missing field.
    """
    return {
        "trace_schema": trc.TRACE_SCHEMA,
        "trace_id": trace_id,
        "ts": trc.utc_now(),
        "app": {"git_sha": trc.git_sha(), "entrypoint": "rag.generate.answer"},
        "meta": meta or {},
        "request": {
            "query": question,
            "strategy": strategy,
            "retriever": retriever,
            "k": k,
            "where": where,
            "code_gate": code_gate,
        },
        "prompt": {
            "version": PROMPT_VERSION,
            "sha256": PROMPT_SHA256,
            "system_text": SYSTEM_PROMPT,
            "user_turn_sha256": trc.sha256_text(build_user_turn(question, context)),
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
                    "distance": round(float(h.distance), 6),
                    "recipe_id": h.recipe_id,
                    "section": h.section,
                    "source_file": h.source_file,
                    "dietary_tags": h.dietary_tags,
                    "char_start": h.metadata.get("char_start"),
                    "char_end": h.metadata.get("char_end"),
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
            "params": reply.params,
        },
        "output": {"raw_text": reply.text, "parsed": result.model_json},
        "gates": {
            "refused": result.refused,
            "refusal_reason": result.refusal_reason,
            "notes": list(result.gate_notes),
            "rendered": result.rendered(),
        },
        "usage": {
            "input_tokens": reply.input_tokens,
            "output_tokens": reply.output_tokens,
            "stop_reason": reply.stop_reason,
            "model_latency_ms": round(model_ms, 1),
        },
    }


def answer(
    question: str,
    strategy: str,
    k: int = TOP_K,
    where: dict[str, Any] | None = None,
    code_gate: bool = True,
    client=None,
    retriever: str = "dense",
    trace: bool = True,
    trace_meta: dict[str, Any] | None = None,
) -> GenerationResult:
    t_retrieve = time.perf_counter()
    collection = get_collection(strategy)
    if retriever == "rerank":
        from .rerank import rerank_search

        hits = rerank_search(collection, question, k=k, where=where)
    else:
        hits = search(collection, question, k=k, where=where)
    retrieve_ms = (time.perf_counter() - t_retrieve) * 1000.0
    retrieved_ids = {h.chunk_id for h in hits}
    context = build_context(hits)

    if client is None:
        client = build_client()

    t_model = time.perf_counter()
    reply = call_model(client, question, context)
    model_ms = (time.perf_counter() - t_model) * 1000.0

    emit = trace and trc.tracing_enabled()
    trace_id = trc.new_trace_id() if emit else None

    def _finish(result: GenerationResult) -> GenerationResult:
        """Single exit point, so no branch below can forget to write its trace."""
        result.trace_id = trace_id
        if emit and trace_id is not None:
            trc.write(
                _trace_record(
                    trace_id=trace_id,
                    question=question,
                    strategy=strategy,
                    retriever=retriever,
                    k=k,
                    where=where,
                    code_gate=code_gate,
                    hits=hits,
                    context=context,
                    reply=reply,
                    result=result,
                    retrieve_ms=retrieve_ms,
                    model_ms=model_ms,
                    meta=trace_meta,
                )
            )
        return result

    gate_notes: list[str] = list(reply.notes)

    usage = {
        "input_tokens": reply.input_tokens,
        "output_tokens": reply.output_tokens,
        "stop_reason": reply.stop_reason,
        "model": reply.model,
    }

    # A provider-side safety decline is a refusal, not an answer. Anthropic
    # reports stop_reason="refusal"; Gemini uses finish_reason SAFETY /
    # PROHIBITED_CONTENT / BLOCKLIST / RECITATION.
    declined = {"refusal", "safety", "prohibited_content", "blocklist", "recitation"}
    if reply.stop_reason.lower().replace("finishreason.", "") in declined:
        return _finish(GenerationResult(
            question=question,
            strategy=strategy,
            refused=True,
            refusal_reason="the model's safety classifier declined this request",
            answer_text="",
            claims=[],
            hits=hits,
            gate_notes=gate_notes + [f"gate: model returned stop_reason={reply.stop_reason}"],
            usage=usage,
        ))

    text = reply.text
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return _finish(GenerationResult(
            question=question,
            strategy=strategy,
            refused=True,
            refusal_reason="the model did not return a parseable grounded answer",
            answer_text="",
            claims=[],
            hits=hits,
            gate_notes=gate_notes + ["gate: response was not valid JSON"],
            usage=usage,
        ))

    can_answer = bool(payload.get("can_answer"))
    claims = [c for c in payload.get("claims") or [] if isinstance(c, dict)]
    missing = str(payload.get("missing") or "").strip()

    # ---- Gate 1b: the model's own verdict --------------------------------
    if not can_answer:
        gate_notes.append("gate 1 (prompt/schema): model set can_answer=false")
        return _finish(GenerationResult(
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
        ))

    # ---- Gate 2: citations must be real ----------------------------------
    if code_gate:
        if not claims:
            gate_notes.append("gate 2 (code): can_answer=true but zero citations -> discarded")
            return _finish(GenerationResult(
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
            ))

        not_retrieved = [c["chunk_id"] for c in claims if c.get("chunk_id") not in retrieved_ids]
        if not_retrieved:
            gate_notes.append(
                f"gate 2 (code): cited chunk_id(s) not in the retrieved set: {not_retrieved} -> discarded"
            )
            return _finish(GenerationResult(
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
            ))

        unresolvable = [
            c["chunk_id"] for c in claims if get_chunk(strategy, c["chunk_id"]) is None
        ]
        if unresolvable:
            gate_notes.append(
                f"gate 2 (code): cited chunk_id(s) do not resolve in the store: {unresolvable} -> discarded"
            )
            return _finish(GenerationResult(
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
            ))

        gate_notes.append(
            f"gate 2 (code): all {len(claims)} citation(s) were retrieved for this question and resolve in the store"
        )
    else:
        gate_notes.append("gate 2 (code): DISABLED for this run (--no-code-gate)")

    return _finish(GenerationResult(
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
    ))


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
