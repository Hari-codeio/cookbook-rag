# Generation — cited answers and forced refusals

```
model      : gemini-3.6-flash
effort     : medium
strategy   : structure
top-k      : 5
generated  : 2026-08-13T02:40:16+00:00
```

## The grounding prompt (gate 1), verbatim

Note what is absent: there is no 'if the context is insufficient, use your best
judgement' clause. Refusal is the required output, not a suggested one.

```text
You answer questions about a recipe archive using ONLY the CONTEXT blocks supplied in the user turn.

RULES

1. The CONTEXT blocks are the entire world. Nothing you know about cooking, baking, fermentation, food science, nutrition, or ingredients may enter your answer. If a fact is not in a CONTEXT block, it does not exist.

2. Every claim in `answer` must be supported by a chunk you cite in `claims`. Each `chunk_id` you cite must be copied character-for-character from a CONTEXT block header in THIS request. Never invent, guess, shorten, reformat, or construct a chunk_id.

3. Never state a weight, percentage, temperature, duration, hydration figure, or any other quantity unless it appears verbatim in a CONTEXT block. Do not convert units, do not do arithmetic, do not scale a recipe up or down, do not interpolate between two values, and do not estimate.

4. If the CONTEXT does not contain the answer, set `can_answer` to false, set `answer` to an empty string, leave `claims` empty, and write in `missing` the specific fact that is absent. This applies even when the context is close, related, about a similar recipe, or about the right recipe but the wrong detail.

5. A partially answerable question is not answerable. If any part of the requested fact is missing from CONTEXT, set `can_answer` to false.

6. Do not apologise, do not offer to help further, and do not suggest where the information might otherwise be found.
```

## 3 answerable questions — cited

### q1 — How much fine sea salt goes into the 2kg country sourdough?
*Known-correct source: sourdough-2kg / ingredients table (fine sea salt row)*

```text
Q (structure): How much fine sea salt goes into the 2kg country sourdough?

retrieved (top-5):
  1. sourdough-2kg::structure::c001  score=0.6028  section=ingredients
  2. sourdough-2kg::structure::c002  score=0.5790  section=method
  3. sourdough-2kg::structure::c004  score=0.5294  section=allergens
  4. sourdough-2kg::structure::c003  score=0.5048  section=method
  5. sourdough-2kg::structure::c000  score=0.4941  section=title

A:
  18 g of fine sea salt goes into the 2kg Country Sourdough.
  
    - 18 g of fine sea salt goes into the 2kg Country Sourdough.  [sourdough-2kg::structure::c001]

gates:
  - provider: gemini, model=gemini-3.6-flash
  - gate 2 (code): all 1 citation(s) were retrieved for this question and resolve in the store

citation resolution (each cited chunk_id looked up in the store):
  - sourdough-2kg::structure::c001 -> recipe_id=sourdough-2kg source_file=card-01-country-sourdough-2kg.md section=ingredients
      chunk text: Recipe: 2kg Country Sourdough (cuisine: european) / Section: Ingredients (rows 1-5 of 5) / | Ingredient | Weight | Baker's % | / | --- | --- | --- | / | Strong 
model: gemini-3.6-flash  stop_reason=FinishReason.STOP
```

### q3 — How much gochugaru goes into the napa cabbage kimchi?
*Known-correct source: napa-kimchi / ingredients table (gochugaru row)*

```text
Q (structure): How much gochugaru goes into the napa cabbage kimchi?

retrieved (top-5):
  1. napa-kimchi::structure::c003  score=0.7078  section=method
  2. napa-kimchi::structure::c002  score=0.7067  section=ingredients
  3. napa-kimchi::structure::c001  score=0.6689  section=ingredients
  4. napa-kimchi::structure::c000  score=0.5692  section=title
  5. napa-kimchi::structure::c004  score=0.5656  section=allergens

A:
  60 g of gochugaru goes into the napa cabbage kimchi.
  
    - 60 g of gochugaru goes into the napa cabbage kimchi.  [napa-kimchi::structure::c001]

gates:
  - provider: gemini, model=gemini-3.6-flash
  - gate 2 (code): all 1 citation(s) were retrieved for this question and resolve in the store

citation resolution (each cited chunk_id looked up in the store):
  - napa-kimchi::structure::c001 -> recipe_id=napa-kimchi source_file=card-02-napa-kimchi.md section=ingredients
      chunk text: Recipe: Napa Cabbage Kimchi (cuisine: korean) / Section: Ingredients (rows 1-8 of 9) / | Ingredient | Weight | Baker's % | / | --- | --- | --- | / | Napa cabbag
model: gemini-3.6-flash  stop_reason=FinishReason.STOP
```

