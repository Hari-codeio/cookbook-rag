# Search-only dump — strategy=structure

```
embedding model : all-MiniLM-L6-v2 (chromadb ONNX DefaultEmbeddingFunction)   (identical for both strategies)
top-k           : 5
questions file  : eval/questions.json
questions sha256: 5dc74b03fbf46ccbf1fbdbb6aff5a338d9e9e7053fef0b6dcaf71d1e0f1d8d27
questions locked: 2026-08-12T13:01:22+00:00
chunk counts    : baseline=30, structure=43
generated       : 2026-08-12T13:18:07+00:00
```

### q1 — How much fine sea salt is in the beef bourguignon?

```
expected recipe_id : beef-bourguignon
expected section   : ingredients table
answer must contain: ['Fine sea salt', '12 g']
table-row question : True

1. score=0.6925  beef-bourguignon::structure::c002   <== HIT (contains the answer)
   section=ingredients  source_file=beef-bourguignon.md
   | Recipe: Beef Bourguignon (cuisine: french)
   | Section: Ingredients (rows 9-12 of 12)
   | | Ingredient | Weight | Notes |
   | | --- | --- | --- |
   | | Tomato puree | 25 g | |
   | | Fine sea salt | 12 g | |
   | | Bay leaf | 2 leaves | |
   | | Thyme | 6 g | |

2. score=0.5897  beef-bourguignon::structure::c001   <-- right recipe, but this chunk lacks the answer
   section=ingredients  source_file=beef-bourguignon.md
   | Recipe: Beef Bourguignon (cuisine: french)
   | Section: Ingredients (rows 1-8 of 12)
   | | Ingredient | Weight | Notes |
   | | --- | --- | --- |
   | | Beef shin | 1200 g | cut into 5 cm pieces |
   | | Smoked bacon lardons | 200 g | |
   | | Red wine (Burgundy) | 750 g | one bottle |
   | | Beef stock | 400 g | |
   | | Button mushrooms | 300 g | |
   | | Shallots | 250 g | peeled, left whole |
   | | Carrot | 150 g | thick coins |
   | | Plain flour | 30 g | for dusting |

3. score=0.5756  beef-bourguignon::structure::c003   <-- right recipe, but this chunk lacks the answer
   section=method  source_file=beef-bourguignon.md
   | Recipe: Beef Bourguignon (cuisine: french)
   | Section: Method
   | Marinate the beef in the wine with the bay and thyme overnight in the fridge. Drain the meat
   | and reserve every drop of the wine.
   | 
   | Dry the beef thoroughly, dust with the flour, and brown it hard in batches — crowding the
   | pan is the single most common way to end up with grey stew. Render the lardons in the same
   | pot, then soften the shallots and carrot in the fat.
   | 
   | Return the beef, stir in the tomato puree, pour over the reserved wine and the stock, and
   | bring barely to a tremble. Cover and cook at 150 C for three hours. Add the mushrooms for
   | the final thirty minutes so they keep their shape. Season with the salt at the end, once the
   | liquid has reduced and concentrated.

4. score=0.5623  beef-bourguignon::structure::c000   <-- right recipe, but this chunk lacks the answer
   section=title  source_file=beef-bourguignon.md
   | Recipe: Beef Bourguignon (cuisine: french)
   | Section: Title
   | # Beef Bourguignon

5. score=0.5510  beef-bourguignon::structure::c004   <-- right recipe, but this chunk lacks the answer
   section=allergens  source_file=beef-bourguignon.md
   | Recipe: Beef Bourguignon (cuisine: french)
   | Section: Allergens
   | Contains wheat (gluten) from the flour dusting, and alcohol. No dairy.

VERDICT: HIT at rank 1
```
### q2 — What is the hydration percentage of the classic rosemary focaccia?

