# Week 11, explained like a person would explain it

This is the teaching companion to `results_week11.md`. It says what the week
asks for in plain words, walks through every file that changed and why, names
every concept and outside term, says how each piece was tested, and ends with
the questions a reviewer is likely to ask you, with answers you can defend.

---

## Part 1. The whole idea in one picture

Up to Week 10 you built an app and measured it **on your own desk**: you chose
the questions, you ran them, you read the answers. Production is different.
Nobody is watching. A customer says *"it gave me a wrong answer last week"*,
and that sentence is all you get.

So the app has to **watch itself**. Week 11 adds three habits:

```
   1. OBSERVABLE   every request leaves a trace you can find again later
                   (who, when, which prompt version, which recipe, each step's time and cost)

   2. AFFORDABLE   you know what each request costs, step by step,
                   and you change the step that costs most, then measure again

   3. SELF-IMPROVING   every real failure becomes a permanent test
                       (watch it fail, fix it, watch it pass, keep it forever)
```

Before this week, a squad request left no record at all. Its only trace was
whatever got printed to the terminal. After it:

```
  user request
      │
      ▼
  rag/squad.py  ── plan ── recipe_search ── scale ── allergen worker ── substitution worker ── synthesise
      │              each step becomes a SPAN: start, duration, tokens, cost, model, prompt version
      ▼
  out/w11/traces.jsonl      one JSON line per request (the "flight recorder")
      │
      ▼
  rag/obs_index.py          SQLite + full-text index over the request AND the answer
      │
      ▼
  eval/drill.py             slice by time / user / prompt version / input type / cost / words
      │
      ▼
  found trace ──► eval/regression_cases.jsonl ──► eval/run_suite.py  RED ──► fix prompt ──► GREEN
```

The one sentence to say to your mentor:

> **If it isn't logged, it didn't happen. So every request now writes one line
> with every step's time, tokens and cost, and every real failure we find
> becomes a test that runs forever.**

---

## Part 2. What the brief asks, in plain words, and what actually happened

The brief (Set B) gives you one vague complaint:

> *"someone said it recommended a dairy-free substitution that wasn't dairy-free, sometime last week."*

and asks for five things. Here is each one, what it means, and what we got:

