# Week 11: make the app watch itself (Set B, recipes)

Headline, in the order the brief scores it:

```
loop closed     w11-r01 RED on squad-v1, GREEN on squad-v2
                suite 6/11 -> 11/11   (same answers under the Week 10 grader: 11/11 -> 11/11)
drill           rehearsal 1: 00:17, slice = input type (contains-dairy) + time, then the swap lines
                rehearsal 2: 00:11, one query on the new residue field   (rows to read: 22 -> 1)
                the graded drill, with a named squadmate: drill.md, for Monday
trace           trace.json: 12 spans, per-span latency / tokens / cost, prompt squad-v1, context ids
cost/query      that request $0.002886: retrieval $0, generation $0.002886 (6 calls), tools $0
                improvement: squad-v3, -25.3% per request on the same 11 cases, 11/11 kept
10x             the per-minute rate limit: busiest 1x minute = 18 calls vs 15/min, named by a real 429
prompt bump     synth-v1 -> synth-v2 (release squad-v1 -> squad-v2), canary + rollback in two lines
```

| rubric line | points | where |
|---|---|---|
| loop closed, RED then GREEN, pass counts both times | 30 | section 3; `out/w11/suite_red.md`, `out/w11/suite_green.md`; case `eval/regression_cases.jsonl` |
| time-to-find mm:ss + slice, or the missing field | 25 | `drill.md` |
| trace with per-span latency, tokens, cost, prompt version, context ids | 20 | `trace.json`; section 2 |
| cost per query by stage, 10x claim with a number | 15 | `cost_by_stage.md`, `tenx.md` |
| prompt version bump + two-line canary and rollback | 10 | `release_notes.md`; section 4 |
| bonus: the field that closed the gap, second plant, both times | | `drill.md` drill 2; `rag/obs_index.py` |

The order things were done in is in the git history and is part of the
evidence: the production log (`00ed2cb`) before the drill; the regression case
and the stricter grader (`e5b2c74`) before RED; RED (`670db62`) before the fix
(`b80906d`); GREEN (`25b9385`); cost attributed (`c7db24c`) before the cost
change (`6ad9082`) and its measurement (`1866d38`).

---

## 0. Two deviations, stated up front

**Which app.** The brief extends "the app you already built". Week 10 kept
the kitchen squad (`rag/squad.py`), so the squad is production and is what this
week instruments, drills, tests and fixes. The older single-shot paths
(`rag/generate.py`, `rag/substitute.py`) keep their Week 5 trace log untouched.

**Which suite.** The brief says to add the eval case "to the Week-6 suite".
This repo's Week 6 harness (`eval/run_eval.py`) grades `rag/substitute.py`'s
output shape (`can_substitute`, chunk-id citations), which the squad does not
produce. Week 10 already raced the squad on `eval/race_cases.jsonl` graded by
`rag/contract.check`, and said so. So the case goes into
`eval/regression_cases.jsonl` and runs with those 10 cases in
`eval/run_suite.py`.

That was checked, not assumed: 14 dairy-free requests sent to the Week 6 path
(`out/w11/substitute_path_probe.json`) were declined 13 times; the 14th swapped
everything to sunflower oil. The Week 6 path does not have this bug, so a case
added there would be green before any fix, which is the exact mistake the brief
names. If the reviewer means the literal Week 6 file, this is the point to
challenge.

## 1. What had to be built first: the squad logged nothing

Until this week a squad request left no record. Its only trace was stdout, or
a `.txt` someone saved by hand. The real failure this week turns on was sitting
in one: `out/squad_demo.txt` (Oct 7), a "completely dairy free" tikka masala
whose method still says *"soften the onion in the ghee"* and *"stir in the
cream"*.

`rag/obs.py` now writes one line per request to `out/w11/traces.jsonl`:
trace_id, ts, user, session, the request text and its input type, the release
and every step's prompt version + sha256, the retrieved recipe ids, and a span
per step with its own start, latency, tokens, cost and model. Spans nest (a
worker contains its laps and tool calls), and only leaf spans carry cost, so
summing by stage never counts a worker twice. `rag/obs_index.py` makes the log
searchable: SQLite with an FTS5 index over the request AND the answer.

