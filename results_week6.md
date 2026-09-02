# Week 6 - validating the substitution judge before trusting its number

Headline, up front, because it is not the result I predicted:

```
agreement_before  84.0%   (21/25)   judge_v1
agreement_after   84.0%   (21/25)   judge_v2
```

**The number did not move.** On the 23 cases that were not fed to v2 as examples,
it went *down*: 91.3% -> 87.0%. The iteration fixed one case, failed to fix a
case it was literally shown the answer to, and broke a case that had been fine.
Section 5 scores the prediction against that, and section 6 names who was right
in the disagreements, including the two where I now think the judge beat me.

| deliverable | file |
|---|---|
| 25 blind hand labels | [labels_25.json](labels_25.json) - commit `449b8b6` |
| judge v1 / v2 | [eval/judge_v1.txt](eval/judge_v1.txt), [eval/judge_v2.txt](eval/judge_v2.txt) |
| prediction, before iterating | [prediction.txt](prediction.txt) - commit `6db35cd` |
| one-command eval | `python eval/run_eval.py` |
| eval output | [out/eval_v1.md](out/eval_v1.md), [out/eval_v2.md](out/eval_v2.md) |
| the 25 frozen substitutions | [out/substitutions_v1.jsonl](out/substitutions_v1.jsonl) |
| BONUS - RAGAS, section 8 | [eval/ragas_reference.json](eval/ragas_reference.json) - commit `d4ccfac` ; `python eval/run_ragas.py` ; [out/ragas.md](out/ragas.md) |

---

## 0. What had to be built first

Week 5 found the app refused all 12 substitution questions in the traffic pool.
There was no substitution path to judge, so `rag/substitute.py` adds one. Its
single design constraint is what makes the eval possible: **a swap is allowed
only when another card in the archive demonstrates it.**

The archive is built out of near-duplicate families, so this cuts real requests
in half:

| request | donor | groundable |
|---|---|---|
| classic brioche -> gluten free | `gf-brioche` is the same enriched dough | yes |
| chocolate brioche -> dairy free | nothing in 21 cards | no |
| wholemeal sourdough -> light rye | `rye-sourdough` | yes |
| tikka masala -> vegan | nothing | no |

Both look identical to a user. Telling them apart is the judgement this week
measures. 12 of the 25 cases are groundable, 13 are not.

Retrieval is **two queries merged**, not one: embedding "make the classic
brioche gluten free" ranks all three brioches highly and the gluten-free donor
nowhere, because the dish name dominates the vector.

---

## 1. Assertions vs judged criteria: **6 vs 1**

Five criteria that would naturally sit in a judge prompt are decided in code
instead, plus one that checks the infrastructure:

| | check | what it decides |
|---|---|---|
| A1 | `method-ingredients-declared` | every ingredient the method names is in the list |
| A2 | `allergen-warning-present` | a warning exists and names every allergen in the list |
| A3 | `oven-temperature-has-units` | a stated oven setting carries C or F |
| A4 | `servings-stated-or-absent` | a real yield or an honest blank, never `N/A` |
| A5 | `quantities-parse` | every amount is number + unit |
| A6 | `model-is-the-pinned-one` | Week-5 mode 7, checked on every case |

**One criterion is left for the judge**: soundness, a single boolean. No 1-10
score. The model cannot tell a 6 from a 7, neither can I, and a within-1
tolerance would inflate agreement into meaninglessness.

`eval/judge_v1.txt` names all six and says *do not consider them*.

### The assertions never fired, and that needed proving

All six pass on all 25 cases. From the outside that is indistinguishable from
six checks that *cannot* fail, so `eval/test_assertions.py` mutates a real
output seven ways and requires each check to catch its own:

```
A1    YES     method names peanuts, the list does not
A2    YES     wheat/egg/dairy present, warning blank
A2    YES     warning omits egg and dairy, which are in the list
A3    YES     oven number with no C or F
A4    YES     placeholder servings
A5    YES     amount does not parse as number+unit
A6    YES     answered by a model other than the pinned gemini-3.1-flash-lite
all 7 mutations caught; the six checks are not decorative
```

