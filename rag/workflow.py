"""The same task as rag/agent.py, as three hard-coded steps. No loop.

    python -m rag.workflow "Make the shakshuka 1.5x and take out anything with egg"

WHAT "SAME TASK" HAD TO MEAN FOR THE RACE TO BE HONEST

  same tools      the identical functions from rag/tools.py, not reimplemented
  same model      the same pinned model, through the same rag/llm.call_with_tools,
                  so latency and token counting are measured the same way
  same contract   rag/contract.RunResult, graded by rag/contract.check
  same accounting per-call usage summed, exactly as the agent sums it

THE ONE THING THAT DIFFERS is who picks the order. Here the order is written
down. The model is called twice, at fixed points, for the two sub-tasks that are
genuinely not fixed: reading a free-text request, and choosing a replacement
ingredient. Everything between those is a straight line.

NO LOOP IS HIDING IN HERE. There is no while, no retry, no "try again if the
substitute is bad". Step 5 proposes replacements and step 6 checks them ONCE. If
a replacement is itself unsafe, this says so in `unsupported` and returns
ok=False. That is the workflow's real ceiling and the race is meant to find it,
so papering over it with a second attempt would have been rigging the result.
"""

from __future__ import annotations

import json
import time
from typing import Any

from rag.agent import _parse_answer
from rag.contract import RunResult
from rag.llm import call_with_tools, user_part
from rag.tools import ALLERGENS, get_allergen_profile, scale_recipe, search_recipes

EXTRACT_PROMPT = """\
You read one recipe adaptation request and pull out three fields. You do not
answer the request.

Reply with ONE JSON object and nothing else:

{
  "query": "<the recipe name to search for>",
  "scale_factor": <the multiplier asked for, as a number; 1 if none is asked>,
  "allergen": "<one of: %s, or an empty string if no allergen is mentioned>"
}
""" % ", ".join(ALLERGENS)

ADAPT_PROMPT = """\
You are given a recipe that has already been found, already scaled, and already
checked for one allergen. Your only job is to choose a replacement for each
unsafe ingredient and write the result out.

RULES

1. Copy the scaled amounts exactly as given. Never recompute them.
2. Copy the method text as given, except that you may delete a sentence that
   depends on an ingredient you removed.
3. For each unsafe ingredient, name a replacement that does NOT carry the
   allergen being avoided. Prefer an ingredient that already appears elsewhere
   in this archive.
4. Reply with ONE JSON object and no other text:

{
  "recipe_id": "...",
  "title": "...",
  "scale_factor": <number>,
  "ingredients": [{"ingredient": "...", "amount": "<scaled amount>"}],
  "substitutions": [{"from": "...", "to": "...", "reason": "..."}],
  "method": "...",
  "unsupported": ""
}
"""


def _model_json(client, result: RunResult, system: str, user: str) -> dict[str, Any] | None:
    """One model call, accounted exactly as the agent accounts for a lap."""
    turn = call_with_tools(client, system, [user_part(user)], None)
    result.laps += 1
    result.input_tokens += turn.input_tokens
    result.output_tokens += turn.output_tokens
    result.cost_usd += turn.cost_usd
    result.log.append(
        {
            "event": "model_call",
            "step": result.laps,
            "input_tokens": turn.input_tokens,
            "output_tokens": turn.output_tokens,
            "cumulative_tokens": result.total_tokens,
            "cumulative_cost_usd": round(result.cost_usd, 6),
        }
    )
    return _parse_answer(turn.text)


