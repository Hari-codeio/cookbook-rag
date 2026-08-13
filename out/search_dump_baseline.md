# Search-only dump — strategy=baseline

```
embedding model : all-MiniLM-L6-v2 (chromadb ONNX DefaultEmbeddingFunction)   (identical for both strategies)
top-k           : 5
questions file  : eval/questions.json
questions sha256: 07436a98184885aa00ba0fe92a1046322e5e4ca05753c3546ae5676eb64c80e5
questions locked: 2026-08-13T01:56:59+00:00
chunk counts    : baseline=52, structure=70
generated       : 2026-08-13T02:46:10+00:00
```

### q1 — How much fine sea salt goes into the 2kg country sourdough?

```
expected recipe_id : sourdough-2kg
expected section   : ingredients table (fine sea salt row)
answer must contain: ['Fine sea salt', '18 g']
table-row question : True

1. score=0.5781  white-miso::baseline::c001
   section=~method  source_file=card-06-white-rice-miso.md
   | Fine sea salt | 130 g | 13% |
   | | Seed miso from a previous batch | 50 g | 5% |
   | | Soybean cooking liquid, reserved | 200 g | 20% |
   | 
   | ## Method
   | 
   | Soak the soybeans for eighteen hours, then simmer them until a bean crushes flat between
   | finger and thumb with no resistance at the core. Reserve the cooking liquid before draining
   | and let the beans cool to below 40 C, because anything hotter kills the koji.
   | 
   | Mash the beans coarsely, then work in the rice koji and the fine sea salt until the mixture
   | holds

2. score=0.5716  napa-kimchi::baseline::c001
   section=~ingredients  source_file=card-02-napa-kimchi.md
   | sea salt, for the dry brine | 40 g | 4% |
   | | Gochugaru (Korean chilli flakes) | 60 g | 6% |
   | | Daikon, julienned | 200 g | 20% |
   | | Glutinous rice porridge, cooled | 100 g | 10% |
   | | Fish sauce | 45 g | 4.5% |
   | | Salted shrimp paste (saeujeot) | 20 g | 2% |
   | | Garlic, grated | 30 g | 3% |
   | | Ginger, grated | 12 g | 1.2% |
   | 
   | ## Method
   | 
   | Quarter the cabbage lengthways and work the coarse sea salt between every leaf, heaviest at
   | the stem end. Leave it to weep for two hours, turning the quarters once, then

3. score=0.4322  classic-focaccia::baseline::c001
   section=~method  source_file=classic-focaccia.md
   | | 60 g | 6% |
   | | Fine sea salt | 20 g | 2% |
   | | Instant dried yeast | 8 g | 0.8% |
   | | Fresh rosemary, picked | 12 g | 1.2% |
   | | Flaky salt, for the top | 6 g | 0.6% |
   | 
   | ## Method
   | 
   | Whisk the yeast into the water and let it slacken for five minutes. Add the flour and mix
   | until no dry patches remain, then rest the dough uncovered for twenty minutes so the flour
   | hydrates fully.
   | 
   | Add the fine sea salt and half the olive oil, then work the dough with wet hands until it
   | tightens. Fold it in the bowl every

4. score=0.4282  dill-pickles::baseline::c001
   section=~method  source_file=card-03-half-sour-dill-pickles.md
   | | 70% |
   | | Coarse sea salt | 24 g | 2.4% |
   | | Fresh dill, flowering heads | 20 g | 2% |
   | | Garlic cloves, crushed | 15 g | 1.5% |
   | | Yellow mustard seed | 5 g | 0.5% |
   | | Black peppercorns | 4 g | 0.4% |
   | | Grape leaf, for tannin | 2 g | 0.2% |
   | 
   | ## Method
   | 
   | Dissolve the coarse sea salt in the filtered water and leave the brine to come to room
   | temperature. Trim the blossom end from every cucumber; the enzyme that lives there is what
   | turns a jar of pickles soft.
   | 
   | Lay the dill, garlic, mustard seed and

5. score=0.4271  sourdough-2kg::baseline::c000   <-- right recipe, but this chunk lacks the answer
   section=~header  source_file=card-01-country-sourdough-2kg.md
   | ---
   | recipe_id: sourdough-2kg
   | title: 2kg Country Sourdough
   | cuisine: european
   | dietary_tags: [vegan, dairy-free, nut-free]
   | ---
   | 
   | # 2kg Country Sourdough
   | 
   | A two-day naturally leavened loaf. Baker's percentages are relative to the total flour
   | weight of 1000 g, so the white and rye flours together make 100%.
   | 
   | ## Ingredients
   | 
   | | Ingredient | Weight | Baker's % |
   | | --- | --- | --- |
   | | Strong white bread flour | 950 g | 95% |
   | | Wholemeal rye flour | 50 g | 5% |
   | | Water (28 C) | 760 g | 76% |
   | | Stiff

VERDICT: MISS
```
### q2 — What hydration percentage does the 2kg country sourdough run at?

