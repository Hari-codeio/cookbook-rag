# Search-only dump — strategy=baseline

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

1. score=0.5474  beef-bourguignon::baseline::c000   <-- right recipe, but this chunk lacks the answer
   section=~ingredients  source_file=beef-bourguignon.md
   | ---
   | recipe_id: beef-bourguignon
   | title: Beef Bourguignon
   | cuisine: french
   | dietary_tags: [dairy-free, contains-alcohol]
   | ---
   | 
   | # Beef Bourguignon
   | 
   | ## Ingredients
   | 
   | | Ingredient | Weight | Notes |
   | | --- | --- | --- |
   | | Beef shin | 1200 g | cut into 5 cm pieces |
   | | Smoked bacon lardons | 200 g | |
   | | Red wine (Burgundy) | 750 g | one bottle |
   | | Beef stock | 400 g | |
   | | Button mushrooms | 300 g | |
   | | Shallots | 250 g | peeled, left whole |
   | | Carrot | 150 g | thick coins |
   | | Plain flour | 30 g | for

2. score=0.5345  beef-bourguignon::baseline::c001   <== HIT (contains the answer)
   section=~method  source_file=beef-bourguignon.md
   | left whole |
   | | Carrot | 150 g | thick coins |
   | | Plain flour | 30 g | for dusting |
   | | Tomato puree | 25 g | |
   | | Fine sea salt | 12 g | |
   | | Bay leaf | 2 leaves | |
   | | Thyme | 6 g | |
   | 
   | ## Method
   | 
   | Marinate the beef in the wine with the bay and thyme overnight in the fridge. Drain the meat
   | and reserve every drop of the wine.
   | 
   | Dry the beef thoroughly, dust with the flour, and brown it hard in batches — crowding the
   | pan is the single most common way to end up with grey stew. Render the lardons in the

3. score=0.4048  chicken-tikka-masala::baseline::c001
   section=~method  source_file=chicken-tikka-masala.md
   | | 50 g | |
   | | Ginger, grated | 25 g | |
   | | Garlic, crushed | 20 g | |
   | | Garam masala | 10 g | |
   | | Ground turmeric | 5 g | |
   | | Kashmiri chilli powder | 8 g | for colour |
   | | Fine sea salt | 12 g | |
   | | Kasoori methi | 4 g | crushed, at the end |
   | 
   | ## Method
   | 
   | Marinate the chicken in the yoghurt with half the ginger, garlic and spices for at least
   | four hours, ideally overnight. The acid in the yoghurt does the tenderising; more than
   | twenty-four hours and the texture turns mealy.
   | 
   | Thread onto skewers

4. score=0.3983  pad-thai::baseline::c001
   section=~method  source_file=pad-thai.md
   | g | shaved |
   | | Fish sauce | 45 g | |
   | | Roasted peanuts | 60 g | roughly crushed |
   | | Beansprouts | 150 g | |
   | | Garlic chives | 50 g | 4 cm lengths |
   | | Neutral oil | 40 g | |
   | 
   | ## Method
   | 
   | Soak the noodles in warm water for thirty minutes until pliable but still firm at the core.
   | They finish cooking in the pan and will turn to paste if you soften them fully now.
   | 
   | Melt the palm sugar with the tamarind and fish sauce over low heat until it forms a smooth
   | syrup. This sauce is the whole dish; taste it

5. score=0.3980  classic-focaccia::baseline::c001
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

