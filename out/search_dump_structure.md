# Search-only dump — strategy=structure

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

1. score=0.6028  sourdough-2kg::structure::c001   <== HIT (contains the answer)
   section=ingredients  source_file=card-01-country-sourdough-2kg.md
   | Recipe: 2kg Country Sourdough (cuisine: european)
   | Section: Ingredients (rows 1-5 of 5)
   | | Ingredient | Weight | Baker's % |
   | | --- | --- | --- |
   | | Strong white bread flour | 950 g | 95% |
   | | Wholemeal rye flour | 50 g | 5% |
   | | Water (28 C) | 760 g | 76% |
   | | Stiff sourdough starter | 200 g | 20% |
   | | Fine sea salt | 18 g | 1.8% |

2. score=0.5790  sourdough-2kg::structure::c002   <-- right recipe, but this chunk lacks the answer
   section=method  source_file=card-01-country-sourdough-2kg.md
   | Recipe: 2kg Country Sourdough (cuisine: european)
   | Section: Method
   | Whisk the starter into the water until no lumps remain, then add both flours and mix to a
   | shaggy mass. Cover and autolyse for forty minutes. Hold the salt back at this stage: added
   | before the autolyse it tightens the gluten and the dough fights you for the rest of the day.
   | 
   | Sprinkle the fine sea salt over the rested dough and pinch it through with wet hands until
   | you can no longer feel grains. Bulk ferment at 24 C for four hours, folding the dough in the
   | bowl every forty-five minutes for the first three.
   | 
   | Divide, pre-shape, and rest for twenty minutes. Shape into two tight boules, seam side up in
   | floured baskets, then cold retard at 4 C overnight for twelve to fourteen hours.

3. score=0.5294  sourdough-2kg::structure::c004   <-- right recipe, but this chunk lacks the answer
   section=allergens  source_file=card-01-country-sourdough-2kg.md
   | Recipe: 2kg Country Sourdough (cuisine: european)
   | Section: Allergens
   | Contains wheat and rye (gluten). Made in a kitchen that also handles sesame and tree nuts.

4. score=0.5048  sourdough-2kg::structure::c003   <-- right recipe, but this chunk lacks the answer
   section=method  source_file=card-01-country-sourdough-2kg.md
   | Recipe: 2kg Country Sourdough (cuisine: european)
   | Section: Method
   | Bake straight from the fridge at 250 C with steam for twenty minutes, then vent the oven and
   | drop to 230 C for a further twenty-five minutes until the crust is deeply coloured.

5. score=0.4941  sourdough-2kg::structure::c000   <-- right recipe, but this chunk lacks the answer
   section=title  source_file=card-01-country-sourdough-2kg.md
   | Recipe: 2kg Country Sourdough (cuisine: european)
   | Section: Title
   | # 2kg Country Sourdough
   | 
   | A two-day naturally leavened loaf. Baker's percentages are relative to the total flour
   | weight of 1000 g, so the white and rye flours together make 100%.