They are worth keeping precisely because they are free. Five of them as judge
criteria would have cost 25 model calls per run to learn nothing.

---

## 2. The blind protocol, and the evidence for it

This is the part that is worth zero without ordering evidence, so here is the
chain:

| # | commit | what |
|---|---|---|
| 1 | `f6546b4` | substitution path, 25 cases, assertions, **judge_v1.txt**. Before any substitution existed. |
| 2 | `959ce8c` | the 25 substitutions, frozen. sha256 `f50218d2...` |
| 3 | `449b8b6` | **labels_25.json**. `ls out/judge_*` -> *No such file or directory*, verified in the terminal immediately before writing it. |
| 4 | - | judge v1 run. `out/judge_v1_verdicts.json` created. |
| 5 | `6db35cd` | **prediction.txt**. `ls eval/judge_v2.txt` -> *No such file or directory*. |
| 6 | - | judge v2 written and run. |

Three further things make the labels blind rather than merely first:

* `eval/judge_v1.txt` was written **before** the labels, so the labels and the
  judge answer the same binary criterion, not two similar-sounding ones.
* The sheet I labelled from (`eval/label_sheet.py`) withholds each case's own
  `groundable` field. That is my prior about what the archive supports, written
  before generation. Showing it would have turned a blind label into a check of
  whether the app agreed with me.
* `labels_25.json` records the sha256 of the substitutions file it was written
  against, so a later regeneration cannot quietly reuse old labels.

**The weakness, stated plainly.** One labeller, who also wrote the criterion and
later ran the judge. A second reader would give an inter-rater figure this study
does not have, and 84% agreement between me and a model is a weaker claim than
84% between two people would be. The blind protocol and the commit order are
what stand in for it. They are not a substitute for a second human.

**The labels**: 19 SOUND, 6 UNSOUND (`c01 c04 c05 c06 c20 c25`).

---

## 3. The one command

```bash
python eval/run_eval.py --judge eval/judge_v2.txt
```

Runs the six assertions, runs the judge (cached, keyed on the sha256 of *both*
the prompt and the substitutions, so editing either forces a re-run), prints
pass rate by mode, and computes agreement against the labels.

```
| mode                                      | n  | assertions | SOUND | PASS  | %    |
|-------------------------------------------|----|------------|-------|-------|------|
| compares-only-retrieved-cards             |  3 | 3/3        | 1/3   | 1/3   |  33% |
| drops-bakers-percentage                   |  4 | 4/4        | 3/4   | 3/4   |  75% |
| refuses-arithmetic-with-table-on-screen   |  4 | 4/4        | 3/4   | 3/4   |  75% |
| refuses-swap-instead-of-quoting-card      | 10 | 10/10      | 6/10  | 6/10  |  60% |
| refuses-when-no-recipe-named              |  2 | 2/2        | 2/2   | 2/2   | 100% |
| says-missing-while-on-screen              |  2 | 2/2        | 2/2   | 2/2   | 100% |
| all                                       | 25 | 25/25      | 17/25 | 17/25 |  68% |
```

The overall row is printed last, deliberately. Between v1 and v2 it sat at
exactly 68% while `compares-only-retrieved-cards` fell from 66% to 33% and
`refuses-arithmetic` rose from 50% to 75%. **A single headline number would have
shown this iteration as a no-op. It was not a no-op; it was two changes in
opposite directions.** That is the whole argument for the by-mode table, and it
happened on the first try.

Three cases (`r01 r02 r03`) are regression cases replayed verbatim from real
Week-5 traces that failed - `tr_f0918dcbd36b`, `tr_c5c65e9f6c06`,
`tr_b8ad80a3b1f5` - with the original trace ids recorded so the old refusal can
be pulled straight out of `out/traces.jsonl`. All three still decline, and all
three are correct to decline: nothing in the retrieved context demonstrates
Greek yoghurt, a soy-for-fish-sauce swap, or a psyllium substitute.

---

## 4. Agreement: before -> after

```
                        all 25          held-out 23
judge_v1                21/25  84.0%    21/23  91.3%
judge_v2                21/25  84.0%    20/23  87.0%
```