VERDICT: HIT at rank 2
```
### q2 — What is the hydration percentage of the classic rosemary focaccia?

```
expected recipe_id : classic-focaccia
expected section   : ingredients table (water row, baker's %)
answer must contain: ['Water', '80%']
table-row question : True

1. score=0.6472  classic-focaccia::baseline::c000   <== HIT (contains the answer)
   section=~ingredients  source_file=classic-focaccia.md
   | ---
   | recipe_id: classic-focaccia
   | title: Classic Rosemary Focaccia
   | cuisine: italian
   | dietary_tags: [vegan, dairy-free, nut-free]
   | ---
   | 
   | # Classic Rosemary Focaccia
   | 
   | A slow-proved tray bread. Baker's percentages are relative to the total flour weight.
   | 
   | ## Ingredients
   | 
   | | Ingredient | Weight | Baker's % |
   | | --- | --- | --- |
   | | Strong white bread flour | 1000 g | 100% |
   | | Water (20 C) | 800 g | 80% |
   | | Extra virgin olive oil | 60 g | 6% |
   | | Fine sea salt | 20 g | 2% |
   | | Instant dried yeast | 8 g | 0.8%

2. score=0.4105  classic-focaccia::baseline::c001   <-- right recipe, but this chunk lacks the answer
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

3. score=0.3361  chicken-tikka-masala::baseline::c001
   section=~method  source_file=chicken-tikka-masala.md
   | | 50 g | |
   | | Ginger, grated | 25 g | |
   | | Garlic, crushed | 20 g | |
   | | Garam masala | 10 g | |
   | | Ground turmeric | 5 g | |
   | | Kashmiri chilli powder | 8 g | for colour |
   | | Fine sea salt | 12 g | |
   | | Kasoori methi | 4 g | crushed, at the end |
   | 
   | ## Method
   | 
   | Marinate the chicken in the yoghurt with half the ginger, garlic and spices for at least
   | four hours, ideally overnight. The acid in the yoghurt does the tenderising; more than
   | twenty-four hours and the texture turns mealy.
   | 
   | Thread onto skewers

4. score=0.2918  beef-bourguignon::baseline::c000
   section=~ingredients  source_file=beef-bourguignon.md
   | ---
   | recipe_id: beef-bourguignon
   | title: Beef Bourguignon
   | cuisine: french
   | dietary_tags: [dairy-free, contains-alcohol]
   | ---
   | 
   | # Beef Bourguignon
   | 
   | ## Ingredients
   | 
   | | Ingredient | Weight | Notes |
   | | --- | --- | --- |
   | | Beef shin | 1200 g | cut into 5 cm pieces |
   | | Smoked bacon lardons | 200 g | |
   | | Red wine (Burgundy) | 750 g | one bottle |
   | | Beef stock | 400 g | |
   | | Button mushrooms | 300 g | |
   | | Shallots | 250 g | peeled, left whole |
   | | Carrot | 150 g | thick coins |
   | | Plain flour | 30 g | for

5. score=0.2910  beef-bourguignon::baseline::c001
   section=~method  source_file=beef-bourguignon.md
   | left whole |
   | | Carrot | 150 g | thick coins |
   | | Plain flour | 30 g | for dusting |
   | | Tomato puree | 25 g | |
   | | Fine sea salt | 12 g | |
   | | Bay leaf | 2 leaves | |
   | | Thyme | 6 g | |
   | 
   | ## Method
   | 
   | Marinate the beef in the wine with the bay and thyme overnight in the fridge. Drain the meat
   | and reserve every drop of the wine.
   | 
   | Dry the beef thoroughly, dust with the flour, and brown it hard in batches — crowding the
   | pan is the single most common way to end up with grey stew. Render the lardons in the

VERDICT: HIT at rank 1
```
### q3 — How much amchur goes into the chana masala?

```
expected recipe_id : chana-masala
expected section   : ingredients table
answer must contain: ['Amchur', '6 g']
table-row question : True

1. score=0.5830  chana-masala::baseline::c000   <-- right recipe, but this chunk lacks the answer
   section=~ingredients  source_file=chana-masala.md
   | ---
   | recipe_id: chana-masala
   | title: Chana Masala
   | cuisine: indian
   | dietary_tags: [vegan, gluten-free, dairy-free]
   | ---
   | 
   | # Chana Masala
   | 
   | ## Ingredients
   | 
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
   | | Amchur (dried mango powder)

2. score=0.4070  chicken-tikka-masala::baseline::c000
   section=~ingredients  source_file=chicken-tikka-masala.md
   | ---
   | recipe_id: chicken-tikka-masala
   | title: Chicken Tikka Masala
   | cuisine: indian
   | dietary_tags: [gluten-free, contains-dairy]
   | ---
   | 
   | # Chicken Tikka Masala
   | 
   | ## Ingredients
   | 
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
   | | Garam

3. score=0.2767  chicken-tikka-masala::baseline::c001
   section=~method  source_file=chicken-tikka-masala.md
   | | 50 g | |
   | | Ginger, grated | 25 g | |
   | | Garlic, crushed | 20 g | |
   | | Garam masala | 10 g | |
   | | Ground turmeric | 5 g | |
   | | Kashmiri chilli powder | 8 g | for colour |
   | | Fine sea salt | 12 g | |
   | | Kasoori methi | 4 g | crushed, at the end |
   | 
   | ## Method
   | 
   | Marinate the chicken in the yoghurt with half the ginger, garlic and spices for at least
   | four hours, ideally overnight. The acid in the yoghurt does the tenderising; more than
   | twenty-four hours and the texture turns mealy.
   | 
   | Thread onto skewers

4. score=0.2593  chana-masala::baseline::c001   <== HIT (contains the answer)
   section=~method  source_file=chana-masala.md
   | und cumin | 8 g | |
   | | Ground coriander | 8 g | |
   | | Amchur (dried mango powder) | 6 g | added at the end |
   | | Fine sea salt | 10 g | |
   | | Green chilli, split | 2 whole | |
   | 
   | ## Method
   | 
   | Drain the soaked chickpeas, cover with fresh water and simmer for 50 minutes until they
   | give completely under a spoon. Keep the cooking liquor.
   | 
   | Fry the onion in the oil over medium heat for a full fifteen minutes, until it collapses and
   | takes on colour at the edges. Add the ginger and garlic, then the ground spices,

5. score=0.2591  chana-masala::baseline::c002   <-- right recipe, but this chunk lacks the answer
   section=~method  source_file=chana-masala.md
   | akes on colour at the edges. Add the ginger and garlic, then the ground spices, and stir
   | for a minute so they toast rather than steam.
   | 
   | Add the tomatoes and cook until the oil separates and pools at the edge of the pan. Tip in
   | the chickpeas with enough of their liquor to loosen, season with the salt, and simmer for
   | twenty minutes. Stir the amchur through off the heat so its sourness stays bright.
   | 
   | ## Allergens
   | 
   | No declared allergens. Prepared in a kitchen that handles wheat and dairy.

VERDICT: HIT at rank 4
```
### q4 — How much double cream is in the chicken tikka masala?

```
expected recipe_id : chicken-tikka-masala
expected section   : ingredients table
answer must contain: ['Double cream', '150 g']
table-row question : True

1. score=0.6334  chicken-tikka-masala::baseline::c000   <== HIT (contains the answer)
   section=~ingredients  source_file=chicken-tikka-masala.md
   | ---
   | recipe_id: chicken-tikka-masala
   | title: Chicken Tikka Masala
   | cuisine: indian
   | dietary_tags: [gluten-free, contains-dairy]
   | ---
   | 
   | # Chicken Tikka Masala
   | 
   | ## Ingredients
   | 
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
   | | Garam

2. score=0.5285  chicken-tikka-masala::baseline::c001   <-- right recipe, but this chunk lacks the answer
   section=~method  source_file=chicken-tikka-masala.md
   | | 50 g | |
   | | Ginger, grated | 25 g | |
   | | Garlic, crushed | 20 g | |
   | | Garam masala | 10 g | |
   | | Ground turmeric | 5 g | |
   | | Kashmiri chilli powder | 8 g | for colour |
   | | Fine sea salt | 12 g | |
   | | Kasoori methi | 4 g | crushed, at the end |
   | 
   | ## Method
   | 
   | Marinate the chicken in the yoghurt with half the ginger, garlic and spices for at least
   | four hours, ideally overnight. The acid in the yoghurt does the tenderising; more than
   | twenty-four hours and the texture turns mealy.
   | 
   | Thread onto skewers

3. score=0.5226  chana-masala::baseline::c000
   section=~ingredients  source_file=chana-masala.md
   | ---
   | recipe_id: chana-masala
   | title: Chana Masala
   | cuisine: indian
   | dietary_tags: [vegan, gluten-free, dairy-free]
   | ---
   | 
   | # Chana Masala
   | 
   | ## Ingredients
   | 
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
   | | Amchur (dried mango powder)

4. score=0.4651  pad-thai::baseline::c001
   section=~method  source_file=pad-thai.md
   | g | shaved |
   | | Fish sauce | 45 g | |
   | | Roasted peanuts | 60 g | roughly crushed |
   | | Beansprouts | 150 g | |
   | | Garlic chives | 50 g | 4 cm lengths |
   | | Neutral oil | 40 g | |
   | 
   | ## Method
   | 
   | Soak the noodles in warm water for thirty minutes until pliable but still firm at the core.
   | They finish cooking in the pan and will turn to paste if you soften them fully now.
   | 
   | Melt the palm sugar with the tamarind and fish sauce over low heat until it forms a smooth
   | syrup. This sauce is the whole dish; taste it

5. score=0.4441  chana-masala::baseline::c001
   section=~method  source_file=chana-masala.md
   | und cumin | 8 g | |
   | | Ground coriander | 8 g | |
   | | Amchur (dried mango powder) | 6 g | added at the end |
   | | Fine sea salt | 10 g | |
   | | Green chilli, split | 2 whole | |
   | 
   | ## Method
   | 
   | Drain the soaked chickpeas, cover with fresh water and simmer for 50 minutes until they
   | give completely under a spoon. Keep the cooking liquor.
   | 
   | Fry the onion in the oil over medium heat for a full fifteen minutes, until it collapses and
   | takes on colour at the edges. Add the ginger and garlic, then the ground spices,

VERDICT: HIT at rank 1
```
### q5 — At what temperature and for how long is the lemon drizzle loaf baked?

```
expected recipe_id : lemon-drizzle-cake
expected section   : method
answer must contain: ['170 C', '45']
table-row question : False

1. score=0.6171  lemon-drizzle-cake::baseline::c002   <== HIT (contains the answer)
   section=~method  source_file=lemon-drizzle-cake.md
   | g loaf tin and bake at 170 C for 45 to 50 minutes.
   | 
   | Stir the granulated sugar into the lemon juice without heating it — the crust should end up
   | crunchy, not glazed. Spike the hot loaf all over with a skewer and spoon the drizzle over
   | while the cake is still in the tin. Let it cool completely before turning out.
   | 
   | ## Allergens
   | 
   | Contains wheat (gluten), egg and dairy.

2. score=0.5648  lemon-drizzle-cake::baseline::c000   <-- right recipe, but this chunk lacks the answer
   section=~ingredients  source_file=lemon-drizzle-cake.md
   | ---
   | recipe_id: lemon-drizzle-cake
   | title: Lemon Drizzle Loaf
   | cuisine: british
   | dietary_tags: [vegetarian, contains-egg, contains-dairy]
   | ---
   | 
   | # Lemon Drizzle Loaf
   | 
   | ## Ingredients
   | 
   | | Ingredient | Weight | Notes |
   | | --- | --- | --- |
   | | Unsalted butter | 225 g | soft |
   | | Caster sugar | 225 g | |
   | | Self-raising flour | 225 g | |
   | | Eggs | 4 whole | room temperature |
   | | Lemon zest | 12 g | from 3 lemons |
   | | Lemon juice, for the drizzle | 75 g | |
   | | Granulated sugar, for the drizzle | 100 g | |
   | | Fine

3. score=0.5561  lemon-drizzle-cake::baseline::c001   <== HIT (contains the answer)
   section=~method  source_file=lemon-drizzle-cake.md
   | he drizzle | 75 g | |
   | | Granulated sugar, for the drizzle | 100 g | |
   | | Fine sea salt | 2 g | |
   | 
   | ## Method
   | 
   | Beat the butter and caster sugar until the mixture turns pale and increases visibly in
   | volume — five minutes in a stand mixer, and no less. Add the eggs one at a time, beating
   | fully between each.
   | 
   | Fold in the flour, salt and zest with a spatula, stopping the moment the flour disappears.
   | Scrape into a lined 900 g loaf tin and bake at 170 C for 45 to 50 minutes.
   | 
   | Stir the granulated sugar

4. score=0.3537  classic-focaccia::baseline::c001
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

5. score=0.3450  classic-focaccia::baseline::c002
   section=~method  source_file=classic-focaccia.md
   | hen work the dough with wet hands until it
   | tightens. Fold it in the bowl every thirty minutes for the first two hours.
   | 
   | Oil a deep tray generously, tip the dough in, and let it relax until it reaches the corners
   | on its own. Dimple it with flat fingers, scatter the rosemary and flaky salt, and bake at
   | 230 C for 22 to 25 minutes until the base sounds hollow.
   | 
   | ## Allergens
   | 
   | Contains wheat (gluten). Made in a kitchen that also handles sesame.

VERDICT: HIT at rank 1
```
### q6 — How long should the pad thai rice noodles soak before they go in the wok?

```
expected recipe_id : pad-thai
expected section   : method
answer must contain: ['thirty minutes']
table-row question : False

1. score=0.4797  pad-thai::baseline::c001   <== HIT (contains the answer)
   section=~method  source_file=pad-thai.md
   | g | shaved |
   | | Fish sauce | 45 g | |
   | | Roasted peanuts | 60 g | roughly crushed |
   | | Beansprouts | 150 g | |
   | | Garlic chives | 50 g | 4 cm lengths |
   | | Neutral oil | 40 g | |
   | 
   | ## Method
   | 
   | Soak the noodles in warm water for thirty minutes until pliable but still firm at the core.
   | They finish cooking in the pan and will turn to paste if you soften them fully now.
   | 
   | Melt the palm sugar with the tamarind and fish sauce over low heat until it forms a smooth
   | syrup. This sauce is the whole dish; taste it

2. score=0.4499  congee::baseline::c001
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

3. score=0.4199  chicken-tikka-masala::baseline::c001
   section=~method  source_file=chicken-tikka-masala.md
   | | 50 g | |
   | | Ginger, grated | 25 g | |
   | | Garlic, crushed | 20 g | |
   | | Garam masala | 10 g | |
   | | Ground turmeric | 5 g | |
   | | Kashmiri chilli powder | 8 g | for colour |
   | | Fine sea salt | 12 g | |
   | | Kasoori methi | 4 g | crushed, at the end |
   | 
   | ## Method
   | 
   | Marinate the chicken in the yoghurt with half the ginger, garlic and spices for at least
   | four hours, ideally overnight. The acid in the yoghurt does the tenderising; more than
   | twenty-four hours and the texture turns mealy.
   | 
   | Thread onto skewers

4. score=0.4008  congee::baseline::c002
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

5. score=0.3897  pad-thai::baseline::c000   <-- right recipe, but this chunk lacks the answer
   section=~ingredients  source_file=pad-thai.md
   | ---
   | recipe_id: pad-thai
   | title: Prawn Pad Thai
   | cuisine: thai
   | dietary_tags: [gluten-free, contains-egg, contains-shellfish, contains-peanut]
   | ---
   | 
   | # Prawn Pad Thai
   | 
   | ## Ingredients
   | 
   | | Ingredient | Weight | Notes |
   | | --- | --- | --- |
   | | Flat rice noodles | 250 g | dried |
   | | Raw prawns | 300 g | peeled, deveined |
   | | Firm tofu | 150 g | diced small |
   | | Eggs | 2 whole | beaten |
   | | Tamarind paste | 60 g | |
   | | Palm sugar | 50 g | shaved |
   | | Fish sauce | 45 g | |
   | | Roasted peanuts | 60 g | roughly crushed

VERDICT: HIT at rank 1
```
### q7 — What allergens does the prawn pad thai contain?

```
expected recipe_id : pad-thai
expected section   : allergens
answer must contain: ['shellfish', 'peanuts']
table-row question : False

1. score=0.7081  pad-thai::baseline::c000   <== HIT (contains the answer)
   section=~ingredients  source_file=pad-thai.md
   | ---
   | recipe_id: pad-thai
   | title: Prawn Pad Thai
   | cuisine: thai
   | dietary_tags: [gluten-free, contains-egg, contains-shellfish, contains-peanut]
   | ---
   | 
   | # Prawn Pad Thai
   | 
   | ## Ingredients
   | 
   | | Ingredient | Weight | Notes |
   | | --- | --- | --- |
   | | Flat rice noodles | 250 g | dried |
   | | Raw prawns | 300 g | peeled, deveined |
   | | Firm tofu | 150 g | diced small |
   | | Eggs | 2 whole | beaten |
   | | Tamarind paste | 60 g | |
   | | Palm sugar | 50 g | shaved |
   | | Fish sauce | 45 g | |
   | | Roasted peanuts | 60 g | roughly crushed

2. score=0.5171  pad-thai::baseline::c003   <== HIT (contains the answer)
   section=~allergens  source_file=pad-thai.md
   | ves so they stay crisp, and finish with the peanuts.
   | 
   | ## Allergens
   | 
   | Contains shellfish, egg, peanuts and fish. Naturally gluten free, but check the fish sauce
   | brand.

3. score=0.4856  chicken-tikka-masala::baseline::c003
   section=~allergens  source_file=chicken-tikka-masala.md
   | eam and the crushed kasoori methi off the
   | heat.
   | 
   | ## Allergens
   | 
   | Contains dairy (yoghurt, cream, ghee). Naturally gluten free.

4. score=0.4277  pad-thai::baseline::c002   <-- right recipe, but this chunk lacks the answer
   section=~method  source_file=pad-thai.md
   | low heat until it forms a smooth
   | syrup. This sauce is the whole dish; taste it and adjust before it goes near the wok.
   | 
   | Get the wok properly hot. Fry the tofu until it takes colour, add the prawns and cook until
   | just opaque, then push everything to one side and scramble the eggs in the clear space.
   | Add the drained noodles and the sauce and toss hard for two minutes. Kill the heat, fold
   | through the beansprouts and chives so they stay crisp, and finish with the peanuts.
   | 
   | ## Allergens
   | 
   | Contains

5. score=0.4200  beef-bourguignon::baseline::c003
   section=~allergens  source_file=beef-bourguignon.md
   | s reduced and concentrated.
   | 
   | ## Allergens
   | 
   | Contains wheat (gluten) from the flour dusting, and alcohol. No dairy.

VERDICT: HIT at rank 1
```
### q8 — What is the rice to water ratio for the ginger and spring onion congee?

```
expected recipe_id : congee
expected section   : ingredients table (water row note)
answer must contain: ['1:12']
table-row question : True

1. score=0.6342  congee::baseline::c000   <== HIT (contains the answer)
   section=~ingredients  source_file=congee.md
   | ---
   | recipe_id: congee
   | title: Ginger and Spring Onion Congee
   | cuisine: chinese
   | dietary_tags: [vegan, gluten-free, dairy-free, nut-free]
   | ---
   | 
   | # Ginger and Spring Onion Congee
   | 
   | ## Ingredients
   | 
   | | Ingredient | Weight | Notes |
   | | --- | --- | --- |
   | | Short grain rice | 200 g | rinsed until the water runs clear |
   | | Water | 2400 g | a 1:12 ratio by weight |
   | | Ginger | 40 g | in coins, plus more to finish |
   | | Spring onion | 60 g | whites and greens separated |
   | | Light soy sauce | 20 g | |
   | | Toasted sesame

2. score=0.6148  congee::baseline::c001   <-- right recipe, but this chunk lacks the answer
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

3. score=0.4808  chana-masala::baseline::c001
   section=~method  source_file=chana-masala.md
   | und cumin | 8 g | |
   | | Ground coriander | 8 g | |
   | | Amchur (dried mango powder) | 6 g | added at the end |
   | | Fine sea salt | 10 g | |
   | | Green chilli, split | 2 whole | |
   | 
   | ## Method
   | 
   | Drain the soaked chickpeas, cover with fresh water and simmer for 50 minutes until they
   | give completely under a spoon. Keep the cooking liquor.
   | 
   | Fry the onion in the oil over medium heat for a full fifteen minutes, until it collapses and
   | takes on colour at the edges. Add the ginger and garlic, then the ground spices,

4. score=0.4732  chicken-tikka-masala::baseline::c001
   section=~method  source_file=chicken-tikka-masala.md
   | | 50 g | |
   | | Ginger, grated | 25 g | |
   | | Garlic, crushed | 20 g | |
   | | Garam masala | 10 g | |
   | | Ground turmeric | 5 g | |
   | | Kashmiri chilli powder | 8 g | for colour |
   | | Fine sea salt | 12 g | |
   | | Kasoori methi | 4 g | crushed, at the end |
   | 
   | ## Method
   | 
   | Marinate the chicken in the yoghurt with half the ginger, garlic and spices for at least
   | four hours, ideally overnight. The acid in the yoghurt does the tenderising; more than
   | twenty-four hours and the texture turns mealy.
   | 
   | Thread onto skewers

5. score=0.4606  congee::baseline::c002   <-- right recipe, but this chunk lacks the answer
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

VERDICT: HIT at rank 1
```