| # | the brief says | in plain words | what we got |
|---|---|---|---|
| 1 | find the planted bad answer from logs alone, report mm:ss + slice | a squadmate hides one bad answer in your logs; find it with your tools, on a stopwatch | rehearsal **00:17** (slice: input type + time, then read 22 swap lines); bonus **00:11** (one query, 1 row). The graded run with a squadmate is yours. |
| 2 | paste the trace: per-span latency, tokens, cost, prompt version, context ids | show the found request's "receipt", step by step | `trace.json`: 12 spans, `squad-v1`, context `chicken-tikka-masala` + `chana-masala` |
| 3 | eval case RED before the fix, GREEN after, pass counts both times | turn the failure into a test; watch it fail; fix; watch it pass; and show the WHOLE suite each time so nothing else silently broke | `w11-r01`; suite **6/11 -> 11/11** |
| 4 | fix at the prompt or retrieval layer, record the version bump, two-line canary + rollback | change the prompt, give it a new name, and say how you'd ship it safely and undo it | `synth-v1 -> synth-v2` (release `squad-v1 -> squad-v2`); `release_notes.md` |
| 5 | cost per query by stage; what breaks first at 10x, with a number | where does the money go, and what falls over if traffic grows 10x | 100% of $ is model calls; **per-minute rate limit** breaks first (18 calls in the busiest minute vs 15/min, named by the API's own 429) |

### The story of the week, in seven steps

1. **The app logged nothing.** The squad (Week 10's winner) left no record per
   request. Step one was a flight recorder: one JSON line per request, with a
   span per step.
2. **Real traffic.** 36 requests from 12 test users went through the live app.
   That is the haystack.
3. **The drill.** A planted answer said "Double cream -> Crème fraîche, suits a
   dairy-free sauce". Crème fraîche is cultured cream. Found by slicing on what
   the request was (dairy) and reading the replacements.
4. **The surprise.** The planted swap was not the real bug. Reading the
   method of the real answers showed that **8 of 9 dairy-free answers still
   told the cook to use the dairy**: "soften the onion in the ghee", "beat the
   butter". The ingredient list was right; the instructions were not.
5. **Why no test caught it.** The Week 10 grader checked the ingredient swaps
   and never read the method. So the race said 10/10.
6. **The loop.** A new grader rule (point 6: nothing in the answer may put the
   allergen back, method included) plus the found request as a test case. On
   the live app: **6/11, RED**. One prompt rule changed ("copy the method
   exactly" became "copy it, but name the replacement"): **11/11, GREEN**.
7. **Cost and scale.** Cost attributed by step first, then one change: the
   allergen step needs no judgement, so code does it (**-25% cost, -32% model
   calls, still 11/11**). At 10x, the per-minute rate limit breaks first; it
   already bit twice at 1x.

---

## Part 3. Every code change, file by file

### `rag/obs.py` (new): the flight recorder

**What it does.** Collects the spans of one request and writes one JSON line
per request to `out/w11/traces.jsonl`.

- `Recorder` holds a stopwatch started when the request arrives. `span(...)` is
  a `with` block that times a step; `add(...)` places a step that was timed
  somewhere else (a lap inside the agent loop) onto the same clock.
- `Span` is one step: `name`, `stage` (retrieval / generation / tool / worker),
  `start_ms`, `latency_ms`, tokens, `cost_usd`, `model`, `prompt_version`,
  `status`, and free-form `attrs` (for example which recipe ids came back).
- `stage_totals` sums **leaf** spans by stage. A worker is a container whose
  cost is its laps' cost; adding the container too would count it twice.
- `flatten_answer` turns the answer into one searchable string, because the
  complaint describes the **output**.
- `write` is best-effort: if the disk fails, the answer still goes out and the
  error goes to `out/w11/trace_errors.log`. Logging must never take the app down.
- `OBS_TRACE_PATH` lets the suite and the drill write to other files, so test
  runs and planted records never mix with production traffic.

**Why.** "If it isn't logged, it didn't happen." Before this, a squad answer
left no record at all.

### `rag/squad.py` (changed): the app now records itself

- **Prompt versions.** The four prompts are named (`plan-v1`, `allergen-v1`,
  `substitution-v1`, `synth-v1`) and grouped into a release (`squad-v1`). Each
  trace stores the release plus every prompt's sha256, so "which wording
  produced this?" has an exact answer.
- **Spans.** `plan` and `synthesise` become generation spans. Recipe search is
  split into `recipe_search` (retrieval: finding the card) and `scale_recipe`
  (tool: multiplying it). Each worker becomes a container span with a child
  span per model lap and per tool call.
- **Who and what.** `run_squad(..., user_id=, session_id=, trace_meta=)`. The
  input type (`allergen-swap` / `scale-only` / `unresolved` / `unparsed`) comes
  from the plan step.
- `_trace_record` assembles the line: request, user, release, prompts,
  retrieved context ids, spans, totals, cost by stage, pricing, output.

### `rag/agent.py` (changed, additive only)

Each `model_turn` log event now also has `started_ms`, `ms`, `model`,
`rate_limited`, `quota`. Each `tool_result` has `started_ms`, `ms` and the tool's
`result`. Nothing that read the old keys changes. Without these, a worker's
laps and tool calls could not become separate spans.

### `rag/llm.py` (changed)

- **Price corrected** to the official list price for gemini-3.1-flash-lite,
  $0.25 / 1M input and $1.50 / 1M output. The old 0.10 / 0.40 made Weeks 7-10
  cost columns read low (tokens were always right).
- **429s are counted** (`rate_limited`, `retry_wait_s`, `quota`) instead of
  being retried silently. A rate limit used to look like a slow call.

### `rag/obs_index.py` (new): making the log searchable

Builds `traces.index.sqlite` next to the log: one row per request, one row per
span, and an FTS5 full-text index over **both** the request text and the answer
text. It rebuilds itself when the log's size or mtime changes, so it can never
be stale for long, and it is gitignored because it can always be rebuilt.

### `eval/drill.py` (new): the support drill

`start` starts a clock, `slice` filters (time, user, prompt, input type,
allergen, words in request/answer, cost outlier), `show` prints a trace with its
span table, `export` writes `trace.json`, `found` stops the clock and checks
the guess against the planter's seal.

### `eval/w11_plant.py` (new): the squadmate's tool

Copies the production log to `out/w11/drill/traces.jsonl` (stripping
test-harness fields), clones a real dairy-free answer as a new request from a
different user at a time inside the traffic window, corrupts one swap so the
replacement is dairy, and writes a salted-hash **seal**. The production log is
never touched.

### `eval/w11_traffic.py` + `eval/w11_traffic_pool.jsonl` (new)

36 requests from 12 test users, written before any run, sent through the live
squad 12 s apart. That is the haystack.

### `eval/w11_cost.py` (new)

Cost per request by stage and by step, from spans only, plus the 10x table.

### `rag/contract.py` (changed): the stricter test

Point 6, `allergen_residue`: an answer to an "X-free" request must not put X
back as a replacement, as a row in the ingredient list, or **in the method**.
It reuses the same allergen matcher as the tools, judges a method word by the
two words in front of it ("the vegan butter" is fine, "the butter" is not), and
skips mentions like "use oil instead of ghee". `check(..., residue=False)` still
gives the old Week 10 grade so both can be shown side by side.

### `eval/run_suite.py` (new)

Runs the 10 race cases plus every regression case **live**, grades each with
both graders, prints pass counts, writes `out/w11/suite_<label>.md`. Its traces
go to `out/w11/suite_traces.jsonl`.

### `eval/test_w11.py` (new)

40 offline checks: 16 method sentences across five allergens, the planted swap
being caught, container spans not double counted, the answer being searchable,
the index rebuilding, the seal accepting only the planted id, the canary split,
and the `asked` patterns.

### `rag/squad.py`, part 2: the fix (`synth-v2`, release `squad-v2`)

The bug was one sentence in the synthesis prompt:

```
synth-v1  1. Copy scaled amounts and the method exactly. Never recompute anything.
          2. ... Delete a method sentence only if it depends on a removed ingredient.

synth-v2  1. Copy scaled amounts exactly. Never recompute anything.
          3. Copy the method, but wherever it names a removed ingredient, write the name
             of its replacement instead: "soften the onion in the ghee" becomes "soften
             the onion in the sunflower oil". ... not even by a short form such as "the
             butter" ... If a sentence only makes sense for the removed ingredient, delete
             it. Change nothing else in the method.
```

The model was obeying v1. "Copy the method exactly" is an instruction to paste
the ghee back in. Nothing else changed, so the result is attributable to this
one prompt.

**Shipping is a setting.** `SQUAD_RELEASE` picks the release (`squad-v1` is the
rollback), `SQUAD_CANARY_PERCENT` sends that percentage of users to it by a
stable hash of their user id (so a user does not flip between versions), and
`SQUAD_PREVIOUS_RELEASE` is what the canary is compared with.

### `rag/squad.py`, part 3: the cost change (`squad-v3`)

`_allergen_step_in_code` does the allergen worker's job with the one tool call
it always made, and returns the report in the same shape. One tool span
replaces two model calls. It is in the code and tested (11/11) but is NOT the
default yet: it ships in its own canary after squad-v2's.

### `rag/obs_index.py`, part 2: the bonus fields

Derived columns, computed from the logged answer with the same check the suite
uses, so old traces are backfilled automatically:

- `asked`: what the user's own words asked to avoid ("no dairy", "lactose
  free", "milk allergy"), read with word-boundary patterns so "shellfish free"
  is not a fish request and "the milk kefir" is not a dairy-free request
- `missed`: asked allergens the planner did not pick
- `residue_swaps` / `residue_rows` / `residue_method` / `residue`

`eval/drill.py slice` gained `--residue`, `--asked`, `--plan-mismatch`.

### `rag/trace.py` (one-line fix)

`git rev-parse` failed in this folder ("dubious ownership": the checkout belongs
to a different Windows account), so every trace said `git_sha: unknown`. The
drill's `show` exposed it. Now it passes `safe.directory` for this repo only.

### `eval/regression_cases.jsonl` (new)

The found request, verbatim, with `regression_of: tr_93031da07c32` and how it
was found. Same shape and same grader as the race cases. Every future real
failure becomes one more line here, RED first.

---

## Part 4. Concepts, in plain words

| Concept | Plain words | Where it lives here |
|---|---|---|
| **Structured log** | One machine-readable line per request (JSON), not a sentence for humans. You can filter it, count it, and sum it. | `out/w11/traces.jsonl`, written by `rag/obs.py` |
| **Trace** | Everything that happened for ONE request, with an id you can quote. | one line in the log; `trace_id` |
| **Span** | One step inside a trace, with its own start time, duration, tokens and cost. Spans nest: a worker span contains its laps. | `trace.spans[]` |
| **Stage** | The kind of step a span is: retrieval (finding the recipe), generation (a model call), tool (deterministic code the model or orchestrator called). | `span.stage` |
| **Slice** | A filter over many traces: by time, user, prompt version, input type, cost. The drill is "pick the slices that shrink 36 rows to 1". | `eval/drill.py slice` |
| **Full-text index** | A lookup table from words to the rows that contain them, so "ghee" finds every answer that mentions ghee without reading each one. | SQLite FTS5 in `rag/obs_index.py` |
| **Derived field** | A column computed from the raw log (not typed by anyone) that answers a question directly, e.g. "did this answer put the allergen back?" | `residue` column (bonus) |
| **Cost attribution** | Splitting the bill by who spent it, before trying to cut it. Otherwise you can't say what a saving came from. | `eval/w11_cost.py` |
| **Tokens and price** | The model bills per token. Input (what you send) and output (what it writes) have different prices; here output is 6x dearer. | `rag/llm.py` constants |
| **Rate limit** | The provider's cap on calls: per minute (RPM) and per day (RPD). On a free tier these break long before money does. | `tenx.md` |
| **Regression test** | A test written from a real failure, so the same failure can never come back unnoticed. | `eval/regression_cases.jsonl` |
| **RED then GREEN** | Watch the new test FAIL on the current code first (proves it can catch the bug), THEN fix and watch it pass. | `out/w11/suite_red.md`, `suite_green.md` |
| **Prompt version** | A name for each exact prompt text, stamped on every trace, so you can say which wording produced an answer and roll back by name. | `PROMPTS` in `rag/squad.py` |
| **Canary** | Ship the change to a small share of users first, compare, then widen. | `SQUAD_CANARY_PERCENT` |
| **Rollback** | Undo a release by flipping a setting, not by writing code at 3am. | `SQUAD_RELEASE=squad-v1` |
| **Data flywheel** | Production failures become test cases, the suite grows, the app gets better while you sleep. | this week's loop |
| **Model routing** | Send each step to the cheapest thing that can do it. The cheapest "model" is plain code, when the step needs no judgement. | allergen step in `squad-v3` |

---

## Part 5. Outside terms you will hear

| Term | What it is | Did we use it? |
|---|---|---|
| **OpenTelemetry (OTel)** | The open standard for traces and spans across languages and vendors. Our trace/span shape (trace_id, span_id, parent_id, start, duration, attributes) is the same idea, written to a file instead of an OTel collector. | Shape yes, library no |
| **LangSmith** | LangChain's hosted tracing + eval product for LLM apps. | No (would replace our JSONL + SQLite) |
| **Arize Phoenix** | An open-source LLM tracing/eval UI built on OpenTelemetry. Same job as LangSmith, self-hostable. | No |
| **LiteLLM** | A library/proxy that puts one API in front of many model providers, with routing, fallbacks, budgets and rate-limit handling. | No; our "routing" is code vs model |
| **Prompt caching** | The provider stores a long, repeated prompt prefix and bills it cheaper next time. Gemini needs a long prefix (and is not available on the free tier); our prompts are a few hundred tokens. | No, and why not is in `cost_by_stage.md` |
| **Semantic caching** | Reusing a stored answer for a "similar enough" new question. Dangerous here: it would serve the bad dairy answer instantly to everyone who asks something similar. | Deliberately no |
| **Fallbacks** | If model A fails or is rate-limited, try model B. Week 6 removed silent fallbacks because they changed the measuring instrument. | No |
| **Fine-tuning** | Training the model on your own examples. The course calls it the last resort; a prompt fix was enough here. | No |
| **p50 / p95 / p99** | The latency that 50% / 95% / 99% of requests are faster than. p99 is what an angry customer screenshots. | `cost_by_stage.md` |
| **SHA-256, salt** | A one-way fingerprint. The seal stores sha256(salt + trace_id), so the finder can check a guess but can't read the answer off the seal. | `eval/w11_plant.py` |
| **JSONL** | One JSON object per line. Append-only friendly: a crash loses at most one line. | every log here |
| **SQLite / FTS5** | A database in a single file, built into Python; FTS5 is its full-text search engine. | `rag/obs_index.py` |

---

## Part 6. How each piece was tested

| what | how | result |
|---|---|---|
| the residue check (it decides RED and GREEN) | 16 real method sentences across 5 allergens, including the ones that must NOT count ("instead of ghee", "the vegan butter", "creamy and buttery"); a planted swap; old vs new grader on the same answer | `eval/test_w11.py`: all pass |
| stage sums | a worker container with one child: cost counted once | pass |
| the index | the answer is searchable and the request column is not; the index rebuilds when the log grows | pass |
| the plant and seal | the planted replacement really is dairy; the seal accepts the planted id and rejects any other | pass |
| canary and rollback | 10% canary puts 10.0% of 2,000 users on v2; a user's release is stable; rollback puts everyone on v1 | pass |
| `asked` patterns | "shellfish free" is not fish; "the milk kefir" is not dairy-free; two constraints are both read | pass (two of these were real bugs in the first version, found on real data) |
| earlier weeks still work | `test_allergens.py` 35/35, `test_assertions.py` 7/7, `test_chunk_invariants.py`, `trajectory_eval.py` (output byte-identical) | pass |
| the app end to end | 36 live requests, then the suite live three times (11 cases each, 63 + 63 + 43 model calls) | 36/36 ok; RED 6/11, GREEN 11/11, v3 11/11 |
| the drill tooling | two plants at random, found and verified against the seal | MATCH twice |

`python eval/test_w11.py` runs all 40 offline checks with no API key.

---

## Part 7. Why we need this

- **A complaint is a sentence, not a trace id.** Without per-request logs, "it
  said ghee was dairy-free last week" is unanswerable. With them, it is one
  query.
- **Totals hide the culprit.** "This request cost $0.0029" tells you nothing.
  "Synthesis is 46% of it, retrieval is $0" tells you where to look, and which
  "optimisation" would save nothing.
- **A test that has only ever been green has never been tested.** RED first
  proves the test can see the failure. Here it also exposed four old cases that
  had been wrong all along.
- **Pass counts on the whole suite** are what stop "fixed one thing, broke
  another" from shipping.
- **Prompt versions + a release switch** turn "undo it" from a 3am code change
  into a setting.
- **On a free tier, rate limits break before money does.** You only know that
  if each call is logged with when it happened and whether it was throttled.

---

## Part 8. Questions a reviewer is likely to ask, and answers you can defend

**"The brief says add the case to the Week 6 suite. Why is it somewhere else?"**
> The Week 6 harness grades `rag/substitute.py`'s output shape, which the squad
> doesn't produce; Week 10 already moved the squad to the race suite. I checked
> the Week 6 path with 14 dairy-free requests: it refused 13. A case there would
> be green before any fix, which is the mistake the brief warns about. Evidence:
> `out/w11/substitute_path_probe.json`.

**"Your RED failed on the method, not on the crème fraîche swap you found. Did you reproduce the bug?"**
> Not the planted swap, and I checked why: the substitution worker verifies
> every replacement with the allergen tool, and `--residue swap` finds 0 of 36
> on the real log. The test checks the promise the customer was given, "no
> dairy anywhere in the answer". On the live app that promise breaks in the
> method, in 8 of 9 real dairy answers. The case guards both: point 4 checks
> replacements, point 6 checks the rest.

**"00:17 is suspiciously fast."**
> It is a rehearsal, self-timed, by the person who wrote the planter, reading at
> machine speed. That's why `drill.md` reports rows read (22 -> 1) next to the
> time, and leaves the graded run with a named squadmate to me.

**"How do you know the fix didn't break something else?"**
> The whole suite runs live every time and shows two grades side by side. Every
> case that passed on squad-v1 still passes on squad-v2, and nothing went from
> PASS to FAIL.

**"Couldn't the model just get lucky at temperature 0?"**
> It's one run per case. 11/11 on 11 cases isn't a guarantee for every
> phrasing. The canary is the next check: its promotion rule is zero residue on
> real squad-v2 traffic, read straight off the log.

**"Isn't your residue check just keyword matching?"**
> Yes, deterministic and lexical, on purpose: it is free, it can't have an off
> day, and it reuses the allergen tool's matcher. It looks at the two words
> before a hit ("the vegan butter" is fine, "the butter" is not) and skips
> mentions ("instead of ghee"). It would miss "the fat" meaning ghee. Its 40
> offline tests are the cases that mattered this week.

**"Why canary a safety fix? Why not ship it to everyone now?"**
> Because the canary is what tells me the fix works on real traffic, not just my
> 11 cases. But the canary is 2 hours, not days: here the OLD version is the
> unsafe one, so the window only needs to see real dairy requests go through v2.

**"Where did the cost saving come from?"**
> Attributed by step before and after on the same 11 requests: 97% of the $0.00059
> saving per request is the allergen step, which went from 1.82 model calls to
> one 11 ms tool call. The rest is noise in steps whose prompts didn't change.

**"Why isn't squad-v3 the default if it's cheaper and passes?"**
> Two changes in one canary can't be told apart. squad-v2 ships first; v3 gets
> its own canary against v2.

**"Is 15/min real?"**
> Yes: the API named it in a real 429 body during the 1x traffic run
> (`GenerateRequestsPerMinutePerProjectPerModel-FreeTier=15`), recorded on the
> span. The 500/day figure is weaker (a third-party table); our own 378 calls in
> one quota-day drew no daily 429.

**"Why not semantic caching to cut cost?"**
> It would have served the bad dairy answer instantly to everyone asking
> something similar. You'd be caching the failure and taking on a staleness risk
> on an allergy answer.

**"Why didn't you fix the planner bugs you found?"**
> One fix per week, so the change is attributable. They're written down in
> `results_week11.md` section 7 as the next regression cases, RED first.

**"What would you do differently in real production?"**
> Send the spans to an OpenTelemetry collector or a tool like LangSmith or
> Phoenix instead of a JSONL file, run the residue check at write time as an
> alert, and put a rate-limit-aware queue in front of the squad.

---

## Part 9. What is left for you to do

1. **The graded drill.** A named squadmate runs `python eval/w11_plant.py
   --random` while you look away, holds the stopwatch while you use
   `eval/drill.py`, and you fill the last table in `drill.md`. Don't diff the
   drill copy against the production log, and don't use your memory of Friday's demo.
2. **Bring the numbers written down** (the brief asks): 6/11 -> 11/11; 00:17 / 00:11
   (rehearsal) and your graded time; $0.002886 for the found request ($0 retrieval,
   $0.002886 generation, $0 tools); -25.3% for squad-v3; 18 calls/min vs 15/min.
3. Optional: run the squad-v2 canary for real:
   `SQUAD_CANARY_PERCENT=10 python eval/w11_traffic.py`, then
   `python eval/drill.py slice --log out/w11/traces.jsonl --prompt squad-v2 --residue any`.