Then 36 requests from 12 test users (`eval/w11_traffic_pool.jsonl`, written
before any run) went through the live squad: **36/36 ok, 189 model calls,
16.2 min, 2 rate-limited calls**. That log is the haystack.

## 2. The drill and the trace (summary; detail in `drill.md`)

| | time-to-find | slice | rows read |
|---|---|---|---|
| rehearsal 1 | **00:17** | input type (`contains-dairy`) + time 7d, then the swap lines | 22 swap lines |
| rehearsal 2 (bonus) | **00:11** | `--residue swap --asked contains-dairy` | **1** |

Both are **rehearsals by the author of the tools**, self-timed by
`eval/drill.py`, not the graded drill: no squadmate held the stopwatch, and
the finder knew what KIND of corruption the planter makes (not which trace).
`drill.md` says what they do and do not prove, and has the table and commands
for the graded run with a named squadmate.

**The field whose absence cost the time:** nothing in the log answered *did
this answer's replacement carry the allergen the user asked to avoid?* The
answer and the allergen were both logged; no field joined them. The bonus adds
it as derived index columns (`residue_swaps`, `residue_rows`, `residue_method`,
`asked`, `missed`), which backfill every old trace on rebuild.

**`trace.json`** is the found trace, `tr_93031da07c32`, as logged:

```
span name                                       stage       start ms latency ms in tok out tok     cost $
s01  plan                                       generation       0.1     4456.2    165      36   0.000095
s02  recipe_search                              retrieval     4467.9      299.6      0       0   0.000000
s03  scale_recipe                               tool          4773.0       32.2      0       0   0.000000
s04  allergen_worker                            worker        4805.9     6708.2      0       0   0.000000
s05    allergen_worker.lap1                     generation    4805.9     3799.0    591     106   0.000307
s06    allergen_worker.get_allergen_profile     tool          8533.0       30.1      0       0   0.000000
s07    allergen_worker.lap2                     generation    8563.7     3008.4    872     130   0.000413
s08  substitution_worker                        worker       11631.0     8523.3      0       0   0.000000
s09    substitution_worker.lap1                 generation   11631.0     4243.8    486      49   0.000195
s10    substitution_worker.get_allergen_profile tool         15761.4       24.1      0       0   0.000000
s11    substitution_worker.lap2                 generation   15786.0     4306.8    620     257   0.000540
s12  synthesise                                 generation   20106.8     5683.0    997     724   0.001335
     TOTAL                                                             25920.5   3731    1302   0.002886

prompt   squad-v1: plan-v1, allergen-v1, substitution-v1, synth-v1 (each with its sha256 in the trace)
context  retrieval.context_ids = [chicken-tikka-masala, chana-masala], used = chicken-tikka-masala
```

It is the planted clone of a real request, so its tokens and cost are real and
its latencies carry the planter's +-10% jitter; `trace.json` also shows
`git_sha: "unknown"`, a real logging bug the drill exposed and `834e807` fixed
(git refused to run in a checkout owned by another Windows account). The 36
production traces keep `unknown`; logs are not edited after the fact.

## 3. The loop closed: RED, then GREEN

**The test.** `eval/regression_cases.jsonl` case `w11-r01`, the found request
verbatim (*"Tikka masala with no dairy, my son has a milk allergy"*), with
`regression_of: tr_93031da07c32`. It asserts the PROPERTY the customer was
promised, not the planted string: `rag/contract.py` gains **point 6**, *nothing
in the answer puts the avoided allergen back: not a replacement, not an
ingredient row, not the method*. Points 1 to 5 never read the method. That is
the whole reason Week 10 scored 10/10.