```
expected recipe_id : classic-focaccia
expected section   : ingredients table (water row, baker's %)
answer must contain: ['Water', '80%']
table-row question : True

1. score=0.6913  classic-focaccia::structure::c001   <== HIT (contains the answer)
   section=ingredients  source_file=classic-focaccia.md
   | Recipe: Classic Rosemary Focaccia (cuisine: italian)
   | Section: Ingredients (rows 1-7 of 7)
   | | Ingredient | Weight | Baker's % |
   | | --- | --- | --- |
   | | Strong white bread flour | 1000 g | 100% |
   | | Water (20 C) | 800 g | 80% |
   | | Extra virgin olive oil | 60 g | 6% |
   | | Fine sea salt | 20 g | 2% |
   | | Instant dried yeast | 8 g | 0.8% |
   | | Fresh rosemary, picked | 12 g | 1.2% |
   | | Flaky salt, for the top | 6 g | 0.6% |

2. score=0.6235  classic-focaccia::structure::c000   <-- right recipe, but this chunk lacks the answer
   section=title  source_file=classic-focaccia.md
   | Recipe: Classic Rosemary Focaccia (cuisine: italian)
   | Section: Title
   | # Classic Rosemary Focaccia
   | 
   | A slow-proved tray bread. Baker's percentages are relative to the total flour weight.

3. score=0.5677  classic-focaccia::structure::c002   <-- right recipe, but this chunk lacks the answer
   section=method  source_file=classic-focaccia.md
   | Recipe: Classic Rosemary Focaccia (cuisine: italian)
   | Section: Method
   | Whisk the yeast into the water and let it slacken for five minutes. Add the flour and mix
   | until no dry patches remain, then rest the dough uncovered for twenty minutes so the flour
   | hydrates fully.
   | 
   | Add the fine sea salt and half the olive oil, then work the dough with wet hands until it
   | tightens. Fold it in the bowl every thirty minutes for the first two hours.
   | 
   | Oil a deep tray generously, tip the dough in, and let it relax until it reaches the corners
   | on its own. Dimple it with flat fingers, scatter the rosemary and flaky salt, and bake at
   | 230 C for 22 to 25 minutes until the base sounds hollow.

4. score=0.5403  classic-focaccia::structure::c003   <-- right recipe, but this chunk lacks the answer
   section=allergens  source_file=classic-focaccia.md
   | Recipe: Classic Rosemary Focaccia (cuisine: italian)
   | Section: Allergens
   | Contains wheat (gluten). Made in a kitchen that also handles sesame.

5. score=0.2675  shakshuka::structure::c002
   section=ingredients  source_file=shakshuka.md
   | Recipe: Red Pepper Shakshuka (cuisine: middle-eastern)
   | Section: Ingredients (rows 9-10 of 10)
   | | Ingredient | Weight | Notes |
   | | --- | --- | --- |
   | | Eggs | 6 whole | room temperature |
   | | Flat leaf parsley | 15 g | to finish |

VERDICT: HIT at rank 1
```
### q3 — How much amchur goes into the chana masala?

```
expected recipe_id : chana-masala
expected section   : ingredients table
answer must contain: ['Amchur', '6 g']
table-row question : True

1. score=0.6174  chana-masala::structure::c002   <== HIT (contains the answer)
   section=ingredients  source_file=chana-masala.md
   | Recipe: Chana Masala (cuisine: indian)
   | Section: Ingredients (rows 9-11 of 11)
   | | Ingredient | Weight | Notes |
   | | --- | --- | --- |
   | | Amchur (dried mango powder) | 6 g | added at the end |
   | | Fine sea salt | 10 g | |
   | | Green chilli, split | 2 whole | |

2. score=0.6022  chana-masala::structure::c001   <-- right recipe, but this chunk lacks the answer
   section=ingredients  source_file=chana-masala.md
   | Recipe: Chana Masala (cuisine: indian)
   | Section: Ingredients (rows 1-8 of 11)
   | | Ingredient | Weight | Notes |
   | | --- | --- | --- |
   | | Dried chickpeas | 400 g | soaked overnight |
   | | Brown onion, diced | 300 g | |
   | | Tinned plum tomatoes | 400 g | crushed by hand |
   | | Sunflower oil | 45 g | |
   | | Ginger, grated | 25 g | |
   | | Garlic, crushed | 20 g | |
   | | Ground cumin | 8 g | |
   | | Ground coriander | 8 g | |

3. score=0.5959  chana-masala::structure::c003   <-- right recipe, but this chunk lacks the answer
   section=method  source_file=chana-masala.md
   | Recipe: Chana Masala (cuisine: indian)
   | Section: Method
   | Drain the soaked chickpeas, cover with fresh water and simmer for 50 minutes until they
   | give completely under a spoon. Keep the cooking liquor.
   | 
   | Fry the onion in the oil over medium heat for a full fifteen minutes, until it collapses and
   | takes on colour at the edges. Add the ginger and garlic, then the ground spices, and stir
   | for a minute so they toast rather than steam.
   | 
   | Add the tomatoes and cook until the oil separates and pools at the edge of the pan. Tip in
   | the chickpeas with enough of their liquor to loosen, season with the salt, and simmer for
   | twenty minutes. Stir the amchur through off the heat so its sourness stays bright.

4. score=0.5597  chana-masala::structure::c004   <-- right recipe, but this chunk lacks the answer
   section=allergens  source_file=chana-masala.md
   | Recipe: Chana Masala (cuisine: indian)
   | Section: Allergens
   | No declared allergens. Prepared in a kitchen that handles wheat and dairy.

5. score=0.5559  chana-masala::structure::c000   <-- right recipe, but this chunk lacks the answer
   section=title  source_file=chana-masala.md
   | Recipe: Chana Masala (cuisine: indian)
   | Section: Title
   | # Chana Masala

VERDICT: HIT at rank 1
```
### q4 — How much double cream is in the chicken tikka masala?