The held-out column excludes `c14` and `c25`, which are quoted inside v2's
prompt. Scoring a judge on the two cases you pasted into its prompt is scoring
its copying, so the 23-case figure is the one that means anything - and it went
**down**.

| case | human | v1 | v2 | |
|---|---|---|---|---|
| `c11` | SOUND | UNSOUND | UNSOUND | still disagrees, for a **different reason** |
| `c14` | SOUND | UNSOUND | SOUND | **fixed** - and it was one of the two examples |
| `c16` | SOUND | UNSOUND | UNSOUND | still disagrees |
| `c19` | SOUND | SOUND | UNSOUND | **broken by the iteration** |
| `c25` | UNSOUND | SOUND | SOUND | still disagrees - **and it was the other example** |

### The three things that actually happened

**1. c25 did not flip even though the judge was shown the answer.** Example 2 in
`judge_v2.txt` quotes c25's request, its context in rank order, its output, the
verdict v1 gave, and the sentence "The correct answer is UNSOUND" with two
paragraphs of reasoning. The judge read that and returned SOUND, with a reason
that is almost a paraphrase of the one it had just been told was wrong:

> v1: "correctly identified that the archive does not contain a gluten-free
> version of the Lemon Drizzle Loaf or instructions for modifying it"
> v2: "correctly identified that the archive does not contain a gluten-free
> version of the Lemon Drizzle Loaf and does not provide a method to convert that
> specific recipe to gluten-free"

Few-shot correction has a floor, and on this model I hit it inside one
iteration. That is the single most useful thing this week produced.

**2. The arithmetic error WAS learned, and the judge moved to a different
objection.** On c11, v1 argued the decline was wrong because baker's percentages
"allow for scaling". v2 stopped making that argument entirely - Example 1
worked. But it still called c11 UNSOUND, now because the assistant claimed it
could not ground the gluten-free part "despite the archive providing a complete
Gluten-Free Brioche recipe". The lesson landed and the verdict did not move,
because there were two independent reasons to fail the case and I had only
addressed one.

**3. Example 2 leaked a criterion I never wrote.** c19 agreed under v1 and broke
under v2. v2's reason: "failed to answer the user's request to identify which of
the brioche recipes can be made gluten-free". That is a **responsiveness**
judgement. My criterion is about whether claims are supported by context; it says
nothing about answering the question asked. Example 2 taught "do not accept a
decline on the assistant's own framing", and the judge generalised it into
"penalise an answer that dodges the question". A worked example does not carry a
scope limit, and it will generalise past the thing you meant.

---

## 5. Scoring the prediction

[prediction.txt](prediction.txt), committed `6db35cd` before `judge_v2.txt`
existed:

| I predicted | what happened | |
|---|---|---|
| agreement 84% -> **96%** (24/25) | **84%** (21/25) | wrong |
| held-out beats 91.3% | **87.0%** | wrong, it got worse |
| `c11` flips to SOUND without being shown | did not flip | wrong |
| `c16` stays a disagreement | stayed | right |
| **0** new disagreements created | **1** (`c19`) | wrong |

Four of five wrong. The one thing I got right is the one I hedged on.

**What I did not see coming, in order of how much it mattered:**

1. That a case *inside the prompt as a worked example* could still come back
   wrong. I assumed the two examples were guaranteed points and predicted from
   there. They were not; one of them was.
2. That fixing a stated reason does not fix a verdict. I read v1's c11 reason,
   diagnosed the arithmetic error correctly, fixed it, and c11 did not move
   because it had a second failure reason I had not looked for.
3. That an example generalises past its lesson. I wrote "nothing else in the
   prompt changes" and believed that meant nothing else in the judge's behaviour
   would change. Example 2 taught a responsiveness rule I never authored.

The prediction's stated risk - that the judge was right about c16 and I was
lenient - is the one thing I called correctly, and section 6 says I now think it
applies to c11 too.

---

## 6. Two disagreements, and who was right

### `c11` - **the judge was right and I was wrong**

Request: classic brioche, gluten free *and* halved to 250 g flour. The app
declined:

> "I cannot ground the request to make the recipe gluten-free or to halve the
> recipe to 250 g of flour. While the archive contains a gluten-free brioche
> recipe, **it does not provide instructions or evidence for converting the
> classic brioche recipe to be gluten-free**, nor does it provide a mechanism
> for scaling."