VERDICT: HIT at rank 1
```
### q2 — What hydration percentage does the 2kg country sourdough run at?

```
expected recipe_id : sourdough-2kg
expected section   : ingredients table (water row, baker's %)
answer must contain: ['Water', '76%']
table-row question : True

1. score=0.5476  sourdough-2kg::structure::c001   <== HIT (contains the answer)
   section=ingredients  source_file=card-01-country-sourdough-2kg.md
   | Recipe: 2kg Country Sourdough (cuisine: european)
   | Section: Ingredients (rows 1-5 of 5)
   | | Ingredient | Weight | Baker's % |
   | | --- | --- | --- |
   | | Strong white bread flour | 950 g | 95% |
   | | Wholemeal rye flour | 50 g | 5% |
   | | Water (28 C) | 760 g | 76% |
   | | Stiff sourdough starter | 200 g | 20% |
   | | Fine sea salt | 18 g | 1.8% |

2. score=0.5359  sourdough-2kg::structure::c000   <-- right recipe, but this chunk lacks the answer
   section=title  source_file=card-01-country-sourdough-2kg.md
   | Recipe: 2kg Country Sourdough (cuisine: european)
   | Section: Title
   | # 2kg Country Sourdough
   | 
   | A two-day naturally leavened loaf. Baker's percentages are relative to the total flour
   | weight of 1000 g, so the white and rye flours together make 100%.

3. score=0.4996  sourdough-2kg::structure::c002   <-- right recipe, but this chunk lacks the answer
   section=method  source_file=card-01-country-sourdough-2kg.md
   | Recipe: 2kg Country Sourdough (cuisine: european)
   | Section: Method
   | Whisk the starter into the water until no lumps remain, then add both flours and mix to a
   | shaggy mass. Cover and autolyse for forty minutes. Hold the salt back at this stage: added
   | before the autolyse it tightens the gluten and the dough fights you for the rest of the day.
   | 
   | Sprinkle the fine sea salt over the rested dough and pinch it through with wet hands until
   | you can no longer feel grains. Bulk ferment at 24 C for four hours, folding the dough in the
   | bowl every forty-five minutes for the first three.
   | 
   | Divide, pre-shape, and rest for twenty minutes. Shape into two tight boules, seam side up in
   | floured baskets, then cold retard at 4 C overnight for twelve to fourteen hours.

4. score=0.4920  sourdough-2kg::structure::c003   <-- right recipe, but this chunk lacks the answer
   section=method  source_file=card-01-country-sourdough-2kg.md
   | Recipe: 2kg Country Sourdough (cuisine: european)
   | Section: Method
   | Bake straight from the fridge at 250 C with steam for twenty minutes, then vent the oven and
   | drop to 230 C for a further twenty-five minutes until the crust is deeply coloured.

5. score=0.4594  sourdough-2kg::structure::c004   <-- right recipe, but this chunk lacks the answer
   section=allergens  source_file=card-01-country-sourdough-2kg.md
   | Recipe: 2kg Country Sourdough (cuisine: european)
   | Section: Allergens
   | Contains wheat and rye (gluten). Made in a kitchen that also handles sesame and tree nuts.

VERDICT: HIT at rank 1
```
### q3 — How much gochugaru goes into the napa cabbage kimchi?

```
expected recipe_id : napa-kimchi
expected section   : ingredients table (gochugaru row)
answer must contain: ['Gochugaru', '60 g']
table-row question : True

1. score=0.7078  napa-kimchi::structure::c003   <-- right recipe, but this chunk lacks the answer
   section=method  source_file=card-02-napa-kimchi.md
   | Recipe: Napa Cabbage Kimchi (cuisine: korean)
   | Section: Method
   | Quarter the cabbage lengthways and work the coarse sea salt between every leaf, heaviest at
   | the stem end. Leave it to weep for two hours, turning the quarters once, then rinse three
   | times and drain stem-down for thirty minutes.
   | 
   | Stir the gochugaru into the cooled rice porridge and let it bloom for ten minutes before
   | adding the daikon, fish sauce, shrimp paste, garlic and ginger. Paste every leaf, then pack
   | into the jar and press down until the brine rises above the vegetables.
   | 
   | Keep the vegetables submerged below the brine for the whole ferment. Leave at 18 C for two
   | days until the jar smells sour and fizzes when tapped, then move it to the fridge.

2. score=0.7067  napa-kimchi::structure::c002   <-- right recipe, but this chunk lacks the answer
   section=ingredients  source_file=card-02-napa-kimchi.md
   | Recipe: Napa Cabbage Kimchi (cuisine: korean)
   | Section: Ingredients (rows 9-9 of 9)
   | | Ingredient | Weight | Baker's % |
   | | --- | --- | --- |
   | | Ginger, grated | 12 g | 1.2% |

3. score=0.6689  napa-kimchi::structure::c001   <== HIT (contains the answer)
   section=ingredients  source_file=card-02-napa-kimchi.md
   | Recipe: Napa Cabbage Kimchi (cuisine: korean)
   | Section: Ingredients (rows 1-8 of 9)
   | | Ingredient | Weight | Baker's % |
   | | --- | --- | --- |
   | | Napa cabbage, trimmed | 1000 g | 100% |
   | | Coarse sea salt, for the dry brine | 40 g | 4% |
   | | Gochugaru (Korean chilli flakes) | 60 g | 6% |
   | | Daikon, julienned | 200 g | 20% |
   | | Glutinous rice porridge, cooled | 100 g | 10% |
   | | Fish sauce | 45 g | 4.5% |
   | | Salted shrimp paste (saeujeot) | 20 g | 2% |
   | | Garlic, grated | 30 g | 3% |

4. score=0.5692  napa-kimchi::structure::c000   <-- right recipe, but this chunk lacks the answer
   section=title  source_file=card-02-napa-kimchi.md
   | Recipe: Napa Cabbage Kimchi (cuisine: korean)
   | Section: Title
   | # Napa Cabbage Kimchi
   | 
   | A cold-fermented winter kimchi. Percentages are relative to the trimmed cabbage weight of
   | 1000 g, not to the finished jar.

5. score=0.5656  napa-kimchi::structure::c004   <-- right recipe, but this chunk lacks the answer
   section=allergens  source_file=card-02-napa-kimchi.md
   | Recipe: Napa Cabbage Kimchi (cuisine: korean)
   | Section: Allergens
   | Contains fish (fish sauce) and shellfish (salted shrimp paste). Not suitable for anyone with
   | a shellfish allergy. Gluten-free despite the name of the glutinous rice.

VERDICT: HIT at rank 3
```
### q4 — How much coarse sea salt do the half-sour dill pickles need?

```
expected recipe_id : dill-pickles
expected section   : ingredients table (coarse sea salt row)
answer must contain: ['Coarse sea salt', '24 g']
table-row question : True

1. score=0.6886  dill-pickles::structure::c002   <-- right recipe, but this chunk lacks the answer
   section=method  source_file=card-03-half-sour-dill-pickles.md
   | Recipe: Half-Sour Dill Pickles (cuisine: eastern-european)
   | Section: Method
   | Dissolve the coarse sea salt in the filtered water and leave the brine to come to room
   | temperature. Trim the blossom end from every cucumber; the enzyme that lives there is what
   | turns a jar of pickles soft.
   | 
   | Lay the dill, garlic, mustard seed and peppercorns in the base of the jar, stand the
   | cucumbers upright on top, and tuck the grape leaf across the surface. Pour over the brine
   | and press down until the brine rises above the vegetables.
   | 
   | Keep the vegetables submerged below the brine for the whole ferment. Leave at 20 C for four
   | days, skimming any white bloom from the surface, then refrigerate while the cucumbers are
   | still translucent at the centre rather than fully sour.

2. score=0.6656  dill-pickles::structure::c001   <== HIT (contains the answer)
   section=ingredients  source_file=card-03-half-sour-dill-pickles.md
   | Recipe: Half-Sour Dill Pickles (cuisine: eastern-european)
   | Section: Ingredients (rows 1-8 of 8)
   | | Ingredient | Weight | Baker's % |
   | | --- | --- | --- |
   | | Small pickling cucumbers | 1000 g | 100% |
   | | Filtered water | 700 g | 70% |
   | | Coarse sea salt | 24 g | 2.4% |
   | | Fresh dill, flowering heads | 20 g | 2% |
   | | Garlic cloves, crushed | 15 g | 1.5% |
   | | Yellow mustard seed | 5 g | 0.5% |
   | | Black peppercorns | 4 g | 0.4% |
   | | Grape leaf, for tannin | 2 g | 0.2% |

3. score=0.6279  dill-pickles::structure::c000   <-- right recipe, but this chunk lacks the answer
   section=title  source_file=card-03-half-sour-dill-pickles.md
   | Recipe: Half-Sour Dill Pickles (cuisine: eastern-european)
   | Section: Title
   | # Half-Sour Dill Pickles
   | 
   | A short brine ferment that keeps the cucumbers snapping. Percentages are relative to the
   | cucumber weight of 1000 g.

4. score=0.6166  dill-pickles::structure::c003   <-- right recipe, but this chunk lacks the answer
   section=allergens  source_file=card-03-half-sour-dill-pickles.md
   | Recipe: Half-Sour Dill Pickles (cuisine: eastern-european)
   | Section: Allergens
   | Contains mustard. No gluten, dairy or nut ingredients; made in a kitchen that also handles
   | wheat and sesame.

5. score=0.4461  napa-kimchi::structure::c001
   section=ingredients  source_file=card-02-napa-kimchi.md
   | Recipe: Napa Cabbage Kimchi (cuisine: korean)
   | Section: Ingredients (rows 1-8 of 9)
   | | Ingredient | Weight | Baker's % |
   | | --- | --- | --- |
   | | Napa cabbage, trimmed | 1000 g | 100% |
   | | Coarse sea salt, for the dry brine | 40 g | 4% |
   | | Gochugaru (Korean chilli flakes) | 60 g | 6% |
   | | Daikon, julienned | 200 g | 20% |
   | | Glutinous rice porridge, cooled | 100 g | 10% |
   | | Fish sauce | 45 g | 4.5% |
   | | Salted shrimp paste (saeujeot) | 20 g | 2% |
   | | Garlic, grated | 30 g | 3% |

VERDICT: HIT at rank 2
```
### q5 — How many grams of live kefir grains go into one litre of milk?

```
expected recipe_id : milk-kefir
expected section   : ingredients table (kefir grains row)
answer must contain: ['kefir grains', '50 g']
table-row question : True

1. score=0.6574  milk-kefir::structure::c001   <== HIT (contains the answer)
   section=ingredients  source_file=card-05-milk-kefir.md
   | Recipe: Milk Kefir (cuisine: caucasian)
   | Section: Ingredients (rows 1-3 of 3)
   | | Ingredient | Weight | Baker's % |
   | | --- | --- | --- |
   | | Whole cow's milk | 1000 g | 100% |
   | | Live kefir grains | 50 g | 5% |
   | | Lemon peel, for the second ferment | 5 g | 0.5% |

2. score=0.6534  milk-kefir::structure::c000   <-- right recipe, but this chunk lacks the answer
   section=title  source_file=card-05-milk-kefir.md
   | Recipe: Milk Kefir (cuisine: caucasian)
   | Section: Title
   | # Milk Kefir
   | 
   | A continuous grain-cultured milk ferment. Percentages are relative to the milk weight of
   | 1000 g, one batch per day.

3. score=0.5415  milk-kefir::structure::c002   <-- right recipe, but this chunk lacks the answer
   section=method  source_file=card-05-milk-kefir.md
   | Recipe: Milk Kefir (cuisine: caucasian)
   | Section: Method
   | Tip the live kefir grains into a clean jar and pour the whole milk over them. Cover with
   | cloth rather than a sealed lid, because the grains need to breathe and the jar will build
   | pressure otherwise.
   | 
   | Leave at 22 C for twenty-four hours. The kefir is ready when it coats the side of the jar
   | and pulls away from the glass in one sheet; past that point it splits into curd and whey and
   | turns aggressively sour.
   | 
   | Strain through a nylon sieve, never metal, and stir the grains straight into fresh milk to
   | begin the next batch. For a second ferment, seal the strained kefir with the lemon peel and
   | leave it at room temperature for a further twelve hours.

4. score=0.5085  milk-kefir::structure::c003   <-- right recipe, but this chunk lacks the answer
   section=allergens  source_file=card-05-milk-kefir.md
   | Recipe: Milk Kefir (cuisine: caucasian)
   | Section: Allergens
   | Contains dairy (cow's milk). Not lactose-free, although fermentation reduces the lactose
   | load. Not suitable for anyone with a milk protein allergy.

5. score=0.4280  sourdough-2kg::structure::c001
   section=ingredients  source_file=card-01-country-sourdough-2kg.md
   | Recipe: 2kg Country Sourdough (cuisine: european)
   | Section: Ingredients (rows 1-5 of 5)
   | | Ingredient | Weight | Baker's % |
   | | --- | --- | --- |
   | | Strong white bread flour | 950 g | 95% |
   | | Wholemeal rye flour | 50 g | 5% |
   | | Water (28 C) | 760 g | 76% |
   | | Stiff sourdough starter | 200 g | 20% |
   | | Fine sea salt | 18 g | 1.8% |

VERDICT: HIT at rank 1
```
### q6 — How long does the red cabbage sauerkraut ferment, and at what temperature?

```
expected recipe_id : red-sauerkraut
expected section   : method
answer must contain: ['three to four weeks', '18 C']
table-row question : False

1. score=0.7252  red-sauerkraut::structure::c002   <== HIT (contains the answer)
   section=method  source_file=card-04-red-cabbage-sauerkraut.md
   | Recipe: Red Cabbage Sauerkraut (cuisine: german)
   | Section: Method
   | Scatter the fine sea salt over the shredded cabbage and massage it hard for ten minutes.
   | The cabbage will collapse to roughly half its volume and a purple brine will pool in the
   | bowl; that liquid is the ferment, so none of it is thrown away.
   | 
   | Fold through the grated apple, caraway and juniper, then pack into the jar a fistful at a
   | time, tamping each layer until the brine rises above the vegetables.
   | 
   | Keep the vegetables submerged below the brine for the whole ferment. Leave at 18 C for
   | three to four weeks, releasing the lid every few days for the first week. The colour shifts
   | from blue-purple to bright magenta as the acidity climbs, which is the clearest sign it is
   | working.

2. score=0.6638  red-sauerkraut::structure::c001   <-- right recipe, but this chunk lacks the answer
   section=ingredients  source_file=card-04-red-cabbage-sauerkraut.md
   | Recipe: Red Cabbage Sauerkraut (cuisine: german)
   | Section: Ingredients (rows 1-5 of 5)
   | | Ingredient | Weight | Baker's % |
   | | --- | --- | --- |
   | | Red cabbage, finely shredded | 1000 g | 100% |
   | | Fine sea salt | 20 g | 2% |
   | | Grated apple | 80 g | 8% |
   | | Caraway seed | 6 g | 0.6% |
   | | Juniper berries | 4 g | 0.4% |

3. score=0.6401  red-sauerkraut::structure::c003   <-- right recipe, but this chunk lacks the answer
   section=allergens  source_file=card-04-red-cabbage-sauerkraut.md
   | Recipe: Red Cabbage Sauerkraut (cuisine: german)
   | Section: Allergens
   | No declared allergens. Made in a kitchen that also handles wheat, mustard and sesame.

4. score=0.5369  red-sauerkraut::structure::c000   <-- right recipe, but this chunk lacks the answer
   section=title  source_file=card-04-red-cabbage-sauerkraut.md
   | Recipe: Red Cabbage Sauerkraut (cuisine: german)
   | Section: Title
   | # Red Cabbage Sauerkraut
   | 
   | A dry-salted kraut that draws its own brine. Percentages are relative to the shredded
   | cabbage weight of 1000 g.

5. score=0.5053  napa-kimchi::structure::c003
   section=method  source_file=card-02-napa-kimchi.md
   | Recipe: Napa Cabbage Kimchi (cuisine: korean)
   | Section: Method
   | Quarter the cabbage lengthways and work the coarse sea salt between every leaf, heaviest at
   | the stem end. Leave it to weep for two hours, turning the quarters once, then rinse three
   | times and drain stem-down for thirty minutes.
   | 
   | Stir the gochugaru into the cooled rice porridge and let it bloom for ten minutes before
   | adding the daikon, fish sauce, shrimp paste, garlic and ginger. Paste every leaf, then pack
   | into the jar and press down until the brine rises above the vegetables.
   | 
   | Keep the vegetables submerged below the brine for the whole ferment. Leave at 18 C for two
   | days until the jar smells sour and fizzes when tapped, then move it to the fridge.

VERDICT: HIT at rank 1
```
### q7 — Is the napa cabbage kimchi safe for someone with a shellfish allergy?

```
expected recipe_id : napa-kimchi
expected section   : allergens
answer must contain: ['shellfish', 'shrimp']
table-row question : False

1. score=0.7967  napa-kimchi::structure::c004   <== HIT (contains the answer)
   section=allergens  source_file=card-02-napa-kimchi.md
   | Recipe: Napa Cabbage Kimchi (cuisine: korean)
   | Section: Allergens
   | Contains fish (fish sauce) and shellfish (salted shrimp paste). Not suitable for anyone with
   | a shellfish allergy. Gluten-free despite the name of the glutinous rice.

2. score=0.6459  napa-kimchi::structure::c003   <-- right recipe, but this chunk lacks the answer
   section=method  source_file=card-02-napa-kimchi.md
   | Recipe: Napa Cabbage Kimchi (cuisine: korean)
   | Section: Method
   | Quarter the cabbage lengthways and work the coarse sea salt between every leaf, heaviest at
   | the stem end. Leave it to weep for two hours, turning the quarters once, then rinse three
   | times and drain stem-down for thirty minutes.
   | 
   | Stir the gochugaru into the cooled rice porridge and let it bloom for ten minutes before
   | adding the daikon, fish sauce, shrimp paste, garlic and ginger. Paste every leaf, then pack
   | into the jar and press down until the brine rises above the vegetables.
   | 
   | Keep the vegetables submerged below the brine for the whole ferment. Leave at 18 C for two
   | days until the jar smells sour and fizzes when tapped, then move it to the fridge.

3. score=0.5535  napa-kimchi::structure::c001   <-- right recipe, but this chunk lacks the answer
   section=ingredients  source_file=card-02-napa-kimchi.md
   | Recipe: Napa Cabbage Kimchi (cuisine: korean)
   | Section: Ingredients (rows 1-8 of 9)
   | | Ingredient | Weight | Baker's % |
   | | --- | --- | --- |
   | | Napa cabbage, trimmed | 1000 g | 100% |
   | | Coarse sea salt, for the dry brine | 40 g | 4% |
   | | Gochugaru (Korean chilli flakes) | 60 g | 6% |
   | | Daikon, julienned | 200 g | 20% |
   | | Glutinous rice porridge, cooled | 100 g | 10% |
   | | Fish sauce | 45 g | 4.5% |
   | | Salted shrimp paste (saeujeot) | 20 g | 2% |
   | | Garlic, grated | 30 g | 3% |

4. score=0.5258  napa-kimchi::structure::c002   <-- right recipe, but this chunk lacks the answer
   section=ingredients  source_file=card-02-napa-kimchi.md
   | Recipe: Napa Cabbage Kimchi (cuisine: korean)
   | Section: Ingredients (rows 9-9 of 9)
   | | Ingredient | Weight | Baker's % |
   | | --- | --- | --- |
   | | Ginger, grated | 12 g | 1.2% |

5. score=0.4974  pad-thai::structure::c005
   section=allergens  source_file=pad-thai.md
   | Recipe: Prawn Pad Thai (cuisine: thai)
   | Section: Allergens
   | Contains shellfish, egg, peanuts and fish. Naturally gluten free, but check the fish sauce
   | brand.

VERDICT: HIT at rank 1
```
### q8 — At what temperature and for how long is the white rice miso fermented?

```
expected recipe_id : white-miso
expected section   : method
answer must contain: ['28 C', 'four to eight weeks']
table-row question : False

1. score=0.7067  white-miso::structure::c003   <== HIT (contains the answer)
   section=method  source_file=card-06-white-rice-miso.md
   | Recipe: White Rice Miso (cuisine: japanese)
   | Section: Method
   | Press the paste into the crock in fistfuls, knocking out air pockets as you go, and smooth
   | the surface flat. Smear the seed miso across the top, weight it, and ferment at 28 C for
   | four to eight weeks, which is short because the high koji ratio does the work quickly.

2. score=0.6067  white-miso::structure::c001   <-- right recipe, but this chunk lacks the answer
   section=ingredients  source_file=card-06-white-rice-miso.md
   | Recipe: White Rice Miso (cuisine: japanese)
   | Section: Ingredients (rows 1-5 of 5)
   | | Ingredient | Weight | Baker's % |
   | | --- | --- | --- |
   | | Dried soybeans | 1000 g | 100% |
   | | Short-grain rice koji | 1200 g | 120% |
   | | Fine sea salt | 130 g | 13% |
   | | Seed miso from a previous batch | 50 g | 5% |
   | | Soybean cooking liquid, reserved | 200 g | 20% |

3. score=0.6067  white-miso::structure::c002   <-- right recipe, but this chunk lacks the answer
   section=method  source_file=card-06-white-rice-miso.md
   | Recipe: White Rice Miso (cuisine: japanese)
   | Section: Method
   | Soak the soybeans for eighteen hours, then simmer them until a bean crushes flat between
   | finger and thumb with no resistance at the core. Reserve the cooking liquid before draining
   | and let the beans cool to below 40 C, because anything hotter kills the koji.
   | 
   | Mash the beans coarsely, then work in the rice koji and the fine sea salt until the mixture
   | holds together when squeezed. Slacken with the reserved cooking liquid a little at a time.

4. score=0.5474  white-miso::structure::c000   <-- right recipe, but this chunk lacks the answer
   section=title  source_file=card-06-white-rice-miso.md
   | Recipe: White Rice Miso (cuisine: japanese)
   | Section: Title
   | # White Rice Miso
   | 
   | A short-aged sweet shiro miso, heavy on koji and light on salt. Percentages are relative to
   | the dried soybean weight of 1000 g.

5. score=0.4887  white-miso::structure::c004   <-- right recipe, but this chunk lacks the answer
   section=allergens  source_file=card-06-white-rice-miso.md
   | Recipe: White Rice Miso (cuisine: japanese)
   | Section: Allergens
   | Contains soy. Gluten-free provided the koji is grown on rice rather than barley. Made in a
   | kitchen that also handles wheat and sesame.

VERDICT: HIT at rank 1
```