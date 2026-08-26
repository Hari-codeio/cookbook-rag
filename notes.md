# Week 5 - reading traces. Evidence, method, and the twenty sentences.

Companion to [taxonomy.md](taxonomy.md). Everything here is reproducible from the repo.

---

## 0. Where the trace file came from, stated plainly

The brief opens with "your trace file has grown past a thousand lines that nobody has
read." Mine had not, because **the app had no trace log at all**. Pretending otherwise
would have made every number below fiction, so here is the actual sequence, and the git
history is the proof of it:

| # | Commit | What happened |
|---|---|---|
| 1 | `bb55542` | Wrote `rag/trace.py`, wired it into `rag/generate.py`, and wrote 150 traffic questions by hand from the 21 cards. Committed **before a single trace existed**. |
| 2 | `ce9a870` | Wrote the sampler with the seed fixed in the file, and the replay harness. Committed **before the draw**. |
| 3 | - | Ran the 150 questions. 150 traces, 0 errors, 14.2 minutes. Then the 12 curated demo questions. |
| 4 | - | Drew the seeded samples. |
| 5 | `e8efaa3` | Replayed one trace, found the one field that was missing, added it. **Before open-coding started.** |
| 6 | - | Read all 20 by hand. **Zero commits during this step - see section 5.** |

The ordering matters because two of the three ways to fake this exercise are ruled out by
it. The questions could not have been chosen to match failures that had not happened yet,
and the seed could not have been chosen after seeing which twenty traces it would give me.

### What the log actually is

```
out/traces.jsonl     1,303,661 bytes    163 traces, one JSON object per line
                     sha256 e58151f7a61b69accc754641931496afb2d1695861a5282c6d9c284700317520
  random-traffic     150   the week's traffic, the population the sample of 20 is drawn from
  curated-demo        12   the golden set, for the bonus
  schema-1.1-proof     1   one trace written after the tracer fix, see section 4
```

**Honest limitation, stated up front.** These are real traces of the real shipped app
answering real questions, but the *questions* are mine, not a live user's. The mix (45
lookups, 21 method, 15 scaling, 12 substitution, 12 allergen, 12 comparison, 10
underspecified, 8 conversion, 8 technique, 7 out-of-scope) is my estimate of what a food
editor's week looks like, not measured demand. **Every frequency in taxonomy.md is
conditional on that mix.** If real users ask twice as many scaling questions as I did,
mode 1 is twice as common. What the sample *does* establish honestly is which failures
exist and what they look like, and that the traces of a given shape fail consistently.

The shipped configuration was constant for all 163 traces: `strategy=structure`,
`retriever=dense`, `k=5`, both refusal gates on, prompt `grounded-recipe-v1`. That is what
Week 4 concluded with, the cross-encoder having won one question in twelve for 3.4x
latency and not been shipped.

---

## 1. What the old record had, and what tracing had to add

The app's pre-existing record was `out/answer_eval_before.md`, a markdown transcript. It is
readable, and it is not replayable. You cannot re-run a markdown table.

| Field | In the old markdown? | In a trace |
|---|---|---|
| question | yes | `request.query` |
| retrieved chunk_ids | yes, top-3 ids only | `retrieval.hits[].chunk_id` |
| retrieval **scores** | no | `retrieval.hits[].score` and `.distance` |
| the retrieved chunk **text** | no | `retrieval.hits[].text` + sha256 |
| **prompt version** | no | `prompt.version`, `prompt.sha256`, full `prompt.system_text` |
| **model** | in a header, for the whole run | `model.name`, per call |
| **model params** | no | `model.params` (temperature, max tokens, mime type, thinking budget) |
| **raw output** | no, only the rendered answer | `output.raw_text`, before parsing |
| parsed output | partly | `output.parsed` |
| gate verdicts | prose | `gates.refused`, `.refusal_reason`, `.notes[]` |
| tokens | no | `usage.input_tokens` / `.output_tokens` |
| latency | no | `usage.model_latency_ms` |
| trace_id | **no** | `trace_id` |

The last row is the one that mattered most. Without a stable id there is nothing to draw a
random sample *of*.

