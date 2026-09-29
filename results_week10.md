# Week 10: race the kitchen squad against the single agent (Set B)

Headline, and it is the unfashionable direction for an unfashionable reason:

```
arm                         pass    p50      p99      total tokens   cost / question
single agent (6 MCP tools)  5/10    32.9 s   50.3 s   170,939        $0.001854
squad (orch + 2 workers)   10/10    23.5 s   44.9 s    40,074        $0.000664
control: single, 3 tools    9/10    21.1 s   51.7 s    97,580        $0.001161
```

**Context re-send multiplier: 40,074 / 170,939 = 0.2x.** The largest squad
share is `orchestrator -> allergen_worker`, **35% of all squad tokens** (13,895
tokens, 18 model calls). Synthesis is second at 33%.

The squad wins all four numbers. It wins because each worker gets a narrow
prompt and 1 or 2 tools, not because agents cooperate: nothing in it runs in
parallel. The 6-tool single agent lost 5 cases to max_laps, each time
re-checking substitutes on both allergen servers.

| deliverable | file |
|---|---|
| 4 metrics x 2 arms, same 10 cases named | [race_table.md](race_table.md) |
| every hand-off with its token count | [handoffs.log](handoffs.log) |
| multiplier line + dominant hand-off | top of this file, and [race_table.md](race_table.md) |
| injected 500 | [failure_case.md](failure_case.md), raw [out/failure_run.json](out/failure_run.json) |
| verdict | [verdict.md](verdict.md) |
| bonus: AgentCard + lifecycle | [a2a/agent-card.json](a2a/agent-card.json), [a2a/lifecycle.md](a2a/lifecycle.md) |
| the squad | [rag/squad.py](rag/squad.py): `python -m rag.squad "<request>" [--inject-500]` |
| the race | [eval/run_squad_race.py](eval/run_squad_race.py): `python eval/run_squad_race.py [--control] [--inject s01]` |
| raw rows | [out/squad_race_cache.json](out/squad_race_cache.json) |

---

## 0. Which "10 Week-6 cases": a deviation, stated up front

The brief says to race on "the same 10 Week-6 eval cases, with the same judge".
This repo's Week 6 set is **25** cases (`eval/substitution_cases.jsonl`). It was
built for the single-shot `rag/substitute.py` pipeline, and its judge
(`eval/judge_v2.txt`) grades fields neither arm produces: `can_substitute` and
chunk_id citations against CONTEXT blocks.

The frozen 10-case set this app's agent has been measured on is
`eval/race_cases.jsonl`, graded in code by `rag/contract.check`. Week 7 raced on
it and Week 8 re-scored it. So this race uses **those 10 cases, unchanged, with
that grader**. No case was written, dropped or reworded, and picking 10 of the
25 would itself have been a new eval set. If the brief means the literal Week 6
file, this is the point to challenge.

## 1. What had to be built first

As in Week 9, the orchestrator the brief calls "last week's" did not exist.
It was built and committed separately (`5bb09fb`) before the race. The squad
works like this:

```
user -> orchestrator.plan        (model, no tools)          recipe_query, scale_factor, allergen
orchestrator -> recipe_search    (MCP, no model)            search + scale
orchestrator -> allergen_worker  (model + 2 tools)          ingredient NAMES only -> must_remove
orchestrator -> substitution_worker (model + 1 tool)        title + allergen report -> verified swaps
orchestrator.synthesise          (model, no tools)          scaled recipe + both reports -> contract
```

Both arms share one `MCPHost` over the Week 9 servers, the same pinned model,
and the same token accounting (summed over every model call). They were
interleaved per case.

Two disclosures about building it:

- **The first smoke test used the tikka masala recipe, which is also case c02**
  (a different scale, a different phrasing). It exposed a structural bug: the
  allergen worker looked unknown ingredients up one at a time and hit its
  6-lap cap. The fix, one profile call with unknowns reported as caveats, is
  generic. After that, development requests used only recipes outside the
  race (chocolate brioche, white miso).
- The allergen worker lost `get_allergens` (the third-party EU-14 lookup) in the
  same fix, so it has 2 tools. The substitution worker always had 1.

## 2. Where the tokens go

```
squad, all 10 cases                          tokens   share
orchestrator -> allergen_worker              13,895   34.7%   2 laps/case: lap 2 re-sends lap 1 + the profile result
orchestrator.synthesise                      13,226   33.0%   the only hop that sees the method text (20k chars of payload)
orchestrator -> substitution_worker          10,894   27.2%
user -> orchestrator.plan                     2,059    5.1%
orchestrator -> recipe_search (MCP)               0    0.0%
```

The single agent spent 166,117 input tokens against 4,822 output tokens. That
is 97% input, because every lap re-sends the prompt, 6 tool schemas, the
attached allergen legend, and every earlier tool result, including the full
scaled recipe and method. Its 5 failed runs alone used 109,770 tokens, 64% of
the arm.

"Multi-agent re-sends context" is true inside each worker. It was outweighed
here because the single agent's conversation is the bigger re-send. The
multiplier measures a context strategy, not the pattern, which is exactly what
the brief warns about in the other direction.

## 3. The control arm, and why it exists

A 5/10 single agent invites the question: did the squad beat the *pattern*, or
a single agent bloated by Week 9's 3 extra tools? The control is the same
agent on the Week 9 server-one config (3 tools, `eval/mcp_config.server_one.json`
= `f499c39:mcp_config.json`). It scored 9/10 at 97,580 tokens, so the squad
is still **0.4x** on tokens and +1 on pass rate. The control ran after the
race, not interleaved, and it is reported as a control, not as one of the two
arms.

## 4. The injected failure

Retried once, then **degraded**. The 500 reached the user word for word, and
no allergen claim was invented. But the substitution worker, which never sees
the ingredient list, checked "eggs" from its own knowledge of shakshuka. So
"nothing else carries egg" was never verified, and **the grader passed it**. A
pass-rate eval cannot see this mode. See `failure_case.md`.

## 5. Verdict

**KEEP**, with the fail-closed fix first. The sunk-cost bias is named in
[verdict.md](verdict.md) before the verdict is stated.

## 6. What this does NOT show

- One run per cell, at temperature 0. The p99 of 10 runs is simply the slowest run.
- Latency is dominated by Gemini free-tier variance. One plan call took 25 s in
  a dev run. Both arms saw the same window because they were interleaved.
- The Week 7 fixed workflow did the same 10 cases in 12,444 tokens at 10/10.
  That was a different day and had no MCP, so it is not in the table. It is
  the obvious next race: the squad's structure is already mostly a fixed
  pipeline with two model workers in it.
