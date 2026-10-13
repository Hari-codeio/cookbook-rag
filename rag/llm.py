"""One tool-calling turn against the pinned model, with honest token counting.

rag/generate.py answers questions in a single shot with a fixed JSON schema.
An agent turn is a different shape: a growing message list, tool declarations,
and a reply that is either tool calls or a final answer. Bending the existing
function to do both would have put a branch through every path the Week 5 and
Week 6 numbers came from, so this is separate and generate.py is untouched.

THE TOKEN COUNT IS THE POINT. Every lap re-sends the entire message list, so
the agent's real cost is the SUM over laps, not the last call's usage. Counting
only the final call understates a 4-lap run by roughly 4x on input tokens. This
returns per-call usage and the loop accumulates it.
"""

from __future__ import annotations

import re
import time
from dataclasses import dataclass, field
from typing import Any

from rag.config import (
    GEMINI_MODELS,
    GEN_MAX_TOKENS,
    GEN_RETRY_ATTEMPTS,
    GEN_RETRY_WAIT_SECONDS,
)

# gemini-3.1-flash-lite LIST price (paid tier), USD per 1M tokens, from
# https://ai.google.dev/pricing, checked 2026-10-13. Output includes thinking
# tokens. Held here as one constant so every cost column is reproducible and a
# pricing change is a one-line diff rather than a hunt.
#
# Weeks 7-10 used 0.10 / 0.40, an older flash-lite price, so their cost columns
# read 2.5x low on input and 3.75x low on output. Their TOKEN counts are
# unaffected. On the free tier the invoice is $0; this is what the same traffic
# costs once it outgrows the free tier, which is the number the 10x plan needs.
USD_PER_1M_INPUT = 0.25
USD_PER_1M_OUTPUT = 1.50


def usd(input_tokens: int, output_tokens: int) -> float:
    return (input_tokens / 1_000_000) * USD_PER_1M_INPUT + (
        output_tokens / 1_000_000
    ) * USD_PER_1M_OUTPUT


@dataclass
class ToolCall:
    name: str
    args: dict[str, Any]


@dataclass
class Turn:
    """One model reply."""

    tool_calls: list[ToolCall] = field(default_factory=list)
    text: str = ""
    input_tokens: int = 0
    output_tokens: int = 0
    model: str = ""
    latency_ms: float = 0.0
    finish_reason: str = ""
    # Week 11: a 429 used to be retried silently, so a rate limit showed up only
    # as a slow call. These make it visible in the trace: how many attempts were
    # turned away, how long we slept, and the quota the last 429 named.
    rate_limited: int = 0
    retry_wait_s: float = 0.0
    quota: str = ""

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens

    @property
    def cost_usd(self) -> float:
        return usd(self.input_tokens, self.output_tokens)


def to_declarations(schemas: list[dict[str, Any]]):
    from google.genai import types

    return [types.Tool(function_declarations=[dict(s) for s in schemas])]


def user_part(text: str):
    from google.genai import types

    return types.Content(role="user", parts=[types.Part.from_text(text=text)])


def model_parts(parts):
    from google.genai import types

    return types.Content(role="model", parts=list(parts))


def function_response_part(name: str, payload: dict[str, Any]):
    from google.genai import types

    return types.Part.from_function_response(name=name, response=payload)


def tool_response_content(parts):
    """Gemini wants tool results back in a user-role Content."""
    from google.genai import types

    return types.Content(role="user", parts=list(parts))


def call_with_tools(
    client,
    system_prompt: str,
    contents: list[Any],
    tool_schemas: list[dict[str, Any]] | None,
    max_tokens: int = GEN_MAX_TOKENS,
) -> Turn:
    """One turn. Retries transient errors on the SAME pinned model.

    Week 6 pinned the model so a number before a change and after it are
    comparable. A 429 here sleeps and retries rather than dropping to a weaker
    model, because a silent model swap mid-race would make the two systems'
    latency and cost columns meaningless.
    """
    from google.genai import types

    cfg: dict[str, Any] = {
        "system_instruction": system_prompt,
        "temperature": 0.0,
        "max_output_tokens": max_tokens,
    }
    if tool_schemas:
        cfg["tools"] = to_declarations(tool_schemas)
        # Let the model decide between a tool call and a final answer. Forcing
        # ANY would hide the thrash this week is trying to measure.
        cfg["tool_config"] = types.ToolConfig(
            function_calling_config=types.FunctionCallingConfig(mode="AUTO")
        )

    last_error: Exception | None = None
    rate_limited = 0
    waited_s = 0.0
    quota = ""
    for attempt in range(1, GEN_RETRY_ATTEMPTS + 1):
        for model_name in GEMINI_MODELS:
            started = time.perf_counter()
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=contents,
                    config=types.GenerateContentConfig(**cfg),
                )
            except Exception as exc:  # noqa: BLE001 - provider taxonomy varies
                last_error = exc
                lowered = str(exc).lower()
                transient = (
                    "429" in str(exc)
                    or "resource_exhausted" in lowered
                    or "503" in str(exc)
                    or "unavailable" in lowered
                    or "overloaded" in lowered
                )
                if not transient:
                    raise
                if "429" in str(exc) or "resource_exhausted" in lowered:
                    rate_limited += 1
                    quota = _quota_named(str(exc)) or quota
                continue

            latency_ms = (time.perf_counter() - started) * 1000.0
            usage = getattr(response, "usage_metadata", None)
            turn = Turn(
                input_tokens=int(getattr(usage, "prompt_token_count", 0) or 0),
                output_tokens=int(getattr(usage, "candidates_token_count", 0) or 0),
                model=model_name,
                latency_ms=latency_ms,
                rate_limited=rate_limited,
                retry_wait_s=waited_s,
                quota=quota,
            )

            candidates = getattr(response, "candidates", None) or []
            if candidates:
                turn.finish_reason = str(getattr(candidates[0], "finish_reason", "") or "")
                content = getattr(candidates[0], "content", None)
                for part in (getattr(content, "parts", None) or []):
                    fc = getattr(part, "function_call", None)
                    if fc is not None and getattr(fc, "name", None):
                        turn.tool_calls.append(
                            ToolCall(name=fc.name, args=dict(fc.args or {}))
                        )
                    elif getattr(part, "text", None):
                        turn.text += part.text
            turn.raw_parts = (  # type: ignore[attr-defined]
                getattr(candidates[0].content, "parts", []) if candidates else []
            )
            return turn

        if attempt < GEN_RETRY_ATTEMPTS:
            time.sleep(GEN_RETRY_WAIT_SECONDS)
            waited_s += GEN_RETRY_WAIT_SECONDS

    raise RuntimeError(f"all {GEN_RETRY_ATTEMPTS} attempts failed: {last_error}")


_QUOTA_RE = re.compile(r"quota(?:Id|_id)['\"]?\s*[:=]\s*['\"]?([A-Za-z0-9_-]+).*?quota(?:Value|_value)['\"]?\s*[:=]\s*['\"]?(\d+)", re.S)


def _quota_named(message: str) -> str:
    """'GenerateRequestsPerDayPerProjectPerModel-FreeTier=500' from a 429 body,
    or '' if the body names no quota. This is the only place the API says what
    the limit actually is, so it is worth keeping rather than retrying past."""
    m = _QUOTA_RE.search(message)
    return f"{m.group(1)}={m.group(2)}" if m else ""
