"""The kitchen squad: an orchestrator that decomposes a cooking request,
delegates to two narrow workers, and synthesises the answer.

    python -m rag.squad "Make the shakshuka 1.5x and take out the egg"
    python -m rag.squad --inject-500 "..."      # the allergen worker fails with HTTP 500

WHO DOES WHAT

  orchestrator.plan        model, no tools      request -> {recipe_query, scale_factor, allergen}
  orchestrator (code)      MCP, no model        search_recipes + scale_recipe on recipe_search
  allergen_worker          model + 2 tools      which scaled ingredients carry the allergen
  substitution_worker      model + 1 tool       a replacement for each, verified clear
  orchestrator.synthesise  model, no tools      writes the final answer in the shared contract

THE WORKERS ARE NARROW ON PURPOSE. The single agent carries 6 tools and one long
prompt. Each worker gets a short prompt and only the tools its job needs, and
receives only the fields it needs: never the corpus, never the method text. If
the squad is going to beat the single agent, that constraint is the only
plausible reason, so it is kept rather than diluted.

EVERY HAND-OFF IS COUNTED. Each one is recorded as a Handoff with the tokens it
consumed, summed over every model call inside it. The question this week is
whether the extra hand-offs re-send more context than the narrower prompts
save, and that cannot be answered from a total alone.

The tools are the same MCP-discovered tools the single agent uses (rag/mcp_host),
filtered by name per worker. Nothing here imports rag/tools.py functions directly.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from typing import Any

from rag.agent import Budgets, _parse_answer, run_agent
from rag.contract import RunResult
from rag.llm import call_with_tools, user_part
from rag.mcp_host import MCPHost
from rag.tools import ALLERGENS

PLAN_PROMPT = """\
You are the orchestrator of a small kitchen team. Read ONE recipe adaptation
request and split it into the fields your team needs. Do not answer it.

Reply with ONE JSON object and nothing else:

{
  "recipe_query": "<only the dish name, to search the archive with>",
  "scale_factor": <the multiplier asked for, as a number; 1 if none>,
  "allergen": "<one of: %s; or an empty string if none is mentioned>"
}
""" % ", ".join(ALLERGENS)

ALLERGEN_WORKER_PROMPT = """\
You are the allergen worker. You are given a list of ingredient names and ONE
allergen code. Your only job: report which of those ingredients carry it.

Call get_allergen_profile ONCE with the whole list and the allergen code. Its
carries_allergen entries are what must go. Do not look ingredients up one by
one: list anything under unknown_to_the_archive as a caveat instead. Never
judge from your own knowledge. You may call get_nutrition_per_100g only if the
request asks for nutrition.

Reply with ONE JSON object and nothing else:

{
  "allergen": "<the code you were given>",
  "must_remove": ["<exact ingredient name as given>", ...],
  "caveats": ["<anything a cook must be told, e.g. an ingredient you could not classify>"]
}
"""

SUBSTITUTION_WORKER_PROMPT = """\
You are the substitution worker. You are given a recipe title, ONE allergen
code, and the allergen worker's report of which ingredients must go.

For each ingredient in must_remove, choose one replacement that does NOT carry
the allergen, and confirm it with get_allergen_profile before you answer. If a
replacement fails the check, choose again. You do not find recipes, scale, or
decide what must go; that has been done.

Reply with ONE JSON object and nothing else:

{
  "substitutions": [{"from": "<ingredient removed>", "to": "<replacement>", "reason": "..."}],
  "caveats": ["<anything a cook must be told>"]
}
"""

SYNTHESIS_PROMPT = """\
You are the orchestrator writing the final answer from your team's reports.
You are given the scaled recipe (amounts already computed), the allergen
worker's report and the substitution worker's report.

RULES
1. Copy scaled amounts and the method exactly. Never recompute anything.
2. Apply each substitution: the replacement takes the removed ingredient's row
   and amount. Delete a method sentence only if it depends on a removed ingredient.
3. Make no allergen claim a report does not make. If a report is missing or
   failed, say so in "unsupported"; do not fill the gap yourself.