Point 6 has its own tests before it was trusted with anything (`eval/test_w11.py`,
40 offline checks): 16 method sentences across five allergens, including the
ones that must NOT count (*"use sunflower oil instead of ghee"*, *"the vegan
butter"*, *"creamy and buttery"*).

**RED**, `python eval/run_suite.py --label red --release squad-v1`, all 11 live:

```
| case | kind | w10 grader (1-5) | now (1-6) | why it failed |
| s01..s02, s04..s06, c01 | race | PASS | PASS | |
| s03 | race | PASS | FAIL | method still tells the cook to use contains-alcohol: ['over the reserved wine'] |
| c02 | race | PASS | FAIL | method ...: ['chicken in the yoghurt', 'onion in the ghee,', 'stir in the cream'] |
| c03 | race | PASS | FAIL | method ...: ['Add the softened butter', 'eggs and warm milk'] |
| c04 | race | PASS | FAIL | method ...: ['Beat the butter'] |
| w11-r01 | regression | PASS | FAIL | method ...: ['acid in the yoghurt', 'chicken in the yoghurt', 'onion in the ghee,', 'stir in the cream'] |

SUITE RED: 6/11 pass   (release squad-v1)
same answers, Week 10 grader: 11/11
```

The new case fails, and so do four race cases the Week 10 grader had been
passing. That is the silent failure the pass counts exist to expose: without
the second column it would read as one new red case, not five.

**GREEN**, `python eval/run_suite.py --label green --release squad-v2`, all 11 live:

```
| s01 .. s06, c01 .. c04, w11-r01 | PASS | PASS |    (every row)

SUITE GREEN: 11/11 pass   (release squad-v2)
same answers, Week 10 grader: 11/11
```

**6/11 -> 11/11**, and nothing that passed on squad-v1 regressed. The fixed
w11-r01 method now reads *"Soften the onion in the Neutral oil or vegan butter
alternative ... stir in the Full-fat coconut milk"*. Full tables:
`out/w11/suite_red.md`, `out/w11/suite_green.md`; every answer and trace id in
the matching `.json`.

**Why RED failed on the method and not on the planted swap.** The planted
answer's crème fraîche swap cannot be reproduced: the substitution worker
checks each replacement with `get_allergen_profile`, and on the real log the
new `--residue swap` slice returns 0 of 36. The same customer promise breaks a
different way, in the method, and that break is real: **8 of 9** dairy-free
answers in the production log have it. The case guards both, because point 4
already checks replacements and point 6 checks the rest.

## 4. The fix, the version bump, and shipping it

**Root cause, from the spans.** In the real request the plant was cloned from
(`tr_919c9b03134d`), the `substitution_worker` span's output has all three
swaps right (coconut yoghurt, coconut milk, neutral oil), and the answer that
leaves `synthesise` still says ghee and cream. So the damage happens in one
step, synthesis. synth-v1 rule 1
said *"Copy scaled amounts **and the method exactly**"*, and rule 2 allowed
deleting a sentence only if it *"depends on"* a removed ingredient. The model
did what it was told.

**The fix, at the prompt layer.** synth-v2 keeps amounts copied exactly and
adds one rule: write the replacement's name wherever the method names a
removed ingredient, short forms included ("the butter"), delete a sentence
only if it makes sense for the removed ingredient alone, change nothing else.
The other three prompts are untouched, so the change is attributable to one
prompt.

**Version bump:** `synth-v1 -> synth-v2`, release `squad-v1 -> squad-v2`,
recorded in `PROMPTS` in `rag/squad.py`, in every trace's `prompts` block, and
in `release_notes.md`.

**Canary and rollback, two lines** (`release_notes.md`):

> **Canary:** set `SQUAD_CANARY_PERCENT=10` so 10% of users (stable hash of user_id) get squad-v2 for 2 hours, and promote to 100% only if no squad-v2 trace in that window shows an allergen residue (`eval/drill.py slice --prompt squad-v2 --residue any` returns 0 rows) and its p50 latency and cost per request are within 10% of squad-v1's.
> **Rollback:** set `SQUAD_RELEASE=squad-v1` (no code change, no deploy) the moment any squad-v2 trace shows a residue or `eval/run_suite.py` drops below 11/11; every trace carries `prompt_version`, so the affected answers are one slice of the log.

Both are settings in `rag/squad.py`, not plans on paper, and both have offline
tests (10% canary puts 10.0% of 2,000 users on v2, each user stays put,
rollback puts everyone on v1).

## 5. Cost per query, and the improvement (summary; detail in `cost_by_stage.md`)

**That request**, by stage: retrieval **$0** (300 ms), generation
**$0.002886** (6 model calls, 25.5 s), tools **$0** (86 ms). Across the 36
production requests: $0.002016 per request, 100% generation; synthesis 48.7%,
allergen worker 23.3%, substitution worker 23.3%, plan 4.7%. Output tokens are
64% of the bill.

**The improvement, chosen from that table:** squad-v3 routes the allergen step
to code. Its job is one tool call and a copy of the answer, and in 27 of 28
production requests its report was exactly the tool's answer. On the same 11
suite requests: **$0.002329 -> $0.001739 (-25.3%), 5.73 -> 3.91 model calls,
11/11 kept**. 97% of the saving is the allergen stage. It is validated and not
yet the default: it gets its own canary after squad-v2's, because two changes in
one canary cannot be told apart. The fix itself cost +2.8% per request.

## 6. 10x (`tenx.md`)

**At 10x the per-minute rate limit breaks first, and it already bit at 1x: the
busiest minute made 18 model calls against the 15/min cap the API named in its
own 429 (`GenerateRequestsPerMinutePerProjectPerModel-FreeTier=15`), so 10x is
180 calls/min (12x the cap); cost at 10x is only $0.73/day.**

## 7. What else the log found (backlog, not fixed this week)

One fix per week, so the fix can be attributed. The rest is written down:

| finding | evidence | why it matters |
|---|---|---|
| the planner invents an allergen on "half" requests, **3 of 3** | t03 half sourdough -> gluten removed; t18 half bourguignon -> wine removed; t27 half miso -> soy removed | a plain scaling request comes back with ingredients the user never asked to lose |
| the planner drops dairy when a request names two constraints | t23 "Gluten-free brioche but dairy free too" -> planned as gluten only; answer keeps milk and butter | an organic "dairy-free answer that wasn't"; `--plan-mismatch` finds it, a slice on the planned allergen cannot |
| the planner drops an allergen it judges irrelevant | t12 shakshuka, t35 chana masala "dairy free" -> scale-only | harmless here (no dairy in either), but the input type is wrong |
| the Week 10 grader never read the method | 4 race cases passed in Week 10 and fail point 6 on squad-v1 | fixed: point 6 is permanent |
| cost constants were an old price | 0.10/0.40 per 1M in Weeks 7 to 10 vs 0.25/1.50 list | fixed in `rag/llm.py`; Weeks 7 to 10 cost columns read low, tokens unaffected |
| traces could not name their code | `git_sha: unknown` | fixed in `834e807` |

The planner findings are the obvious next regression cases: each is one line in
`eval/regression_cases.jsonl`, RED first.

## 8. What this does NOT show

- **The drill times are rehearsals by the author.** No squadmate timed them,
  and a machine reads faster than a person. The graded run is Hari's, with a
  named squadmate.
- **The haystack is 36 real requests, not thousands.** At this size reading
  every dairy answer still works; the derived residue field is what scales.
  The users are test users from a written pool.
- **One live run per suite cell, at temperature 0.** 11/11 twice is strong
  for these 11 requests, not a guarantee for every phrasing.
- **The residue check is lexical.** It catches a removed ingredient named in
  the method, short forms included, and skips "instead of" mentions. It
  would miss a method that says "the fat" for ghee, and would flag "butter
  knife". Its 40 offline checks are the cases that mattered this week.
- **500/day is unconfirmed.** 15/min was named by a real 429; 500/day comes
  from a third-party table. This week's own runs made 378 calls in one Pacific
  quota-day with no daily 429, consistent with a cap of at least 378.
- **squad-v3's latency gain is mostly noise except the allergen step itself**
  (2.4 s -> 11 ms); free-tier latency moves between runs with nothing changed.

## 9. Reproduce

```bash
PY=.venv/Scripts/python
$PY eval/test_w11.py                                   # 40 offline checks, no API
$PY eval/w11_traffic.py                                # the production log   [needs API key]
$PY eval/w11_plant.py --random                         # squadmate
$PY eval/drill.py start --finder Hari                  # finder
$PY eval/drill.py slice --since 7d --type allergen-swap --allergen contains-dairy --show-answer --grep "swap "
$PY eval/drill.py slice --since 7d --asked contains-dairy --residue swap      # bonus field
$PY eval/drill.py found tr_xxx --slice "..." --timer "<squadmate>"
$PY eval/drill.py export tr_xxx --out trace.json
$PY eval/run_suite.py --label red   --release squad-v1 # [needs API key]
$PY eval/run_suite.py --label green --release squad-v2 # [needs API key]
$PY eval/w11_cost.py                                   # cost by stage + 10x, from the log
$PY eval/w11_cost.py --trace tr_xxx                    # one request by stage
```
