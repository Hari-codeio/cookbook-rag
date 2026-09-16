# Week 7 - racing the recipe agent against a fixed workflow

Headline, and it is not the fashionable answer:

```
system      pass rate   p50 latency   total tokens   cost / request
agent_v2    10/10        8013 ms       85,244        $0.001034
workflow    10/10        3006 ms       12,444        $0.000271
agent_v1    10/10        4580 ms       38,770        $0.000543
```

Same 10 requests, same tools, same pinned model, same output contract. The
workflow ties on correctness and wins the other three by 2.7x, 6.9x and 3.8x.

| deliverable | file |
|---|---|
| the 8 numbers | [out/race.csv](out/race.csv), [out/race.md](out/race.md) |
| the 10 requests | [eval/race_cases.jsonl](eval/race_cases.jsonl) |
| agent | [rag/agent.py](rag/agent.py) - `python -m rag.agent "<request>"` |
| workflow | [rag/workflow.py](rag/workflow.py) - `python -m rag.workflow "<request>"` |
| the race | `python eval/run_race.py --systems all` |
| budget terminations | [out/budget_termination.log](out/budget_termination.log) |
| tool description diff | [out/tool_description_diff.txt](out/tool_description_diff.txt) |

---

## 1. What had to be built first

The practical is written as an extension of a Week 7 agent. This repo did not
have one, so the base was built and committed separately (`e797f1e`) before the
practical touched it, which is what makes the third tool's description diff real
git history rather than an assertion.

One deviation, stated rather than buried. The brief says "scale it to the
requested servings". Not one of the 21 cards states a serving count -
`grep -rliE "(serves|makes|yields)[^a-z]*[0-9]" data/*/*.md` returns zero files -
and only 11 carry a baker's-percentage basis. The only scaling anchor every card
supports is a multiplier, so the requests ask for "1.5x" or "double". Inventing a
servings number per card would have been fabricating corpus data to make a tool
signature look tidier.

## 2. Why the input mix is the whole experiment

Ten straightforward scale-and-swap requests would hand the workflow the win by
construction. So four of the ten are **cascade** cases, built so the obvious
replacement carries the same allergen the user is avoiding:

| case | request | the trap |
|---|---|---|
| `c01` | aubergine, no soy | tamari is the reflex swap for soy sauce, and is soy |
| `c02` | tikka masala, dairy free | Greek yoghurt for yoghurt, ghee for butter |
| `c03` | brioche, dairy free | ghee is the reflex swap for butter in enriched dough |
| `c04` | lemon drizzle, dairy free | ghee and buttermilk both read as obvious |

## 3. The four budgets

All four are enforced, in one function (`_over_budget`) called at the top of
every lap **and again after each model call**, because a single expensive turn
can blow the token budget without the lap counter moving. Five runs in
[out/budget_termination.log](out/budget_termination.log):

```
expecting max_laps      -> terminated_by = max_laps       laps=2  raised: no
expecting max_tokens    -> terminated_by = max_tokens     laps=3  raised: no
expecting max_cost_usd  -> terminated_by = max_cost_usd   laps=3  raised: no
expecting max_seconds   -> terminated_by = max_seconds    laps=4  raised: no
spin guard, unsatisfiable request
                        -> terminated_by = max_laps       laps=5  raised: no
```

None raises. Each returns the name of the budget that fired, so a run that hit a
wall can be told apart from one that crashed.

Token counting is per lap and summed. The loop re-sends the whole message list
every time, so a three-lap run measured input tokens of 545, 855 and 1446.
Reporting only the final call would have said 1446 instead of 2846.

## 4. The cascade did not fire, and that is the result

In all eight cascade runs, across both systems, the model picked a safe
substitute **first time**:

```
c01  Light soy sauce  -> Coconut aminos          (both systems)
c02  Full fat yoghurt -> Coconut yoghurt         Double cream -> Coconut cream
c03  Whole milk       -> Oat milk / soy milk     butter -> Vegan butter block
c04  Unsalted butter  -> Dairy-free margarine / Vegan butter block
```

Not once did it reach for tamari, ghee or Greek yoghurt. So step 3 never
depended on what step 2 found, the path never varied, and the trap I built to
force an agent never closed.

The cases were designed on an assumption about what the model would do, and the
assumption was wrong. That is a more useful outcome than a case rigged until it
produced the answer I expected.

## 5. The third tool made the agent worse

`agent_v2` adds `get_allergen_profile`. Against `agent_v1`, which has only search
and scale:

```
                laps   tokens    cost/req    pass
agent_v1        3.0    38,770    $0.000543   10/10
agent_v2        4.8    85,244    $0.001034   10/10
```

1.8 more laps, 2.2x the tokens, 1.9x the cost, for exactly the same pass rate.
The extra tool is two extra round trips to confirm something the model was
already getting right.

The overlapping v1 descriptions produced **no measurable thrash** either.
`agent_v1` took exactly 3 laps on all ten requests, never re-calling a tool it
had already used. The description bug is real and worth fixing on principle (see
[out/tool_description_diff.txt](out/tool_description_diff.txt): one capitalised
verb each, an explicit "Does not ..." line, and a nine-value enum on `allergen`),
but this race did not price it. I am not claiming a benefit the table does not
show.

## 6. VERDICT

The decision rule is whether the path varies by input. On these ten requests it
does not. Every one is the same three steps: find the recipe, multiply the
amounts, check and swap the allergen. The workflow walks that line in two model
calls and wins every number, tying at 10/10 while running 2.7x faster, using
6.9x fewer tokens and costing 3.8x less.

**No request class in this set forces an agent.** I built four cascade cases
specifically to find one, where the obvious substitute carries the same
allergen. The model defeated the trap every time, choosing a safe replacement on
the first attempt, so the dependency the agent exists to handle never arose.

The class that would force an agent is one where the replacement is constrained
by the archive and the first choice can genuinely fail. This corpus does not
contain it. Ship the workflow.

*(147 words)*

## 7. Where this is weak

**A grader bug nearly became a finding.** The first race failed the workflow on
`c02`, `c03` and `c04` with "replacement still carries contains-dairy" for
Coconut yoghurt, Coconut cream and Vegan butter block. All three are dairy free.
The matcher was hitting the words yoghurt, cream and butter. That would have been
reported as the cascade biting, and it was my own bug. It is the second bug in
the same function - the first had "Tamarind paste" matching the soy marker
"tamari" - so [eval/test_allergens.py](eval/test_allergens.py) now pins 35 cases
in both directions.

**Latency is noisy.** Free-tier 429s add 20-second retry sleeps, visible as
43-47 second outliers in [out/race.md](out/race.md). p50 is reported rather than
the mean for exactly this reason, but with n=10 one bad draw still moves it.

**Ten requests is a small race,** and all ten come from one 21-card corpus on one
weak pinned model. A stronger model would likely widen the workflow's win, since
more of the agent's laps are spent confirming things it already knew.
