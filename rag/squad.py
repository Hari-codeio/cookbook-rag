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

import hashlib
import json
import os
import time
from dataclasses import asdict, dataclass, field
from typing import Any

from rag import obs
from rag.agent import Budgets, _parse_answer, run_agent
from rag.config import GEN_PIN, GEN_PINNED_MODEL, GEN_PROVIDER
from rag.contract import RunResult
from rag.llm import call_with_tools, user_part
from rag.mcp_host import MCPHost
from rag.tools import ALLERGENS
from rag.trace import git_sha

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

# Week 11: synth-v2. v1's rule 1 said "Copy scaled amounts AND THE METHOD
# exactly", and rule 2 allowed deleting a sentence only if it "depends on" a
# removed ingredient. Read together, they told the model to paste the original
# method back verbatim, so a "dairy-free" tikka masala still said "soften the
# onion in the ghee". 8 of 9 dairy-free answers in the Week 11 production log
# did this. v2 changes exactly those two rules and nothing else: amounts are
# still copied, and the method is copied EXCEPT that every removed ingredient
# is renamed to its replacement.
SYNTHESIS_PROMPT_V2 = """\
You are the orchestrator writing the final answer from your team's reports.
You are given the scaled recipe (amounts already computed), the allergen
worker's report and the substitution worker's report.

RULES
1. Copy scaled amounts exactly. Never recompute anything.
2. Apply each substitution: the replacement takes the removed ingredient's row
   and amount.
3. Copy the method, but wherever it names a removed ingredient, write the name
   of its replacement instead: "soften the onion in the ghee" becomes "soften
   the onion in the sunflower oil". A removed ingredient must not be named
   anywhere in the method, not even by a short form such as "the butter" for
   "Unsalted butter". If a sentence only makes sense for the removed
   ingredient, delete it. Change nothing else in the method.
4. Make no allergen claim a report does not make. If a report is missing or
   failed, say so in "unsupported"; do not fill the gap yourself.
5. Every caveat in either report goes into "unsupported", word for word.
6. Reply with ONE JSON object and no other text:

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

# Not a prompt: the description of the code that replaces the allergen worker
# in squad-v3. Versioned and hashed like a prompt so a trace still says
# exactly what did this step.
ALLERGEN_STEP_IN_CODE = """\
(no model) get_allergen_profile(ingredient names, allergen) over MCP, then
must_remove = carries_allergen, caveats = unknown_to_the_archive.
"""

ALLERGEN_TOOLS = ("get_allergen_profile", "get_nutrition_per_100g")
SUBSTITUTION_TOOLS = ("get_allergen_profile",)
WORKER_BUDGETS = Budgets(max_laps=6, max_tokens=30_000, max_cost_usd=0.01, max_seconds=60.0)

# ---------------------------------------------------------------------------
# Week 11: every prompt has a version, and a RELEASE names the set that answered.
#
# Week 10 shipped these four prompts with no version at all, so a trace could
# not say which wording produced an answer, and a fix could not be rolled back
# by name. The release id is what a trace is sliced on; the per-step version
# and sha256 say exactly which text changed between two releases.
# ---------------------------------------------------------------------------
PROMPTS: dict[str, dict[str, tuple[str, str]]] = {
    "squad-v1": {
        "plan": ("plan-v1", PLAN_PROMPT),
        "allergen_worker": ("allergen-v1", ALLERGEN_WORKER_PROMPT),
        "substitution_worker": ("substitution-v1", SUBSTITUTION_WORKER_PROMPT),
        "synthesise": ("synth-v1", SYNTHESIS_PROMPT),
    },
    # Week 11 fix: one prompt changed, three untouched.
    "squad-v2": {
        "plan": ("plan-v1", PLAN_PROMPT),
        "allergen_worker": ("allergen-v1", ALLERGEN_WORKER_PROMPT),
        "substitution_worker": ("substitution-v1", SUBSTITUTION_WORKER_PROMPT),
        "synthesise": ("synth-v2", SYNTHESIS_PROMPT_V2),
    },
    # Week 11 cost change, measured separately from the fix: the allergen step
    # is routed to CODE. Its whole job is one get_allergen_profile call and a
    # copy of the answer, and in 27 of 28 production requests the model's
    # report was exactly the tool's answer. Same prompts otherwise.
    "squad-v3": {
        "plan": ("plan-v1", PLAN_PROMPT),
        "allergen_worker": ("allergen-code-v1", ALLERGEN_STEP_IN_CODE),
        "substitution_worker": ("substitution-v1", SUBSTITUTION_WORKER_PROMPT),
        "synthesise": ("synth-v2", SYNTHESIS_PROMPT_V2),
    },
}

# ---------------------------------------------------------------------------
# Which release answers is a SETTING, not a deploy, so shipping and undoing a
# prompt change are both one environment variable:
#
#   SQUAD_RELEASE=squad-v1        rollback: everyone back on the old prompts
#   SQUAD_CANARY_PERCENT=10       canary: 10% of users (a stable hash of the
#                                 user id, so a user does not flip-flop between
#                                 requests) get RELEASE, the rest PREVIOUS_RELEASE
#
# Every trace records the release that answered it, so the canary is read by
# slicing the log on prompt_version. See release_notes.md for the plan.
# ---------------------------------------------------------------------------
RELEASE = os.environ.get("SQUAD_RELEASE", "squad-v2").strip()
PREVIOUS_RELEASE = "squad-v1"
CANARY_PERCENT = int(os.environ.get("SQUAD_CANARY_PERCENT", "100"))
if RELEASE not in PROMPTS:
    raise SystemExit(f"SQUAD_RELEASE={RELEASE!r} is not one of {sorted(PROMPTS)}")


def release_for(user_id: str) -> str:
    if CANARY_PERCENT >= 100 or RELEASE == PREVIOUS_RELEASE:
        return RELEASE
    bucket = int(hashlib.sha256(user_id.encode("utf-8")).hexdigest()[:8], 16) % 100
    return RELEASE if bucket < CANARY_PERCENT else PREVIOUS_RELEASE


def prompt_manifest(release: str) -> dict[str, dict[str, str]]:
    return {step: {"version": v, "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest()}
            for step, (v, text) in PROMPTS[release].items()}


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
    trace_id: str | None = None
    release: str = RELEASE


def _add(result: SquadResult, h: Handoff) -> None:
    result.handoffs.append(h)
    result.laps += h.model_calls
    result.input_tokens += h.input_tokens
    result.output_tokens += h.output_tokens
    result.cost_usd += h.cost_usd
    result.log.append({"event": "handoff", "handoff": h.name, "status": h.status,
                       "model_calls": h.model_calls, "tokens": h.total_tokens,
                       "ms": round(h.ms, 1), **h.detail})


def _model_step(client, name: str, system: str, payload: dict[str, Any], rec: obs.Recorder,
                span_name: str, prompt_version: str, keep_output: bool = True,
                ) -> tuple[Handoff, dict[str, Any] | None]:
    user = json.dumps(payload, ensure_ascii=False)
    start_ms = rec.now_ms()
    started = time.perf_counter()
    turn = call_with_tools(client, system, [user_part(user)], None)
    ms = (time.perf_counter() - started) * 1000.0
    h = Handoff(name, 1, turn.input_tokens, turn.output_tokens, turn.cost_usd, ms, payload_chars=len(user))
    answer = _parse_answer(turn.text)
    sp = rec.add(span_name, "generation", start_ms, ms, model=turn.model, prompt_version=prompt_version,
                 status="ok" if answer is not None else "error: reply was not parseable JSON",
                 attrs={"payload_chars": len(user), "rate_limited": turn.rate_limited, "quota": turn.quota,
                        "output": (answer if answer is not None else turn.text[:2000]) if keep_output
                        else "(the final answer; see output.answer)"})
    sp.tokens(turn.input_tokens, turn.output_tokens)
    return h, answer


def _worker(client, host: MCPHost, name: str, system: str, tools: tuple[str, ...],
            payload: dict[str, Any], rec: obs.Recorder, span_name: str, prompt_version: str,
            ) -> tuple[Handoff, dict[str, Any] | None]:
    """A worker is the Week 7 agent loop with a narrow prompt and a tool subset.

    It becomes one container span plus a child span per lap (generation) and per
    tool call (tool), so a slow or expensive worker can be pinned to the lap.
    """
    user = json.dumps(payload, ensure_ascii=False)
    schemas = [s for s in host.tool_schemas if s["name"] in tools]
    registry = {k: v for k, v in host.registry.items() if k in tools}
    start_ms = rec.now_ms()
    run = run_agent(client, user, WORKER_BUDGETS, schemas, registry, system)
    h = Handoff(name, run.laps, run.input_tokens, run.output_tokens, run.cost_usd,
                run.latency_ms, "ok" if run.ok else f"failed: {run.error}", len(user),
                {"tools_called": [e["tool"] for e in run.log if e.get("event") == "tool_result"]})

    parent = rec.add(span_name, obs.CONTAINER, start_ms, run.latency_ms, prompt_version=prompt_version,
                     status="ok" if run.ok else f"error: {run.error}",
                     attrs={"laps": run.laps, "terminated_by": run.terminated_by,
                            "payload_chars": len(user), "output": run.answer if run.ok else None})
    for e in run.log:
        if e.get("event") == "model_turn":
            sp = rec.add(f"{span_name}.lap{e['lap']}", "generation", start_ms + e.get("started_ms", 0.0),
                         e.get("ms", 0.0), parent=parent, model=e.get("model", ""),
                         prompt_version=prompt_version,
                         attrs={"tool_calls": e["tool_calls"], "rate_limited": e.get("rate_limited", 0),
                                "quota": e.get("quota", "")})
            sp.tokens(e["input_tokens"], e["output_tokens"])
        elif e.get("event") == "tool_result":
            rec.add(f"{span_name}.{e['tool']}", "tool", start_ms + e.get("started_ms", 0.0),
                    e.get("ms", 0.0), parent=parent,
                    status="ok" if e.get("ok") else f"error: {e.get('error')}",
                    attrs={"tool": e["tool"], "args": e["args"], "result": e.get("result")})
    return h, run.answer if run.ok else None


def _allergen_step_in_code(host: MCPHost, names: list[str], allergen: str, rec: obs.Recorder,
                           version: str) -> tuple[Handoff, dict[str, Any] | None]:
    """squad-v3: the allergen worker's job, done by the tool it always called.

    One tool span, no generation span. The report has the worker's exact shape,
    so the substitution worker and synthesis see the same input as before.
    """
    started = time.perf_counter()
    with rec.span("allergen_step", "tool", tool="get_allergen_profile", args={"n": len(names)}) as sp:
        sp.prompt_version = version
        prof = host.call("get_allergen_profile", {"ingredients": names, "allergen": allergen})
        sp.status = "ok" if prof.ok else f"error: {prof.error}"
        sp.attrs["result"] = prof.data if prof.ok else prof.error
    h = Handoff("orchestrator -> allergen_step (code, no model)", 0,
                ms=(time.perf_counter() - started) * 1000.0,
                status="ok" if prof.ok else f"failed: {prof.error}")
    if not prof.ok:
        return h, None
    return h, {"allergen": allergen,
               "must_remove": [c["ingredient"] for c in prof.data.get("carries_allergen", [])],
               "caveats": list(prof.data.get("unknown_to_the_archive", []))}


def run_squad(client, host: MCPHost, request: str, inject_500: bool = False, *,
              user_id: str = "anon", session_id: str = "", trace: bool = True,
              trace_meta: dict[str, Any] | None = None, release: str | None = None) -> SquadResult:
    release = release or release_for(user_id)
    steps = PROMPTS[release]
    result = SquadResult(release=release)
    rec = obs.Recorder()
    ts = obs.utc_now()
    started = time.perf_counter()
    ctx: dict[str, Any] = {"input_type": "unparsed", "allergen": "", "query": "", "factor": None,
                           "context_ids": [], "used": ""}

    def done(error: str = "") -> SquadResult:
        result.error = error
        result.latency_ms = (time.perf_counter() - started) * 1000.0
        if trace and obs.tracing_enabled():
            result.trace_id = obs.new_trace_id()
            obs.write(_trace_record(result, rec, ts, request, release, user_id, session_id,
                                    trace_meta or {}, ctx))
        return result

    # 1. user -> orchestrator.plan -------------------------------------------
    h, plan = _model_step(client, "user -> orchestrator.plan", steps["plan"][1], {"request": request},
                          rec, "plan", steps["plan"][0])
    _add(result, h)
    if not plan:
        return done("orchestrator could not plan the request")
    try:
        factor = float(plan.get("scale_factor") or 1)
    except (TypeError, ValueError):
        factor = 1.0
    allergen = str(plan.get("allergen") or "").strip()
    query = str(plan.get("recipe_query") or "").strip()
    ctx.update(input_type="allergen-swap" if allergen else "scale-only", allergen=allergen,
               query=query, factor=factor)

    # 2. orchestrator -> recipe_search, over MCP, no model --------------------
    #    Two spans: finding the card is RETRIEVAL, multiplying it is a TOOL.
    t0 = time.perf_counter()
    with rec.span("recipe_search", "retrieval", query=query) as sp:
        found = host.call("search_recipes", {"query": query})
        matches = found.data.get("matches", []) if found.ok else []
        ctx["context_ids"] = [m["recipe_id"] for m in matches]
        sp.attrs["context_ids"] = ctx["context_ids"]
        sp.status = "ok" if found.ok else f"error: {found.error}"
    if found.ok:
        ctx["used"] = matches[0]["recipe_id"]
        with rec.span("scale_recipe", "tool", recipe_id=ctx["used"], scale_factor=factor) as sp:
            scaled = host.call("scale_recipe", {"recipe_id": ctx["used"], "scale_factor": factor})
            sp.status = "ok" if scaled.ok else f"error: {scaled.error}"
    else:
        scaled = found
    _add(result, Handoff("orchestrator -> recipe_search (MCP, no model)", ms=(time.perf_counter() - t0) * 1000.0,
                         status="ok" if scaled.ok else f"failed: {scaled.error}"))
    if not scaled.ok:
        ctx["input_type"] = "unresolved"
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
                if steps["allergen_worker"][0].startswith("allergen-code"):
                    h, report = _allergen_step_in_code(host, names, allergen, rec,
                                                       steps["allergen_worker"][0])
                else:
                    h, report = _worker(client, host, "orchestrator -> allergen_worker",
                                        steps["allergen_worker"][1], ALLERGEN_TOOLS,
                                        {"ingredients": names, "allergen": allergen},
                                        rec, "allergen_worker", steps["allergen_worker"][0])
            except WorkerHTTPError as exc:
                rec.add("allergen_worker", obs.CONTAINER, rec.now_ms(), 0.0,
                        prompt_version=steps["allergen_worker"][0], status=f"error: HTTP {exc.status}",
                        attrs={"attempt": attempts})
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
                            steps["substitution_worker"][1], SUBSTITUTION_TOOLS,
                            {"recipe_title": recipe["title"], "allergen": allergen,
                             "allergen_report": allergen_report},
                            rec, "substitution_worker", steps["substitution_worker"][0])
        _add(result, h)
        sub_report = report or {"error": "substitution worker gave no parseable report"}

    # 5. orchestrator.synthesise ----------------------------------------------
    h, answer = _model_step(client, "orchestrator.synthesise (both reports + scaled recipe)",
                            steps["synthesise"][1], {
                                "request": request,
                                "recipe_id": recipe["recipe_id"], "title": recipe["title"],
                                "scale_factor": factor,
                                "ingredients": [{"ingredient": r["ingredient"], "amount": r["scaled_amount"]}
                                                for r in recipe["ingredients"]],
                                "method": recipe["method"],
                                "allergen_report": allergen_report,
                                "substitution_report": sub_report,
                            }, rec, "synthesise", steps["synthesise"][0], keep_output=False)
    _add(result, h)
    if not answer:
        return done("synthesis did not return parseable JSON")
    result.answer = answer
    result.ok = True
    return done()


def _trace_record(result: SquadResult, rec: obs.Recorder, ts: str, request: str, release: str,
                  user_id: str, session_id: str, meta: dict[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
    """One request, as the line the drill searches and the cost report sums."""
    spans = [asdict(s) for s in rec.spans]
    models = sorted({s["model"] for s in spans if s["model"]})
    return {
        "trace_schema": obs.TRACE_SCHEMA,
        "trace_id": result.trace_id,
        "ts": ts,
        "app": {"entrypoint": "rag.squad.run_squad", "git_sha": git_sha(), "release": release},
        "user": {"user_id": user_id, "session_id": session_id},
        "meta": meta,
        "request": {"text": request, "input_type": ctx["input_type"], "allergen": ctx["allergen"],
                    "recipe_query": ctx["query"], "scale_factor": ctx["factor"]},
        "prompt_version": release,
        "prompts": prompt_manifest(release),
        "model": {"provider": GEN_PROVIDER, "pinned": GEN_PINNED_MODEL if GEN_PIN else None, "used": models},
        "retrieval": {"context_ids": ctx["context_ids"], "used": ctx["used"]},
        "spans": spans,
        "totals": {"latency_ms": round(result.latency_ms, 1), "model_calls": result.laps,
                   "input_tokens": result.input_tokens, "output_tokens": result.output_tokens,
                   "cost_usd": round(result.cost_usd, 8),
                   "rate_limited": sum(s["attrs"].get("rate_limited", 0) for s in spans)},
        "cost_by_stage": obs.stage_totals(spans),
        "pricing": obs.pricing(),
        "output": {"ok": result.ok, "error": result.error, "answer": result.answer or None,
                   "answer_text": obs.flatten_answer(result.answer)},
        "status": "ok" if result.ok else "error",
    }


def main() -> None:
    import argparse

    from rag.generate import build_client

    ap = argparse.ArgumentParser(description="Run the kitchen squad on one request.")
    ap.add_argument("request")
    ap.add_argument("--inject-500", action="store_true", help="the allergen worker returns HTTP 500")
    ap.add_argument("--user", default="cli", help="user id stamped on the trace")
    ap.add_argument("--session", default="", help="session id stamped on the trace")
    args = ap.parse_args()

    with MCPHost() as host:
        result = run_squad(build_client(), host, args.request, args.inject_500,
                           user_id=args.user, session_id=args.session)
    for h in result.handoffs:
        print(f"{h.name:<58} calls={h.model_calls} tokens={h.total_tokens:<6} "
              f"{h.ms:>7.0f}ms  {h.status}")
    print(f"\nok: {result.ok}  tokens: {result.total_tokens}  cost: ${result.cost_usd:.6f}  "
          f"latency: {result.latency_ms:.0f} ms")
    print(f"trace_id: {result.trace_id}  release: {result.release}  log: {obs.trace_path()}")
    if result.answer:
        print(json.dumps(result.answer, indent=2, ensure_ascii=False))
    elif result.error:
        print(f"error: {result.error}")


if __name__ == "__main__":
    main()