One deliberate omission: the trace does **not** store the context string, only
`context.sha256`. The replay harness has to rebuild the context from the stored hits and
match that hash. Storing the string would have proved only that a string was stored.

---

## 2. Requirement 1 - replay evidence

Trace picked at random by trace_id, **seed `20260826`**:

```
random.Random(20260826).choice(sorted(trace_ids where source == "random-traffic"))
  -> tr_cd5496e418be
```

Reproduce with `python eval/replay_trace.py --pick-seeded --seed 20260826 --repeats 3`.
Full output in `out/replay_tr_cd5496e418be.md`.

**The replay is not allowed to cheat.** Before it starts, `eval/replay_trace.py` replaces
`rag.store.search`, `rag.store.get_collection` and `rag.store.get_chunk` with functions
that raise. If any part of the replay path reaches for the index, the run dies instead of
producing a comfortable result.

```
trace_id     : tr_cd5496e418be
picked by    : random.Random(20260826).choice(sorted(trace_ids where source=random-traffic))
logged at    : 2026-08-26T02:25:13+00:00
query        : 'what size tin for the lemon drizzle'
trace schema : 1.0
code git sha : bb55542

RECONSTRUCTION (nothing below reads the index - it is sealed shut)
  system prompt    MATCH   65d70be1520bcfbd  vs recorded 65d70be1520bcfbd
  context          MATCH   a27855afbfc414f9  vs recorded a27855afbfc414f9
  user turn        MATCH   b0eb25df6800b0cc  vs recorded b0eb25df6800b0cc
  response schema  GAP     NOT in the trace; recovered from rag/generate.py, sha matches

MODEL AND PARAMS, AS RECORDED
  provider          : gemini
  model             : gemini-3.1-flash-lite
  temperature       : 0.0
  max_output_tokens : 4096
  response_mime_type: 'application/json'
  thinking_budget   : None
  prompt version    : grounded-recipe-v1
```

### Original, as logged

```json
{
  "can_answer": true,
  "answer": "The lemon drizzle loaf should be baked in a 900 g loaf tin.",
  "claims": [
    {
      "claim": "The lemon drizzle loaf should be baked in a 900 g loaf tin.",
      "chunk_id": "lemon-drizzle-cake::structure::c002"
    }
  ],
  "missing": ""
}
```

### Replayed, three times

```
REPLAY 1 of 3 - byte-identical to the original: True
REPLAY 2 of 3 - byte-identical to the original: True
REPLAY 3 of 3 - byte-identical to the original: True
  tokens in/out original=1199/102  replay=1199/102   (all three runs)
```

All three replays returned the identical JSON above, character for character, with the
same token counts. Reproduced at temperature 0 against the same model.

### The field that was missing, and what I did about it

**Missing: the response schema itself.** Trace schema 1.0 recorded
`model.params.response_schema_sha256` but not the schema. The hash proves *which* schema
was used and cannot *produce* it, so the harness had to open `rag/generate.py` to get it.
The replay was therefore verified but not self-contained.

Found by running the harness, not by reading the code. That is the argument for building
the replay tool before you think you need it.

**Fixed in `e8efaa3`:** trace schema 1.1 stores `model.params.response_schema` inline.
Proof, on the same question:

```
trace_id     : tr_815107f4c299
trace schema : 1.1
  system prompt    MATCH   65d70be1520bcfbd  vs recorded 65d70be1520bcfbd
  context          MATCH   a27855afbfc414f9  vs recorded a27855afbfc414f9
  user turn        MATCH   b0eb25df6800b0cc  vs recorded b0eb25df6800b0cc
  response schema  MATCH   taken from the trace
REPLAY 1 of 1 - byte-identical to the original: True
```

The 20 sampled traces are 1.0 and stay 1.0. They were frozen on disk before the fix, and
rewriting them would have destroyed the sample.

### What I still cannot reconstruct

1. **The exact model build.** The trace records `gemini-3.1-flash-lite`, an alias. Google
   can move it behind my back. Byte-identical replays today prove nothing about next
   month, and there is no weights digest in the API to pin.
