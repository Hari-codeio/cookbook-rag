# Failure taxonomy - recipe assistant, week of 2026-08-26

Read by hand from a seeded random sample of **20 traces** drawn from 150 logged this week.
Seed `20260826`, population sha256 `cc2e3b39…`. Evidence and method in [notes.md](notes.md).

**The food editor's report is not what the traces show.** She said it "sometimes gets the
quantities wrong". In 20 random traces **every quantity the app stated was correct** and
matched its cited card. What it actually does is refuse (7/20) and under-answer.

| # | Failure mode | Count | % of 20 | Severity | Example trace_id |
|---|---|---|---|---|---|
| 1 | **Refuses to do the arithmetic with the ingredient table already on screen** - user asks to halve, triple or convert; the full table is in context; answer is `INSUFFICIENT_CONTEXT` | 4 | 20% | annoys the cook | `tr_b16917339414` |
| 2 | **Gives the gram weight and drops the baker's percentage printed beside it** - cites a row reading `200 g \| 20%`, says "200 g", never says 20% | 4 | 20% | annoys the cook | `tr_f7e8565ee4fc` |
| 3 | **Answers "do they all…" from only the cards that happened to be retrieved** - said "the sourdoughs" and compared two, corpus has three, third was never retrieved and never mentioned | 1 | 5% | **ruins the dish** | `tr_b2c78a0e952e` |
| 4 | **Says a figure is not in the context while a chunk on screen carries it** - refused "which loaf has the highest hydration" naming two loaves whose numbers were absent, ignoring the retrieved table with `Water \| 400 g \| 80%` | 1 | 5% | annoys the cook | `tr_e76c2f033e24` |
| 5 | **Refuses a swap question instead of quoting the ingredient the card does name** - "can I use Greek yoghurt" got a refusal, not "the card specifies full fat yoghurt, 250 g" | 1 | 5% | annoys the cook | `tr_f0918dcbd36b` |
| 6 | **Refuses when the question names no recipe, instead of asking which one** - "how long does it ferment" retrieved four different recipes and refused rather than listing them | 1 | 5% | annoys the cook | `tr_4796cf8933c6` |
| 7 | **The model that answers is whichever one is not rate-limited** - 4 different Gemini models served the week; one call waited 26 s through a full sweep | 18 | 90% | annoys the cook | `tr_b16917339414` |

Modes 1-6 are mutually exclusive and cover **12 of 20** traces. Mode 7 is orthogonal and
overlaps all of them. **8 of 20** traces show no cook-facing fault at all.

Severity is the brief's two-way split. Only mode 3 can put a wrong number in an oven: it
presents a partial comparison as a complete one. Modes 1, 2, 4, 5 and 6 all withhold
something the app was holding, which wastes the cook's time without spoiling food. Mode 7
costs the cook 26 seconds at worst; its real cost is that it makes every before/after
number the team quotes unreproducible.

Counts of 1 are one trace out of twenty. Modes 3-6 are real observations, but their 5% is
worth roughly "somewhere between 0% and 15%" and should not be used to order fixes on its
own.

**Attacking next:** mode 1. Dated, numbered, falsifiable prediction in
[notes.md](notes.md#the-prediction), committed as `POST_PREDICTION_HASH`.
