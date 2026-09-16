"""The agent: a model choosing which tool to call next, until it answers.

    python -m rag.agent "Make the shakshuka 1.5x and take out the egg"

FOUR BUDGETS, ALL FOUR CHECKED EVERY LAP.

The common failure this is written against is declaring MAX_ITERS, MAX_TOKENS
and MAX_COST as module constants and then only ever testing the iteration
counter. An unenforced budget is a comment with ambition. So `_over_budget`
returns the name of whichever budget tripped, it is called at the top of every
lap AND again after each model call, and every one of the four has a test case
that fires it.

Termination is CLEAN. A tripped budget does not raise. It stops the loop, sets
`terminated_by` to the budget's name, and returns whatever partial answer exists
with ok=False. A run that dies on an exception cannot be told apart from a run
that hit a wall, and the log has to show which one happened.
"""

from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass
from typing import Any

from rag.contract import RunResult
from rag.llm import (
    call_with_tools,
    function_response_part,
    model_parts,
    tool_response_content,
    user_part,
)
from rag.tools import REGISTRY_V1, TOOL_SCHEMAS_V1, ToolResult

FENCE_RE = re.compile(r"```(?:json)?\s*(.*?)\s*```", re.DOTALL)


@dataclass(frozen=True)
class Budgets:
    """All four are enforced. Defaults are sized for this corpus: a correct run
    takes 3 to 5 laps, so 8 leaves room for one wrong turn and stops a spin."""

    max_laps: int = 8
    max_tokens: int = 40_000
    max_cost_usd: float = 0.02
    max_seconds: float = 90.0


SYSTEM_PROMPT = """\
You adapt recipes from a fixed archive of 21 cards, using the tools provided.

THE TASK, every time: find the recipe the user names, scale it by the factor they
ask for, remove any ingredient carrying an allergen they cannot eat, and return
the method.

RULES

1. Work only from what the tools return. You have no other knowledge of these
   recipes. Never invent an ingredient, an amount or a method step.
2. Never do arithmetic yourself. scale_recipe returns the scaled amounts already
   computed. Copy them exactly as given.
3. A substitute you introduce must itself be checked. If the replacement carries
   the same allergen the user is avoiding, it is not a valid substitute and you
   must choose again. Keep going until every remaining ingredient is safe.
4. When you are done, reply with ONE JSON object and no other text:

{
  "recipe_id": "<the archive id>",
  "title": "<the recipe title>",
  "scale_factor": <the number you were asked for>,
  "ingredients": [{"ingredient": "...", "amount": "<scaled amount>"}],
  "substitutions": [{"from": "<ingredient removed>", "to": "<what replaced it>", "reason": "..."}],
  "method": "<the method text>",
  "unsupported": "<anything you could not ground, or an empty string>"
}

If nothing had to be substituted, "substitutions" is an empty list.
"""


def _parse_answer(text: str) -> dict[str, Any] | None:
    if not text or not text.strip():
        return None
    fenced = FENCE_RE.search(text)
    candidate = fenced.group(1) if fenced else text
    candidate = candidate.strip()
    try:
        parsed = json.loads(candidate)
        return parsed if isinstance(parsed, dict) else None
    except json.JSONDecodeError:
        pass
    # Last resort: the outermost {...} span.
    start, end = candidate.find("{"), candidate.rfind("}")
    if start != -1 and end > start:
        try:
            parsed = json.loads(candidate[start : end + 1])
            return parsed if isinstance(parsed, dict) else None
        except json.JSONDecodeError:
            return None
    return None


def _over_budget(
    budgets: Budgets, laps: int, tokens: int, cost: float, started: float
) -> str:
    """Return the name of the first budget exceeded, or "" if all are fine.

    Every one of the four is tested here, and this is the ONLY place the
    question is asked, so a budget cannot be enforced in one branch and
    forgotten in another.
    """
    if laps >= budgets.max_laps:
        return "max_laps"
    if tokens >= budgets.max_tokens:
        return "max_tokens"
    if cost >= budgets.max_cost_usd:
        return "max_cost_usd"
    if (time.perf_counter() - started) >= budgets.max_seconds:
        return "max_seconds"
    return ""