### q7 — Is the napa cabbage kimchi safe for someone with a shellfish allergy?
*Known-correct source: napa-kimchi / allergens*

```text
Q (structure): Is the napa cabbage kimchi safe for someone with a shellfish allergy?

retrieved (top-5):
  1. napa-kimchi::structure::c004  score=0.7967  section=allergens
  2. napa-kimchi::structure::c003  score=0.6459  section=method
  3. napa-kimchi::structure::c001  score=0.5535  section=ingredients
  4. napa-kimchi::structure::c002  score=0.5258  section=ingredients
  5. pad-thai::structure::c005  score=0.4974  section=allergens

A:
  No, Napa Cabbage Kimchi is not suitable for anyone with a shellfish allergy because it contains shellfish (salted shrimp paste).
  
    - Napa Cabbage Kimchi contains shellfish (salted shrimp paste) and is not suitable for anyone with a shellfish allergy.  [napa-kimchi::structure::c004]

gates:
  - provider: gemini, model=gemini-3.6-flash
  - gate 2 (code): all 1 citation(s) were retrieved for this question and resolve in the store

citation resolution (each cited chunk_id looked up in the store):
  - napa-kimchi::structure::c004 -> recipe_id=napa-kimchi source_file=card-02-napa-kimchi.md section=allergens
      chunk text: Recipe: Napa Cabbage Kimchi (cuisine: korean) / Section: Allergens / Contains fish (fish sauce) and shellfish (salted shrimp paste). Not suitable for anyone wit
model: gemini-3.6-flash  stop_reason=FinishReason.STOP
```

## 3 out-of-corpus questions — must refuse

### R1 — What is the calorie and macronutrient breakdown per 100 g of the napa cabbage kimchi?

```text
Q (structure): What is the calorie and macronutrient breakdown per 100 g of the napa cabbage kimchi?

retrieved (top-5):
  1. napa-kimchi::structure::c002  score=0.6844  section=ingredients
  2. napa-kimchi::structure::c001  score=0.6236  section=ingredients
  3. napa-kimchi::structure::c000  score=0.6018  section=title
  4. napa-kimchi::structure::c003  score=0.5392  section=method
  5. napa-kimchi::structure::c004  score=0.5335  section=allergens

A:
  INSUFFICIENT_CONTEXT: the calorie and macronutrient breakdown per 100 g of the napa cabbage kimchi

gates:
  - provider: gemini, model=gemini-3.6-flash
  - gate 1 (prompt/schema): model set can_answer=false
model: gemini-3.6-flash  stop_reason=FinishReason.STOP
```

**Refused: YES**

### R2 — What is the live probiotic CFU count per gram of the milk kefir?

```text
Q (structure): What is the live probiotic CFU count per gram of the milk kefir?

retrieved (top-5):
  1. milk-kefir::structure::c001  score=0.5636  section=ingredients
  2. milk-kefir::structure::c000  score=0.5406  section=title
  3. milk-kefir::structure::c003  score=0.4426  section=allergens
  4. milk-kefir::structure::c002  score=0.4271  section=method
  5. sourdough-2kg::structure::c001  score=0.3763  section=ingredients

A:
  INSUFFICIENT_CONTEXT: The live probiotic CFU count per gram of the milk kefir is not provided in the context.

gates:
  - provider: gemini, model=gemini-3.6-flash
  - gate 1 (prompt/schema): model set can_answer=false
model: gemini-3.6-flash  stop_reason=FinishReason.STOP
```

**Refused: YES**

### R3 — What baker's percentage of caraway seed does the napa cabbage kimchi use?

