# Release notes: the squad's prompt versions

Every trace records `prompt_version` (the release) and each step's version and
sha256 (`prompts`), so any answer in the log can be tied to the exact wording
that produced it. Releases are defined in `PROMPTS` in `rag/squad.py`.

| release | plan | allergen_worker | substitution_worker | synthesise | what changed | suite |
|---|---|---|---|---|---|---|
| `squad-v1` | plan-v1 | allergen-v1 | substitution-v1 | synth-v1 | Week 10, first versioned in Week 11 | RED: see `out/w11/suite_red.md` |
| `squad-v2` | plan-v1 | allergen-v1 | substitution-v1 | **synth-v2** | method must name the replacement, never the removed ingredient | GREEN: see `out/w11/suite_green.md` |

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