def run_agent(
    client,
    request: str,
    budgets: Budgets | None = None,
    tool_schemas: list[dict[str, Any]] | None = None,
    registry: dict[str, Any] | None = None,
    system_prompt: str | None = None,
) -> RunResult:
    budgets = budgets or Budgets()
    tool_schemas = tool_schemas if tool_schemas is not None else TOOL_SCHEMAS_V1
    registry = registry if registry is not None else REGISTRY_V1
    system_prompt = system_prompt or SYSTEM_PROMPT

    result = RunResult()
    contents: list[Any] = [user_part(request)]
    started = time.perf_counter()

    while True:
        tripped = _over_budget(
            budgets, result.laps, result.total_tokens, result.cost_usd, started
        )
        if tripped:
            result.terminated_by = tripped
            result.ok = False
            result.error = f"budget {tripped} exceeded"
            result.log.append({"event": "budget_exceeded", "budget": tripped, "lap": result.laps})
            break

        turn = call_with_tools(client, system_prompt, contents, tool_schemas)
        result.laps += 1
        result.input_tokens += turn.input_tokens
        result.output_tokens += turn.output_tokens
        result.cost_usd += turn.cost_usd

        result.log.append(
            {
                "event": "model_turn",
                "lap": result.laps,
                "tool_calls": [tc.name for tc in turn.tool_calls],
                "input_tokens": turn.input_tokens,
                "output_tokens": turn.output_tokens,
                "cumulative_tokens": result.total_tokens,
                "cumulative_cost_usd": round(result.cost_usd, 6),
                "elapsed_s": round(time.perf_counter() - started, 2),
            }
        )

        # Checked again straight after the call: a single expensive turn can
        # blow the token or cost budget without the lap counter moving.
        tripped = _over_budget(
            budgets, result.laps, result.total_tokens, result.cost_usd, started
        )
        if tripped:
            result.terminated_by = tripped
            result.ok = False
            result.error = f"budget {tripped} exceeded"
            result.log.append({"event": "budget_exceeded", "budget": tripped, "lap": result.laps})
            break

        if not turn.tool_calls:
            answer = _parse_answer(turn.text)
            if answer is None:
                result.ok = False
                result.error = "final reply was not parseable JSON"
                result.log.append({"event": "unparseable_final", "lap": result.laps})
            else:
                result.answer = answer
                result.ok = True
                result.log.append({"event": "answered", "lap": result.laps})
            break

        contents.append(model_parts(getattr(turn, "raw_parts", [])))
        response_parts = []
        for call in turn.tool_calls:
            fn = registry.get(call.name)
            if fn is None:
                payload = {"ok": False, "error": f"no such tool {call.name!r}"}
            else:
                try:
                    out: ToolResult = fn(**call.args)
                    payload = {"ok": out.ok, "error": out.error, **out.data}
                except TypeError as exc:
                    payload = {"ok": False, "error": f"bad arguments for {call.name}: {exc}"}
            result.log.append(
                {
                    "event": "tool_result",
                    "lap": result.laps,
                    "tool": call.name,
                    "args": call.args,
                    "ok": bool(payload.get("ok")),
                    "error": payload.get("error", ""),
                }
            )
            response_parts.append(function_response_part(call.name, payload))
        contents.append(tool_response_content(response_parts))

    result.latency_ms = (time.perf_counter() - started) * 1000.0
    return result


def main() -> None:
    import argparse

    from rag.generate import build_client

    ap = argparse.ArgumentParser(description="Run the recipe agent on one request.")
    ap.add_argument("request")
    ap.add_argument("--max-laps", type=int, default=Budgets.max_laps)
    ap.add_argument("--max-tokens", type=int, default=Budgets.max_tokens)
    ap.add_argument("--max-cost", type=float, default=Budgets.max_cost_usd)
    ap.add_argument("--max-seconds", type=float, default=Budgets.max_seconds)
    args = ap.parse_args()

    budgets = Budgets(args.max_laps, args.max_tokens, args.max_cost, args.max_seconds)
    result = run_agent(build_client(), args.request, budgets)

    for entry in result.log:
        print(json.dumps(entry, ensure_ascii=False))
    print()
    print(f"ok            : {result.ok}")
    print(f"terminated_by : {result.terminated_by or '(ran to completion)'}")
    print(f"laps          : {result.laps}")
    print(f"tokens        : {result.total_tokens} (in {result.input_tokens} / out {result.output_tokens})")
    print(f"cost          : ${result.cost_usd:.6f}")
    print(f"latency       : {result.latency_ms:.0f} ms")
    if result.answer:
        print(json.dumps(result.answer, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