```
expected recipe_id : sourdough-2kg
expected section   : ingredients table (water row, baker's %)
answer must contain: ['Water', '76%']
table-row question : True

1. score=0.5085  sourdough-2kg::baseline::c000   <== HIT (contains the answer)
   section=~header  source_file=card-01-country-sourdough-2kg.md
   | ---
   | recipe_id: sourdough-2kg
   | title: 2kg Country Sourdough
   | cuisine: european
   | dietary_tags: [vegan, dairy-free, nut-free]
   | ---
   | 
   | # 2kg Country Sourdough
   | 
   | A two-day naturally leavened loaf. Baker's percentages are relative to the total flour
   | weight of 1000 g, so the white and rye flours together make 100%.
   | 
   | ## Ingredients
   | 
   | | Ingredient | Weight | Baker's % |
   | | --- | --- | --- |
   | | Strong white bread flour | 950 g | 95% |
   | | Wholemeal rye flour | 50 g | 5% |
   | | Water (28 C) | 760 g | 76% |
   | | Stiff

2. score=0.3686  milk-kefir::baseline::c000
   section=~header  source_file=card-05-milk-kefir.md
   | ---
   | recipe_id: milk-kefir
   | title: Milk Kefir
   | cuisine: caucasian
   | dietary_tags: [contains-dairy, vegetarian, gluten-free]
   | ---
   | 
   | # Milk Kefir
   | 
   | A continuous grain-cultured milk ferment. Percentages are relative to the milk weight of
   | 1000 g, one batch per day.
   | 
   | ## Ingredients
   | 
   | | Ingredient | Weight | Baker's % |
   | | --- | --- | --- |
   | | Whole cow's milk | 1000 g | 100% |
   | | Live kefir grains | 50 g | 5% |
   | | Lemon peel, for the second ferment | 5 g | 0.5% |
   | 
   | ## Method
   | 
   | Tip the live kefir grains into a

3. score=0.3608  milk-kefir::baseline::c001
   section=~method  source_file=card-05-milk-kefir.md
   | second ferment | 5 g | 0.5% |
   | 
   | ## Method
   | 
   | Tip the live kefir grains into a clean jar and pour the whole milk over them. Cover with
   | cloth rather than a sealed lid, because the grains need to breathe and the jar will build
   | pressure otherwise.
   | 
   | Leave at 22 C for twenty-four hours. The kefir is ready when it coats the side of the jar
   | and pulls away from the glass in one sheet; past that point it splits into curd and whey and
   | turns aggressively sour.
   | 
   | Strain through a nylon sieve, never metal, and

4. score=0.3220  sourdough-2kg::baseline::c001   <== HIT (contains the answer)
   section=~method  source_file=card-01-country-sourdough-2kg.md
   | Wholemeal rye flour | 50 g | 5% |
   | | Water (28 C) | 760 g | 76% |
   | | Stiff sourdough starter | 200 g | 20% |
   | | Fine sea salt | 18 g | 1.8% |
   | 
   | ## Method
   | 
   | Whisk the starter into the water until no lumps remain, then add both flours and mix to a
   | shaggy mass. Cover and autolyse for forty minutes. Hold the salt back at this stage: added
   | before the autolyse it tightens the gluten and the dough fights you for the rest of the day.
   | 
   | Sprinkle the fine sea salt over the rested dough and pinch it through

5. score=0.2839  dill-pickles::baseline::c000
   section=~header  source_file=card-03-half-sour-dill-pickles.md
   | ---
   | recipe_id: dill-pickles
   | title: Half-Sour Dill Pickles
   | cuisine: eastern-european
   | dietary_tags: [vegan, gluten-free, dairy-free]
   | ---
   | 
   | # Half-Sour Dill Pickles
   | 
   | A short brine ferment that keeps the cucumbers snapping. Percentages are relative to the
   | cucumber weight of 1000 g.
   | 
   | ## Ingredients
   | 
   | | Ingredient | Weight | Baker's % |
   | | --- | --- | --- |
   | | Small pickling cucumbers | 1000 g | 100% |
   | | Filtered water | 700 g | 70% |
   | | Coarse sea salt | 24 g | 2.4% |
   | | Fresh dill, flowering heads | 20 g

VERDICT: HIT at rank 1
```
### q3 — How much gochugaru goes into the napa cabbage kimchi?