```
expected recipe_id : chicken-tikka-masala
expected section   : ingredients table
answer must contain: ['Double cream', '150 g']
table-row question : True

1. score=0.7079  chicken-tikka-masala::structure::c001   <== HIT (contains the answer)
   section=ingredients  source_file=chicken-tikka-masala.md
   | Recipe: Chicken Tikka Masala (cuisine: indian)
   | Section: Ingredients (rows 1-8 of 13)
   | | Ingredient | Weight | Notes |
   | | --- | --- | --- |
   | | Chicken thigh, boneless | 900 g | 4 cm pieces |
   | | Full fat yoghurt | 250 g | for the marinade |
   | | Double cream | 150 g | |
   | | Tinned plum tomatoes | 400 g | |
   | | Brown onion | 250 g | diced |
   | | Ghee | 50 g | |
   | | Ginger, grated | 25 g | |
   | | Garlic, crushed | 20 g | |

2. score=0.6636  chicken-tikka-masala::structure::c002   <-- right recipe, but this chunk lacks the answer
   section=ingredients  source_file=chicken-tikka-masala.md
   | Recipe: Chicken Tikka Masala (cuisine: indian)
   | Section: Ingredients (rows 9-13 of 13)
   | | Ingredient | Weight | Notes |
   | | --- | --- | --- |
   | | Garam masala | 10 g | |
   | | Ground turmeric | 5 g | |
   | | Kashmiri chilli powder | 8 g | for colour |
   | | Fine sea salt | 12 g | |
   | | Kasoori methi | 4 g | crushed, at the end |

3. score=0.6205  chicken-tikka-masala::structure::c000   <-- right recipe, but this chunk lacks the answer
   section=title  source_file=chicken-tikka-masala.md
   | Recipe: Chicken Tikka Masala (cuisine: indian)
   | Section: Title
   | # Chicken Tikka Masala

4. score=0.6106  chicken-tikka-masala::structure::c003   <-- right recipe, but this chunk lacks the answer
   section=method  source_file=chicken-tikka-masala.md
   | Recipe: Chicken Tikka Masala (cuisine: indian)
   | Section: Method
   | Marinate the chicken in the yoghurt with half the ginger, garlic and spices for at least
   | four hours, ideally overnight. The acid in the yoghurt does the tenderising; more than
   | twenty-four hours and the texture turns mealy.
   | 
   | Thread onto skewers and grill hard until the edges char in places. You want colour, not
   | doneness — the pieces finish in the sauce.
   | 
   | Soften the onion in the ghee, add the remaining ginger, garlic and spices, then the tomatoes.
   | Cook until thick and glossy, blend smooth, and return to the pan. Add the grilled chicken
   | and simmer for ten minutes, then stir in the cream and the crushed kasoori methi off the
   | heat.

5. score=0.6071  chicken-tikka-masala::structure::c004   <-- right recipe, but this chunk lacks the answer
   section=allergens  source_file=chicken-tikka-masala.md
   | Recipe: Chicken Tikka Masala (cuisine: indian)
   | Section: Allergens
   | Contains dairy (yoghurt, cream, ghee). Naturally gluten free.

VERDICT: HIT at rank 1
```
### q5 — At what temperature and for how long is the lemon drizzle loaf baked?