2. **Which model *would* have answered.** `tr_cd5496e418be` was served by flash-lite only
   because 3.6-flash and 3.5-flash were both rate-limited at that second. The trace records
   the fallback chain but the rate-limit state is gone. Replaying now takes a different
   path through the model list.
3. **Provider-side non-determinism.** Three identical replays are evidence, not a
   guarantee. Temperature 0 constrains sampling, not the serving stack.
4. **Wall-clock conditions.** `usage.model_latency_ms` is recorded but not reproducible;
   it was a fact about Google's load that minute.

---

## 3. Requirement 2 - the seeded random sample

```
seed                : 20260826          (today's date; fixed in eval/sample_traces.py,
                                         committed in ce9a870 BEFORE the draw)
source              : random-traffic     (the 150; the 12 demo traces are excluded)
population          : 150 traces
population sha256   : cc2e3b39ec248a6678bcbca9ff7ac362df4e091ad0497a27a9d821ac3984e39b
sampler             : random.Random(seed).sample(sorted(population), 20)
python              : 3.13.5
trace file sha256   : 4e92554c65bcbca16a2d4a6541ec2149675383c246a6b2c4a49efdfc9c7804ba
                      (162 traces, the state of the file AT THE MOMENT OF THE DRAW)
```

That hash is not the hash of `out/traces.jsonl` as committed, and the difference is
accounted for: one trace was appended after the draw, `tr_815107f4c299`, the schema-1.1
replay proof from section 2. The file went 162 -> 163 traces and
`4e92554c…` -> `e58151f7…`. The **population** hash `cc2e3b39…` is over the 150
`random-traffic` trace_ids only and is unchanged by that append, which is why `--verify`
still passes and the twenty below are still the twenty that were drawn.

The population is sorted by `trace_id` before drawing, so the result does not depend on
the order lines happen to sit in the file. Seed plus population hash plus n determines the
output completely: publish those three and anyone can reproduce the exact twenty without
my machine. Verify with
`python eval/sample_traces.py --source random-traffic --n 20 --verify` (prints `VERIFY OK`).

`sample_traces.py` refuses to overwrite an existing sample file, so a redraw has to be a
deliberate, visible act rather than a quiet re-roll.

**The twenty:**

```
 1. tr_0cb1bb28c42e     11. tr_4796cf8933c6
 2. tr_0f7e2efe3af5     12. tr_5c8a45d5f1f9
 3. tr_2343f31d8926     13. tr_6124bcab3fcb
 4. tr_2c6154629bb2     14. tr_86368b7412b3
 5. tr_3228dac28a01     15. tr_b16917339414
 6. tr_3414b9769de5     16. tr_b2c78a0e952e
 7. tr_351be2af8a72     17. tr_cd5496e418be
 8. tr_36b913af218a     18. tr_e76c2f033e24
 9. tr_39a45c43e005     19. tr_f0918dcbd36b
10. tr_3c28c307492f     20. tr_f7e8565ee4fc
```

What the draw happened to give me, which I did not choose: 6 lookups, 3 scaling, 2
comparison, 2 method, 1 conversion, 1 substitution, 1 allergen, 1 technique, 1
underspecified, and 2 more lookups. Rendered for reading in `out/sample_render_20.md` by
`eval/show_trace.py`, which has no answer key and no notion of a failure mode, so it
cannot leak a category into the reading step.

---

## 4. Requirement 3 - twenty open-coding sentences, one per trace

Written while reading `out/sample_render_20.md`, in the sampled order, one sentence each,
describing what I saw. Quantities were checked against the source cards in `data/`, so
"matches the card" is a thing I verified rather than assumed.

1. **`tr_0cb1bb28c42e`** (*how long do i leave the kefir*) - Answered "leave at 22 C for twenty-four hours" and added the twelve-hour second ferment, both cited to the milk kefir method chunk, and both figures appear on that card.

2. **`tr_0f7e2efe3af5`** (*why do my pickles go soft*) - Gave the blossom-end enzyme as the cause, which is on the card word for word; the `answer` field carried only the cause, and the instruction to trim the blossom end appeared only in the citation line printed underneath.

