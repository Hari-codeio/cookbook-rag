# Weeks 9 and 10 together, explained plainly

Week 9 and Week 10 are two halves of one question: **how does an AI reach
things outside itself?**

| | reaches... | standard | this repo |
|---|---|---|---|
| **Week 9** | **tools and data** | **MCP** | `rag/mcp_host.py` discovers tools from `mcp_config.json` |
| **Week 10** | **other agents** | **A2A** | `rag/squad.py`, an orchestrator handing work to two worker agents |

Week 10 is built directly on Week 9. The squad's workers use the same
MCP-discovered tools, through the same `MCPHost`. Nothing in Week 10 imports
a tool function directly.

---

## 1. The kitchen analogy, now with a team

In Week 9 there was **one chef** (the model, in your app) and **suppliers**
(the MCP servers) who deliver when asked and never cook.

In Week 10 the chef became a **head chef with two line cooks**:

```
                    ┌────────────────────── YOUR APP (host) ──────────────────────┐
  user request ───► │ HEAD CHEF (orchestrator)                                    │
                    │   1. reads the order          (plan: model, no tools)       │
                    │   2. fetches + scales recipe  (MCP call, NO model)          │
                    │   3. "what must go?"  ──► ALLERGEN COOK   (model + 2 tools)  │
                    │   4. "replace it"     ──► SUBSTITUTION COOK (model + 1 tool)│
                    │   5. plates the dish          (synthesis: model, no tools)  │
                    └───────────────┬────────────────────────────────┬────────────┘
                                    │ MCP (Week 9)                   │ MCP
                              recipe_search server            ingredient_db server
```

Every arrow between the head chef and a cook is a **hand-off**. At each
hand-off the receiving cook gets a written brief (JSON), and that brief costs
tokens. The whole of Week 10 is about counting those costs honestly.

**Where does the AI run?** Still only in your app. The head chef and both
cooks are all model calls inside the host. The MCP servers still never see a
model. That answer from Week 9 did not change.

---

## 2. The one idea each week tests

**Week 9: is discovery real?** Proof: adding a whole server took 6 lines of
config and 0 lines of agent code, and `tools/list` went from 3 to 6 tools.

**Week 10: is a team worth it?** It is not assumed; it is raced. Same 10 cases,
same grader, four numbers each:

```
                            pass    p50      p99      tokens    $/question
single agent (6 tools)      5/10    32.9 s   50.3 s   170,939   0.001854
squad                      10/10    23.5 s   44.9 s    40,074   0.000664
control: single, 3 tools    9/10    21.1 s   51.7 s    97,580   0.001161
```

### How the two weeks connect in the result