```
expected recipe_id : lemon-drizzle-cake
expected section   : method
answer must contain: ['170 C', '45']
table-row question : False

1. score=0.7225  lemon-drizzle-cake::structure::c002   <== HIT (contains the answer)
   section=method  source_file=lemon-drizzle-cake.md
   | Recipe: Lemon Drizzle Loaf (cuisine: british)
   | Section: Method
   | Beat the butter and caster sugar until the mixture turns pale and increases visibly in
   | volume — five minutes in a stand mixer, and no less. Add the eggs one at a time, beating
   | fully between each.
   | 
   | Fold in the flour, salt and zest with a spatula, stopping the moment the flour disappears.
   | Scrape into a lined 900 g loaf tin and bake at 170 C for 45 to 50 minutes.
   | 
   | Stir the granulated sugar into the lemon juice without heating it — the crust should end up
   | crunchy, not glazed. Spike the hot loaf all over with a skewer and spoon the drizzle over
   | while the cake is still in the tin. Let it cool completely before turning out.

2. score=0.6169  lemon-drizzle-cake::structure::c001   <-- right recipe, but this chunk lacks the answer
   section=ingredients  source_file=lemon-drizzle-cake.md
   | Recipe: Lemon Drizzle Loaf (cuisine: british)
   | Section: Ingredients (rows 1-8 of 8)
   | | Ingredient | Weight | Notes |
   | | --- | --- | --- |
   | | Unsalted butter | 225 g | soft |
   | | Caster sugar | 225 g | |
   | | Self-raising flour | 225 g | |
   | | Eggs | 4 whole | room temperature |
   | | Lemon zest | 12 g | from 3 lemons |
   | | Lemon juice, for the drizzle | 75 g | |
   | | Granulated sugar, for the drizzle | 100 g | |
   | | Fine sea salt | 2 g | |

3. score=0.5984  lemon-drizzle-cake::structure::c000   <-- right recipe, but this chunk lacks the answer
   section=title  source_file=lemon-drizzle-cake.md
   | Recipe: Lemon Drizzle Loaf (cuisine: british)
   | Section: Title
   | # Lemon Drizzle Loaf

4. score=0.5152  lemon-drizzle-cake::structure::c003   <-- right recipe, but this chunk lacks the answer
   section=allergens  source_file=lemon-drizzle-cake.md
   | Recipe: Lemon Drizzle Loaf (cuisine: british)
   | Section: Allergens
   | Contains wheat (gluten), egg and dairy.

5. score=0.3115  classic-focaccia::structure::c002
   section=method  source_file=classic-focaccia.md
   | Recipe: Classic Rosemary Focaccia (cuisine: italian)
   | Section: Method
   | Whisk the yeast into the water and let it slacken for five minutes. Add the flour and mix
   | until no dry patches remain, then rest the dough uncovered for twenty minutes so the flour
   | hydrates fully.
   | 
   | Add the fine sea salt and half the olive oil, then work the dough with wet hands until it
   | tightens. Fold it in the bowl every thirty minutes for the first two hours.
   | 
   | Oil a deep tray generously, tip the dough in, and let it relax until it reaches the corners
   | on its own. Dimple it with flat fingers, scatter the rosemary and flaky salt, and bake at
   | 230 C for 22 to 25 minutes until the base sounds hollow.

VERDICT: HIT at rank 1
```
### q6 — How long should the pad thai rice noodles soak before they go in the wok?