```
expected recipe_id : napa-kimchi
expected section   : ingredients table (gochugaru row)
answer must contain: ['Gochugaru', '60 g']
table-row question : True

1. score=0.6959  napa-kimchi::baseline::c000   <-- right recipe, but this chunk lacks the answer
   section=~header  source_file=card-02-napa-kimchi.md
   | ---
   | recipe_id: napa-kimchi
   | title: Napa Cabbage Kimchi
   | cuisine: korean
   | dietary_tags: [contains-fish, contains-shellfish, gluten-free, dairy-free]
   | ---
   | 
   | # Napa Cabbage Kimchi
   | 
   | A cold-fermented winter kimchi. Percentages are relative to the trimmed cabbage weight of
   | 1000 g, not to the finished jar.
   | 
   | ## Ingredients
   | 
   | | Ingredient | Weight | Baker's % |
   | | --- | --- | --- |
   | | Napa cabbage, trimmed | 1000 g | 100% |
   | | Coarse sea salt, for the dry brine | 40 g | 4% |
   | | Gochugaru (Korean chilli flakes) |

2. score=0.5852  napa-kimchi::baseline::c002   <-- right recipe, but this chunk lacks the answer
   section=~method  source_file=card-02-napa-kimchi.md
   | the stem end. Leave it to weep for two hours, turning the quarters once, then rinse three
   | times and drain stem-down for thirty minutes.
   | 
   | Stir the gochugaru into the cooled rice porridge and let it bloom for ten minutes before
   | adding the daikon, fish sauce, shrimp paste, garlic and ginger. Paste every leaf, then pack
   | into the jar and press down until the brine rises above the vegetables.
   | 
   | Keep the vegetables submerged below the brine for the whole ferment. Leave at 18 C for two
   | days until the

3. score=0.5299  napa-kimchi::baseline::c001   <== HIT (contains the answer)
   section=~ingredients  source_file=card-02-napa-kimchi.md
   | sea salt, for the dry brine | 40 g | 4% |
   | | Gochugaru (Korean chilli flakes) | 60 g | 6% |
   | | Daikon, julienned | 200 g | 20% |
   | | Glutinous rice porridge, cooled | 100 g | 10% |
   | | Fish sauce | 45 g | 4.5% |
   | | Salted shrimp paste (saeujeot) | 20 g | 2% |
   | | Garlic, grated | 30 g | 3% |
   | | Ginger, grated | 12 g | 1.2% |
   | 
   | ## Method
   | 
   | Quarter the cabbage lengthways and work the coarse sea salt between every leaf, heaviest at
   | the stem end. Leave it to weep for two hours, turning the quarters once, then

4. score=0.4423  red-sauerkraut::baseline::c000
   section=~header  source_file=card-04-red-cabbage-sauerkraut.md
   | ---
   | recipe_id: red-sauerkraut
   | title: Red Cabbage Sauerkraut
   | cuisine: german
   | dietary_tags: [vegan, gluten-free, dairy-free]
   | ---
   | 
   | # Red Cabbage Sauerkraut
   | 
   | A dry-salted kraut that draws its own brine. Percentages are relative to the shredded
   | cabbage weight of 1000 g.
   | 
   | ## Ingredients
   | 
   | | Ingredient | Weight | Baker's % |
   | | --- | --- | --- |
   | | Red cabbage, finely shredded | 1000 g | 100% |
   | | Fine sea salt | 20 g | 2% |
   | | Grated apple | 80 g | 8% |
   | | Caraway seed | 6 g | 0.6% |
   | | Juniper berries | 4

5. score=0.4333  red-sauerkraut::baseline::c001
   section=~method  source_file=card-04-red-cabbage-sauerkraut.md
   | Grated apple | 80 g | 8% |
   | | Caraway seed | 6 g | 0.6% |
   | | Juniper berries | 4 g | 0.4% |
   | 
   | ## Method
   | 
   | Scatter the fine sea salt over the shredded cabbage and massage it hard for ten minutes.
   | The cabbage will collapse to roughly half its volume and a purple brine will pool in the
   | bowl; that liquid is the ferment, so none of it is thrown away.
   | 
   | Fold through the grated apple, caraway and juniper, then pack into the jar a fistful at a
   | time, tamping each layer until the brine rises above the

VERDICT: HIT at rank 3
```
### q4 — How much coarse sea salt do the half-sour dill pickles need?