```text
Q (structure): What baker's percentage of caraway seed does the napa cabbage kimchi use?

retrieved (top-5):
  1. napa-kimchi::structure::c002  score=0.7075  section=ingredients
  2. napa-kimchi::structure::c001  score=0.6166  section=ingredients
  3. napa-kimchi::structure::c000  score=0.6071  section=title
  4. napa-kimchi::structure::c003  score=0.5825  section=method
  5. napa-kimchi::structure::c004  score=0.5164  section=allergens

A:
  INSUFFICIENT_CONTEXT: The recipe does not contain caraway seed or its baker's percentage.

gates:
  - provider: gemini, model=gemini-3.6-flash
  - gate 1 (prompt/schema): model set can_answer=false
model: gemini-3.6-flash  stop_reason=FinishReason.STOP
```

**Refused: YES**

## Is the refusal an artefact of the code gate?

The same out-of-corpus question, re-run with gate 2 (the code gate) disabled.
If it still refuses, the refusal came from the prompt and schema alone.

```text
Q (structure): What is the calorie and macronutrient breakdown per 100 g of the napa cabbage kimchi?

retrieved (top-5):
  1. napa-kimchi::structure::c002  score=0.6844  section=ingredients
  2. napa-kimchi::structure::c001  score=0.6236  section=ingredients
  3. napa-kimchi::structure::c000  score=0.6018  section=title
  4. napa-kimchi::structure::c003  score=0.5392  section=method
  5. napa-kimchi::structure::c004  score=0.5335  section=allergens

A:
  INSUFFICIENT_CONTEXT: The calorie and macronutrient breakdown per 100 g of the napa cabbage kimchi is not provided in the context.

gates:
  - provider: gemini, model=gemini-3.6-flash
  - gate 1 (prompt/schema): model set can_answer=false
model: gemini-3.6-flash  stop_reason=FinishReason.STOP
```

**Refused with code gate OFF: YES — the prompt gate is doing the work**

## Bonus — precision vs completeness

**Question:** How much fine sea salt goes into the 2kg country sourdough, and at what point in the mix is it added?

The precision/completeness probe required by the bonus. The structure-aware ingredient chunk holds 'Fine sea salt | 18 g | 1.8%' with its title and table header, so it answers 'how much' exactly - and carries no method prose, so it cannot say when. The sourdough method deliberately states that the salt is held back until after the forty-minute autolyse, which lives in a different chunk entirely. The looser baseline window may straddle the table/method boundary and answer both halves less precisely.

### strategy = baseline