```
expected recipe_id : pad-thai
expected section   : method
answer must contain: ['thirty minutes']
table-row question : False

1. score=0.6198  pad-thai::structure::c003   <== HIT (contains the answer)
   section=method  source_file=pad-thai.md
   | Recipe: Prawn Pad Thai (cuisine: thai)
   | Section: Method
   | Soak the noodles in warm water for thirty minutes until pliable but still firm at the core.
   | They finish cooking in the pan and will turn to paste if you soften them fully now.
   | 
   | Melt the palm sugar with the tamarind and fish sauce over low heat until it forms a smooth
   | syrup. This sauce is the whole dish; taste it and adjust before it goes near the wok.

2. score=0.4953  pad-thai::structure::c004   <-- right recipe, but this chunk lacks the answer
   section=method  source_file=pad-thai.md
   | Recipe: Prawn Pad Thai (cuisine: thai)
   | Section: Method
   | Get the wok properly hot. Fry the tofu until it takes colour, add the prawns and cook until
   | just opaque, then push everything to one side and scramble the eggs in the clear space.
   | Add the drained noodles and the sauce and toss hard for two minutes. Kill the heat, fold
   | through the beansprouts and chives so they stay crisp, and finish with the peanuts.

3. score=0.4445  congee::structure::c002
   section=method  source_file=congee.md
   | Recipe: Ginger and Spring Onion Congee (cuisine: chinese)
   | Section: Method
   | Rinse the rice until the water runs clear, then freeze it for an hour if you have time — the
   | ice fractures the grains and they break down far faster.
   | 
   | Bring the rice, water, ginger coins and spring onion whites to a boil, then drop to the
   | barest simmer. Stir every ten minutes or so, scraping the base, for ninety minutes. The
   | grains should dissolve into a loose, pourable porridge that thickens as it cools.
   | 
   | Season with the salt, soy and white pepper at the end; salting early slows the grains from
   | breaking down. Finish each bowl with the sesame oil, the sliced greens and fresh ginger.

4. score=0.4406  chicken-tikka-masala::structure::c003
   section=method  source_file=chicken-tikka-masala.md
   | Recipe: Chicken Tikka Masala (cuisine: indian)
   | Section: Method
   | Marinate the chicken in the yoghurt with half the ginger, garlic and spices for at least
   | four hours, ideally overnight. The acid in the yoghurt does the tenderising; more than
   | twenty-four hours and the texture turns mealy.
   | 
   | Thread onto skewers and grill hard until the edges char in places. You want colour, not
   | doneness — the pieces finish in the sauce.
   | 
   | Soften the onion in the ghee, add the remaining ginger, garlic and spices, then the tomatoes.
   | Cook until thick and glossy, blend smooth, and return to the pan. Add the grilled chicken
   | and simmer for ten minutes, then stir in the cream and the crushed kasoori methi off the
   | heat.

5. score=0.3778  pad-thai::structure::c001   <-- right recipe, but this chunk lacks the answer
   section=ingredients  source_file=pad-thai.md
   | Recipe: Prawn Pad Thai (cuisine: thai)
   | Section: Ingredients (rows 1-8 of 11)
   | | Ingredient | Weight | Notes |
   | | --- | --- | --- |
   | | Flat rice noodles | 250 g | dried |
   | | Raw prawns | 300 g | peeled, deveined |
   | | Firm tofu | 150 g | diced small |
   | | Eggs | 2 whole | beaten |
   | | Tamarind paste | 60 g | |
   | | Palm sugar | 50 g | shaved |
   | | Fish sauce | 45 g | |
   | | Roasted peanuts | 60 g | roughly crushed |

VERDICT: HIT at rank 1
```
### q7 — What allergens does the prawn pad thai contain?