```
expected recipe_id : dill-pickles
expected section   : ingredients table (coarse sea salt row)
answer must contain: ['Coarse sea salt', '24 g']
table-row question : True

1. score=0.7256  dill-pickles::baseline::c001   <== HIT (contains the answer)
   section=~method  source_file=card-03-half-sour-dill-pickles.md
   | | 70% |
   | | Coarse sea salt | 24 g | 2.4% |
   | | Fresh dill, flowering heads | 20 g | 2% |
   | | Garlic cloves, crushed | 15 g | 1.5% |
   | | Yellow mustard seed | 5 g | 0.5% |
   | | Black peppercorns | 4 g | 0.4% |
   | | Grape leaf, for tannin | 2 g | 0.2% |
   | 
   | ## Method
   | 
   | Dissolve the coarse sea salt in the filtered water and leave the brine to come to room
   | temperature. Trim the blossom end from every cucumber; the enzyme that lives there is what
   | turns a jar of pickles soft.
   | 
   | Lay the dill, garlic, mustard seed and

2. score=0.6497  dill-pickles::baseline::c000   <== HIT (contains the answer)
   section=~header  source_file=card-03-half-sour-dill-pickles.md
   | ---
   | recipe_id: dill-pickles
   | title: Half-Sour Dill Pickles
   | cuisine: eastern-european
   | dietary_tags: [vegan, gluten-free, dairy-free]
   | ---
   | 
   | # Half-Sour Dill Pickles
   | 
   | A short brine ferment that keeps the cucumbers snapping. Percentages are relative to the
   | cucumber weight of 1000 g.
   | 
   | ## Ingredients
   | 
   | | Ingredient | Weight | Baker's % |
   | | --- | --- | --- |
   | | Small pickling cucumbers | 1000 g | 100% |
   | | Filtered water | 700 g | 70% |
   | | Coarse sea salt | 24 g | 2.4% |
   | | Fresh dill, flowering heads | 20 g

3. score=0.5765  napa-kimchi::baseline::c001
   section=~ingredients  source_file=card-02-napa-kimchi.md
   | sea salt, for the dry brine | 40 g | 4% |
   | | Gochugaru (Korean chilli flakes) | 60 g | 6% |
   | | Daikon, julienned | 200 g | 20% |
   | | Glutinous rice porridge, cooled | 100 g | 10% |
   | | Fish sauce | 45 g | 4.5% |
   | | Salted shrimp paste (saeujeot) | 20 g | 2% |
   | | Garlic, grated | 30 g | 3% |
   | | Ginger, grated | 12 g | 1.2% |
   | 
   | ## Method
   | 
   | Quarter the cabbage lengthways and work the coarse sea salt between every leaf, heaviest at
   | the stem end. Leave it to weep for two hours, turning the quarters once, then

4. score=0.5597  white-miso::baseline::c001
   section=~method  source_file=card-06-white-rice-miso.md
   | Fine sea salt | 130 g | 13% |
   | | Seed miso from a previous batch | 50 g | 5% |
   | | Soybean cooking liquid, reserved | 200 g | 20% |
   | 
   | ## Method
   | 
   | Soak the soybeans for eighteen hours, then simmer them until a bean crushes flat between
   | finger and thumb with no resistance at the core. Reserve the cooking liquid before draining
   | and let the beans cool to below 40 C, because anything hotter kills the koji.
   | 
   | Mash the beans coarsely, then work in the rice koji and the fine sea salt until the mixture
   | holds

5. score=0.5554  dill-pickles::baseline::c002   <-- right recipe, but this chunk lacks the answer
   section=~method  source_file=card-03-half-sour-dill-pickles.md
   | e is what
   | turns a jar of pickles soft.
   | 
   | Lay the dill, garlic, mustard seed and peppercorns in the base of the jar, stand the
   | cucumbers upright on top, and tuck the grape leaf across the surface. Pour over the brine
   | and press down until the brine rises above the vegetables.
   | 
   | Keep the vegetables submerged below the brine for the whole ferment. Leave at 20 C for four
   | days, skimming any white bloom from the surface, then refrigerate while the cucumbers are
   | still translucent at the centre rather

VERDICT: HIT at rank 1
```
### q5 — How many grams of live kefir grains go into one litre of milk?