3. **`tr_2343f31d8926`** (*make the shakshuka for 2 people instead of 4*) - Retrieval returned all five shakshuka chunks including both halves of the ten-row ingredient table, and the app returned `INSUFFICIENT_CONTEXT: the provided context does not contain instructions or information on how to scale the recipe for a different number of people`.

4. **`tr_2c6154629bb2`** (*is the chocolate brioche dairy free*) - Answered "No, the Chocolate Chip Brioche contains dairy" citing that recipe's own allergen chunk at rank 1, with two other brioches' allergen chunks also in context and not mixed in.

5. **`tr_3228dac28a01`** (*how much butter in the classic brioche*) - Answered 250 g of softened unsalted butter for the Classic Brioche, which matches the card; the cited table row also reads 50% and the answer did not repeat it.

6. **`tr_3414b9769de5`** (*how much fine sea salt in the 2kg country sourdough*) - Answered "18 g (1.8%)", matching the card and keeping the percentage, while the wholemeal sourdough's ingredient table carrying a different salt figure sat at rank 5 and did not appear in the answer.

7. **`tr_351be2af8a72`** (*what is 28 C in fahrenheit for the dough water*) - Refused with "the conversion of 28 C to Fahrenheit for the dough water is not provided in the context"; the five retrieved chunks were three brioche titles and two dough methods, top score 0.40, and I checked the context afterwards: the string "28 C" was not in it, the only temperatures present being 180 C, 24 C and 4 C.

8. **`tr_36b913af218a`** (*mustard seed dill pickles amount*) - Answered 5 g of yellow mustard seed, matching the card; the top-ranked chunk was the pickle allergen note that only says "contains mustard", the number came from the ingredient chunk ranked second, and the 0.5% in that same row was not repeated.

9. **`tr_39a45c43e005`** (*how much paprika in the shakshuka*) - Answered 6 g of sweet paprika, matching the card, with all five retrieved chunks from that one recipe.

10. **`tr_3c28c307492f`** (*i want 3kg of sourdough not 2kg*) - Refused on the grounds that the context holds a 2kg and a wholemeal sourdough "but does not contain a recipe or instructions for 3kg of sourdough", with the 2kg card's complete five-row ingredient table sitting at rank 2 in that same context.

11. **`tr_4796cf8933c6`** (*how long does it ferment*) - Refused with "the question does not specify which recipe's fermentation time is requested" after retrieving five method chunks spanning four different recipes, and did not list the four or ask which one was meant.

12. **`tr_5c8a45d5f1f9`** (*how much yoghurt for the tikka marinade*) - Answered 250 g of full fat yoghurt, matching the card, cited to rows 1-8 of that card's thirteen-row ingredient table.

13. **`tr_6124bcab3fcb`** (*dark chocolate chips weight brioche*) - Answered 150 g of dark chocolate chips, matching the card; the query said only "brioche" and the app resolved it to the Chocolate Chip Brioche whose title chunk ranked first at 0.73, and the 30% in the cited row was not repeated.

14. **`tr_86368b7412b3`** (*koji amount white rice miso*) - Answered "1200 g (120%)" of short-grain rice koji, matching the card and keeping the percentage; all five chunks came from the miso card and scored 0.71 to 0.81, the highest scores anywhere in this sample.

15. **`tr_b16917339414`** (*how much xanthan gum if i use 250g flour blend*) - Refused with "the context does not contain information on how to scale the xanthan gum amount based on a specific weight of flour blend" while both gluten-free ingredient tables, each stating xanthan gum as both a gram weight and a percentage of flour, were in context; the call took 26 seconds and the gate notes show all four models rate-limited or overloaded, a 20-second sleep, then two more rate limits before flash-lite answered.

16. **`tr_b2c78a0e952e`** (*do the sourdoughs bake at the same temperature*) - Answered "No, the sourdoughs do not bake at the same temperature" and gave 250 C then 230 C for the 2kg and 240 C then 220 C for the wholemeal, both of which match their cards; the corpus holds three sourdoughs, the Light Rye card was not among the five retrieved chunks, and neither the answer nor the refusal machinery mentions that a third loaf exists.