```
expected recipe_id : pad-thai
expected section   : allergens
answer must contain: ['shellfish', 'peanuts']
table-row question : False

1. score=0.8267  pad-thai::structure::c005   <== HIT (contains the answer)
   section=allergens  source_file=pad-thai.md
   | Recipe: Prawn Pad Thai (cuisine: thai)
   | Section: Allergens
   | Contains shellfish, egg, peanuts and fish. Naturally gluten free, but check the fish sauce
   | brand.

2. score=0.6691  pad-thai::structure::c001   <-- right recipe, but this chunk lacks the answer
   section=ingredients  source_file=pad-thai.md
   | Recipe: Prawn Pad Thai (cuisine: thai)
   | Section: Ingredients (rows 1-8 of 11)
   | | Ingredient | Weight | Notes |
   | | --- | --- | --- |
   | | Flat rice noodles | 250 g | dried |
   | | Raw prawns | 300 g | peeled, deveined |
   | | Firm tofu | 150 g | diced small |
   | | Eggs | 2 whole | beaten |
   | | Tamarind paste | 60 g | |
   | | Palm sugar | 50 g | shaved |
   | | Fish sauce | 45 g | |
   | | Roasted peanuts | 60 g | roughly crushed |

3. score=0.6603  pad-thai::structure::c002   <-- right recipe, but this chunk lacks the answer
   section=ingredients  source_file=pad-thai.md
   | Recipe: Prawn Pad Thai (cuisine: thai)
   | Section: Ingredients (rows 9-11 of 11)
   | | Ingredient | Weight | Notes |
   | | --- | --- | --- |
   | | Beansprouts | 150 g | |
   | | Garlic chives | 50 g | 4 cm lengths |
   | | Neutral oil | 40 g | |

4. score=0.6526  pad-thai::structure::c000   <-- right recipe, but this chunk lacks the answer
   section=title  source_file=pad-thai.md
   | Recipe: Prawn Pad Thai (cuisine: thai)
   | Section: Title
   | # Prawn Pad Thai

5. score=0.6222  pad-thai::structure::c003   <-- right recipe, but this chunk lacks the answer
   section=method  source_file=pad-thai.md
   | Recipe: Prawn Pad Thai (cuisine: thai)
   | Section: Method
   | Soak the noodles in warm water for thirty minutes until pliable but still firm at the core.
   | They finish cooking in the pan and will turn to paste if you soften them fully now.
   | 
   | Melt the palm sugar with the tamarind and fish sauce over low heat until it forms a smooth
   | syrup. This sauce is the whole dish; taste it and adjust before it goes near the wok.

VERDICT: HIT at rank 1
```
### q8 — What is the rice to water ratio for the ginger and spring onion congee?

```
expected recipe_id : congee
expected section   : ingredients table (water row note)
answer must contain: ['1:12']
table-row question : True

1. score=0.7365  congee::structure::c001   <== HIT (contains the answer)
   section=ingredients  source_file=congee.md
   | Recipe: Ginger and Spring Onion Congee (cuisine: chinese)
   | Section: Ingredients (rows 1-8 of 8)
   | | Ingredient | Weight | Notes |
   | | --- | --- | --- |
   | | Short grain rice | 200 g | rinsed until the water runs clear |
   | | Water | 2400 g | a 1:12 ratio by weight |
   | | Ginger | 40 g | in coins, plus more to finish |
   | | Spring onion | 60 g | whites and greens separated |
   | | Light soy sauce | 20 g | |
   | | Toasted sesame oil | 10 g | |
   | | Fine sea salt | 6 g | |
   | | White pepper | 1 g | |

2. score=0.7003  congee::structure::c002   <-- right recipe, but this chunk lacks the answer
   section=method  source_file=congee.md
   | Recipe: Ginger and Spring Onion Congee (cuisine: chinese)
   | Section: Method
   | Rinse the rice until the water runs clear, then freeze it for an hour if you have time — the
   | ice fractures the grains and they break down far faster.
   | 
   | Bring the rice, water, ginger coins and spring onion whites to a boil, then drop to the
   | barest simmer. Stir every ten minutes or so, scraping the base, for ninety minutes. The
   | grains should dissolve into a loose, pourable porridge that thickens as it cools.
   | 
   | Season with the salt, soy and white pepper at the end; salting early slows the grains from
   | breaking down. Finish each bowl with the sesame oil, the sliced greens and fresh ginger.

3. score=0.6045  congee::structure::c000   <-- right recipe, but this chunk lacks the answer
   section=title  source_file=congee.md
   | Recipe: Ginger and Spring Onion Congee (cuisine: chinese)
   | Section: Title
   | # Ginger and Spring Onion Congee

4. score=0.5424  congee::structure::c003   <-- right recipe, but this chunk lacks the answer
   section=allergens  source_file=congee.md
   | Recipe: Ginger and Spring Onion Congee (cuisine: chinese)
   | Section: Allergens
   | Contains soy (soy sauce) and sesame. Use tamari to keep it gluten free.

5. score=0.4430  shakshuka::structure::c001
   section=ingredients  source_file=shakshuka.md
   | Recipe: Red Pepper Shakshuka (cuisine: middle-eastern)
   | Section: Ingredients (rows 1-8 of 10)
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

VERDICT: HIT at rank 1
```