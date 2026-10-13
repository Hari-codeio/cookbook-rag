# Release notes: the squad's prompt versions

Every trace records `prompt_version` (the release) and each step's version and
sha256 (`prompts`), so any answer in the log can be tied to the exact wording
that produced it. Releases are defined in `PROMPTS` in `rag/squad.py`.

| release | plan | allergen_worker | substitution_worker | synthesise | what changed | suite |
|---|---|---|---|---|---|---|
| `squad-v1` | plan-v1 | allergen-v1 | substitution-v1 | synth-v1 | Week 10, first versioned in Week 11 | RED: see `out/w11/suite_red.md` |
| `squad-v2` | plan-v1 | allergen-v1 | substitution-v1 | **synth-v2** | method must name the replacement, never the removed ingredient. **The default.** | RED 6/11 -> GREEN **11/11** (`out/w11/suite_green.md`) |
| `squad-v3` | plan-v1 | **allergen-code-v1** | substitution-v1 | synth-v2 | allergen step done by code, no model: -1.82 calls and -25.3% cost per request | **11/11** (`out/w11/suite_v3-cost.md`); ships after v2's canary |

## squad-v1 -> squad-v2 (Week 11)

**The bug.** synth-v1 rule 1 said *"Copy scaled amounts and the method
exactly"*, and rule 2 let it delete a sentence only if the sentence *"depends
on"* a removed ingredient. Together they told the model to paste the original
method back, so 8 of 9 dairy-free answers in the production log swapped the
ingredient list and kept *"soften the onion in the ghee"* in the method.

**The change.** synth-v2 splits rule 1 (amounts are still copied exactly) and
adds rule 3: copy the method, but write the replacement's name wherever a
removed ingredient is named, short forms included ("the butter"); delete a
sentence only if it makes sense for the removed ingredient alone; change
nothing else. Plan, allergen and substitution prompts are untouched, so any
change in behaviour is attributable to this one prompt.

**Shipping it (two lines).**

> **Canary:** set `SQUAD_CANARY_PERCENT=10` so 10% of users (stable hash of user_id) get squad-v2 for 2 hours, and promote to 100% only if no squad-v2 trace in that window shows an allergen residue (`eval/drill.py slice --prompt squad-v2 --residue any` returns 0 rows) and its p50 latency and cost per request are within 10% of squad-v1's.
> **Rollback:** set `SQUAD_RELEASE=squad-v1` (no code change, no deploy) the moment any squad-v2 trace shows a residue or `eval/run_suite.py` drops below 11/11; every trace carries `prompt_version`, so the affected answers are one slice of the log.

The canary is short on purpose. Normally a canary protects users from the new
version; here the OLD version is the unsafe one, so the window only has to be
long enough to see real dairy requests go through squad-v2, not long enough to
"prove" it.

## squad-v2 -> squad-v3 (Week 11, the cost change; next, not yet)

**The change.** The allergen worker (a model with two tools) is replaced by
the one tool call it always made: `get_allergen_profile`, then `must_remove =
carries_allergen`, `caveats = unknown_to_the_archive`. The step is versioned
`allergen-code-v1` and hashed like a prompt, so a trace still says exactly what
did it. Measured in `cost_by_stage.md` section 3: 11/11, -25.3% cost, -1.82
model calls per request.

**Why it waits.** squad-v2's canary has to finish first. Two changes in one
canary cannot be told apart: if residue or latency moved, you would not know
which change moved it.

**Shipping it, the same two lines:** `SQUAD_RELEASE=squad-v3
SQUAD_PREVIOUS_RELEASE=squad-v2 SQUAD_CANARY_PERCENT=10` for 24 h, promoted if
the canary's residue count is 0, its `--plan-mismatch` rate is no higher, and
its cost per request is lower than squad-v2's on the same day; roll back with
`SQUAD_RELEASE=squad-v2`.