4. Every caveat in either report goes into "unsupported", word for word.
5. Reply with ONE JSON object and no other text:

{
  "recipe_id": "...",
  "title": "...",
  "scale_factor": <number>,
  "ingredients": [{"ingredient": "...", "amount": "<scaled amount>"}],
  "substitutions": [{"from": "...", "to": "...", "reason": "..."}],
  "method": "...",
  "unsupported": "<caveats and gaps, or an empty string>"
}
"""

ALLERGEN_TOOLS = ("get_allergen_profile", "get_nutrition_per_100g")
SUBSTITUTION_TOOLS = ("get_allergen_profile",)
WORKER_BUDGETS = Budgets(max_laps=6, max_tokens=30_000, max_cost_usd=0.01, max_seconds=60.0)


class WorkerHTTPError(RuntimeError):
    """What a remote worker behind HTTP (A2A or plain REST) looks like when it dies."""

    def __init__(self, status: int, worker: str):
        super().__init__(f"{worker} returned HTTP {status} Internal Server Error")
        self.status = status


@dataclass
class Handoff:
    """One hop in the squad, with everything it cost."""

    name: str  # e.g. "orchestrator -> allergen_worker"
    model_calls: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0
    ms: float = 0.0
    status: str = "ok"
    payload_chars: int = 0  # size of what was handed over, before any prompt
    detail: dict[str, Any] = field(default_factory=dict)

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens


@dataclass
class SquadResult(RunResult):
    handoffs: list[Handoff] = field(default_factory=list)


def _add(result: SquadResult, h: Handoff) -> None:
    result.handoffs.append(h)
    result.laps += h.model_calls
    result.input_tokens += h.input_tokens
    result.output_tokens += h.output_tokens
    result.cost_usd += h.cost_usd
    result.log.append({"event": "handoff", "handoff": h.name, "status": h.status,
                       "model_calls": h.model_calls, "tokens": h.total_tokens,
                       "ms": round(h.ms, 1), **h.detail})


def _model_step(client, name: str, system: str, payload: dict[str, Any]) -> tuple[Handoff, dict[str, Any] | None]:
    user = json.dumps(payload, ensure_ascii=False)
    started = time.perf_counter()
    turn = call_with_tools(client, system, [user_part(user)], None)
    h = Handoff(name, 1, turn.input_tokens, turn.output_tokens, turn.cost_usd,
                (time.perf_counter() - started) * 1000.0, payload_chars=len(user))
    return h, _parse_answer(turn.text)


def _worker(client, host: MCPHost, name: str, system: str, tools: tuple[str, ...],
            payload: dict[str, Any]) -> tuple[Handoff, dict[str, Any] | None]:
    """A worker is the Week 7 agent loop with a narrow prompt and a tool subset."""
    user = json.dumps(payload, ensure_ascii=False)
    schemas = [s for s in host.tool_schemas if s["name"] in tools]
    registry = {k: v for k, v in host.registry.items() if k in tools}
    run = run_agent(client, user, WORKER_BUDGETS, schemas, registry, system)
    h = Handoff(name, run.laps, run.input_tokens, run.output_tokens, run.cost_usd,
                run.latency_ms, "ok" if run.ok else f"failed: {run.error}", len(user),
                {"tools_called": [e["tool"] for e in run.log if e.get("event") == "tool_result"]})
    return h, run.answer if run.ok else None


def run_squad(client, host: MCPHost, request: str, inject_500: bool = False) -> SquadResult:
    result = SquadResult()
    started = time.perf_counter()

    def done(error: str = "") -> SquadResult:
        result.error = error
        result.latency_ms = (time.perf_counter() - started) * 1000.0
        return result

    # 1. user -> orchestrator.plan -------------------------------------------
    h, plan = _model_step(client, "user -> orchestrator.plan", PLAN_PROMPT, {"request": request})
    _add(result, h)
    if not plan:
        return done("orchestrator could not plan the request")
    try:
        factor = float(plan.get("scale_factor") or 1)
    except (TypeError, ValueError):
        factor = 1.0
    allergen = str(plan.get("allergen") or "").strip()
    query = str(plan.get("recipe_query") or "").strip()

    # 2. orchestrator -> recipe_search, over MCP, no model --------------------
    t0 = time.perf_counter()
    found = host.call("search_recipes", {"query": query})
    scaled = host.call("scale_recipe", {"recipe_id": found.data["matches"][0]["recipe_id"],
                                        "scale_factor": factor}) if found.ok else found
    _add(result, Handoff("orchestrator -> recipe_search (MCP, no model)", ms=(time.perf_counter() - t0) * 1000.0,
                         status="ok" if scaled.ok else f"failed: {scaled.error}"))
    if not scaled.ok:
        return done(scaled.error)
    recipe = scaled.data
    names = [r["ingredient"] for r in recipe["ingredients"]]

    # 3. orchestrator -> allergen_worker --------------------------------------
    allergen_report: dict[str, Any] = {"allergen": allergen, "must_remove": [], "caveats": []}
    if allergen:
        attempts = 0
        while True:
            attempts += 1
            try:
                if inject_500:
                    raise WorkerHTTPError(500, "allergen_worker")
                h, report = _worker(client, host, "orchestrator -> allergen_worker",
                                    ALLERGEN_WORKER_PROMPT, ALLERGEN_TOOLS,
                                    {"ingredients": names, "allergen": allergen})
            except WorkerHTTPError as exc:
                _add(result, Handoff("orchestrator -> allergen_worker", status=f"HTTP {exc.status}",
                                     detail={"attempt": attempts}))
                if attempts < 2:  # one retry, as for any flaky dependency
                    continue
                allergen_report = {"status": exc.status, "error": str(exc),
                                   "note": "no allergen findings are available for this request"}
                break
            h.detail["attempt"] = attempts
            _add(result, h)
            allergen_report = report or {"error": "allergen worker gave no parseable report"}
            break

    # 4. orchestrator -> substitution_worker ----------------------------------
    sub_report: dict[str, Any] = {"substitutions": [], "caveats": []}
    if allergen:
        h, report = _worker(client, host, "orchestrator -> substitution_worker",
                            SUBSTITUTION_WORKER_PROMPT, SUBSTITUTION_TOOLS,
                            {"recipe_title": recipe["title"], "allergen": allergen,
                             "allergen_report": allergen_report})
        _add(result, h)
        sub_report = report or {"error": "substitution worker gave no parseable report"}

    # 5. orchestrator.synthesise ----------------------------------------------
    h, answer = _model_step(client, "orchestrator.synthesise (both reports + scaled recipe)",
                            SYNTHESIS_PROMPT, {
                                "request": request,
                                "recipe_id": recipe["recipe_id"], "title": recipe["title"],
                                "scale_factor": factor,
                                "ingredients": [{"ingredient": r["ingredient"], "amount": r["scaled_amount"]}
                                                for r in recipe["ingredients"]],
                                "method": recipe["method"],
                                "allergen_report": allergen_report,
                                "substitution_report": sub_report,
                            })
    _add(result, h)
    if not answer:
        return done("synthesis did not return parseable JSON")
    result.answer = answer
    result.ok = True
    return done()


def main() -> None:
    import argparse

    from rag.generate import build_client

    ap = argparse.ArgumentParser(description="Run the kitchen squad on one request.")
    ap.add_argument("request")
    ap.add_argument("--inject-500", action="store_true", help="the allergen worker returns HTTP 500")
    args = ap.parse_args()

    with MCPHost() as host:
        result = run_squad(build_client(), host, args.request, args.inject_500)
    for h in result.handoffs:
        print(f"{h.name:<58} calls={h.model_calls} tokens={h.total_tokens:<6} "
              f"{h.ms:>7.0f}ms  {h.status}")
    print(f"\nok: {result.ok}  tokens: {result.total_tokens}  cost: ${result.cost_usd:.6f}  "
          f"latency: {result.latency_ms:.0f} ms")
    if result.answer:
        print(json.dumps(result.answer, indent=2, ensure_ascii=False))
    elif result.error:
        print(f"error: {result.error}")


if __name__ == "__main__":
    main()