I labelled it SOUND: the halving is ungroundable arithmetic, a partly groundable
request is not groundable, so declining is correct. I noticed the bolded clause
was false and wrote in my own label that it "overreaches" - and forgave it,
because the decision was right.

The criterion does not allow that. It says *every claim* must be supported by
the context blocks. `gf-brioche::structure::c001` was in the context. The
assistant asserted the archive lacks evidence that was on screen, which is
exactly criterion (b), and I let a correct decision cover an incorrect
statement. The judge caught it in both versions.

**Relabelling c11 would take agreement to 22/25 = 88%.** I am not doing it. The
label stands as written, because a validation study where the labels move after
you see the verdicts is not a validation study. The honest report is: judge
right, human wrong, one of my six UNSOUND-side calls was soft.

### `c25` - **I was right and the judge was wrong, twice, the second time with the answer in front of it**

Request: "the loaf", gluten free. Ambiguous. The context came back with all four
chunks of the **Gluten-Free Sandwich Loaf ranked above** the Lemon Drizzle Loaf
chunks. The app resolved "the loaf" to the Lemon Drizzle Loaf, then declined
because the archive has no gluten-free lemon drizzle.

Every word of that decline is true, which is why the judge passed it. It is
still UNSOUND: the assistant picked the one reading it could not serve while a
complete gluten-free loaf sat at rank 1 of its own context. This is Week-5 mode
4 - "says a figure is not in the context while a chunk on screen carries it" -
reappearing in a new surface.

The judge failed this in v1, was shown the correct verdict and the reasoning as
Example 2 in v2, and failed it again in the same words. **A judge that cannot
reproduce a verdict it has been handed cannot be trusted to find that class of
error unprompted.**

### Also worth recording: `c16`, unresolved

I labelled SOUND, the judge said UNSOUND both times. The app built a "Light Rye
Sourdough" from rye's flours with wholemeal's water, starter and salt - a recipe
on no card - but *declared* it in `unsupported`. I passed it for the disclosure.
The judge says a hybrid is a hybrid. I still lean to my label, and I flagged in
advance that I might be wrong. `c01` is the same hybrid **without** disclosure
and we both call it UNSOUND, so the disclosure is doing real work in my
labelling and none in the judge's.

---

## 7. What I would change next, and what this means for publishing

**The judge is not fit to gate publication at 84%.** One in six substitutions
gets a verdict I disagree with, and the residual disagreements are not noise -
they cluster on exactly the failure the food team cares about, a decline or an
answer that is locally true and globally wrong.

Next iteration, in priority order, and none of it is relabelling:

1. **Split the criterion.** c11 failed for two independent reasons and one fix
   moved neither. A judge answering "is every claim supported?" and "was
   declining correct?" as separate booleans would have shown the arithmetic fix
   landing on one of them.
2. **Give worked examples an explicit scope line.** Example 2 leaked a
   responsiveness rule. "This example is about criterion (b) and changes nothing
   about what counts as a claim" would likely recover c19.
3. **Stop trying to fix c25 with examples.** It survived being handed the answer.
   That class - decline accurate on its own framing, wrong against the full
   context list - probably needs a deterministic pre-check that lists every
   recipe_id in the context and asks the judge about each, rather than more
   prose.

### A correction to the Week 5 taxonomy

Pinning the model for this week failed with `429 RESOURCE_EXHAUSTED, quotaId
GenerateRequestsPerDayPerProjectPerModel-FreeTier, quotaValue 20`. **Twenty
requests per day, not per minute.** Re-reading the Week 5 log in that light:

```
calls   2- 19   gemini-3.6-flash        then never again
calls  20- 50   gemini-3.5-flash        (~18 calls) then never again
calls  51-150   gemini-3.1-flash-lite   carries the remaining 100
```

Week 5's mode 7 was not "whichever model is free this second". It is the daily
quota being spent in ladder order: **the first 20 questions of each day get the
best model and every question after gets a weaker one, silently, until
midnight.** [taxonomy.md](taxonomy.md) recorded the symptom correctly (18 of 20
sampled traces on a non-primary model) and the mechanism loosely. The Week 5
deliverable is left as written; this is the correction.