```
expected recipe_id : milk-kefir
expected section   : ingredients table (kefir grains row)
answer must contain: ['kefir grains', '50 g']
table-row question : True

1. score=0.6845  milk-kefir::baseline::c000   <== HIT (contains the answer)
   section=~header  source_file=card-05-milk-kefir.md
   | ---
   | recipe_id: milk-kefir
   | title: Milk Kefir
   | cuisine: caucasian
   | dietary_tags: [contains-dairy, vegetarian, gluten-free]
   | ---
   | 
   | # Milk Kefir
   | 
   | A continuous grain-cultured milk ferment. Percentages are relative to the milk weight of
   | 1000 g, one batch per day.
   | 
   | ## Ingredients
   | 
   | | Ingredient | Weight | Baker's % |
   | | --- | --- | --- |
   | | Whole cow's milk | 1000 g | 100% |
   | | Live kefir grains | 50 g | 5% |
   | | Lemon peel, for the second ferment | 5 g | 0.5% |
   | 
   | ## Method
   | 
   | Tip the live kefir grains into a

2. score=0.6278  milk-kefir::baseline::c001   <-- right recipe, but this chunk lacks the answer
   section=~method  source_file=card-05-milk-kefir.md
   | second ferment | 5 g | 0.5% |
   | 
   | ## Method
   | 
   | Tip the live kefir grains into a clean jar and pour the whole milk over them. Cover with
   | cloth rather than a sealed lid, because the grains need to breathe and the jar will build
   | pressure otherwise.
   | 
   | Leave at 22 C for twenty-four hours. The kefir is ready when it coats the side of the jar
   | and pulls away from the glass in one sheet; past that point it splits into curd and whey and
   | turns aggressively sour.
   | 
   | Strain through a nylon sieve, never metal, and

3. score=0.4780  milk-kefir::baseline::c002   <-- right recipe, but this chunk lacks the answer
   section=~method  source_file=card-05-milk-kefir.md
   | and
   | turns aggressively sour.
   | 
   | Strain through a nylon sieve, never metal, and stir the grains straight into fresh milk to
   | begin the next batch. For a second ferment, seal the strained kefir with the lemon peel and
   | leave it at room temperature for a further twelve hours.
   | 
   | ## Allergens
   | 
   | Contains dairy (cow's milk). Not lactose-free, although fermentation reduces the lactose
   | load. Not suitable for anyone with a milk protein allergy.

4. score=0.4715  sourdough-2kg::baseline::c000
   section=~header  source_file=card-01-country-sourdough-2kg.md
   | ---
   | recipe_id: sourdough-2kg
   | title: 2kg Country Sourdough
   | cuisine: european
   | dietary_tags: [vegan, dairy-free, nut-free]
   | ---
   | 
   | # 2kg Country Sourdough
   | 
   | A two-day naturally leavened loaf. Baker's percentages are relative to the total flour
   | weight of 1000 g, so the white and rye flours together make 100%.
   | 
   | ## Ingredients
   | 
   | | Ingredient | Weight | Baker's % |
   | | --- | --- | --- |
   | | Strong white bread flour | 950 g | 95% |
   | | Wholemeal rye flour | 50 g | 5% |
   | | Water (28 C) | 760 g | 76% |
   | | Stiff

5. score=0.3680  sourdough-2kg::baseline::c003
   section=~method  source_file=card-01-country-sourdough-2kg.md
   | ke straight from the fridge at 250 C with steam for twenty minutes, then vent the oven and
   | drop to 230 C for a further twenty-five minutes until the crust is deeply coloured.
   | 
   | ## Allergens
   | 
   | Contains wheat and rye (gluten). Made in a kitchen that also handles sesame and tree nuts.

VERDICT: HIT at rank 1
```
### q6 — How long does the red cabbage sauerkraut ferment, and at what temperature?