17. **`tr_cd5496e418be`** (*what size tin for the lemon drizzle*) - Answered "900 g loaf tin", matching the card; the top-ranked chunk at 0.43 was that card's ingredient table and the tin size came from the method chunk ranked second.

18. **`tr_e76c2f033e24`** (*which loaf has the highest hydration*) - Refused, saying "the hydration percentages for the Wholemeal Sourdough and 2kg Country Sourdough recipes are not provided in the context"; those two appeared only as title chunks, and I then checked the fourth-ranked chunk, the Gluten-Free Sandwich Loaf ingredient table, which does carry a row reading `| Water (30 C) | 400 g | 80% |` that the refusal does not mention.

19. **`tr_f0918dcbd36b`** (*can i use greek yoghurt in the tikka masala*) - Refused with "the context does not specify if Greek yoghurt can be used; it only lists 'Full fat yoghurt' as an ingredient", after retrieving all five chunks of the correct recipe.

20. **`tr_f7e8565ee4fc`** (*how much starter in the rye sourdough*) - Answered 200 g of stiff sourdough starter for the Light Rye Sourdough, matching the card; the method chunk outranked the ingredient table, the figure came from the ingredient chunk at rank 2, and the 20% in that row was not repeated.

### Zero code changes during the reading

`git log` shows the last commit before the read was `e8efaa3` and the next commit after it
is the prediction. Nothing landed in between. Verify:

```bash
git log --oneline e8efaa3..HEAD    # the prediction commit, and nothing before it
```

The temptation was real and specific. At trace 15 the fix for the scaling refusals looked
like one sentence of prompt editing. Had I made it, traces 16 to 20 would have come from a
different app and the 20% in taxonomy.md would describe software that no longer exists.

### Counts I only worked out after all twenty sentences were written

```
refused                                      7 / 20   (35%)
answered                                    13 / 20   (65%)
every quantity stated matched its card      13 / 13   (100%)
served by a model other than the primary    18 / 20   (90%)
model latency                               1.1 s min, 2.9 s median, 26.1 s max
```

**The single most useful sentence in this document:** in twenty random traces, the app
never once stated a wrong quantity. The food editor's complaint, "it sometimes gets the
quantities wrong", is not what the log shows.

---

## 5. Requirement 4 - how the sentences became modes

Method, so it can be argued with. I laid the twenty sentences out and grouped by what the
app *did*, not by what I think causes it. Three sentences said "asked for a calculation,
got a refusal" (3, 10, 15) and a fourth was the same shape with the number supplied by the
user instead of the corpus (7), which became mode 1. Four sentences ended with the same
clause about a percentage sitting in the cited row and not being repeated (5, 8, 13, 20),
which I had written independently four times before noticing they were one thing; that is
mode 2. The remaining four failures (11, 16, 18, 19) refused to group with anything and
stayed as modes 3 to 6 at one trace each. Mode 7 came from the gate notes, which I had
been reading past until sentence 15 forced me to look at them.

Naming rule I held to: a mode name has to tell my manager what to go and look at. "Retrieval
issue" and "hallucination" are diagnoses wearing an observation's coat, and the diagnosis
is next week's job. "Gives the gram weight and drops the baker's percentage printed beside
it" names something you can go and see in `tr_f7e8565ee4fc` in thirty seconds.

**What I could not explain, and am not going to pretend I can.** In sentence 18 the app
refused a hydration question while an 80% water row was on screen at rank 4. I do not know
whether it read that chunk and rejected it as the wrong loaf, or did not read it. Nothing
in the trace distinguishes those. Same for sentence 7: I cannot tell whether the refusal
was because 28 C was absent from the context or because rule 3 forbids conversions, and
both are true at once.

Full table in [taxonomy.md](taxonomy.md).

---

## 6. Requirement 5 - the prediction

<a name="the-prediction"></a>

> **Dated 2026-08-26.** Committed as `POST_PREDICTION_HASH`, before any fix.