Everything this week ran on `gemini-3.1-flash-lite`, pinned, all 25
substitutions and both judge runs, verified by assertion A6. That discharges
part 1 of the Week 5 prediction (`618744c`). Part 2, the arithmetic rule, is
untouched and still open. flash-lite is the weakest model in the ladder and the
only one whose free-tier day can carry ~75 calls; a stronger judge might well
clear the c25 floor, and I cannot test that on this key.

---

## 8. BONUS - RAGAS faithfulness and context precision

Headline, because it is sharper than the thing the bonus asked for:

```
                        faithfulness   context precision
the 4 broken cases          1.000            1.000
the other 21                0.832            0.987
```

**The broken answers score higher than the healthy ones.** Not "the average hides
them" - they are the top of the distribution. No threshold on either metric, at
any value, separates them out, because the direction of the effect is backwards.

| deliverable | file |
|---|---|
| reference ground truth | [eval/ragas_reference.json](eval/ragas_reference.json) - commit `d4ccfac` |
| the two metrics | [eval/ragas_metrics.py](eval/ragas_metrics.py) |
| one command | `python eval/run_ragas.py` |
| scored output | [out/ragas.md](out/ragas.md), [out/ragas_scores.json](out/ragas_scores.json) |
| the run this replaced | [out/ragas_v1_decisionclaim.md](out/ragas_v1_decisionclaim.md) |

### 8.1 What is and is not RAGAS here

The two metrics are implemented against the published definitions rather than
imported from the `ragas` package, for two reasons worth stating rather than
burying: the library's faithfulness issues one verification call PER CLAIM, which
a 20-call free-tier day cannot survive, and its LLM plumbing defaults to a
different provider, which would mean this section came off a different instrument
than the rest of the week. Both formulas were stated independently by two readers
from the published definitions and cross-checked before a line was written; both
statements are kept at
[out/ragas_raw/formula_statements.json](out/ragas_raw/formula_statements.json).

Faithfulness keeps RAGAS's two-step shape, including the part that is easy to
collapse: **decomposition sees only (question, answer), never the context.** Show
it the context and the model can tailor which claims it extracts to whatever
happens to be supported. Verification then joins every chunk into one premise,
exactly as RAGAS does, and that single join is the whole reason the metric cannot
see attribution.

Context precision is the rank-aware average precision, with the three details
implementations get wrong: the `if v_k` gate, the denominator being relevants
FOUND rather than K, and the `+1e-10`. It reproduces the published worked examples
exactly, checked before it was pointed at any real data:

```
v=[1,0,1,1,0] -> 0.8055555555     v=[1,1,1,0,0] -> 0.9999999999
v=[0,0,1,1,1] -> 0.4777777778     v=[0,1]       -> 0.49999999995
```

One deviation, named: `v_k` is set by exact `recipe_id` membership rather than
RAGAS's Levenshtein-similarity-over-reference-contexts, because every chunk in
this corpus carries its `recipe_id` in the block header, so the thing string
similarity approximates is available exactly.

### 8.2 The reference is blind too, for the same reason the labels were

Context precision needs a per-case statement of which chunk counts as relevant.
Written after reading the app's answers, that is not a reference, it is a
rationalisation. So it got the labels' treatment: three readers, each given ONLY
the case list and the 21 cards, explicitly barred from `out/`, `labels_25.json`
and this write-up, and deliberately decorrelated by being made to work three
different ways (case-first, card-first, adversarial). Reconciled by per-recipe_id
majority, a rule fixed in `eval/build_ragas_reference.py` before it was applied.

**22 of 25 unanimous.** All three splits are recorded in the artefact rather than
smoothed away. All three readers independently flagged `c25` as ambiguous and all
three named the same donors, before any metric existed.

Ordering evidence: commit `d4ccfac`, whose message carries the terminal output of
`ls eval/run_ragas.py eval/ragas_metrics.py out/ragas.md` returning *No such file
or directory* for every one of them.

### 8.3 The instrument was wrong first, and reading its output is what caught it