```
expected recipe_id : red-sauerkraut
expected section   : method
answer must contain: ['three to four weeks', '18 C']
table-row question : False

1. score=0.5761  red-sauerkraut::baseline::c000   <-- right recipe, but this chunk lacks the answer
   section=~header  source_file=card-04-red-cabbage-sauerkraut.md
   | ---
   | recipe_id: red-sauerkraut
   | title: Red Cabbage Sauerkraut
   | cuisine: german
   | dietary_tags: [vegan, gluten-free, dairy-free]
   | ---
   | 
   | # Red Cabbage Sauerkraut
   | 
   | A dry-salted kraut that draws its own brine. Percentages are relative to the shredded
   | cabbage weight of 1000 g.
   | 
   | ## Ingredients
   | 
   | | Ingredient | Weight | Baker's % |
   | | --- | --- | --- |
   | | Red cabbage, finely shredded | 1000 g | 100% |
   | | Fine sea salt | 20 g | 2% |
   | | Grated apple | 80 g | 8% |
   | | Caraway seed | 6 g | 0.6% |
   | | Juniper berries | 4

2. score=0.5126  napa-kimchi::baseline::c001
   section=~ingredients  source_file=card-02-napa-kimchi.md
   | sea salt, for the dry brine | 40 g | 4% |
   | | Gochugaru (Korean chilli flakes) | 60 g | 6% |
   | | Daikon, julienned | 200 g | 20% |
   | | Glutinous rice porridge, cooled | 100 g | 10% |
   | | Fish sauce | 45 g | 4.5% |
   | | Salted shrimp paste (saeujeot) | 20 g | 2% |
   | | Garlic, grated | 30 g | 3% |
   | | Ginger, grated | 12 g | 1.2% |
   | 
   | ## Method
   | 
   | Quarter the cabbage lengthways and work the coarse sea salt between every leaf, heaviest at
   | the stem end. Leave it to weep for two hours, turning the quarters once, then

3. score=0.4910  red-sauerkraut::baseline::c001   <-- right recipe, but this chunk lacks the answer
   section=~method  source_file=card-04-red-cabbage-sauerkraut.md
   | Grated apple | 80 g | 8% |
   | | Caraway seed | 6 g | 0.6% |
   | | Juniper berries | 4 g | 0.4% |
   | 
   | ## Method
   | 
   | Scatter the fine sea salt over the shredded cabbage and massage it hard for ten minutes.
   | The cabbage will collapse to roughly half its volume and a purple brine will pool in the
   | bowl; that liquid is the ferment, so none of it is thrown away.
   | 
   | Fold through the grated apple, caraway and juniper, then pack into the jar a fistful at a
   | time, tamping each layer until the brine rises above the

4. score=0.4268  shakshuka::baseline::c000
   section=~ingredients  source_file=shakshuka.md
   | ---
   | recipe_id: shakshuka
   | title: Red Pepper Shakshuka
   | cuisine: middle-eastern
   | dietary_tags: [vegetarian, gluten-free, contains-egg]
   | ---
   | 
   | # Red Pepper Shakshuka
   | 
   | ## Ingredients
   | 
   | | Ingredient | Weight | Notes |
   | | --- | --- | --- |
   | | Red peppers | 450 g | deseeded, sliced |
   | | Brown onion | 200 g | sliced |
   | | Tinned plum tomatoes | 400 g | |
   | | Olive oil | 40 g | |
   | | Garlic | 15 g | sliced thin |
   | | Sweet paprika | 6 g | |
   | | Ground cumin | 4 g | |
   | | Fine sea salt | 8 g | |
   | | Eggs | 6 whole | room

5. score=0.4135  napa-kimchi::baseline::c000
   section=~header  source_file=card-02-napa-kimchi.md
   | ---
   | recipe_id: napa-kimchi
   | title: Napa Cabbage Kimchi
   | cuisine: korean
   | dietary_tags: [contains-fish, contains-shellfish, gluten-free, dairy-free]
   | ---
   | 
   | # Napa Cabbage Kimchi
   | 
   | A cold-fermented winter kimchi. Percentages are relative to the trimmed cabbage weight of
   | 1000 g, not to the finished jar.
   | 
   | ## Ingredients
   | 
   | | Ingredient | Weight | Baker's % |
   | | --- | --- | --- |
   | | Napa cabbage, trimmed | 1000 g | 100% |
   | | Coarse sea salt, for the dry brine | 40 g | 4% |
   | | Gochugaru (Korean chilli flakes) |

VERDICT: MISS
```
### q7 — Is the napa cabbage kimchi safe for someone with a shellfish allergy?