**Mode I will attack:** mode 1, *refuses to do the arithmetic with the ingredient table
already on screen*. Currently **4 / 20 = 20%** of the random sample.

**Why this one and not mode 7, which is nine times more frequent.** Mode 7 is a config
line, it is free, and it goes in the same change because without it no before/after number
means anything. It is not the interesting bet. Mode 3 is the only one that can ruin a dish
but it is 1 trace, and I will not spend a week on a 5% with an error bar wider than itself.

**The specific change, two parts:**

1. Pin `GEN_MODEL` to one model and raise on rate limit instead of falling back down the
   list, so the before and after are measured on the same model. This week 18/20 traces
   were served by something other than the configured primary.
2. Replace rule 3's blanket ban on arithmetic in `SYSTEM_PROMPT` with a narrow permission:
   the model may multiply every row of **one** cited ingredient table by **one** factor
   stated in the question, must print the factor it used, and must still refuse unit
   conversion, interpolation, and any arithmetic spanning two recipes.

**The numbers I expect, measured on a fresh sample of 20 drawn with seed `20260902` from a
new 150-trace run of the same locked question pool:**

| Measure | Now | After | I am wrong if |
|---|---|---|---|
| Mode 1 frequency | 20% (4/20) | **at most 5% (1/20)** | it is 2/20 or worse |
| Overall refusal rate | 35% (7/20) | **between 15% and 25%** | it is outside that band |
| Invented quantities | 0/20 | **0/20** | any answer states a gram weight that is neither in its cited chunk nor the product of the printed factor and a weight in that chunk |
| Traces on a non-primary model | 90% (18/20) | **0%** | any trace names a different model |

**The kill condition.** If even one invented quantity appears, the change is a net loss
whatever mode 1 does, and I revert it. Trading a refusal for a wrong gram weight in a
reader's dough is a bad trade at any frequency.

I am putting the risk in writing: I expect part 2 to leak. The prompt currently forbids
arithmetic in one absolute sentence, and absolute rules are the reason the app has never
stated a wrong quantity in 20 traces. Narrowing it to "one table, one factor" is exactly
the kind of hedge a model reads as permission, and my honest guess is a 30% chance the
kill condition fires and I report a reverted change next week.

---

## 7. Requirement 6 - why a public benchmark would have missed the top three

All three of my top modes are defined by the **shape of the question**, and a public
retrieval benchmark like MS MARCO or Natural Questions is built from questions that have
an answer written down somewhere in the corpus, so it contains no "halve this recipe", no
"convert this to Fahrenheit" and no "do they all bake at the same temperature", and a
benchmark cannot count a failure on a question it never asks.

A benchmark scores an answer against a reference string, which means both of my modes where
the app was **right but incomplete** would have scored as correct: mode 2 answered "200 g"
where the reference says 200 g, and mode 3's two bake temperatures both match their cards,
so an F1 or exact-match scorer sees two passes and my food editor sees a cook who cannot
scale the loaf and a comparison that silently left out a third of the corpus.

And a benchmark run pins one model and reports one number, so it could not have surfaced
the thing that shows up in 18 of my 20 traces, that the answering model was picked at
runtime by whichever one was not rate-limited that second, which means any benchmark score
I had quoted this week would have been a score for a system that existed for about four
seconds.

---

## 8. Bonus - the same reading, on the demo set

The recipes we show at reviews are the 12 golden-set questions in `eval/golden_set.jsonl`,
the ones in `DEMO.md`. Sampled 10 with the same seed `20260826`, population sha256
`acacf964787aca32a1a0f9304828dbf8b0752f529475e7f85d558b4f777638dc`. Rendered in
`out/sample_render_demo10.md`.

### Ten more open-coding sentences

