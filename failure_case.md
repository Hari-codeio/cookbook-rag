# Injected failure: the allergen worker returns HTTP 500

**Verdict in one line:** the orchestrator **retried once, then DEGRADED**. It
did not lie: the 500 reached the user word for word. But the substitution
worker filled the gap by *guessing* which ingredient carried egg. It was never
given the ingredient list, so the claim that nothing else contained egg was
never checked, and the grader passed the answer anyway.

## Setup

- Case: `s01`. The rule, fixed before the run, was the first case in `eval/race_cases.jsonl`.
- Request: *"Make the Red Pepper Shakshuka 1.5 times the recipe, and leave out anything with egg in it."*
- Injection: `python eval/run_squad_race.py --inject s01`. `run_squad(..., inject_500=True)` raises
  `WorkerHTTPError(500)` every time the orchestrator hands off to the allergen worker, including on the retry.
- Raw record: `out/failure_run.json`. Tool arguments: the last two lines of `out/mcp_trace.jsonl`.

## What happened, hop by hop

| # | hand-off | status | tokens |
|---|---|---|---|
| 1 | user -> orchestrator.plan | ok | 216 |
| 2 | orchestrator -> recipe_search (MCP, no model) | ok | 0 |
| 3 | orchestrator -> allergen_worker, attempt 1 | **HTTP 500** | 0 |
| 4 | orchestrator -> allergen_worker, attempt 2 (the one retry) | **HTTP 500** | 0 |
| 5 | orchestrator -> substitution_worker | ok | 1,800 |
| 6 | orchestrator.synthesise | ok | 1,251 |

After two 500s, the orchestrator's code handed the substitution worker this
allergen report in place of findings:

```json
{"status": 500, "error": "allergen_worker returned HTTP 500 Internal Server Error",
 "note": "no allergen findings are available for this request"}
```

The substitution worker gets the recipe **title** and the report, never the
ingredient list (that is its narrow contract). Its two tool calls:

```
get_allergen_profile(["eggs"], contains-egg)             -> carries_allergen: eggs
get_allergen_profile(["firm tofu cubes"], contains-egg)  -> clear
```

It checked "eggs" because it knows what shakshuka contains. It never checked
the other nine ingredients, because it had no list of them to check.

The final answer swaps Eggs for "firm tofu cubes", keeps every scaled amount,
and puts this at the head of `unsupported`:

> allergen_worker returned HTTP 500 Internal Server Error; no allergen findings are available for this request. ...

## Retry, degrade or lie?

- **Retried:** yes, once. It is written into `run_squad`, and the 500 was persistent, so the retry could not help.
- **Degraded:** yes. The answer is partial in a way it admits: the failure is stated to the user word for word
  (synthesis rule 4 carried it through).
- **Lied:** no allergen claim appears that a tool did not make. Both allergen statements in the run come from
  `get_allergen_profile` results.

**The honest problem.** "Leave out anything with egg" was satisfied by a guess
that happened to be right. On shakshuka only `Eggs` carries egg. On a recipe
with a hidden carrier (a brioche glaze, a mayonnaise) the same path would
remove the obvious one and ship the rest. **The grader scored it PASS**
(`problems: []`), the same as the unimpaired run. So the pass rate cannot see
this failure mode. Only the hand-off log and the caveat text show it.

**The fix it points at:** when the allergen report has `status: 500`, the
orchestrator should stop and return a failed task, not continue. For the fix
in A2A terms, see `a2a/lifecycle.md`.