```
expected recipe_id : napa-kimchi
expected section   : allergens
answer must contain: ['shellfish', 'shrimp']
table-row question : False

1. score=0.6189  napa-kimchi::baseline::c000   <-- right recipe, but this chunk lacks the answer
   section=~header  source_file=card-02-napa-kimchi.md
   | ---
   | recipe_id: napa-kimchi
   | title: Napa Cabbage Kimchi
   | cuisine: korean
   | dietary_tags: [contains-fish, contains-shellfish, gluten-free, dairy-free]
   | ---
   | 
   | # Napa Cabbage Kimchi
   | 
   | A cold-fermented winter kimchi. Percentages are relative to the trimmed cabbage weight of
   | 1000 g, not to the finished jar.
   | 
   | ## Ingredients
   | 
   | | Ingredient | Weight | Baker's % |
   | | --- | --- | --- |
   | | Napa cabbage, trimmed | 1000 g | 100% |
   | | Coarse sea salt, for the dry brine | 40 g | 4% |
   | | Gochugaru (Korean chilli flakes) |

2. score=0.5615  napa-kimchi::baseline::c003   <== HIT (contains the answer)
   section=~allergens  source_file=card-02-napa-kimchi.md
   | d below the brine for the whole ferment. Leave at 18 C for two
   | days until the jar smells sour and fizzes when tapped, then move it to the fridge.
   | 
   | ## Allergens
   | 
   | Contains fish (fish sauce) and shellfish (salted shrimp paste). Not suitable for anyone with
   | a shellfish allergy. Gluten-free despite the name of the glutinous rice.

3. score=0.4605  napa-kimchi::baseline::c001   <-- right recipe, but this chunk lacks the answer
   section=~ingredients  source_file=card-02-napa-kimchi.md
   | sea salt, for the dry brine | 40 g | 4% |
   | | Gochugaru (Korean chilli flakes) | 60 g | 6% |
   | | Daikon, julienned | 200 g | 20% |
   | | Glutinous rice porridge, cooled | 100 g | 10% |
   | | Fish sauce | 45 g | 4.5% |
   | | Salted shrimp paste (saeujeot) | 20 g | 2% |
   | | Garlic, grated | 30 g | 3% |
   | | Ginger, grated | 12 g | 1.2% |
   | 
   | ## Method
   | 
   | Quarter the cabbage lengthways and work the coarse sea salt between every leaf, heaviest at
   | the stem end. Leave it to weep for two hours, turning the quarters once, then

4. score=0.4589  pad-thai::baseline::c003
   section=~allergens  source_file=pad-thai.md
   | ves so they stay crisp, and finish with the peanuts.
   | 
   | ## Allergens
   | 
   | Contains shellfish, egg, peanuts and fish. Naturally gluten free, but check the fish sauce
   | brand.

5. score=0.3799  red-sauerkraut::baseline::c002
   section=~method  source_file=card-04-red-cabbage-sauerkraut.md
   | a fistful at a
   | time, tamping each layer until the brine rises above the vegetables.
   | 
   | Keep the vegetables submerged below the brine for the whole ferment. Leave at 18 C for
   | three to four weeks, releasing the lid every few days for the first week. The colour shifts
   | from blue-purple to bright magenta as the acidity climbs, which is the clearest sign it is
   | working.
   | 
   | ## Allergens
   | 
   | No declared allergens. Made in a kitchen that also handles wheat, mustard and sesame.

VERDICT: HIT at rank 2
```
### q8 — At what temperature and for how long is the white rice miso fermented?