1. **`tr_059e0df1746a`** (*amchur amount chana masala*) - Answered 6 g of amchur, matching the card, with all five retrieved chunks from that one recipe.
2. **`tr_0b7c7693e0c3`** (*salt in the rye sourdough*) - Answered 19 g of fine sea salt, matching the card; the cited row also reads 1.9% and the answer did not repeat it.
3. **`tr_184d7acc9c86`** (*how much xanthan gum in the gluten free brioche*) - Answered 6 g of xanthan gum, matching the card; the cited row also reads 1.2% and the answer did not repeat it.
4. **`tr_2802ae86300e`** (*psyllium husk amount*) - Refused with "the amount of psyllium husk is not specified in the provided context"; the five retrieved chunks were three red cabbage sauerkraut chunks, a shakshuka chunk and the gluten-free sandwich loaf's method, and that loaf's ingredient table, which carries the figure, was not among them.
5. **`tr_2c4fc3c1e36b`** (*xanthan for the gf sandwich loaf*) - Answered 10 g of xanthan gum, matching the card; the cited row also reads 2% and the answer did not repeat it.
6. **`tr_9fef61c54210`** (*why do pickles turn soft*) - Gave the blossom-end enzyme as the cause, and unlike the near-identical question in the random sample this answer contained no instruction to trim it, in either the answer or the citation line.
7. **`tr_a813163e87d6`** (*how much saeujeot in the kimchi*) - Answered 20 g of salted shrimp paste, matching the card; the cited row also reads 2% and the answer did not repeat it.
8. **`tr_c4f92ef1e7bd`** (*can i strain kefir with a metal sieve*) - Answered "No, you should strain the kefir through a nylon sieve, never metal", which is the card's phrasing.
9. **`tr_dc9fdef98a6b`** (*how much butter in the chocolate brioche*) - Answered 225 g of unsalted butter, matching the card, with two Classic Brioche chunks carrying a different butter figure also in context and not mixed in; the cited row's 45% was not repeated.
10. **`tr_eb298b6c77ee`** (*what temp do i bake the 2kg sourdough at*) - Answered the whole schedule, 250 C with steam for twenty minutes then 230 C for a further twenty-five, near-verbatim from the method chunk.

### The two numbers

| | Random sample of 20 | Curated demo set of 10 |
|---|---|---|
| **Mode 1** (refuses the arithmetic) | **20%** (4/20) | **0%** (0/10) |
| Mode 2 (drops the baker's percentage) | 20% (4/20) | **50%** (5/10) |
| Refusal rate | 35% (7/20) | 10% (1/10) |
| Quantities correct where stated | 13/13 | 9/9 |

### The paragraph

Mode 1 runs at 20% in random traffic and **0% in the demo set**, and the reason is not that
the demo recipes are better. It is that all ten demo questions have the same shape. Every
one names exactly one recipe and asks for one fact that is printed on that card, which is
the one question shape this app is genuinely good at. There is not a single scaling
request, unit conversion, substitution, cross-recipe comparison or unnamed-recipe question
anywhere in the demo set, so the demo cannot show mode 1 at any frequency, and it never
has. For a month we have been telling ourselves the assistant works because we watch it
pass a test we accidentally built to exclude everything it fails. The refusal rate we quote
in reviews is 10%; in random traffic it is 35%. And the second row of that table is worse,
because it is the part we could have caught: mode 2 runs at **50% in the demo set**, higher
than in random traffic, which means we have stood in front of the team and watched the app
drop the baker's percentage five times out of five and called it a pass, because the gram
weight was right and the gram weight is all we ever checked. The demo did not hide that
one. We just were not looking at it.

---

## 9. Reproducing everything here

```bash
PY=.venv/Scripts/python

$PY eval/run_traffic.py --set random          # 150 traces  -> out/traces.jsonl
$PY eval/run_traffic.py --set demo            # 12 traces
$PY eval/sample_traces.py --source random-traffic --n 20 --verify   # -> VERIFY OK
$PY eval/replay_trace.py --pick-seeded --seed 20260826 --repeats 3
$PY eval/show_trace.py --from-sample out/sample_random-traffic_20.json --out out/sample_render_20.md
$PY eval/trace_summary.py --out out/trace_summary.md
```

A re-run of `run_traffic.py` produces new traces with new trace_ids, so the sample of 20
above is reproducible from the committed `out/traces.jsonl`, not from a fresh run. That
file, its sha256, and both sample files are committed for exactly that reason.