```text
Q (baseline): How much fine sea salt goes into the 2kg country sourdough, and at what point in the mix is it added?

retrieved (top-5):
  1. napa-kimchi::baseline::c001  score=0.5939  section=~ingredients
  2. white-miso::baseline::c001  score=0.5919  section=~method
  3. classic-focaccia::baseline::c001  score=0.4716  section=~method
  4. sourdough-2kg::baseline::c001  score=0.4529  section=~method
  5. dill-pickles::baseline::c001  score=0.4431  section=~method

context supplied to the model:
  --- napa-kimchi::baseline::c001 ---
  sea salt, for the dry brine | 40 g | 4% |
  | Gochugaru (Korean chilli flakes) | 60 g | 6% |
  | Daikon, julienned | 200 g | 20% |
  | Glutinous rice porridge, cooled | 100 g | 10% |
  | Fish sauce | 45 g | 4.5% |
  | Salted shrimp paste (saeujeot) | 20 g | 2% |
  | Garlic, grated | 30 g | 3% |
  | Ginger, grated | 12 g | 1.2% |
  
  ## Method
  
  Quarter the cabbage lengthways and work the coarse sea salt between every leaf, heaviest at
  the stem end. Leave it to weep for two hours, turning the quarters once, then
  --- white-miso::baseline::c001 ---
  Fine sea salt | 130 g | 13% |
  | Seed miso from a previous batch | 50 g | 5% |
  | Soybean cooking liquid, reserved | 200 g | 20% |
  
  ## Method
  
  Soak the soybeans for eighteen hours, then simmer them until a bean crushes flat between
  finger and thumb with no resistance at the core. Reserve the cooking liquid before draining
  and let the beans cool to below 40 C, because anything hotter kills the koji.
  
  Mash the beans coarsely, then work in the rice koji and the fine sea salt until the mixture
  holds
  --- classic-focaccia::baseline::c001 ---
  | 60 g | 6% |
  | Fine sea salt | 20 g | 2% |
  | Instant dried yeast | 8 g | 0.8% |
  | Fresh rosemary, picked | 12 g | 1.2% |
  | Flaky salt, for the top | 6 g | 0.6% |
  
  ## Method
  
  Whisk the yeast into the water and let it slacken for five minutes. Add the flour and mix
  until no dry patches remain, then rest the dough uncovered for twenty minutes so the flour
  hydrates fully.
  
  Add the fine sea salt and half the olive oil, then work the dough with wet hands until it
  tightens. Fold it in the bowl every
  --- sourdough-2kg::baseline::c001 ---
  Wholemeal rye flour | 50 g | 5% |
  | Water (28 C) | 760 g | 76% |
  | Stiff sourdough starter | 200 g | 20% |
  | Fine sea salt | 18 g | 1.8% |
  
  ## Method
  
  Whisk the starter into the water until no lumps remain, then add both flours and mix to a
  shaggy mass. Cover and autolyse for forty minutes. Hold the salt back at this stage: added
  before the autolyse it tightens the gluten and the dough fights you for the rest of the day.
  
  Sprinkle the fine sea salt over the rested dough and pinch it through
  --- dill-pickles::baseline::c001 ---
  | 70% |
  | Coarse sea salt | 24 g | 2.4% |
  | Fresh dill, flowering heads | 20 g | 2% |
  | Garlic cloves, crushed | 15 g | 1.5% |
  | Yellow mustard seed | 5 g | 0.5% |
  | Black peppercorns | 4 g | 0.4% |
  | Grape leaf, for tannin | 2 g | 0.2% |
  
  ## Method
  
  Dissolve the coarse sea salt in the filtered water and leave the brine to come to room
  temperature. Trim the blossom end from every cucumber; the enzyme that lives there is what
  turns a jar of pickles soft.
  
  Lay the dill, garlic, mustard seed and

A:
  The 2kg country sourdough recipe uses 18 g of fine sea salt. It is held back during the initial mix and forty-minute autolyse, and is then sprinkled over the rested dough and pinched through.
  
    - The 2kg country sourdough recipe uses 18 g of fine sea salt.  [sourdough-2kg::baseline::c001]
    - It is held back during the initial mix and forty-minute autolyse, and is then sprinkled over the rested dough and pinched through.  [sourdough-2kg::baseline::c001]

gates:
  - provider: gemini, model=gemini-3.6-flash
  - gate 2 (code): all 2 citation(s) were retrieved for this question and resolve in the store

citation resolution (each cited chunk_id looked up in the store):
  - sourdough-2kg::baseline::c001 -> recipe_id=sourdough-2kg source_file=card-01-country-sourdough-2kg.md section=~method
      chunk text: Wholemeal rye flour | 50 g | 5% | / | Water (28 C) | 760 g | 76% | / | Stiff sourdough starter | 200 g | 20% | / | Fine sea salt | 18 g | 1.8% | / ## Method / W
  - sourdough-2kg::baseline::c001 -> recipe_id=sourdough-2kg source_file=card-01-country-sourdough-2kg.md section=~method
      chunk text: Wholemeal rye flour | 50 g | 5% | / | Water (28 C) | 760 g | 76% | / | Stiff sourdough starter | 200 g | 20% | / | Fine sea salt | 18 g | 1.8% | / ## Method / W
model: gemini-3.6-flash  stop_reason=FinishReason.STOP
```

### strategy = structure