The first run scored mean faithfulness **0.699** and flagged **0 of 25** cases.
Both numbers were artefacts.

`render_response` was turning `can_substitute: false` into the claim "The
requested substitution cannot be made." The NLI step then returned verdict 0 on
that claim in **25 cases out of 25**, with the same reason every time: *the
context does not mention a requested substitution.* It is right. The context is
recipe cards; it holds no representation of the user's request, so a claim about
the request is not something the cards can entail or contradict.

That is a constant -1 on every numerator. It moved every score down and
discriminated between none of them, and it pushed the exact cases this bonus
exists to find below the 0.9 threshold for a reason that has nothing to do with
grounding. `can_substitute` is a control-flow decision about the app's own
behaviour, not an assertion about recipes, so it is no longer rendered as a
claim. The decline's substance is `unsupported`, which is rendered and is
scorable.

```
                        mean faithfulness   cases flagged
v1  decision-as-claim         0.699             0 / 25
v2  corrected                 0.859             4 / 25
```

Both runs are kept. This is the week's own lesson landing on the week's own
bonus: the number was not wrong because the app was fine, it was wrong because
nobody had read what the judge was actually being asked.

### 8.4 The case the bonus asks for: `c25`

```
faithfulness      : 1.000   (4 of 4 claims entailed)
context precision : 1.000
grounded on       : lemon-drizzle-cake, at rank 5
walked past       : gf-sandwich-loaf, ranks 1-4 - Allergens, Ingredients, Title, Method
```

Request: "the loaf", made gluten free. The retrieved context opens with **all four
chunks of the Gluten-Free Sandwich Loaf**, the entire card, method included. The
app resolved "the loaf" to the Lemon Drizzle Loaf at rank 5 and declined, because
the archive has no gluten-free lemon drizzle.

Every sentence of that decline is true, so all four claims are entailed and
faithfulness is 1.000. Every retrieved chunk belongs to a card the reference calls
relevant, so context precision is 1.000. **Both metrics sit at their maximum on an
answer that declined with a complete gluten-free loaf at rank 1 of its own
context.**

This is the same case the judge failed in v1, was handed the correct verdict for
as Example 2 in v2, and failed again in the same words (section 6). Three
instruments now, none of which catches it.

### 8.5 Why neither metric can catch it, and what does

Not a tuning problem. Structural, and both formula readers reached it
independently:

* **Faithfulness** joins every chunk into ONE premise before judging. After the
  join there is no chunk identity left, so "supported by some chunk" and
  "supported by the RIGHT chunk" are the same event.
* **Context precision** never reads the answer at all. The with-reference variant
  does not even accept it. The score is identical whether the app grounded on
  rank 1, on rank 5, or answered nothing.

Each throws away exactly the axis the other would need, so running both cannot
recover it. Worse, on `c25` the good ranking *raises* the score: the metric
rewards the retriever for the very condition that makes the generation failure
worse.

What catches it costs nothing. No model call, no threshold:

```
declined_with_donor_on_screen = can_substitute is False
                                AND a reference donor card appears in the context
```

That is the judge's criterion (b) made deterministic, and it is the fourth thing
this week that belongs in `assertions.py` rather than in a prompt.

### 8.6 Where this is weak

**One of the four flags is a false positive, and I am not tuning it away.** `c23`
fires because `wholemeal-sourdough` is "on screen", but only its **Title** chunk
is, at rank 6. No hydration figure was retrieved, so the app's decline is correct
and the check is wrong. The check tests recipe_id presence, not whether the
retrieved chunk carries the evidence. Precision is therefore **3 of 4**, and the
fix (require a non-title section) is left for next week, because tightening a
check after seeing which case it embarrasses is the same move as relabelling
`c11` would have been.

The other three hold up on inspection: `c25` has the donor's full card including
Method at ranks 1-4, `c12` has the donor's Ingredients at rank 1 and Method at
rank 8, `c05` has the donor's Ingredients at rank 5.

Also still true: one labeller wrote the criterion, the labels and the reference,
and everything ran on `gemini-3.1-flash-lite`, the weakest model in the ladder.
The blind protocol and the commit order stand in for a second reader. They are not
a substitute for one.