Week 9 bolted 3 extra tools onto the single agent. In Week 10 that agent spent
its laps re-checking every substitute on **both** allergen servers (ours says
`contains-dairy`, the content team's says `milk`) and ran out of laps 5 times.

The squad avoided this because each cook is only handed the tools its job
needs. **Adding tools is free with MCP, but it is not free for the model.**
Every extra tool is one more option to wander into, and one more schema
re-sent on every lap.

---

## 3. Week 10's code, block by block

### `rag/squad.py`: the team

| Lines | What it does, in plain words |
|---|---|
| docstring (1-30) | The team chart, and the rule: **workers stay narrow**. Short prompt, few tools, only the fields they need. |
| `PLAN_PROMPT` (L43) | The head chef's first job: turn a sentence into 3 fields (dish, multiplier, allergen). It is told *not* to answer. |
| `ALLERGEN_WORKER_PROMPT` (L56) | The allergen cook's whole job: "which of these names carry this allergen?" One tool call, and unknowns become caveats. Never its own knowledge. |
| `SUBSTITUTION_WORKER_PROMPT` (L75) | The substitution cook: pick a replacement for each removed ingredient and **check it** with the tool before answering. |
| `SYNTHESIS_PROMPT` (L92) | Plating. Copy amounts exactly. **Rule 3:** make no allergen claim a report didn't make. **Rule 4:** copy every caveat word for word. These two rules stop the brief's last "common mistake", tidying away a warning. |
| `ALLERGEN_TOOLS`, `SUBSTITUTION_TOOLS` (L117-118) | The **narrow tool lists**: 2 tools and 1 tool, versus the single agent's 6. This is the design choice that won the race. |
| `WORKER_BUDGETS` (L119) | Each cook gets its own 4 budgets (the Week 7 idea), so one cook can't spin forever. |
| `WorkerHTTPError` (L122) | What a worker behind a network looks like when it crashes. Used for the injected 500. |
| `Handoff` (L131) | **The receipt for one hand-off**: name, model calls, input/output tokens, cost, time, status, and the size of the brief. `handoffs.log` is built from these. |
| `SquadResult` (L150) | The same `RunResult` both arms return (so one grader can judge both), plus the list of receipts. |
| `_model_step` (L165) | One plain model call with a JSON brief. Used for the plan and the synthesis. |
| `_worker` (L174) | **A worker is just the Week 7 agent loop** (`run_agent`) given a narrow prompt and a filtered subset of the Week 9 MCP tools. There is no new magic: an "agent" is a loop plus tools plus a prompt. |
| `run_squad` step 1 (L196) | Plan. |
| step 2 (L208) | Search and scale **over MCP with no model**. Choosing the top search hit and multiplying don't need judgement, so they cost 0 tokens. |
| step 3 (L220) | Hand off to the allergen cook, sending **only ingredient names**. It retries once on a 500. After two failures it hands downstream an honest error report instead of an empty list. |
| step 4 (L245) | Hand off to the substitution cook: the title plus the allergen report, **not** the ingredient list. That narrowness is also why the failure case was only degraded, not safe (section 4). |
| step 5 (L255) | Synthesis: the one hop that sees the whole method text. That's why it is 33% of the squad's tokens. |

### `eval/run_squad_race.py`: the fair race

| Lines | What it does |
|---|---|
| docstring | The fairness rules: same cases, same grader, same servers, same model, **arms interleaved per case** so a slow minute on the API hits both arms. |
| `ARMS` / `CONTROL` (L49-54) | The two required arms, plus a clearly labelled control arm (the 3-tool single agent). |
| `run_one` (L65) | Runs one arm on one case and grades it with `rag.contract.check`. For the single agent it logs each lap as a "hand-off to itself", because each lap re-sends the whole conversation. |
| `p99` (L90) | Nearest-rank p99. With 10 runs that is the slowest one, and it is reported anyway, because the slowest run is the one a client screenshots. |
| `write_outputs` (L106) | Builds `handoffs.log` (every hop with its tokens, plus the share per hop type) and `race_table.md` (the 4 × 2 table, the multiplier, per-case results, and failures with reasons). |
| `--inject s01` | Runs the squad once with the allergen cook returning 500, saved to `out/failure_run.json`. |

### `a2a/agent-card.json` + `a2a/lifecycle.md`: the bonus

- The **AgentCard** is to A2A what `tools/list` is to MCP: a published
  description of what an agent can do, what it accepts and returns, and what
  auth it needs, so other agents can find and call it.
- The **task lifecycle** (`submitted -> working -> completed / failed /
  input-required ...`) is the A2A equivalent of `isError` from Week 9: a
  standard way to say how things went, which every caller understands.

---

## 4. The same lesson in both weeks: the error message is part of the product

| Week | What failed | Bad version | What we saw |
|---|---|---|---|
| 9 | recipe search missed | `Error: lookup failed` | the model retried 7 times and never answered |
| 9 | fixed | "not in the archive, stop, answer unsupported" | 2 laps, an honest answer |
| 10 | allergen cook crashed (500) | code carried on with a guess | the substitution cook guessed "eggs"; the answer was right by luck, and **the grader passed it** |
| 10 | should be | fail the task (A2A `failed`) | a caller can't mistake it for a checked recipe |

The Week 10 lesson on top of that: **a pass rate can hide a safety failure.**
The degraded s01 answer scored exactly like the healthy one. Only the
hand-off log and the caveat text show the difference.

---

## 5. When is multi-agent worth it? (the mentor's question)

**Worth it when:**
- parts of the job are **truly independent**, so they can run **in parallel**
  (for example, nutrition lookup while scaling);
- parts need **clearly different instructions or tools**, and giving one agent
  all of them makes it wander. That is what happened here.

**Not worth it when:**
- every step depends on the previous one (our squad is fully sequential, so it
  gets no speed-up from parallelism);
- a **fixed workflow in code** can do the routing. The Week 7 workflow did these
  10 cases in 12,444 tokens, a third of the squad's. The honest next race is
  squad vs workflow.
- each hand-off would re-send big context. We avoided that by sending names,
  not the corpus. Send the corpus and the multiplier flips above 1.

**The one-sentence verdict:** the squad beat our single agent 10/10 vs 5/10 on
a quarter of the tokens, because narrow workers with few tools don't wander,
not because a team of agents is inherently smarter. And I named my sunk-cost
bias before saying "keep", because I built it.

---

## 6. Mentor's Friday questions, both weeks

| Question | Answer in plain words |
|---|---|
| W9: Is the tool discovered, not hard-coded? | Yes. The names come from `tools/list`. Run `python -m rag.mcp_host --list-tools`. |
| W9: A second tool without changing agent code? | Yes. 6 lines of config, `git diff rag/` empty. |
| W9: Your own server someone else can call? | Yes: `mcp_servers/recipe_search`, a standard MCP server. |
| W9: Where does the AI run? | In my app (the host). Never in the MCP servers. |
| W10: Raced on the SAME tests? | Yes. The same 10 frozen cases and the same code grader for all arms. None added. |
| W10: All four numbers? | Pass rate, p50 **and** p99, tokens, and cost per question, for both arms. |
| W10: Verdict backed by numbers? | KEEP: 10/10 vs 5/10, 40k vs 171k tokens (0.2x). With the fail-closed fix first. |
| W10: When would multi-agent be worth it? | Independent parallel parts, or genuinely different tools and instructions. Not for a sequential chain a fixed workflow can do. |