```text
Q (structure): How much fine sea salt goes into the 2kg country sourdough, and at what point in the mix is it added?

retrieved (top-5):
  1. sourdough-2kg::structure::c001  score=0.6213  section=ingredients
  2. sourdough-2kg::structure::c002  score=0.5691  section=method
  3. sourdough-2kg::structure::c004  score=0.5228  section=allergens
  4. napa-kimchi::structure::c001  score=0.5192  section=ingredients
  5. sourdough-2kg::structure::c000  score=0.4881  section=title

context supplied to the model:
  --- sourdough-2kg::structure::c001 ---
  Recipe: 2kg Country Sourdough (cuisine: european)
  Section: Ingredients (rows 1-5 of 5)
  | Ingredient | Weight | Baker's % |
  | --- | --- | --- |
  | Strong white bread flour | 950 g | 95% |
  | Wholemeal rye flour | 50 g | 5% |
  | Water (28 C) | 760 g | 76% |
  | Stiff sourdough starter | 200 g | 20% |
  | Fine sea salt | 18 g | 1.8% |
  --- sourdough-2kg::structure::c002 ---
  Recipe: 2kg Country Sourdough (cuisine: european)
  Section: Method
  Whisk the starter into the water until no lumps remain, then add both flours and mix to a
  shaggy mass. Cover and autolyse for forty minutes. Hold the salt back at this stage: added
  before the autolyse it tightens the gluten and the dough fights you for the rest of the day.
  
  Sprinkle the fine sea salt over the rested dough and pinch it through with wet hands until
  you can no longer feel grains. Bulk ferment at 24 C for four hours, folding the dough in the
  bowl every forty-five minutes for the first three.
  
  Divide, pre-shape, and rest for twenty minutes. Shape into two tight boules, seam side up in
  floured baskets, then cold retard at 4 C overnight for twelve to fourteen hours.
  --- sourdough-2kg::structure::c004 ---
  Recipe: 2kg Country Sourdough (cuisine: european)
  Section: Allergens
  Contains wheat and rye (gluten). Made in a kitchen that also handles sesame and tree nuts.
  --- napa-kimchi::structure::c001 ---
  Recipe: Napa Cabbage Kimchi (cuisine: korean)
  Section: Ingredients (rows 1-8 of 9)
  | Ingredient | Weight | Baker's % |
  | --- | --- | --- |
  | Napa cabbage, trimmed | 1000 g | 100% |
  | Coarse sea salt, for the dry brine | 40 g | 4% |
  | Gochugaru (Korean chilli flakes) | 60 g | 6% |
  | Daikon, julienned | 200 g | 20% |
  | Glutinous rice porridge, cooled | 100 g | 10% |
  | Fish sauce | 45 g | 4.5% |
  | Salted shrimp paste (saeujeot) | 20 g | 2% |
  | Garlic, grated | 30 g | 3% |
  --- sourdough-2kg::structure::c000 ---
  Recipe: 2kg Country Sourdough (cuisine: european)
  Section: Title
  # 2kg Country Sourdough
  
  A two-day naturally leavened loaf. Baker's percentages are relative to the total flour
  weight of 1000 g, so the white and rye flours together make 100%.

A:
  The recipe calls for 18 g of fine sea salt. It is held back during the initial mix and autolyse, then sprinkled over the rested dough after the forty-minute autolyse and pinched through with wet hands until grains can no longer be felt.
  
    - The recipe calls for 18 g of fine sea salt.  [sourdough-2kg::structure::c001]
    - It is held back during the initial mix and autolyse, then sprinkled over the rested dough after the forty-minute autolyse and pinched through with wet hands until grains can no longer be felt.  [sourdough-2kg::structure::c002]

gates:
  - provider: gemini, model=gemini-3.6-flash
  - gate 2 (code): all 2 citation(s) were retrieved for this question and resolve in the store

citation resolution (each cited chunk_id looked up in the store):
  - sourdough-2kg::structure::c001 -> recipe_id=sourdough-2kg source_file=card-01-country-sourdough-2kg.md section=ingredients
      chunk text: Recipe: 2kg Country Sourdough (cuisine: european) / Section: Ingredients (rows 1-5 of 5) / | Ingredient | Weight | Baker's % | / | --- | --- | --- | / | Strong 
  - sourdough-2kg::structure::c002 -> recipe_id=sourdough-2kg source_file=card-01-country-sourdough-2kg.md section=method
      chunk text: Recipe: 2kg Country Sourdough (cuisine: european) / Section: Method / Whisk the starter into the water until no lumps remain, then add both flours and mix to a 
model: gemini-3.6-flash  stop_reason=FinishReason.STOP
```