def run_workflow(client, request: str) -> RunResult:
    result = RunResult()
    started = time.perf_counter()

    # ---- STEP 1 (model): read the request into three fields ----------------
    fields = _model_json(client, result, EXTRACT_PROMPT, request)
    if not fields:
        result.error = "could not read the request"
        result.latency_ms = (time.perf_counter() - started) * 1000.0
        return result

    query = str(fields.get("query") or "").strip()
    try:
        factor = float(fields.get("scale_factor") or 1)
    except (TypeError, ValueError):
        factor = 1.0
    allergen = str(fields.get("allergen") or "").strip()
    result.log.append({"event": "extracted", "query": query, "scale_factor": factor, "allergen": allergen})

    # ---- STEP 2 (tool): find the recipe ------------------------------------
    found = search_recipes(query)
    result.log.append({"event": "tool", "tool": "search_recipes", "ok": found.ok, "error": found.error})
    if not found.ok:
        result.error = found.error
        result.latency_ms = (time.perf_counter() - started) * 1000.0
        return result
    recipe_id = found.data["matches"][0]["recipe_id"]

    # ---- STEP 3 (tool): scale it -------------------------------------------
    scaled = scale_recipe(recipe_id, factor)
    result.log.append({"event": "tool", "tool": "scale_recipe", "ok": scaled.ok, "error": scaled.error})
    if not scaled.ok:
        result.error = scaled.error
        result.latency_ms = (time.perf_counter() - started) * 1000.0
        return result

    names = [r["ingredient"] for r in scaled.data["ingredients"]]

    # ---- STEP 4 (tool): which ingredients carry the allergen ---------------
    unsafe: list[str] = []
    if allergen in ALLERGENS:
        profile = get_allergen_profile(names, allergen)
        result.log.append(
            {"event": "tool", "tool": "get_allergen_profile", "ok": profile.ok, "scope": "original"}
        )
        if profile.ok:
            unsafe = [c["ingredient"] for c in profile.data["carries_allergen"]]
    result.log.append({"event": "unsafe_found", "ingredients": unsafe})

    # ---- STEP 5 (model): choose replacements and write the answer ----------
    payload = {
        "recipe_id": recipe_id,
        "title": scaled.data["title"],
        "scale_factor": factor,
        "allergen_to_avoid": allergen,
        "unsafe_ingredients": unsafe,
        "ingredients": [
            {"ingredient": r["ingredient"], "amount": r["scaled_amount"]}
            for r in scaled.data["ingredients"]
        ],
        "method": scaled.data["method"],
    }
    answer = _model_json(client, result, ADAPT_PROMPT, json.dumps(payload, ensure_ascii=False))
    if not answer:
        result.error = "adapt step did not return parseable JSON"
        result.latency_ms = (time.perf_counter() - started) * 1000.0
        return result

    # ---- STEP 6 (tool): check the replacements ONCE ------------------------
    # This is a check, not a retry. It runs exactly once whatever it finds.
    proposed = [
        str(s.get("to") or "")
        for s in (answer.get("substitutions") or [])
        if isinstance(s, dict) and s.get("to")
    ]
    still_unsafe: list[str] = []
    if proposed and allergen in ALLERGENS:
        verify = get_allergen_profile(proposed, allergen)
        result.log.append(
            {"event": "tool", "tool": "get_allergen_profile", "ok": verify.ok, "scope": "replacements"}
        )
        if verify.ok:
            still_unsafe = [c["ingredient"] for c in verify.data["carries_allergen"]]

    if still_unsafe:
        # The linear pipeline has nowhere left to go. Say so rather than
        # returning an answer that quietly still contains the allergen.
        note = (
            f"replacement(s) {', '.join(still_unsafe)} still carry {allergen}; "
            "a fixed pipeline has no second pass to choose again"
        )
        answer["unsupported"] = note
        result.log.append({"event": "cascade_unresolved", "ingredients": still_unsafe})
        result.answer = answer
        result.ok = False
        result.error = note
        result.latency_ms = (time.perf_counter() - started) * 1000.0
        return result

    result.answer = answer
    result.ok = True
    result.log.append({"event": "answered", "step": result.laps})
    result.latency_ms = (time.perf_counter() - started) * 1000.0
    return result


def main() -> None:
    import argparse

    from rag.generate import build_client

    ap = argparse.ArgumentParser(description="Run the fixed workflow on one request.")
    ap.add_argument("request")
    args = ap.parse_args()

    result = run_workflow(build_client(), args.request)
    for entry in result.log:
        print(json.dumps(entry, ensure_ascii=False))
    print()
    print(f"ok         : {result.ok}")
    print(f"model calls: {result.laps}")
    print(f"tokens     : {result.total_tokens} (in {result.input_tokens} / out {result.output_tokens})")
    print(f"cost       : ${result.cost_usd:.6f}")
    print(f"latency    : {result.latency_ms:.0f} ms")
    if result.answer:
        print(json.dumps(result.answer, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