```
expected recipe_id : white-miso
expected section   : method
answer must contain: ['28 C', 'four to eight weeks']
table-row question : False

1. score=0.5578  white-miso::baseline::c000   <-- right recipe, but this chunk lacks the answer
   section=~header  source_file=card-06-white-rice-miso.md
   | ---
   | recipe_id: white-miso
   | title: White Rice Miso
   | cuisine: japanese
   | dietary_tags: [vegan, gluten-free, contains-soy]
   | ---
   | 
   | # White Rice Miso
   | 
   | A short-aged sweet shiro miso, heavy on koji and light on salt. Percentages are relative to
   | the dried soybean weight of 1000 g.
   | 
   | ## Ingredients
   | 
   | | Ingredient | Weight | Baker's % |
   | | --- | --- | --- |
   | | Dried soybeans | 1000 g | 100% |
   | | Short-grain rice koji | 1200 g | 120% |
   | | Fine sea salt | 130 g | 13% |
   | | Seed miso from a previous batch | 50 g | 5% |
   | |

2. score=0.5281  white-miso::baseline::c002   <== HIT (contains the answer)
   section=~method  source_file=card-06-white-rice-miso.md
   | sely, then work in the rice koji and the fine sea salt until the mixture
   | holds together when squeezed. Slacken with the reserved cooking liquid a little at a time.
   | 
   | Press the paste into the crock in fistfuls, knocking out air pockets as you go, and smooth
   | the surface flat. Smear the seed miso across the top, weight it, and ferment at 28 C for
   | four to eight weeks, which is short because the high koji ratio does the work quickly.
   | 
   | ## Allergens
   | 
   | Contains soy. Gluten-free provided the koji is grown

3. score=0.5256  congee::baseline::c001
   section=~method  source_file=congee.md
   | g | whites and greens separated |
   | | Light soy sauce | 20 g | |
   | | Toasted sesame oil | 10 g | |
   | | Fine sea salt | 6 g | |
   | | White pepper | 1 g | |
   | 
   | ## Method
   | 
   | Rinse the rice until the water runs clear, then freeze it for an hour if you have time — the
   | ice fractures the grains and they break down far faster.
   | 
   | Bring the rice, water, ginger coins and spring onion whites to a boil, then drop to the
   | barest simmer. Stir every ten minutes or so, scraping the base, for ninety minutes. The
   | grains should

4. score=0.4879  napa-kimchi::baseline::c002
   section=~method  source_file=card-02-napa-kimchi.md
   | the stem end. Leave it to weep for two hours, turning the quarters once, then rinse three
   | times and drain stem-down for thirty minutes.
   | 
   | Stir the gochugaru into the cooled rice porridge and let it bloom for ten minutes before
   | adding the daikon, fish sauce, shrimp paste, garlic and ginger. Paste every leaf, then pack
   | into the jar and press down until the brine rises above the vegetables.
   | 
   | Keep the vegetables submerged below the brine for the whole ferment. Leave at 18 C for two
   | days until the

5. score=0.4328  congee::baseline::c002
   section=~method  source_file=congee.md
   | ry ten minutes or so, scraping the base, for ninety minutes. The
   | grains should dissolve into a loose, pourable porridge that thickens as it cools.
   | 
   | Season with the salt, soy and white pepper at the end; salting early slows the grains from
   | breaking down. Finish each bowl with the sesame oil, the sliced greens and fresh ginger.
   | 
   | ## Allergens
   | 
   | Contains soy (soy sauce) and sesame. Use tamari to keep it gluten free.

VERDICT: HIT at rank 2
```