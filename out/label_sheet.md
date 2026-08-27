# Blind label sheet - substitution soundness

substitutions: `substitutions_v1.jsonl`  sha256 `f50218d27cf5bf2e00ab641c2c3242001e8a5fe415e7e2eb7ef3720343ba6849`
cases: 25

One binary criterion, copied from eval/judge_v1.txt:

> SOUND means BOTH: (a) every claim is supported by the CONTEXT blocks shown,
> every quantity appears verbatim in one, and every cited chunk_id is one of the
> blocks shown and does contain the claimed evidence; and (b) the output does not
> overstate what the archive supports - declining is SOUND when the archive really
> does not ground the change, and UNSOUND when the evidence was in the blocks given.

The case's `groundable` field and every judge verdict are deliberately absent.

---
## c01

**request**: `classic brioche` -> `gluten free`

context blocks given (11):

```
<context chunk_id="gf-brioche::structure::c000" recipe_id="gf-brioche" source_file="card-07-gluten-free-brioche.md" section="title" dietary_tags="gluten-free|contains-egg|contains-dairy">
Recipe: Gluten-Free Brioche (cuisine: french)
Section: Title
# Gluten-Free Brioche

An enriched overnight dough. Baker's percentages are relative to the 500 g flour blend.
</context>

<context chunk_id="gf-brioche::structure::c003" recipe_id="gf-brioche" source_file="card-07-gluten-free-brioche.md" section="allergens" dietary_tags="gluten-free|contains-egg|contains-dairy">
Recipe: Gluten-Free Brioche (cuisine: french)
Section: Allergens
Contains egg and dairy. Gluten free, provided the flour blend is certified.
</context>

<context chunk_id="classic-brioche::structure::c003" recipe_id="classic-brioche" source_file="card-08-classic-brioche.md" section="allergens" dietary_tags="contains-egg|contains-dairy|contains-gluten">
Recipe: Classic Brioche (cuisine: french)
Section: Allergens
Contains wheat (gluten), egg and dairy.
</context>

<context chunk_id="gf-brioche::structure::c001" recipe_id="gf-brioche" source_file="card-07-gluten-free-brioche.md" section="ingredients" dietary_tags="gluten-free|contains-egg|contains-dairy">
Recipe: Gluten-Free Brioche (cuisine: french)
Section: Ingredients (rows 1-8 of 8)
| Ingredient | Weight | Baker's % |
| --- | --- | --- |
| Gluten-free flour blend | 500 g | 100% |
| Xanthan gum | 6 g | 1.2% |
| Caster sugar | 60 g | 12% |
| Instant dried yeast | 8 g | 1.6% |
| Fine sea salt | 9 g | 1.8% |
| Whole eggs | 250 g | 50% |
| Whole milk (32 C) | 150 g | 30% |
| Unsalted butter, softened | 175 g | 35% |
</context>

<context chunk_id="chocolate-brioche::structure::c003" recipe_id="chocolate-brioche" source_file="card-09-chocolate-brioche.md" section="allergens" dietary_tags="contains-egg|contains-dairy|contains-gluten|contains-soy">
Recipe: Chocolate Chip Brioche (cuisine: french)
Section: Allergens
Contains wheat (gluten), egg, dairy and soy (from the chocolate).
</context>

<context chunk_id="gf-brioche::structure::c002" recipe_id="gf-brioche" source_file="card-07-gluten-free-brioche.md" section="method" dietary_tags="gluten-free|contains-egg|contains-dairy">
Recipe: Gluten-Free Brioche (cuisine: french)
Section: Method
Whisk the flour blend, xanthan gum, sugar, yeast and salt together dry, so the gum disperses
before it meets any liquid. Lumped gum turns the crumb slimy and no amount of mixing later
will fix it.

Beat in the eggs and warm milk until the batter climbs the paddle, then add the softened
butter in five additions, waiting for each to disappear. The dough stays a thick batter
rather than a ball, which is normal without gluten.

Chill overnight at 4 C. Scale into a lined tin the next morning, prove until risen by half,
and bake at 180 C for 35 minutes.
</context>

<context chunk_id="classic-brioche::structure::c002" recipe_id="classic-brioche" source_file="card-08-classic-brioche.md" section="method" dietary_tags="contains-egg|contains-dairy|contains-gluten">
Recipe: Classic Brioche (cuisine: french)
Section: Method
Whisk the flour, sugar, yeast and salt together dry, then beat in the eggs and warm milk
until the dough climbs the hook and cleans the bowl.

Add the softened butter in five additions, waiting for each to disappear before the next.
The dough should end up glossy and slack enough to fall from the hook in a sheet.

Chill overnight at 4 C. Scale into a lined tin the next morning, prove until risen by half,
and bake at 180 C for 35 minutes.
</context>

<context chunk_id="classic-brioche::structure::c000" recipe_id="classic-brioche" source_file="card-08-classic-brioche.md" section="title" dietary_tags="contains-egg|contains-dairy|contains-gluten">
Recipe: Classic Brioche (cuisine: french)
Section: Title
# Classic Brioche

An enriched overnight dough. Baker's percentages are relative to the 500 g of flour.
</context>

<context chunk_id="classic-brioche::structure::c001" recipe_id="classic-brioche" source_file="card-08-classic-brioche.md" section="ingredients" dietary_tags="contains-egg|contains-dairy|contains-gluten">
Recipe: Classic Brioche (cuisine: french)
Section: Ingredients (rows 1-7 of 7)
| Ingredient | Weight | Baker's % |
| --- | --- | --- |
| Strong white bread flour | 500 g | 100% |
| Caster sugar | 60 g | 12% |
| Instant dried yeast | 8 g | 1.6% |
| Fine sea salt | 9 g | 1.8% |
| Whole eggs | 250 g | 50% |
| Whole milk (32 C) | 100 g | 20% |
| Unsalted butter, softened | 250 g | 50% |
</context>

<context chunk_id="chocolate-brioche::structure::c002" recipe_id="chocolate-brioche" source_file="card-09-chocolate-brioche.md" section="method" dietary_tags="contains-egg|contains-dairy|contains-gluten|contains-soy">
Recipe: Chocolate Chip Brioche (cuisine: french)
Section: Method
Whisk the flour, sugar, yeast and salt together dry, then beat in the eggs and warm milk
until the dough climbs the hook and cleans the bowl.

Add the softened butter in five additions, waiting for each to disappear before the next.
Fold the chocolate chips through by hand at the very end, or the paddle will smash them into
the crumb and grey the whole loaf.

Chill overnight at 4 C. Scale into a lined tin the next morning, prove until risen by half,
and bake at 180 C for 35 minutes.
</context>

<context chunk_id="chocolate-brioche::structure::c000" recipe_id="chocolate-brioche" source_file="card-09-chocolate-brioche.md" section="title" dietary_tags="contains-egg|contains-dairy|contains-gluten|contains-soy">
Recipe: Chocolate Chip Brioche (cuisine: french)
Section: Title
# Chocolate Chip Brioche

An enriched overnight dough. Baker's percentages are relative to the 500 g of flour.
</context>
```

**output**:

```json
{
  "can_substitute": true,
  "base_recipe_id": "classic-brioche",
  "title": "Gluten-Free Brioche",
  "swaps": [
    {
      "removed": "Strong white bread flour",
      "added": "Gluten-free flour blend",
      "evidence_chunk_id": "gf-brioche::structure::c001"
    },
    {
      "removed": "No xanthan gum",
      "added": "Xanthan gum",
      "evidence_chunk_id": "gf-brioche::structure::c001"
    }
  ],
  "ingredients": [
    {
      "name": "Gluten-free flour blend",
      "amount": "500 g",
      "source_chunk_id": "gf-brioche::structure::c001"
    },
    {
      "name": "Xanthan gum",
      "amount": "6 g",
      "source_chunk_id": "gf-brioche::structure::c001"
    },
    {
      "name": "Caster sugar",
      "amount": "60 g",
      "source_chunk_id": "classic-brioche::structure::c001"
    },
    {
      "name": "Instant dried yeast",
      "amount": "8 g",
      "source_chunk_id": "classic-brioche::structure::c001"
    },
    {
      "name": "Fine sea salt",
      "amount": "9 g",
      "source_chunk_id": "classic-brioche::structure::c001"
    },
    {
      "name": "Whole eggs",
      "amount": "250 g",
      "source_chunk_id": "classic-brioche::structure::c001"
    },
    {
      "name": "Whole milk (32 C)",
      "amount": "100 g",
      "source_chunk_id": "classic-brioche::structure::c001"
    },
    {
      "name": "Unsalted butter, softened",
      "amount": "250 g",
      "source_chunk_id": "classic-brioche::structure::c001"
    }
  ],
  "method": "Whisk the flour blend, xanthan gum, sugar, yeast and salt together dry, so the gum disperses before it meets any liquid. Beat in the eggs and warm milk until the batter climbs the paddle, then add the softened butter in five additions, waiting for each to disappear. The dough stays a thick batter rather than a ball, which is normal without gluten. Chill overnight at 4 C. Scale into a lined tin the next morning, prove until risen by half, and bake at 180 C for 35 minutes.",
  "oven": "180 C",
  "allergen_warning": "Contains egg and dairy.",
  "unsupported": ""
}
```

`sound`: [ ] true   [ ] false

---

## c02

**request**: `chocolate brioche` -> `dairy free`

context blocks given (8):

```
<context chunk_id="chocolate-brioche::structure::c002" recipe_id="chocolate-brioche" source_file="card-09-chocolate-brioche.md" section="method" dietary_tags="contains-egg|contains-dairy|contains-gluten|contains-soy">
Recipe: Chocolate Chip Brioche (cuisine: french)
Section: Method
Whisk the flour, sugar, yeast and salt together dry, then beat in the eggs and warm milk
until the dough climbs the hook and cleans the bowl.

Add the softened butter in five additions, waiting for each to disappear before the next.
Fold the chocolate chips through by hand at the very end, or the paddle will smash them into
the crumb and grey the whole loaf.

Chill overnight at 4 C. Scale into a lined tin the next morning, prove until risen by half,
and bake at 180 C for 35 minutes.
</context>

<context chunk_id="chocolate-brioche::structure::c000" recipe_id="chocolate-brioche" source_file="card-09-chocolate-brioche.md" section="title" dietary_tags="contains-egg|contains-dairy|contains-gluten|contains-soy">
Recipe: Chocolate Chip Brioche (cuisine: french)
Section: Title
# Chocolate Chip Brioche

An enriched overnight dough. Baker's percentages are relative to the 500 g of flour.
</context>

<context chunk_id="chocolate-brioche::structure::c003" recipe_id="chocolate-brioche" source_file="card-09-chocolate-brioche.md" section="allergens" dietary_tags="contains-egg|contains-dairy|contains-gluten|contains-soy">
Recipe: Chocolate Chip Brioche (cuisine: french)
Section: Allergens
Contains wheat (gluten), egg, dairy and soy (from the chocolate).
</context>

<context chunk_id="chocolate-brioche::structure::c001" recipe_id="chocolate-brioche" source_file="card-09-chocolate-brioche.md" section="ingredients" dietary_tags="contains-egg|contains-dairy|contains-gluten|contains-soy">
Recipe: Chocolate Chip Brioche (cuisine: french)
Section: Ingredients (rows 1-8 of 8)
| Ingredient | Weight | Baker's % |
| --- | --- | --- |
| Strong white bread flour | 500 g | 100% |
| Caster sugar | 70 g | 14% |
| Instant dried yeast | 8 g | 1.6% |
| Fine sea salt | 9 g | 1.8% |
| Whole eggs | 250 g | 50% |
| Whole milk (32 C) | 100 g | 20% |
| Unsalted butter, softened | 225 g | 45% |
| Dark chocolate chips | 150 g | 30% |
</context>

<context chunk_id="gf-brioche::structure::c003" recipe_id="gf-brioche" source_file="card-07-gluten-free-brioche.md" section="allergens" dietary_tags="gluten-free|contains-egg|contains-dairy">
Recipe: Gluten-Free Brioche (cuisine: french)
Section: Allergens
Contains egg and dairy. Gluten free, provided the flour blend is certified.
</context>

<context chunk_id="classic-brioche::structure::c002" recipe_id="classic-brioche" source_file="card-08-classic-brioche.md" section="method" dietary_tags="contains-egg|contains-dairy|contains-gluten">
Recipe: Classic Brioche (cuisine: french)
Section: Method
Whisk the flour, sugar, yeast and salt together dry, then beat in the eggs and warm milk
until the dough climbs the hook and cleans the bowl.

Add the softened butter in five additions, waiting for each to disappear before the next.
The dough should end up glossy and slack enough to fall from the hook in a sheet.

Chill overnight at 4 C. Scale into a lined tin the next morning, prove until risen by half,
and bake at 180 C for 35 minutes.
</context>

<context chunk_id="classic-brioche::structure::c001" recipe_id="classic-brioche" source_file="card-08-classic-brioche.md" section="ingredients" dietary_tags="contains-egg|contains-dairy|contains-gluten">
Recipe: Classic Brioche (cuisine: french)
Section: Ingredients (rows 1-7 of 7)
| Ingredient | Weight | Baker's % |
| --- | --- | --- |
| Strong white bread flour | 500 g | 100% |
| Caster sugar | 60 g | 12% |
| Instant dried yeast | 8 g | 1.6% |
| Fine sea salt | 9 g | 1.8% |
| Whole eggs | 250 g | 50% |
| Whole milk (32 C) | 100 g | 20% |
| Unsalted butter, softened | 250 g | 50% |
</context>

<context chunk_id="classic-brioche::structure::c003" recipe_id="classic-brioche" source_file="card-08-classic-brioche.md" section="allergens" dietary_tags="contains-egg|contains-dairy|contains-gluten">
Recipe: Classic Brioche (cuisine: french)
Section: Allergens
Contains wheat (gluten), egg and dairy.
</context>
```

**output**:

```json
{
  "can_substitute": false,
  "base_recipe_id": "chocolate-brioche",
  "title": "Chocolate Chip Brioche",
  "swaps": [],
  "ingredients": [],
  "method": "",
  "oven": "",
  "allergen_warning": "",
  "unsupported": "dairy free"
}
```

`sound`: [ ] true   [ ] false

---

## c03

**request**: `napa cabbage kimchi` -> `vegan, no fish or shellfish`

context blocks given (7):

```
<context chunk_id="napa-kimchi::structure::c002" recipe_id="napa-kimchi" source_file="card-02-napa-kimchi.md" section="ingredients" dietary_tags="contains-fish|contains-shellfish|gluten-free|dairy-free">
Recipe: Napa Cabbage Kimchi (cuisine: korean)
Section: Ingredients (rows 9-9 of 9)
| Ingredient | Weight | Baker's % |
| --- | --- | --- |
| Ginger, grated | 12 g | 1.2% |
</context>

<context chunk_id="napa-kimchi::structure::c003" recipe_id="napa-kimchi" source_file="card-02-napa-kimchi.md" section="method" dietary_tags="contains-fish|contains-shellfish|gluten-free|dairy-free">
Recipe: Napa Cabbage Kimchi (cuisine: korean)
Section: Method
Quarter the cabbage lengthways and work the coarse sea salt between every leaf, heaviest at
the stem end. Leave it to weep for two hours, turning the quarters once, then rinse three
times and drain stem-down for thirty minutes.

Stir the gochugaru into the cooled rice porridge and let it bloom for ten minutes before
adding the daikon, fish sauce, shrimp paste, garlic and ginger. Paste every leaf, then pack
into the jar and press down until the brine rises above the vegetables.

Keep the vegetables submerged below the brine for the whole ferment. Leave at 18 C for two
days until the jar smells sour and fizzes when tapped, then move it to the fridge.
</context>

<context chunk_id="napa-kimchi::structure::c004" recipe_id="napa-kimchi" source_file="card-02-napa-kimchi.md" section="allergens" dietary_tags="contains-fish|contains-shellfish|gluten-free|dairy-free">
Recipe: Napa Cabbage Kimchi (cuisine: korean)
Section: Allergens
Contains fish (fish sauce) and shellfish (salted shrimp paste). Not suitable for anyone with
a shellfish allergy. Gluten-free despite the name of the glutinous rice.
</context>

<context chunk_id="napa-kimchi::structure::c000" recipe_id="napa-kimchi" source_file="card-02-napa-kimchi.md" section="title" dietary_tags="contains-fish|contains-shellfish|gluten-free|dairy-free">
Recipe: Napa Cabbage Kimchi (cuisine: korean)
Section: Title
# Napa Cabbage Kimchi

A cold-fermented winter kimchi. Percentages are relative to the trimmed cabbage weight of
1000 g, not to the finished jar.
</context>

<context chunk_id="napa-kimchi::structure::c001" recipe_id="napa-kimchi" source_file="card-02-napa-kimchi.md" section="ingredients" dietary_tags="contains-fish|contains-shellfish|gluten-free|dairy-free">
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
</context>

<context chunk_id="red-sauerkraut::structure::c003" recipe_id="red-sauerkraut" source_file="card-04-red-cabbage-sauerkraut.md" section="allergens" dietary_tags="vegan|gluten-free|dairy-free">
Recipe: Red Cabbage Sauerkraut (cuisine: german)
Section: Allergens
No declared allergens. Made in a kitchen that also handles wheat, mustard and sesame.
</context>

<context chunk_id="red-sauerkraut::structure::c001" recipe_id="red-sauerkraut" source_file="card-04-red-cabbage-sauerkraut.md" section="ingredients" dietary_tags="vegan|gluten-free|dairy-free">
Recipe: Red Cabbage Sauerkraut (cuisine: german)
Section: Ingredients (rows 1-5 of 5)
| Ingredient | Weight | Baker's % |
| --- | --- | --- |
| Red cabbage, finely shredded | 1000 g | 100% |
| Fine sea salt | 20 g | 2% |
| Grated apple | 80 g | 8% |
| Caraway seed | 6 g | 0.6% |
| Juniper berries | 4 g | 0.4% |
</context>
```

**output**:

```json
{
  "can_substitute": false,
  "base_recipe_id": "napa-kimchi",
  "title": "Napa Cabbage Kimchi",
  "swaps": [],
  "ingredients": [],
  "method": "",
  "oven": "",
  "allergen_warning": "",
  "unsupported": "The provided context does not contain a vegan alternative for fish sauce or salted shrimp paste."
}
```

`sound`: [ ] true   [ ] false

---

## c04

**request**: `2kg country sourdough` -> `wholemeal`

context blocks given (7):

```
<context chunk_id="sourdough-2kg::structure::c001" recipe_id="sourdough-2kg" source_file="card-01-country-sourdough-2kg.md" section="ingredients" dietary_tags="vegan|dairy-free|nut-free">
Recipe: 2kg Country Sourdough (cuisine: european)
Section: Ingredients (rows 1-5 of 5)
| Ingredient | Weight | Baker's % |
| --- | --- | --- |
| Strong white bread flour | 950 g | 95% |
| Wholemeal rye flour | 50 g | 5% |
| Water (28 C) | 760 g | 76% |
| Stiff sourdough starter | 200 g | 20% |
| Fine sea salt | 18 g | 1.8% |
</context>

<context chunk_id="sourdough-2kg::structure::c003" recipe_id="sourdough-2kg" source_file="card-01-country-sourdough-2kg.md" section="method" dietary_tags="vegan|dairy-free|nut-free">
Recipe: 2kg Country Sourdough (cuisine: european)
Section: Method
Bake straight from the fridge at 250 C with steam for twenty minutes, then vent the oven and
drop to 230 C for a further twenty-five minutes until the crust is deeply coloured.
</context>

<context chunk_id="sourdough-2kg::structure::c000" recipe_id="sourdough-2kg" source_file="card-01-country-sourdough-2kg.md" section="title" dietary_tags="vegan|dairy-free|nut-free">
Recipe: 2kg Country Sourdough (cuisine: european)
Section: Title
# 2kg Country Sourdough

A two-day naturally leavened loaf. Baker's percentages are relative to the total flour
weight of 1000 g, so the white and rye flours together make 100%.
</context>

<context chunk_id="sourdough-2kg::structure::c004" recipe_id="sourdough-2kg" source_file="card-01-country-sourdough-2kg.md" section="allergens" dietary_tags="vegan|dairy-free|nut-free">
Recipe: 2kg Country Sourdough (cuisine: european)
Section: Allergens
Contains wheat and rye (gluten). Made in a kitchen that also handles sesame and tree nuts.
</context>

<context chunk_id="sourdough-2kg::structure::c002" recipe_id="sourdough-2kg" source_file="card-01-country-sourdough-2kg.md" section="method" dietary_tags="vegan|dairy-free|nut-free">
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
</context>

<context chunk_id="wholemeal-sourdough::structure::c002" recipe_id="wholemeal-sourdough" source_file="card-11-wholemeal-sourdough.md" section="method" dietary_tags="vegan|dairy-free|nut-free|contains-gluten">
Recipe: Wholemeal Sourdough (cuisine: european)
Section: Method
Whisk the starter into the water, add both flours, and mix to a shaggy mass. Autolyse for
one hour rather than forty minutes, because wholemeal bran drinks slowly and a short rest
leaves the dough gritty.

Add the salt and pinch it through. Bulk ferment at 24 C for three and a half hours, folding
every forty-five minutes. Wholemeal ferments faster than white, so watch the dough and not
the clock.

Shape, then cold retard at 4 C overnight. Bake at 240 C with steam for twenty minutes, then
vent and drop to 220 C for a further twenty-five.
</context>

<context chunk_id="wholemeal-sourdough::structure::c000" recipe_id="wholemeal-sourdough" source_file="card-11-wholemeal-sourdough.md" section="title" dietary_tags="vegan|dairy-free|nut-free|contains-gluten">
Recipe: Wholemeal Sourdough (cuisine: european)
Section: Title
# Wholemeal Sourdough

A high-extraction naturally leavened loaf. Baker's percentages are relative to the total
flour weight of 1000 g.
</context>
```

**output**:

```json
{
  "can_substitute": true,
  "base_recipe_id": "sourdough-2kg",
  "title": "2kg Country Sourdough",
  "swaps": [
    {
      "removed": "Strong white bread flour",
      "added": "Wholemeal flour",
      "evidence_chunk_id": "wholemeal-sourdough::structure::c002"
    }
  ],
  "ingredients": [
    {
      "name": "Wholemeal flour",
      "amount": "950 g",
      "source_chunk_id": "sourdough-2kg::structure::c001"
    },
    {
      "name": "Wholemeal rye flour",
      "amount": "50 g",
      "source_chunk_id": "sourdough-2kg::structure::c001"
    },
    {
      "name": "Water (28 C)",
      "amount": "760 g",
      "source_chunk_id": "sourdough-2kg::structure::c001"
    },
    {
      "name": "Stiff sourdough starter",
      "amount": "200 g",
      "source_chunk_id": "sourdough-2kg::structure::c001"
    },
    {
      "name": "Fine sea salt",
      "amount": "18 g",
      "source_chunk_id": "sourdough-2kg::structure::c001"
    }
  ],
  "method": "Whisk the starter into the water, add both flours, and mix to a shaggy mass. Autolyse for one hour rather than forty minutes, because wholemeal bran drinks slowly and a short rest leaves the dough gritty. Add the salt and pinch it through. Bulk ferment at 24 C for three and a half hours, folding every forty-five minutes. Wholemeal ferments faster than white, so watch the dough and not the clock. Shape, then cold retard at 4 C overnight. Bake at 240 C with steam for twenty minutes, then vent and drop to 220 C for a further twenty-five.",
  "oven": "240 C with steam for twenty minutes, then vent and drop to 220 C for a further twenty-five",
  "allergen_warning": "Contains wheat and rye (gluten). Made in a kitchen that also handles sesame and tree nuts.",
  "unsupported": ""
}
```

`sound`: [ ] true   [ ] false

---

## c05

**request**: `gluten-free sandwich loaf` -> `enriched, like a brioche`

context blocks given (8):

```
<context chunk_id="gf-sandwich-loaf::structure::c003" recipe_id="gf-sandwich-loaf" source_file="card-10-gluten-free-sandwich-loaf.md" section="allergens" dietary_tags="gluten-free|vegan|dairy-free">
Recipe: Gluten-Free Sandwich Loaf (cuisine: european)
Section: Allergens
Gluten free, provided the flour blend is certified. No egg or dairy.
</context>

<context chunk_id="gf-sandwich-loaf::structure::c000" recipe_id="gf-sandwich-loaf" source_file="card-10-gluten-free-sandwich-loaf.md" section="title" dietary_tags="gluten-free|vegan|dairy-free">
Recipe: Gluten-Free Sandwich Loaf (cuisine: european)
Section: Title
# Gluten-Free Sandwich Loaf

A lean tin loaf. Baker's percentages are relative to the 500 g flour blend.
</context>

<context chunk_id="gf-sandwich-loaf::structure::c001" recipe_id="gf-sandwich-loaf" source_file="card-10-gluten-free-sandwich-loaf.md" section="ingredients" dietary_tags="gluten-free|vegan|dairy-free">
Recipe: Gluten-Free Sandwich Loaf (cuisine: european)
Section: Ingredients (rows 1-7 of 7)
| Ingredient | Weight | Baker's % |
| --- | --- | --- |
| Gluten-free flour blend | 500 g | 100% |
| Xanthan gum | 10 g | 2% |
| Psyllium husk | 15 g | 3% |
| Instant dried yeast | 7 g | 1.4% |
| Fine sea salt | 10 g | 2% |
| Water (30 C) | 400 g | 80% |
| Olive oil | 30 g | 6% |
</context>

<context chunk_id="gf-sandwich-loaf::structure::c002" recipe_id="gf-sandwich-loaf" source_file="card-10-gluten-free-sandwich-loaf.md" section="method" dietary_tags="gluten-free|vegan|dairy-free">
Recipe: Gluten-Free Sandwich Loaf (cuisine: european)
Section: Method
Whisk the flour blend, xanthan gum, psyllium husk, yeast and salt together dry so both gums
disperse before they meet water. Psyllium hydrates far faster than xanthan, so skipping the
dry mix leaves you picking gel lumps out of the batter.

Add the warm water and oil, beat for four minutes, then rest the batter for twenty so the
psyllium sets up. It should hold a peak rather than pour.

Scrape into a lined tin, prove until risen by half, and bake at 200 C for 45 minutes.
</context>

<context chunk_id="gf-brioche::structure::c001" recipe_id="gf-brioche" source_file="card-07-gluten-free-brioche.md" section="ingredients" dietary_tags="gluten-free|contains-egg|contains-dairy">
Recipe: Gluten-Free Brioche (cuisine: french)
Section: Ingredients (rows 1-8 of 8)
| Ingredient | Weight | Baker's % |
| --- | --- | --- |
| Gluten-free flour blend | 500 g | 100% |
| Xanthan gum | 6 g | 1.2% |
| Caster sugar | 60 g | 12% |
| Instant dried yeast | 8 g | 1.6% |
| Fine sea salt | 9 g | 1.8% |
| Whole eggs | 250 g | 50% |
| Whole milk (32 C) | 150 g | 30% |
| Unsalted butter, softened | 175 g | 35% |
</context>

<context chunk_id="gf-brioche::structure::c000" recipe_id="gf-brioche" source_file="card-07-gluten-free-brioche.md" section="title" dietary_tags="gluten-free|contains-egg|contains-dairy">
Recipe: Gluten-Free Brioche (cuisine: french)
Section: Title
# Gluten-Free Brioche

An enriched overnight dough. Baker's percentages are relative to the 500 g flour blend.
</context>

<context chunk_id="lemon-drizzle-cake::structure::c003" recipe_id="lemon-drizzle-cake" source_file="lemon-drizzle-cake.md" section="allergens" dietary_tags="vegetarian|contains-egg|contains-dairy">
Recipe: Lemon Drizzle Loaf (cuisine: british)
Section: Allergens
Contains wheat (gluten), egg and dairy.
</context>

<context chunk_id="sourdough-2kg::structure::c000" recipe_id="sourdough-2kg" source_file="card-01-country-sourdough-2kg.md" section="title" dietary_tags="vegan|dairy-free|nut-free">
Recipe: 2kg Country Sourdough (cuisine: european)
Section: Title
# 2kg Country Sourdough

A two-day naturally leavened loaf. Baker's percentages are relative to the total flour
weight of 1000 g, so the white and rye flours together make 100%.
</context>
```

**output**:

```json
{
  "can_substitute": false,
  "base_recipe_id": "gf-sandwich-loaf",
  "title": "Gluten-Free Sandwich Loaf",
  "swaps": [],
  "ingredients": [],
  "method": "",
  "oven": "",
  "allergen_warning": "",
  "unsupported": "The archive does not provide a method or ingredient list to transform a lean sandwich loaf into an enriched brioche-style dough."
}
```

`sound`: [ ] true   [ ] false

---

## c06

**request**: `chicken tikka masala` -> `vegan`

context blocks given (6):

```
<context chunk_id="chicken-tikka-masala::structure::c000" recipe_id="chicken-tikka-masala" source_file="chicken-tikka-masala.md" section="title" dietary_tags="gluten-free|contains-dairy">
Recipe: Chicken Tikka Masala (cuisine: indian)
Section: Title
# Chicken Tikka Masala
</context>

<context chunk_id="chicken-tikka-masala::structure::c001" recipe_id="chicken-tikka-masala" source_file="chicken-tikka-masala.md" section="ingredients" dietary_tags="gluten-free|contains-dairy">
Recipe: Chicken Tikka Masala (cuisine: indian)
Section: Ingredients (rows 1-8 of 13)
| Ingredient | Weight | Notes |
| --- | --- | --- |
| Chicken thigh, boneless | 900 g | 4 cm pieces |
| Full fat yoghurt | 250 g | for the marinade |
| Double cream | 150 g | |
| Tinned plum tomatoes | 400 g | |
| Brown onion | 250 g | diced |
| Ghee | 50 g | |
| Ginger, grated | 25 g | |
| Garlic, crushed | 20 g | |
</context>

<context chunk_id="chicken-tikka-masala::structure::c004" recipe_id="chicken-tikka-masala" source_file="chicken-tikka-masala.md" section="allergens" dietary_tags="gluten-free|contains-dairy">
Recipe: Chicken Tikka Masala (cuisine: indian)
Section: Allergens
Contains dairy (yoghurt, cream, ghee). Naturally gluten free.
</context>

<context chunk_id="chicken-tikka-masala::structure::c002" recipe_id="chicken-tikka-masala" source_file="chicken-tikka-masala.md" section="ingredients" dietary_tags="gluten-free|contains-dairy">
Recipe: Chicken Tikka Masala (cuisine: indian)
Section: Ingredients (rows 9-13 of 13)
| Ingredient | Weight | Notes |
| --- | --- | --- |
| Garam masala | 10 g | |
| Ground turmeric | 5 g | |
| Kashmiri chilli powder | 8 g | for colour |
| Fine sea salt | 12 g | |
| Kasoori methi | 4 g | crushed, at the end |
</context>

<context chunk_id="chicken-tikka-masala::structure::c003" recipe_id="chicken-tikka-masala" source_file="chicken-tikka-masala.md" section="method" dietary_tags="gluten-free|contains-dairy">
Recipe: Chicken Tikka Masala (cuisine: indian)
Section: Method
Marinate the chicken in the yoghurt with half the ginger, garlic and spices for at least
four hours, ideally overnight. The acid in the yoghurt does the tenderising; more than
twenty-four hours and the texture turns mealy.

Thread onto skewers and grill hard until the edges char in places. You want colour, not
doneness — the pieces finish in the sauce.

Soften the onion in the ghee, add the remaining ginger, garlic and spices, then the tomatoes.
Cook until thick and glossy, blend smooth, and return to the pan. Add the grilled chicken
and simmer for ten minutes, then stir in the cream and the crushed kasoori methi off the
heat.
</context>

<context chunk_id="chana-masala::structure::c001" recipe_id="chana-masala" source_file="chana-masala.md" section="ingredients" dietary_tags="vegan|gluten-free|dairy-free">
Recipe: Chana Masala (cuisine: indian)
Section: Ingredients (rows 1-8 of 11)
| Ingredient | Weight | Notes |
| --- | --- | --- |
| Dried chickpeas | 400 g | soaked overnight |
| Brown onion, diced | 300 g | |
| Tinned plum tomatoes | 400 g | crushed by hand |
| Sunflower oil | 45 g | |
| Ginger, grated | 25 g | |
| Garlic, crushed | 20 g | |
| Ground cumin | 8 g | |
| Ground coriander | 8 g | |
</context>
```

**output**:

```json
{
  "can_substitute": true,
  "base_recipe_id": "chicken-tikka-masala",
  "title": "Vegan Chicken Tikka Masala",
  "swaps": [
    {
      "removed": "Chicken thigh, boneless",
      "added": "Dried chickpeas",
      "evidence_chunk_id": "chana-masala::structure::c001"
    },
    {
      "removed": "Full fat yoghurt",
      "added": "None",
      "evidence_chunk_id": "chana-masala::structure::c001"
    },
    {
      "removed": "Double cream",
      "added": "None",
      "evidence_chunk_id": "chana-masala::structure::c001"
    },
    {
      "removed": "Ghee",
      "added": "Sunflower oil",
      "evidence_chunk_id": "chana-masala::structure::c001"
    }
  ],
  "ingredients": [
    {
      "name": "Dried chickpeas",
      "amount": "400 g",
      "source_chunk_id": "chana-masala::structure::c001"
    },
    {
      "name": "Tinned plum tomatoes",
      "amount": "400 g",
      "source_chunk_id": "chicken-tikka-masala::structure::c001"
    },
    {
      "name": "Brown onion",
      "amount": "250 g",
      "source_chunk_id": "chicken-tikka-masala::structure::c001"
    },
    {
      "name": "Sunflower oil",
      "amount": "45 g",
      "source_chunk_id": "chana-masala::structure::c001"
    },
    {
      "name": "Ginger, grated",
      "amount": "25 g",
      "source_chunk_id": "chicken-tikka-masala::structure::c001"
    },
    {
      "name": "Garlic, crushed",
      "amount": "20 g",
      "source_chunk_id": "chicken-tikka-masala::structure::c001"
    },
    {
      "name": "Garam masala",
      "amount": "10 g",
      "source_chunk_id": "chicken-tikka-masala::structure::c002"
    },
    {
      "name": "Ground turmeric",
      "amount": "5 g",
      "source_chunk_id": "chicken-tikka-masala::structure::c002"
    },
    {
      "name": "Kashmiri chilli powder",
      "amount": "8 g",
      "source_chunk_id": "chicken-tikka-masala::structure::c002"
    },
    {
      "name": "Fine sea salt",
      "amount": "12 g",
      "source_chunk_id": "chicken-tikka-masala::structure::c002"
    },
    {
      "name": "Kasoori methi",
      "amount": "4 g",
      "source_chunk_id": "chicken-tikka-masala::structure::c002"
    }
  ],
  "method": "Soften the onion in the sunflower oil, add the ginger, garlic and spices, then the tomatoes. Cook until thick and glossy, blend smooth, and return to the pan. Add the chickpeas and simmer for ten minutes, then stir in the crushed kasoori methi off the heat.",
  "oven": "",
  "allergen_warning": "The provided context does not state this recipe is free of any allergens.",
  "unsupported": ""
}
```

`sound`: [ ] true   [ ] false

---

## c09

**request**: `light rye sourdough` -> `higher hydration`

context blocks given (6):

```
<context chunk_id="rye-sourdough::structure::c002" recipe_id="rye-sourdough" source_file="card-12-light-rye-sourdough.md" section="method" dietary_tags="vegan|dairy-free|nut-free|contains-gluten">
Recipe: Light Rye Sourdough (cuisine: european)
Section: Method
Whisk the starter into the water, add both flours, and mix to a shaggy mass. Autolyse for
forty minutes. Rye carries no meaningful gluten, so handle the dough gently and expect it to
feel tackier than an all-white build.

Add the salt and pinch it through. Bulk ferment at 24 C for three hours with folds every
forty-five minutes, then shape tightly and cold retard at 4 C overnight.

Bake at 250 C with steam for twenty minutes, then vent and drop to 225 C for a further
twenty-five. Rye colours faster, so check at twenty.
</context>

<context chunk_id="rye-sourdough::structure::c003" recipe_id="rye-sourdough" source_file="card-12-light-rye-sourdough.md" section="allergens" dietary_tags="vegan|dairy-free|nut-free|contains-gluten">
Recipe: Light Rye Sourdough (cuisine: european)
Section: Allergens
Contains wheat and rye (gluten). Made in a kitchen that also handles sesame and tree nuts.
</context>

<context chunk_id="rye-sourdough::structure::c001" recipe_id="rye-sourdough" source_file="card-12-light-rye-sourdough.md" section="ingredients" dietary_tags="vegan|dairy-free|nut-free|contains-gluten">
Recipe: Light Rye Sourdough (cuisine: european)
Section: Ingredients (rows 1-5 of 5)
| Ingredient | Weight | Baker's % |
| --- | --- | --- |
| Strong white bread flour | 800 g | 80% |
| Dark rye flour | 200 g | 20% |
| Water (28 C) | 780 g | 78% |
| Stiff sourdough starter | 200 g | 20% |
| Fine sea salt | 19 g | 1.9% |
</context>

<context chunk_id="rye-sourdough::structure::c000" recipe_id="rye-sourdough" source_file="card-12-light-rye-sourdough.md" section="title" dietary_tags="vegan|dairy-free|nut-free|contains-gluten">
Recipe: Light Rye Sourdough (cuisine: european)
Section: Title
# Light Rye Sourdough

A twenty percent rye naturally leavened loaf. Baker's percentages are relative to the total
flour weight of 1000 g.
</context>

<context chunk_id="sourdough-2kg::structure::c000" recipe_id="sourdough-2kg" source_file="card-01-country-sourdough-2kg.md" section="title" dietary_tags="vegan|dairy-free|nut-free">
Recipe: 2kg Country Sourdough (cuisine: european)
Section: Title
# 2kg Country Sourdough

A two-day naturally leavened loaf. Baker's percentages are relative to the total flour
weight of 1000 g, so the white and rye flours together make 100%.
</context>

<context chunk_id="sourdough-2kg::structure::c001" recipe_id="sourdough-2kg" source_file="card-01-country-sourdough-2kg.md" section="ingredients" dietary_tags="vegan|dairy-free|nut-free">
Recipe: 2kg Country Sourdough (cuisine: european)
Section: Ingredients (rows 1-5 of 5)
| Ingredient | Weight | Baker's % |
| --- | --- | --- |
| Strong white bread flour | 950 g | 95% |
| Wholemeal rye flour | 50 g | 5% |
| Water (28 C) | 760 g | 76% |
| Stiff sourdough starter | 200 g | 20% |
| Fine sea salt | 18 g | 1.8% |
</context>
```

**output**:

```json
{
  "can_substitute": false,
  "base_recipe_id": "rye-sourdough",
  "title": "Light Rye Sourdough",
  "swaps": [],
  "ingredients": [],
  "method": "",
  "oven": "",
  "allergen_warning": "",
  "unsupported": "The provided context does not contain information on how to adjust hydration levels for the Light Rye Sourdough recipe."
}
```

`sound`: [ ] true   [ ] false

---

## c11

**request**: `classic brioche` -> `gluten free, and halve it to 250 g flour`

context blocks given (11):

```
<context chunk_id="gf-brioche::structure::c000" recipe_id="gf-brioche" source_file="card-07-gluten-free-brioche.md" section="title" dietary_tags="gluten-free|contains-egg|contains-dairy">
Recipe: Gluten-Free Brioche (cuisine: french)
Section: Title
# Gluten-Free Brioche

An enriched overnight dough. Baker's percentages are relative to the 500 g flour blend.
</context>

<context chunk_id="gf-brioche::structure::c001" recipe_id="gf-brioche" source_file="card-07-gluten-free-brioche.md" section="ingredients" dietary_tags="gluten-free|contains-egg|contains-dairy">
Recipe: Gluten-Free Brioche (cuisine: french)
Section: Ingredients (rows 1-8 of 8)
| Ingredient | Weight | Baker's % |
| --- | --- | --- |
| Gluten-free flour blend | 500 g | 100% |
| Xanthan gum | 6 g | 1.2% |
| Caster sugar | 60 g | 12% |
| Instant dried yeast | 8 g | 1.6% |
| Fine sea salt | 9 g | 1.8% |
| Whole eggs | 250 g | 50% |
| Whole milk (32 C) | 150 g | 30% |
| Unsalted butter, softened | 175 g | 35% |
</context>

<context chunk_id="gf-brioche::structure::c002" recipe_id="gf-brioche" source_file="card-07-gluten-free-brioche.md" section="method" dietary_tags="gluten-free|contains-egg|contains-dairy">
Recipe: Gluten-Free Brioche (cuisine: french)
Section: Method
Whisk the flour blend, xanthan gum, sugar, yeast and salt together dry, so the gum disperses
before it meets any liquid. Lumped gum turns the crumb slimy and no amount of mixing later
will fix it.

Beat in the eggs and warm milk until the batter climbs the paddle, then add the softened
butter in five additions, waiting for each to disappear. The dough stays a thick batter
rather than a ball, which is normal without gluten.

Chill overnight at 4 C. Scale into a lined tin the next morning, prove until risen by half,
and bake at 180 C for 35 minutes.
</context>

<context chunk_id="gf-brioche::structure::c003" recipe_id="gf-brioche" source_file="card-07-gluten-free-brioche.md" section="allergens" dietary_tags="gluten-free|contains-egg|contains-dairy">
Recipe: Gluten-Free Brioche (cuisine: french)
Section: Allergens
Contains egg and dairy. Gluten free, provided the flour blend is certified.
</context>

<context chunk_id="classic-brioche::structure::c002" recipe_id="classic-brioche" source_file="card-08-classic-brioche.md" section="method" dietary_tags="contains-egg|contains-dairy|contains-gluten">
Recipe: Classic Brioche (cuisine: french)
Section: Method
Whisk the flour, sugar, yeast and salt together dry, then beat in the eggs and warm milk
until the dough climbs the hook and cleans the bowl.

Add the softened butter in five additions, waiting for each to disappear before the next.
The dough should end up glossy and slack enough to fall from the hook in a sheet.

Chill overnight at 4 C. Scale into a lined tin the next morning, prove until risen by half,
and bake at 180 C for 35 minutes.
</context>

<context chunk_id="classic-brioche::structure::c000" recipe_id="classic-brioche" source_file="card-08-classic-brioche.md" section="title" dietary_tags="contains-egg|contains-dairy|contains-gluten">
Recipe: Classic Brioche (cuisine: french)
Section: Title
# Classic Brioche

An enriched overnight dough. Baker's percentages are relative to the 500 g of flour.
</context>

<context chunk_id="classic-brioche::structure::c003" recipe_id="classic-brioche" source_file="card-08-classic-brioche.md" section="allergens" dietary_tags="contains-egg|contains-dairy|contains-gluten">
Recipe: Classic Brioche (cuisine: french)
Section: Allergens
Contains wheat (gluten), egg and dairy.
</context>

<context chunk_id="chocolate-brioche::structure::c003" recipe_id="chocolate-brioche" source_file="card-09-chocolate-brioche.md" section="allergens" dietary_tags="contains-egg|contains-dairy|contains-gluten|contains-soy">
Recipe: Chocolate Chip Brioche (cuisine: french)
Section: Allergens
Contains wheat (gluten), egg, dairy and soy (from the chocolate).
</context>

<context chunk_id="classic-brioche::structure::c001" recipe_id="classic-brioche" source_file="card-08-classic-brioche.md" section="ingredients" dietary_tags="contains-egg|contains-dairy|contains-gluten">
Recipe: Classic Brioche (cuisine: french)
Section: Ingredients (rows 1-7 of 7)
| Ingredient | Weight | Baker's % |
| --- | --- | --- |
| Strong white bread flour | 500 g | 100% |
| Caster sugar | 60 g | 12% |
| Instant dried yeast | 8 g | 1.6% |
| Fine sea salt | 9 g | 1.8% |
| Whole eggs | 250 g | 50% |
| Whole milk (32 C) | 100 g | 20% |
| Unsalted butter, softened | 250 g | 50% |
</context>

<context chunk_id="chocolate-brioche::structure::c002" recipe_id="chocolate-brioche" source_file="card-09-chocolate-brioche.md" section="method" dietary_tags="contains-egg|contains-dairy|contains-gluten|contains-soy">
Recipe: Chocolate Chip Brioche (cuisine: french)
Section: Method
Whisk the flour, sugar, yeast and salt together dry, then beat in the eggs and warm milk
until the dough climbs the hook and cleans the bowl.

Add the softened butter in five additions, waiting for each to disappear before the next.
Fold the chocolate chips through by hand at the very end, or the paddle will smash them into
the crumb and grey the whole loaf.

Chill overnight at 4 C. Scale into a lined tin the next morning, prove until risen by half,
and bake at 180 C for 35 minutes.
</context>

<context chunk_id="chocolate-brioche::structure::c000" recipe_id="chocolate-brioche" source_file="card-09-chocolate-brioche.md" section="title" dietary_tags="contains-egg|contains-dairy|contains-gluten|contains-soy">
Recipe: Chocolate Chip Brioche (cuisine: french)
Section: Title
# Chocolate Chip Brioche

An enriched overnight dough. Baker's percentages are relative to the 500 g of flour.
</context>
```

**output**:

```json
{
  "can_substitute": false,
  "base_recipe_id": "classic-brioche",
  "title": "Classic Brioche",
  "swaps": [],
  "ingredients": [],
  "method": "",
  "oven": "",
  "allergen_warning": "",
  "unsupported": "I cannot ground the request to make the recipe gluten-free or to halve the recipe to 250 g of flour. While the archive contains a gluten-free brioche recipe, it does not provide instructions or evidence for converting the classic brioche recipe to be gluten-free, nor does it provide a mechanism for scaling the recipe quantities."
}
```

`sound`: [ ] true   [ ] false

---

## c12

**request**: `2kg country sourdough` -> `wholemeal, scaled to 500 g total flour`

context blocks given (8):

```
<context chunk_id="wholemeal-sourdough::structure::c001" recipe_id="wholemeal-sourdough" source_file="card-11-wholemeal-sourdough.md" section="ingredients" dietary_tags="vegan|dairy-free|nut-free|contains-gluten">
Recipe: Wholemeal Sourdough (cuisine: european)
Section: Ingredients (rows 1-5 of 5)
| Ingredient | Weight | Baker's % |
| --- | --- | --- |
| Wholemeal flour | 700 g | 70% |
| Strong white bread flour | 300 g | 30% |
| Water (28 C) | 800 g | 80% |
| Stiff sourdough starter | 200 g | 20% |
| Fine sea salt | 20 g | 2% |
</context>

<context chunk_id="sourdough-2kg::structure::c001" recipe_id="sourdough-2kg" source_file="card-01-country-sourdough-2kg.md" section="ingredients" dietary_tags="vegan|dairy-free|nut-free">
Recipe: 2kg Country Sourdough (cuisine: european)
Section: Ingredients (rows 1-5 of 5)
| Ingredient | Weight | Baker's % |
| --- | --- | --- |
| Strong white bread flour | 950 g | 95% |
| Wholemeal rye flour | 50 g | 5% |
| Water (28 C) | 760 g | 76% |
| Stiff sourdough starter | 200 g | 20% |
| Fine sea salt | 18 g | 1.8% |
</context>

<context chunk_id="sourdough-2kg::structure::c003" recipe_id="sourdough-2kg" source_file="card-01-country-sourdough-2kg.md" section="method" dietary_tags="vegan|dairy-free|nut-free">
Recipe: 2kg Country Sourdough (cuisine: european)
Section: Method
Bake straight from the fridge at 250 C with steam for twenty minutes, then vent the oven and
drop to 230 C for a further twenty-five minutes until the crust is deeply coloured.
</context>

<context chunk_id="sourdough-2kg::structure::c000" recipe_id="sourdough-2kg" source_file="card-01-country-sourdough-2kg.md" section="title" dietary_tags="vegan|dairy-free|nut-free">
Recipe: 2kg Country Sourdough (cuisine: european)
Section: Title
# 2kg Country Sourdough

A two-day naturally leavened loaf. Baker's percentages are relative to the total flour
weight of 1000 g, so the white and rye flours together make 100%.
</context>

<context chunk_id="wholemeal-sourdough::structure::c000" recipe_id="wholemeal-sourdough" source_file="card-11-wholemeal-sourdough.md" section="title" dietary_tags="vegan|dairy-free|nut-free|contains-gluten">
Recipe: Wholemeal Sourdough (cuisine: european)
Section: Title
# Wholemeal Sourdough

A high-extraction naturally leavened loaf. Baker's percentages are relative to the total
flour weight of 1000 g.
</context>

<context chunk_id="sourdough-2kg::structure::c004" recipe_id="sourdough-2kg" source_file="card-01-country-sourdough-2kg.md" section="allergens" dietary_tags="vegan|dairy-free|nut-free">
Recipe: 2kg Country Sourdough (cuisine: european)
Section: Allergens
Contains wheat and rye (gluten). Made in a kitchen that also handles sesame and tree nuts.
</context>

<context chunk_id="sourdough-2kg::structure::c002" recipe_id="sourdough-2kg" source_file="card-01-country-sourdough-2kg.md" section="method" dietary_tags="vegan|dairy-free|nut-free">
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
</context>

<context chunk_id="wholemeal-sourdough::structure::c002" recipe_id="wholemeal-sourdough" source_file="card-11-wholemeal-sourdough.md" section="method" dietary_tags="vegan|dairy-free|nut-free|contains-gluten">
Recipe: Wholemeal Sourdough (cuisine: european)
Section: Method
Whisk the starter into the water, add both flours, and mix to a shaggy mass. Autolyse for
one hour rather than forty minutes, because wholemeal bran drinks slowly and a short rest
leaves the dough gritty.

Add the salt and pinch it through. Bulk ferment at 24 C for three and a half hours, folding
every forty-five minutes. Wholemeal ferments faster than white, so watch the dough and not
the clock.

Shape, then cold retard at 4 C overnight. Bake at 240 C with steam for twenty minutes, then
vent and drop to 220 C for a further twenty-five.
</context>
```

**output**:

```json
{
  "can_substitute": false,
  "base_recipe_id": "sourdough-2kg",
  "title": "2kg Country Sourdough",
  "swaps": [],
  "ingredients": [],
  "method": "",
  "oven": "",
  "allergen_warning": "",
  "unsupported": "The archive does not contain instructions or a mechanism to scale the recipe to 500 g total flour weight."
}
```

`sound`: [ ] true   [ ] false

---

## c13

**request**: `gluten-free sandwich loaf` -> `double the batch`

context blocks given (6):

```
<context chunk_id="gf-sandwich-loaf::structure::c003" recipe_id="gf-sandwich-loaf" source_file="card-10-gluten-free-sandwich-loaf.md" section="allergens" dietary_tags="gluten-free|vegan|dairy-free">
Recipe: Gluten-Free Sandwich Loaf (cuisine: european)
Section: Allergens
Gluten free, provided the flour blend is certified. No egg or dairy.
</context>

<context chunk_id="gf-sandwich-loaf::structure::c000" recipe_id="gf-sandwich-loaf" source_file="card-10-gluten-free-sandwich-loaf.md" section="title" dietary_tags="gluten-free|vegan|dairy-free">
Recipe: Gluten-Free Sandwich Loaf (cuisine: european)
Section: Title
# Gluten-Free Sandwich Loaf

A lean tin loaf. Baker's percentages are relative to the 500 g flour blend.
</context>

<context chunk_id="gf-sandwich-loaf::structure::c001" recipe_id="gf-sandwich-loaf" source_file="card-10-gluten-free-sandwich-loaf.md" section="ingredients" dietary_tags="gluten-free|vegan|dairy-free">
Recipe: Gluten-Free Sandwich Loaf (cuisine: european)
Section: Ingredients (rows 1-7 of 7)
| Ingredient | Weight | Baker's % |
| --- | --- | --- |
| Gluten-free flour blend | 500 g | 100% |
| Xanthan gum | 10 g | 2% |
| Psyllium husk | 15 g | 3% |
| Instant dried yeast | 7 g | 1.4% |
| Fine sea salt | 10 g | 2% |
| Water (30 C) | 400 g | 80% |
| Olive oil | 30 g | 6% |
</context>

<context chunk_id="gf-sandwich-loaf::structure::c002" recipe_id="gf-sandwich-loaf" source_file="card-10-gluten-free-sandwich-loaf.md" section="method" dietary_tags="gluten-free|vegan|dairy-free">
Recipe: Gluten-Free Sandwich Loaf (cuisine: european)
Section: Method
Whisk the flour blend, xanthan gum, psyllium husk, yeast and salt together dry so both gums
disperse before they meet water. Psyllium hydrates far faster than xanthan, so skipping the
dry mix leaves you picking gel lumps out of the batter.

Add the warm water and oil, beat for four minutes, then rest the batter for twenty so the
psyllium sets up. It should hold a peak rather than pour.

Scrape into a lined tin, prove until risen by half, and bake at 200 C for 45 minutes.
</context>

<context chunk_id="lemon-drizzle-cake::structure::c003" recipe_id="lemon-drizzle-cake" source_file="lemon-drizzle-cake.md" section="allergens" dietary_tags="vegetarian|contains-egg|contains-dairy">
Recipe: Lemon Drizzle Loaf (cuisine: british)
Section: Allergens
Contains wheat (gluten), egg and dairy.
</context>

<context chunk_id="sourdough-2kg::structure::c000" recipe_id="sourdough-2kg" source_file="card-01-country-sourdough-2kg.md" section="title" dietary_tags="vegan|dairy-free|nut-free">
Recipe: 2kg Country Sourdough (cuisine: european)
Section: Title
# 2kg Country Sourdough

A two-day naturally leavened loaf. Baker's percentages are relative to the total flour
weight of 1000 g, so the white and rye flours together make 100%.
</context>
```

**output**:

```json
{
  "can_substitute": false,
  "base_recipe_id": "gf-sandwich-loaf",
  "title": "Gluten-Free Sandwich Loaf",
  "swaps": [],
  "ingredients": [],
  "method": "",
  "oven": "",
  "allergen_warning": "",
  "unsupported": "The provided context does not contain instructions or grounding for scaling the batch size of the Gluten-Free Sandwich Loaf."
}
```

`sound`: [ ] true   [ ] false

---

## c14

**request**: `red cabbage sauerkraut` -> `made with 2 kg of cabbage instead of 1 kg`

context blocks given (7):

```
<context chunk_id="red-sauerkraut::structure::c003" recipe_id="red-sauerkraut" source_file="card-04-red-cabbage-sauerkraut.md" section="allergens" dietary_tags="vegan|gluten-free|dairy-free">
Recipe: Red Cabbage Sauerkraut (cuisine: german)
Section: Allergens
No declared allergens. Made in a kitchen that also handles wheat, mustard and sesame.
</context>

<context chunk_id="red-sauerkraut::structure::c001" recipe_id="red-sauerkraut" source_file="card-04-red-cabbage-sauerkraut.md" section="ingredients" dietary_tags="vegan|gluten-free|dairy-free">
Recipe: Red Cabbage Sauerkraut (cuisine: german)
Section: Ingredients (rows 1-5 of 5)
| Ingredient | Weight | Baker's % |
| --- | --- | --- |
| Red cabbage, finely shredded | 1000 g | 100% |
| Fine sea salt | 20 g | 2% |
| Grated apple | 80 g | 8% |
| Caraway seed | 6 g | 0.6% |
| Juniper berries | 4 g | 0.4% |
</context>

<context chunk_id="red-sauerkraut::structure::c002" recipe_id="red-sauerkraut" source_file="card-04-red-cabbage-sauerkraut.md" section="method" dietary_tags="vegan|gluten-free|dairy-free">
Recipe: Red Cabbage Sauerkraut (cuisine: german)
Section: Method
Scatter the fine sea salt over the shredded cabbage and massage it hard for ten minutes.
The cabbage will collapse to roughly half its volume and a purple brine will pool in the
bowl; that liquid is the ferment, so none of it is thrown away.

Fold through the grated apple, caraway and juniper, then pack into the jar a fistful at a
time, tamping each layer until the brine rises above the vegetables.

Keep the vegetables submerged below the brine for the whole ferment. Leave at 18 C for
three to four weeks, releasing the lid every few days for the first week. The colour shifts
from blue-purple to bright magenta as the acidity climbs, which is the clearest sign it is
working.
</context>

<context chunk_id="red-sauerkraut::structure::c000" recipe_id="red-sauerkraut" source_file="card-04-red-cabbage-sauerkraut.md" section="title" dietary_tags="vegan|gluten-free|dairy-free">
Recipe: Red Cabbage Sauerkraut (cuisine: german)
Section: Title
# Red Cabbage Sauerkraut

A dry-salted kraut that draws its own brine. Percentages are relative to the shredded
cabbage weight of 1000 g.
</context>

<context chunk_id="napa-kimchi::structure::c001" recipe_id="napa-kimchi" source_file="card-02-napa-kimchi.md" section="ingredients" dietary_tags="contains-fish|contains-shellfish|gluten-free|dairy-free">
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
</context>

<context chunk_id="shakshuka::structure::c002" recipe_id="shakshuka" source_file="shakshuka.md" section="ingredients" dietary_tags="vegetarian|gluten-free|contains-egg">
Recipe: Red Pepper Shakshuka (cuisine: middle-eastern)
Section: Ingredients (rows 9-10 of 10)
| Ingredient | Weight | Notes |
| --- | --- | --- |
| Eggs | 6 whole | room temperature |
| Flat leaf parsley | 15 g | to finish |
</context>

<context chunk_id="napa-kimchi::structure::c002" recipe_id="napa-kimchi" source_file="card-02-napa-kimchi.md" section="ingredients" dietary_tags="contains-fish|contains-shellfish|gluten-free|dairy-free">
Recipe: Napa Cabbage Kimchi (cuisine: korean)
Section: Ingredients (rows 9-9 of 9)
| Ingredient | Weight | Baker's % |
| --- | --- | --- |
| Ginger, grated | 12 g | 1.2% |
</context>
```

**output**:

```json
{
  "can_substitute": false,
  "base_recipe_id": "red-sauerkraut",
  "title": "Red Cabbage Sauerkraut",
  "swaps": [],
  "ingredients": [],
  "method": "",
  "oven": "",
  "allergen_warning": "",
  "unsupported": "Scaling the recipe to 2 kg of cabbage"
}
```

`sound`: [ ] true   [ ] false

---

## c15

**request**: `chocolate brioche` -> `plain, no chocolate`

context blocks given (7):

```
<context chunk_id="chocolate-brioche::structure::c002" recipe_id="chocolate-brioche" source_file="card-09-chocolate-brioche.md" section="method" dietary_tags="contains-egg|contains-dairy|contains-gluten|contains-soy">
Recipe: Chocolate Chip Brioche (cuisine: french)
Section: Method
Whisk the flour, sugar, yeast and salt together dry, then beat in the eggs and warm milk
until the dough climbs the hook and cleans the bowl.

Add the softened butter in five additions, waiting for each to disappear before the next.
Fold the chocolate chips through by hand at the very end, or the paddle will smash them into
the crumb and grey the whole loaf.

Chill overnight at 4 C. Scale into a lined tin the next morning, prove until risen by half,
and bake at 180 C for 35 minutes.
</context>

<context chunk_id="chocolate-brioche::structure::c000" recipe_id="chocolate-brioche" source_file="card-09-chocolate-brioche.md" section="title" dietary_tags="contains-egg|contains-dairy|contains-gluten|contains-soy">
Recipe: Chocolate Chip Brioche (cuisine: french)
Section: Title
# Chocolate Chip Brioche

An enriched overnight dough. Baker's percentages are relative to the 500 g of flour.
</context>

<context chunk_id="chocolate-brioche::structure::c001" recipe_id="chocolate-brioche" source_file="card-09-chocolate-brioche.md" section="ingredients" dietary_tags="contains-egg|contains-dairy|contains-gluten|contains-soy">
Recipe: Chocolate Chip Brioche (cuisine: french)
Section: Ingredients (rows 1-8 of 8)
| Ingredient | Weight | Baker's % |
| --- | --- | --- |
| Strong white bread flour | 500 g | 100% |
| Caster sugar | 70 g | 14% |
| Instant dried yeast | 8 g | 1.6% |
| Fine sea salt | 9 g | 1.8% |
| Whole eggs | 250 g | 50% |
| Whole milk (32 C) | 100 g | 20% |
| Unsalted butter, softened | 225 g | 45% |
| Dark chocolate chips | 150 g | 30% |
</context>

<context chunk_id="chocolate-brioche::structure::c003" recipe_id="chocolate-brioche" source_file="card-09-chocolate-brioche.md" section="allergens" dietary_tags="contains-egg|contains-dairy|contains-gluten|contains-soy">
Recipe: Chocolate Chip Brioche (cuisine: french)
Section: Allergens
Contains wheat (gluten), egg, dairy and soy (from the chocolate).
</context>

<context chunk_id="classic-brioche::structure::c002" recipe_id="classic-brioche" source_file="card-08-classic-brioche.md" section="method" dietary_tags="contains-egg|contains-dairy|contains-gluten">
Recipe: Classic Brioche (cuisine: french)
Section: Method
Whisk the flour, sugar, yeast and salt together dry, then beat in the eggs and warm milk
until the dough climbs the hook and cleans the bowl.

Add the softened butter in five additions, waiting for each to disappear before the next.
The dough should end up glossy and slack enough to fall from the hook in a sheet.

Chill overnight at 4 C. Scale into a lined tin the next morning, prove until risen by half,
and bake at 180 C for 35 minutes.
</context>

<context chunk_id="classic-brioche::structure::c001" recipe_id="classic-brioche" source_file="card-08-classic-brioche.md" section="ingredients" dietary_tags="contains-egg|contains-dairy|contains-gluten">
Recipe: Classic Brioche (cuisine: french)
Section: Ingredients (rows 1-7 of 7)
| Ingredient | Weight | Baker's % |
| --- | --- | --- |
| Strong white bread flour | 500 g | 100% |
| Caster sugar | 60 g | 12% |
| Instant dried yeast | 8 g | 1.6% |
| Fine sea salt | 9 g | 1.8% |
| Whole eggs | 250 g | 50% |
| Whole milk (32 C) | 100 g | 20% |
| Unsalted butter, softened | 250 g | 50% |
</context>

<context chunk_id="gf-brioche::structure::c002" recipe_id="gf-brioche" source_file="card-07-gluten-free-brioche.md" section="method" dietary_tags="gluten-free|contains-egg|contains-dairy">
Recipe: Gluten-Free Brioche (cuisine: french)
Section: Method
Whisk the flour blend, xanthan gum, sugar, yeast and salt together dry, so the gum disperses
before it meets any liquid. Lumped gum turns the crumb slimy and no amount of mixing later
will fix it.

Beat in the eggs and warm milk until the batter climbs the paddle, then add the softened
butter in five additions, waiting for each to disappear. The dough stays a thick batter
rather than a ball, which is normal without gluten.

Chill overnight at 4 C. Scale into a lined tin the next morning, prove until risen by half,
and bake at 180 C for 35 minutes.
</context>
```

**output**:

```json
{
  "can_substitute": true,
  "base_recipe_id": "chocolate-brioche",
  "title": "Brioche",
  "swaps": [
    {
      "removed": "Dark chocolate chips",
      "added": "None",
      "evidence_chunk_id": "chocolate-brioche::structure::c001"
    }
  ],
  "ingredients": [
    {
      "name": "Strong white bread flour",
      "amount": "500 g",
      "source_chunk_id": "chocolate-brioche::structure::c001"
    },
    {
      "name": "Caster sugar",
      "amount": "70 g",
      "source_chunk_id": "chocolate-brioche::structure::c001"
    },
    {
      "name": "Instant dried yeast",
      "amount": "8 g",
      "source_chunk_id": "chocolate-brioche::structure::c001"
    },
    {
      "name": "Fine sea salt",
      "amount": "9 g",
      "source_chunk_id": "chocolate-brioche::structure::c001"
    },
    {
      "name": "Whole eggs",
      "amount": "250 g",
      "source_chunk_id": "chocolate-brioche::structure::c001"
    },
    {
      "name": "Whole milk (32 C)",
      "amount": "100 g",
      "source_chunk_id": "chocolate-brioche::structure::c001"
    },
    {
      "name": "Unsalted butter, softened",
      "amount": "225 g",
      "source_chunk_id": "chocolate-brioche::structure::c001"
    }
  ],
  "method": "Whisk the flour, sugar, yeast and salt together dry, then beat in the eggs and warm milk until the dough climbs the hook and cleans the bowl. Add the softened butter in five additions, waiting for each to disappear before the next. Chill overnight at 4 C. Scale into a lined tin the next morning, prove until risen by half, and bake at 180 C for 35 minutes.",
  "oven": "180 C",
  "allergen_warning": "Contains wheat (gluten), egg, and dairy.",
  "unsupported": ""
}
```

`sound`: [ ] true   [ ] false

---

## c16

**request**: `wholemeal sourdough` -> `light rye instead of wholemeal`

context blocks given (10):

```
<context chunk_id="rye-sourdough::structure::c003" recipe_id="rye-sourdough" source_file="card-12-light-rye-sourdough.md" section="allergens" dietary_tags="vegan|dairy-free|nut-free|contains-gluten">
Recipe: Light Rye Sourdough (cuisine: european)
Section: Allergens
Contains wheat and rye (gluten). Made in a kitchen that also handles sesame and tree nuts.
</context>

<context chunk_id="rye-sourdough::structure::c002" recipe_id="rye-sourdough" source_file="card-12-light-rye-sourdough.md" section="method" dietary_tags="vegan|dairy-free|nut-free|contains-gluten">
Recipe: Light Rye Sourdough (cuisine: european)
Section: Method
Whisk the starter into the water, add both flours, and mix to a shaggy mass. Autolyse for
forty minutes. Rye carries no meaningful gluten, so handle the dough gently and expect it to
feel tackier than an all-white build.

Add the salt and pinch it through. Bulk ferment at 24 C for three hours with folds every
forty-five minutes, then shape tightly and cold retard at 4 C overnight.

Bake at 250 C with steam for twenty minutes, then vent and drop to 225 C for a further
twenty-five. Rye colours faster, so check at twenty.
</context>

<context chunk_id="wholemeal-sourdough::structure::c002" recipe_id="wholemeal-sourdough" source_file="card-11-wholemeal-sourdough.md" section="method" dietary_tags="vegan|dairy-free|nut-free|contains-gluten">
Recipe: Wholemeal Sourdough (cuisine: european)
Section: Method
Whisk the starter into the water, add both flours, and mix to a shaggy mass. Autolyse for
one hour rather than forty minutes, because wholemeal bran drinks slowly and a short rest
leaves the dough gritty.

Add the salt and pinch it through. Bulk ferment at 24 C for three and a half hours, folding
every forty-five minutes. Wholemeal ferments faster than white, so watch the dough and not
the clock.

Shape, then cold retard at 4 C overnight. Bake at 240 C with steam for twenty minutes, then
vent and drop to 220 C for a further twenty-five.
</context>

<context chunk_id="wholemeal-sourdough::structure::c003" recipe_id="wholemeal-sourdough" source_file="card-11-wholemeal-sourdough.md" section="allergens" dietary_tags="vegan|dairy-free|nut-free|contains-gluten">
Recipe: Wholemeal Sourdough (cuisine: european)
Section: Allergens
Contains wheat (gluten). Made in a kitchen that also handles sesame and tree nuts.
</context>

<context chunk_id="rye-sourdough::structure::c001" recipe_id="rye-sourdough" source_file="card-12-light-rye-sourdough.md" section="ingredients" dietary_tags="vegan|dairy-free|nut-free|contains-gluten">
Recipe: Light Rye Sourdough (cuisine: european)
Section: Ingredients (rows 1-5 of 5)
| Ingredient | Weight | Baker's % |
| --- | --- | --- |
| Strong white bread flour | 800 g | 80% |
| Dark rye flour | 200 g | 20% |
| Water (28 C) | 780 g | 78% |
| Stiff sourdough starter | 200 g | 20% |
| Fine sea salt | 19 g | 1.9% |
</context>

<context chunk_id="rye-sourdough::structure::c000" recipe_id="rye-sourdough" source_file="card-12-light-rye-sourdough.md" section="title" dietary_tags="vegan|dairy-free|nut-free|contains-gluten">
Recipe: Light Rye Sourdough (cuisine: european)
Section: Title
# Light Rye Sourdough

A twenty percent rye naturally leavened loaf. Baker's percentages are relative to the total
flour weight of 1000 g.
</context>

<context chunk_id="wholemeal-sourdough::structure::c001" recipe_id="wholemeal-sourdough" source_file="card-11-wholemeal-sourdough.md" section="ingredients" dietary_tags="vegan|dairy-free|nut-free|contains-gluten">
Recipe: Wholemeal Sourdough (cuisine: european)
Section: Ingredients (rows 1-5 of 5)
| Ingredient | Weight | Baker's % |
| --- | --- | --- |
| Wholemeal flour | 700 g | 70% |
| Strong white bread flour | 300 g | 30% |
| Water (28 C) | 800 g | 80% |
| Stiff sourdough starter | 200 g | 20% |
| Fine sea salt | 20 g | 2% |
</context>

<context chunk_id="wholemeal-sourdough::structure::c000" recipe_id="wholemeal-sourdough" source_file="card-11-wholemeal-sourdough.md" section="title" dietary_tags="vegan|dairy-free|nut-free|contains-gluten">
Recipe: Wholemeal Sourdough (cuisine: european)
Section: Title
# Wholemeal Sourdough

A high-extraction naturally leavened loaf. Baker's percentages are relative to the total
flour weight of 1000 g.
</context>

<context chunk_id="sourdough-2kg::structure::c002" recipe_id="sourdough-2kg" source_file="card-01-country-sourdough-2kg.md" section="method" dietary_tags="vegan|dairy-free|nut-free">
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
</context>

<context chunk_id="sourdough-2kg::structure::c004" recipe_id="sourdough-2kg" source_file="card-01-country-sourdough-2kg.md" section="allergens" dietary_tags="vegan|dairy-free|nut-free">
Recipe: 2kg Country Sourdough (cuisine: european)
Section: Allergens
Contains wheat and rye (gluten). Made in a kitchen that also handles sesame and tree nuts.
</context>
```

**output**:

```json
{
  "can_substitute": true,
  "base_recipe_id": "wholemeal-sourdough",
  "title": "Light Rye Sourdough",
  "swaps": [
    {
      "removed": "Wholemeal flour",
      "added": "Strong white bread flour",
      "evidence_chunk_id": "rye-sourdough::structure::c001"
    },
    {
      "removed": "Strong white bread flour",
      "added": "Dark rye flour",
      "evidence_chunk_id": "rye-sourdough::structure::c001"
    }
  ],
  "ingredients": [
    {
      "name": "Strong white bread flour",
      "amount": "800 g",
      "source_chunk_id": "rye-sourdough::structure::c001"
    },
    {
      "name": "Dark rye flour",
      "amount": "200 g",
      "source_chunk_id": "rye-sourdough::structure::c001"
    },
    {
      "name": "Water (28 C)",
      "amount": "800 g",
      "source_chunk_id": "wholemeal-sourdough::structure::c001"
    },
    {
      "name": "Stiff sourdough starter",
      "amount": "200 g",
      "source_chunk_id": "wholemeal-sourdough::structure::c001"
    },
    {
      "name": "Fine sea salt",
      "amount": "20 g",
      "source_chunk_id": "wholemeal-sourdough::structure::c001"
    }
  ],
  "method": "Whisk the starter into the water, add both flours, and mix to a shaggy mass. Autolyse for forty minutes. Rye carries no meaningful gluten, so handle the dough gently and expect it to feel tackier than an all-white build. Add the salt and pinch it through. Bulk ferment at 24 C for three and a half hours, folding every forty-five minutes. Shape, then cold retard at 4 C overnight. Bake at 240 C with steam for twenty minutes, then vent and drop to 220 C for a further twenty-five.",
  "oven": "240 C with steam for twenty minutes, then vent and drop to 220 C for a further twenty-five",
  "allergen_warning": "Contains wheat and rye (gluten). Made in a kitchen that also handles sesame and tree nuts.",
  "unsupported": "The total flour weight of the base recipe is 1000 g, which matches the Light Rye Sourdough recipe, but the individual ingredient quantities differ from the base recipe. I have used the ingredient quantities from the base recipe while swapping the flour types as requested."
}
```

`sound`: [ ] true   [ ] false

---

## c17

**request**: `gluten-free brioche` -> `vegan, no eggs or dairy`

context blocks given (6):

```
<context chunk_id="gf-brioche::structure::c003" recipe_id="gf-brioche" source_file="card-07-gluten-free-brioche.md" section="allergens" dietary_tags="gluten-free|contains-egg|contains-dairy">
Recipe: Gluten-Free Brioche (cuisine: french)
Section: Allergens
Contains egg and dairy. Gluten free, provided the flour blend is certified.
</context>

<context chunk_id="gf-brioche::structure::c000" recipe_id="gf-brioche" source_file="card-07-gluten-free-brioche.md" section="title" dietary_tags="gluten-free|contains-egg|contains-dairy">
Recipe: Gluten-Free Brioche (cuisine: french)
Section: Title
# Gluten-Free Brioche

An enriched overnight dough. Baker's percentages are relative to the 500 g flour blend.
</context>

<context chunk_id="classic-brioche::structure::c003" recipe_id="classic-brioche" source_file="card-08-classic-brioche.md" section="allergens" dietary_tags="contains-egg|contains-dairy|contains-gluten">
Recipe: Classic Brioche (cuisine: french)
Section: Allergens
Contains wheat (gluten), egg and dairy.
</context>

<context chunk_id="gf-brioche::structure::c001" recipe_id="gf-brioche" source_file="card-07-gluten-free-brioche.md" section="ingredients" dietary_tags="gluten-free|contains-egg|contains-dairy">
Recipe: Gluten-Free Brioche (cuisine: french)
Section: Ingredients (rows 1-8 of 8)
| Ingredient | Weight | Baker's % |
| --- | --- | --- |
| Gluten-free flour blend | 500 g | 100% |
| Xanthan gum | 6 g | 1.2% |
| Caster sugar | 60 g | 12% |
| Instant dried yeast | 8 g | 1.6% |
| Fine sea salt | 9 g | 1.8% |
| Whole eggs | 250 g | 50% |
| Whole milk (32 C) | 150 g | 30% |
| Unsalted butter, softened | 175 g | 35% |
</context>

<context chunk_id="chocolate-brioche::structure::c003" recipe_id="chocolate-brioche" source_file="card-09-chocolate-brioche.md" section="allergens" dietary_tags="contains-egg|contains-dairy|contains-gluten|contains-soy">
Recipe: Chocolate Chip Brioche (cuisine: french)
Section: Allergens
Contains wheat (gluten), egg, dairy and soy (from the chocolate).
</context>

<context chunk_id="gf-brioche::structure::c002" recipe_id="gf-brioche" source_file="card-07-gluten-free-brioche.md" section="method" dietary_tags="gluten-free|contains-egg|contains-dairy">
Recipe: Gluten-Free Brioche (cuisine: french)
Section: Method
Whisk the flour blend, xanthan gum, sugar, yeast and salt together dry, so the gum disperses
before it meets any liquid. Lumped gum turns the crumb slimy and no amount of mixing later
will fix it.

Beat in the eggs and warm milk until the batter climbs the paddle, then add the softened
butter in five additions, waiting for each to disappear. The dough stays a thick batter
rather than a ball, which is normal without gluten.

Chill overnight at 4 C. Scale into a lined tin the next morning, prove until risen by half,
and bake at 180 C for 35 minutes.
</context>
```

**output**:

```json
{
  "can_substitute": false,
  "base_recipe_id": "gf-brioche",
  "title": "Gluten-Free Brioche",
  "swaps": [],
  "ingredients": [],
  "method": "",
  "oven": "",
  "allergen_warning": "",
  "unsupported": "vegan, no eggs or dairy"
}
```

`sound`: [ ] true   [ ] false

---

## c18

**request**: `classic brioche` -> `chocolate chip version`

context blocks given (8):

```
<context chunk_id="chocolate-brioche::structure::c002" recipe_id="chocolate-brioche" source_file="card-09-chocolate-brioche.md" section="method" dietary_tags="contains-egg|contains-dairy|contains-gluten|contains-soy">
Recipe: Chocolate Chip Brioche (cuisine: french)
Section: Method
Whisk the flour, sugar, yeast and salt together dry, then beat in the eggs and warm milk
until the dough climbs the hook and cleans the bowl.

Add the softened butter in five additions, waiting for each to disappear before the next.
Fold the chocolate chips through by hand at the very end, or the paddle will smash them into
the crumb and grey the whole loaf.

Chill overnight at 4 C. Scale into a lined tin the next morning, prove until risen by half,
and bake at 180 C for 35 minutes.
</context>

<context chunk_id="chocolate-brioche::structure::c000" recipe_id="chocolate-brioche" source_file="card-09-chocolate-brioche.md" section="title" dietary_tags="contains-egg|contains-dairy|contains-gluten|contains-soy">
Recipe: Chocolate Chip Brioche (cuisine: french)
Section: Title
# Chocolate Chip Brioche

An enriched overnight dough. Baker's percentages are relative to the 500 g of flour.
</context>

<context chunk_id="chocolate-brioche::structure::c001" recipe_id="chocolate-brioche" source_file="card-09-chocolate-brioche.md" section="ingredients" dietary_tags="contains-egg|contains-dairy|contains-gluten|contains-soy">
Recipe: Chocolate Chip Brioche (cuisine: french)
Section: Ingredients (rows 1-8 of 8)
| Ingredient | Weight | Baker's % |
| --- | --- | --- |
| Strong white bread flour | 500 g | 100% |
| Caster sugar | 70 g | 14% |
| Instant dried yeast | 8 g | 1.6% |
| Fine sea salt | 9 g | 1.8% |
| Whole eggs | 250 g | 50% |
| Whole milk (32 C) | 100 g | 20% |
| Unsalted butter, softened | 225 g | 45% |
| Dark chocolate chips | 150 g | 30% |
</context>

<context chunk_id="chocolate-brioche::structure::c003" recipe_id="chocolate-brioche" source_file="card-09-chocolate-brioche.md" section="allergens" dietary_tags="contains-egg|contains-dairy|contains-gluten|contains-soy">
Recipe: Chocolate Chip Brioche (cuisine: french)
Section: Allergens
Contains wheat (gluten), egg, dairy and soy (from the chocolate).
</context>

<context chunk_id="classic-brioche::structure::c002" recipe_id="classic-brioche" source_file="card-08-classic-brioche.md" section="method" dietary_tags="contains-egg|contains-dairy|contains-gluten">
Recipe: Classic Brioche (cuisine: french)
Section: Method
Whisk the flour, sugar, yeast and salt together dry, then beat in the eggs and warm milk
until the dough climbs the hook and cleans the bowl.

Add the softened butter in five additions, waiting for each to disappear before the next.
The dough should end up glossy and slack enough to fall from the hook in a sheet.

Chill overnight at 4 C. Scale into a lined tin the next morning, prove until risen by half,
and bake at 180 C for 35 minutes.
</context>

<context chunk_id="classic-brioche::structure::c000" recipe_id="classic-brioche" source_file="card-08-classic-brioche.md" section="title" dietary_tags="contains-egg|contains-dairy|contains-gluten">
Recipe: Classic Brioche (cuisine: french)
Section: Title
# Classic Brioche

An enriched overnight dough. Baker's percentages are relative to the 500 g of flour.
</context>

<context chunk_id="classic-brioche::structure::c001" recipe_id="classic-brioche" source_file="card-08-classic-brioche.md" section="ingredients" dietary_tags="contains-egg|contains-dairy|contains-gluten">
Recipe: Classic Brioche (cuisine: french)
Section: Ingredients (rows 1-7 of 7)
| Ingredient | Weight | Baker's % |
| --- | --- | --- |
| Strong white bread flour | 500 g | 100% |
| Caster sugar | 60 g | 12% |
| Instant dried yeast | 8 g | 1.6% |
| Fine sea salt | 9 g | 1.8% |
| Whole eggs | 250 g | 50% |
| Whole milk (32 C) | 100 g | 20% |
| Unsalted butter, softened | 250 g | 50% |
</context>

<context chunk_id="classic-brioche::structure::c003" recipe_id="classic-brioche" source_file="card-08-classic-brioche.md" section="allergens" dietary_tags="contains-egg|contains-dairy|contains-gluten">
Recipe: Classic Brioche (cuisine: french)
Section: Allergens
Contains wheat (gluten), egg and dairy.
</context>
```

**output**:

```json
{
  "can_substitute": true,
  "base_recipe_id": "classic-brioche",
  "title": "Chocolate Chip Brioche",
  "swaps": [
    {
      "removed": "Unsalted butter, softened (250 g)",
      "added": "Unsalted butter, softened (225 g)",
      "evidence_chunk_id": "chocolate-brioche::structure::c001"
    },
    {
      "removed": "Caster sugar (60 g)",
      "added": "Caster sugar (70 g)",
      "evidence_chunk_id": "chocolate-brioche::structure::c001"
    },
    {
      "removed": "None",
      "added": "Dark chocolate chips (150 g)",
      "evidence_chunk_id": "chocolate-brioche::structure::c001"
    }
  ],
  "ingredients": [
    {
      "name": "Strong white bread flour",
      "amount": "500 g",
      "source_chunk_id": "chocolate-brioche::structure::c001"
    },
    {
      "name": "Caster sugar",
      "amount": "70 g",
      "source_chunk_id": "chocolate-brioche::structure::c001"
    },
    {
      "name": "Instant dried yeast",
      "amount": "8 g",
      "source_chunk_id": "chocolate-brioche::structure::c001"
    },
    {
      "name": "Fine sea salt",
      "amount": "9 g",
      "source_chunk_id": "chocolate-brioche::structure::c001"
    },
    {
      "name": "Whole eggs",
      "amount": "250 g",
      "source_chunk_id": "chocolate-brioche::structure::c001"
    },
    {
      "name": "Whole milk (32 C)",
      "amount": "100 g",
      "source_chunk_id": "chocolate-brioche::structure::c001"
    },
    {
      "name": "Unsalted butter, softened",
      "amount": "225 g",
      "source_chunk_id": "chocolate-brioche::structure::c001"
    },
    {
      "name": "Dark chocolate chips",
      "amount": "150 g",
      "source_chunk_id": "chocolate-brioche::structure::c001"
    }
  ],
  "method": "Whisk the flour, sugar, yeast and salt together dry, then beat in the eggs and warm milk until the dough climbs the hook and cleans the bowl. Add the softened butter in five additions, waiting for each to disappear before the next. Fold the chocolate chips through by hand at the very end, or the paddle will smash them into the crumb and grey the whole loaf. Chill overnight at 4 C. Scale into a lined tin the next morning, prove until risen by half, and bake at 180 C for 35 minutes.",
  "oven": "180 C",
  "allergen_warning": "Contains wheat (gluten), egg, dairy and soy (from the chocolate).",
  "unsupported": ""
}
```

`sound`: [ ] true   [ ] false

---

## c19

**request**: `the brioches` -> `which of them can be made gluten free`

context blocks given (11):

```
<context chunk_id="gf-brioche::structure::c003" recipe_id="gf-brioche" source_file="card-07-gluten-free-brioche.md" section="allergens" dietary_tags="gluten-free|contains-egg|contains-dairy">
Recipe: Gluten-Free Brioche (cuisine: french)
Section: Allergens
Contains egg and dairy. Gluten free, provided the flour blend is certified.
</context>

<context chunk_id="gf-brioche::structure::c001" recipe_id="gf-brioche" source_file="card-07-gluten-free-brioche.md" section="ingredients" dietary_tags="gluten-free|contains-egg|contains-dairy">
Recipe: Gluten-Free Brioche (cuisine: french)
Section: Ingredients (rows 1-8 of 8)
| Ingredient | Weight | Baker's % |
| --- | --- | --- |
| Gluten-free flour blend | 500 g | 100% |
| Xanthan gum | 6 g | 1.2% |
| Caster sugar | 60 g | 12% |
| Instant dried yeast | 8 g | 1.6% |
| Fine sea salt | 9 g | 1.8% |
| Whole eggs | 250 g | 50% |
| Whole milk (32 C) | 150 g | 30% |
| Unsalted butter, softened | 175 g | 35% |
</context>

<context chunk_id="classic-brioche::structure::c003" recipe_id="classic-brioche" source_file="card-08-classic-brioche.md" section="allergens" dietary_tags="contains-egg|contains-dairy|contains-gluten">
Recipe: Classic Brioche (cuisine: french)
Section: Allergens
Contains wheat (gluten), egg and dairy.
</context>

<context chunk_id="gf-brioche::structure::c000" recipe_id="gf-brioche" source_file="card-07-gluten-free-brioche.md" section="title" dietary_tags="gluten-free|contains-egg|contains-dairy">
Recipe: Gluten-Free Brioche (cuisine: french)
Section: Title
# Gluten-Free Brioche

An enriched overnight dough. Baker's percentages are relative to the 500 g flour blend.
</context>

<context chunk_id="chocolate-brioche::structure::c003" recipe_id="chocolate-brioche" source_file="card-09-chocolate-brioche.md" section="allergens" dietary_tags="contains-egg|contains-dairy|contains-gluten|contains-soy">
Recipe: Chocolate Chip Brioche (cuisine: french)
Section: Allergens
Contains wheat (gluten), egg, dairy and soy (from the chocolate).
</context>

<context chunk_id="gf-brioche::structure::c002" recipe_id="gf-brioche" source_file="card-07-gluten-free-brioche.md" section="method" dietary_tags="gluten-free|contains-egg|contains-dairy">
Recipe: Gluten-Free Brioche (cuisine: french)
Section: Method
Whisk the flour blend, xanthan gum, sugar, yeast and salt together dry, so the gum disperses
before it meets any liquid. Lumped gum turns the crumb slimy and no amount of mixing later
will fix it.

Beat in the eggs and warm milk until the batter climbs the paddle, then add the softened
butter in five additions, waiting for each to disappear. The dough stays a thick batter
rather than a ball, which is normal without gluten.

Chill overnight at 4 C. Scale into a lined tin the next morning, prove until risen by half,
and bake at 180 C for 35 minutes.
</context>

<context chunk_id="classic-brioche::structure::c002" recipe_id="classic-brioche" source_file="card-08-classic-brioche.md" section="method" dietary_tags="contains-egg|contains-dairy|contains-gluten">
Recipe: Classic Brioche (cuisine: french)
Section: Method
Whisk the flour, sugar, yeast and salt together dry, then beat in the eggs and warm milk
until the dough climbs the hook and cleans the bowl.

Add the softened butter in five additions, waiting for each to disappear before the next.
The dough should end up glossy and slack enough to fall from the hook in a sheet.

Chill overnight at 4 C. Scale into a lined tin the next morning, prove until risen by half,
and bake at 180 C for 35 minutes.
</context>

<context chunk_id="chocolate-brioche::structure::c002" recipe_id="chocolate-brioche" source_file="card-09-chocolate-brioche.md" section="method" dietary_tags="contains-egg|contains-dairy|contains-gluten|contains-soy">
Recipe: Chocolate Chip Brioche (cuisine: french)
Section: Method
Whisk the flour, sugar, yeast and salt together dry, then beat in the eggs and warm milk
until the dough climbs the hook and cleans the bowl.

Add the softened butter in five additions, waiting for each to disappear before the next.
Fold the chocolate chips through by hand at the very end, or the paddle will smash them into
the crumb and grey the whole loaf.

Chill overnight at 4 C. Scale into a lined tin the next morning, prove until risen by half,
and bake at 180 C for 35 minutes.
</context>

<context chunk_id="classic-brioche::structure::c000" recipe_id="classic-brioche" source_file="card-08-classic-brioche.md" section="title" dietary_tags="contains-egg|contains-dairy|contains-gluten">
Recipe: Classic Brioche (cuisine: french)
Section: Title
# Classic Brioche

An enriched overnight dough. Baker's percentages are relative to the 500 g of flour.
</context>

<context chunk_id="chocolate-brioche::structure::c000" recipe_id="chocolate-brioche" source_file="card-09-chocolate-brioche.md" section="title" dietary_tags="contains-egg|contains-dairy|contains-gluten|contains-soy">
Recipe: Chocolate Chip Brioche (cuisine: french)
Section: Title
# Chocolate Chip Brioche

An enriched overnight dough. Baker's percentages are relative to the 500 g of flour.
</context>

<context chunk_id="classic-brioche::structure::c001" recipe_id="classic-brioche" source_file="card-08-classic-brioche.md" section="ingredients" dietary_tags="contains-egg|contains-dairy|contains-gluten">
Recipe: Classic Brioche (cuisine: french)
Section: Ingredients (rows 1-7 of 7)
| Ingredient | Weight | Baker's % |
| --- | --- | --- |
| Strong white bread flour | 500 g | 100% |
| Caster sugar | 60 g | 12% |
| Instant dried yeast | 8 g | 1.6% |
| Fine sea salt | 9 g | 1.8% |
| Whole eggs | 250 g | 50% |
| Whole milk (32 C) | 100 g | 20% |
| Unsalted butter, softened | 250 g | 50% |
</context>
```

**output**:

```json
{
  "can_substitute": true,
  "base_recipe_id": "gf-brioche",
  "title": "Gluten-Free Brioche",
  "swaps": [],
  "ingredients": [
    {
      "name": "Gluten-free flour blend",
      "amount": "500 g",
      "source_chunk_id": "gf-brioche::structure::c001"
    },
    {
      "name": "Xanthan gum",
      "amount": "6 g",
      "source_chunk_id": "gf-brioche::structure::c001"
    },
    {
      "name": "Caster sugar",
      "amount": "60 g",
      "source_chunk_id": "gf-brioche::structure::c001"
    },
    {
      "name": "Instant dried yeast",
      "amount": "8 g",
      "source_chunk_id": "gf-brioche::structure::c001"
    },
    {
      "name": "Fine sea salt",
      "amount": "9 g",
      "source_chunk_id": "gf-brioche::structure::c001"
    },
    {
      "name": "Whole eggs",
      "amount": "250 g",
      "source_chunk_id": "gf-brioche::structure::c001"
    },
    {
      "name": "Whole milk (32 C)",
      "amount": "150 g",
      "source_chunk_id": "gf-brioche::structure::c001"
    },
    {
      "name": "Unsalted butter, softened",
      "amount": "175 g",
      "source_chunk_id": "gf-brioche::structure::c001"
    }
  ],
  "method": "Whisk the flour blend, xanthan gum, sugar, yeast and salt together dry, so the gum disperses before it meets any liquid. Lumped gum turns the crumb slimy and no amount of mixing later will fix it. Beat in the eggs and warm milk until the batter climbs the paddle, then add the softened butter in five additions, waiting for each to disappear. The dough stays a thick batter rather than a ball, which is normal without gluten. Chill overnight at 4 C. Scale into a lined tin the next morning, prove until risen by half, and bake at 180 C for 35 minutes.",
  "oven": "180 C",
  "allergen_warning": "Contains egg and dairy.",
  "unsupported": ""
}
```

`sound`: [ ] true   [ ] false

---

## c20

**request**: `the sourdoughs` -> `which has the lowest salt, and swap the others to match`

context blocks given (9):

```
<context chunk_id="sourdough-2kg::structure::c003" recipe_id="sourdough-2kg" source_file="card-01-country-sourdough-2kg.md" section="method" dietary_tags="vegan|dairy-free|nut-free">
Recipe: 2kg Country Sourdough (cuisine: european)
Section: Method
Bake straight from the fridge at 250 C with steam for twenty minutes, then vent the oven and
drop to 230 C for a further twenty-five minutes until the crust is deeply coloured.
</context>

<context chunk_id="sourdough-2kg::structure::c002" recipe_id="sourdough-2kg" source_file="card-01-country-sourdough-2kg.md" section="method" dietary_tags="vegan|dairy-free|nut-free">
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
</context>

<context chunk_id="wholemeal-sourdough::structure::c000" recipe_id="wholemeal-sourdough" source_file="card-11-wholemeal-sourdough.md" section="title" dietary_tags="vegan|dairy-free|nut-free|contains-gluten">
Recipe: Wholemeal Sourdough (cuisine: european)
Section: Title
# Wholemeal Sourdough

A high-extraction naturally leavened loaf. Baker's percentages are relative to the total
flour weight of 1000 g.
</context>

<context chunk_id="sourdough-2kg::structure::c000" recipe_id="sourdough-2kg" source_file="card-01-country-sourdough-2kg.md" section="title" dietary_tags="vegan|dairy-free|nut-free">
Recipe: 2kg Country Sourdough (cuisine: european)
Section: Title
# 2kg Country Sourdough

A two-day naturally leavened loaf. Baker's percentages are relative to the total flour
weight of 1000 g, so the white and rye flours together make 100%.
</context>

<context chunk_id="sourdough-2kg::structure::c004" recipe_id="sourdough-2kg" source_file="card-01-country-sourdough-2kg.md" section="allergens" dietary_tags="vegan|dairy-free|nut-free">
Recipe: 2kg Country Sourdough (cuisine: european)
Section: Allergens
Contains wheat and rye (gluten). Made in a kitchen that also handles sesame and tree nuts.
</context>

<context chunk_id="wholemeal-sourdough::structure::c002" recipe_id="wholemeal-sourdough" source_file="card-11-wholemeal-sourdough.md" section="method" dietary_tags="vegan|dairy-free|nut-free|contains-gluten">
Recipe: Wholemeal Sourdough (cuisine: european)
Section: Method
Whisk the starter into the water, add both flours, and mix to a shaggy mass. Autolyse for
one hour rather than forty minutes, because wholemeal bran drinks slowly and a short rest
leaves the dough gritty.

Add the salt and pinch it through. Bulk ferment at 24 C for three and a half hours, folding
every forty-five minutes. Wholemeal ferments faster than white, so watch the dough and not
the clock.

Shape, then cold retard at 4 C overnight. Bake at 240 C with steam for twenty minutes, then
vent and drop to 220 C for a further twenty-five.
</context>

<context chunk_id="sourdough-2kg::structure::c001" recipe_id="sourdough-2kg" source_file="card-01-country-sourdough-2kg.md" section="ingredients" dietary_tags="vegan|dairy-free|nut-free">
Recipe: 2kg Country Sourdough (cuisine: european)
Section: Ingredients (rows 1-5 of 5)
| Ingredient | Weight | Baker's % |
| --- | --- | --- |
| Strong white bread flour | 950 g | 95% |
| Wholemeal rye flour | 50 g | 5% |
| Water (28 C) | 760 g | 76% |
| Stiff sourdough starter | 200 g | 20% |
| Fine sea salt | 18 g | 1.8% |
</context>

<context chunk_id="wholemeal-sourdough::structure::c001" recipe_id="wholemeal-sourdough" source_file="card-11-wholemeal-sourdough.md" section="ingredients" dietary_tags="vegan|dairy-free|nut-free|contains-gluten">
Recipe: Wholemeal Sourdough (cuisine: european)
Section: Ingredients (rows 1-5 of 5)
| Ingredient | Weight | Baker's % |
| --- | --- | --- |
| Wholemeal flour | 700 g | 70% |
| Strong white bread flour | 300 g | 30% |
| Water (28 C) | 800 g | 80% |
| Stiff sourdough starter | 200 g | 20% |
| Fine sea salt | 20 g | 2% |
</context>

<context chunk_id="rye-sourdough::structure::c001" recipe_id="rye-sourdough" source_file="card-12-light-rye-sourdough.md" section="ingredients" dietary_tags="vegan|dairy-free|nut-free|contains-gluten">
Recipe: Light Rye Sourdough (cuisine: european)
Section: Ingredients (rows 1-5 of 5)
| Ingredient | Weight | Baker's % |
| --- | --- | --- |
| Strong white bread flour | 800 g | 80% |
| Dark rye flour | 200 g | 20% |
| Water (28 C) | 780 g | 78% |
| Stiff sourdough starter | 200 g | 20% |
| Fine sea salt | 19 g | 1.9% |
</context>
```

**output**:

```json
{
  "can_substitute": true,
  "base_recipe_id": "sourdough-2kg",
  "title": "2kg Country Sourdough",
  "swaps": [
    {
      "removed": "18 g",
      "added": "18 g",
      "evidence_chunk_id": "sourdough-2kg::structure::c001"
    }
  ],
  "ingredients": [
    {
      "name": "Strong white bread flour",
      "amount": "950 g",
      "source_chunk_id": "sourdough-2kg::structure::c001"
    },
    {
      "name": "Wholemeal rye flour",
      "amount": "50 g",
      "source_chunk_id": "sourdough-2kg::structure::c001"
    },
    {
      "name": "Water (28 C)",
      "amount": "760 g",
      "source_chunk_id": "sourdough-2kg::structure::c001"
    },
    {
      "name": "Stiff sourdough starter",
      "amount": "200 g",
      "source_chunk_id": "sourdough-2kg::structure::c001"
    },
    {
      "name": "Fine sea salt",
      "amount": "18 g",
      "source_chunk_id": "sourdough-2kg::structure::c001"
    }
  ],
  "method": "Whisk the starter into the water until no lumps remain, then add both flours and mix to a shaggy mass. Cover and autolyse for forty minutes. Hold the salt back at this stage: added before the autolyse it tightens the gluten and the dough fights you for the rest of the day. Sprinkle the fine sea salt over the rested dough and pinch it through with wet hands until you can no longer feel grains. Bulk ferment at 24 C for four hours, folding the dough in the bowl every forty-five minutes for the first three. Divide, pre-shape, and rest for twenty minutes. Shape into two tight boules, seam side up in floured baskets, then cold retard at 4 C overnight for twelve to fourteen hours. Bake straight from the fridge at 250 C with steam for twenty minutes, then vent the oven and drop to 230 C for a further twenty-five minutes until the crust is deeply coloured.",
  "oven": "250 C with steam for twenty minutes, then vent the oven and drop to 230 C for a further twenty-five minutes",
  "allergen_warning": "Contains wheat and rye (gluten). Made in a kitchen that also handles sesame and tree nuts.",
  "unsupported": ""
}
```

`sound`: [ ] true   [ ] false

---

## c21

**request**: `the gluten-free loaves` -> `which one is already vegan`

context blocks given (6):

```
<context chunk_id="gf-sandwich-loaf::structure::c001" recipe_id="gf-sandwich-loaf" source_file="card-10-gluten-free-sandwich-loaf.md" section="ingredients" dietary_tags="gluten-free|vegan|dairy-free">
Recipe: Gluten-Free Sandwich Loaf (cuisine: european)
Section: Ingredients (rows 1-7 of 7)
| Ingredient | Weight | Baker's % |
| --- | --- | --- |
| Gluten-free flour blend | 500 g | 100% |
| Xanthan gum | 10 g | 2% |
| Psyllium husk | 15 g | 3% |
| Instant dried yeast | 7 g | 1.4% |
| Fine sea salt | 10 g | 2% |
| Water (30 C) | 400 g | 80% |
| Olive oil | 30 g | 6% |
</context>

<context chunk_id="gf-sandwich-loaf::structure::c003" recipe_id="gf-sandwich-loaf" source_file="card-10-gluten-free-sandwich-loaf.md" section="allergens" dietary_tags="gluten-free|vegan|dairy-free">
Recipe: Gluten-Free Sandwich Loaf (cuisine: european)
Section: Allergens
Gluten free, provided the flour blend is certified. No egg or dairy.
</context>

<context chunk_id="gf-sandwich-loaf::structure::c002" recipe_id="gf-sandwich-loaf" source_file="card-10-gluten-free-sandwich-loaf.md" section="method" dietary_tags="gluten-free|vegan|dairy-free">
Recipe: Gluten-Free Sandwich Loaf (cuisine: european)
Section: Method
Whisk the flour blend, xanthan gum, psyllium husk, yeast and salt together dry so both gums
disperse before they meet water. Psyllium hydrates far faster than xanthan, so skipping the
dry mix leaves you picking gel lumps out of the batter.

Add the warm water and oil, beat for four minutes, then rest the batter for twenty so the
psyllium sets up. It should hold a peak rather than pour.

Scrape into a lined tin, prove until risen by half, and bake at 200 C for 45 minutes.
</context>

<context chunk_id="gf-sandwich-loaf::structure::c000" recipe_id="gf-sandwich-loaf" source_file="card-10-gluten-free-sandwich-loaf.md" section="title" dietary_tags="gluten-free|vegan|dairy-free">
Recipe: Gluten-Free Sandwich Loaf (cuisine: european)
Section: Title
# Gluten-Free Sandwich Loaf

A lean tin loaf. Baker's percentages are relative to the 500 g flour blend.
</context>

<context chunk_id="gf-brioche::structure::c001" recipe_id="gf-brioche" source_file="card-07-gluten-free-brioche.md" section="ingredients" dietary_tags="gluten-free|contains-egg|contains-dairy">
Recipe: Gluten-Free Brioche (cuisine: french)
Section: Ingredients (rows 1-8 of 8)
| Ingredient | Weight | Baker's % |
| --- | --- | --- |
| Gluten-free flour blend | 500 g | 100% |
| Xanthan gum | 6 g | 1.2% |
| Caster sugar | 60 g | 12% |
| Instant dried yeast | 8 g | 1.6% |
| Fine sea salt | 9 g | 1.8% |
| Whole eggs | 250 g | 50% |
| Whole milk (32 C) | 150 g | 30% |
| Unsalted butter, softened | 175 g | 35% |
</context>

<context chunk_id="lemon-drizzle-cake::structure::c003" recipe_id="lemon-drizzle-cake" source_file="lemon-drizzle-cake.md" section="allergens" dietary_tags="vegetarian|contains-egg|contains-dairy">
Recipe: Lemon Drizzle Loaf (cuisine: british)
Section: Allergens
Contains wheat (gluten), egg and dairy.
</context>
```

**output**:

```json
{
  "can_substitute": true,
  "base_recipe_id": "gf-sandwich-loaf",
  "title": "Gluten-Free Sandwich Loaf",
  "swaps": [],
  "ingredients": [
    {
      "name": "Gluten-free flour blend",
      "amount": "500 g",
      "source_chunk_id": "gf-sandwich-loaf::structure::c001"
    },
    {
      "name": "Xanthan gum",
      "amount": "10 g",
      "source_chunk_id": "gf-sandwich-loaf::structure::c001"
    },
    {
      "name": "Psyllium husk",
      "amount": "15 g",
      "source_chunk_id": "gf-sandwich-loaf::structure::c001"
    },
    {
      "name": "Instant dried yeast",
      "amount": "7 g",
      "source_chunk_id": "gf-sandwich-loaf::structure::c001"
    },
    {
      "name": "Fine sea salt",
      "amount": "10 g",
      "source_chunk_id": "gf-sandwich-loaf::structure::c001"
    },
    {
      "name": "Water (30 C)",
      "amount": "400 g",
      "source_chunk_id": "gf-sandwich-loaf::structure::c001"
    },
    {
      "name": "Olive oil",
      "amount": "30 g",
      "source_chunk_id": "gf-sandwich-loaf::structure::c001"
    }
  ],
  "method": "Whisk the flour blend, xanthan gum, psyllium husk, yeast and salt together dry so both gums disperse before they meet water. Psyllium hydrates far faster than xanthan, so skipping the dry mix leaves you picking gel lumps out of the batter. Add the warm water and oil, beat for four minutes, then rest the batter for twenty so the psyllium sets up. It should hold a peak rather than pour. Scrape into a lined tin, prove until risen by half, and bake at 200 C for 45 minutes.",
  "oven": "200 C",
  "allergen_warning": "Gluten free, provided the flour blend is certified. No egg or dairy.",
  "unsupported": ""
}
```

`sound`: [ ] true   [ ] false

---

## c22

**request**: `classic brioche` -> `swap the milk for the same weight the gluten-free brioche uses`

context blocks given (11):

```
<context chunk_id="classic-brioche::structure::c002" recipe_id="classic-brioche" source_file="card-08-classic-brioche.md" section="method" dietary_tags="contains-egg|contains-dairy|contains-gluten">
Recipe: Classic Brioche (cuisine: french)
Section: Method
Whisk the flour, sugar, yeast and salt together dry, then beat in the eggs and warm milk
until the dough climbs the hook and cleans the bowl.

Add the softened butter in five additions, waiting for each to disappear before the next.
The dough should end up glossy and slack enough to fall from the hook in a sheet.

Chill overnight at 4 C. Scale into a lined tin the next morning, prove until risen by half,
and bake at 180 C for 35 minutes.
</context>

<context chunk_id="gf-brioche::structure::c003" recipe_id="gf-brioche" source_file="card-07-gluten-free-brioche.md" section="allergens" dietary_tags="gluten-free|contains-egg|contains-dairy">
Recipe: Gluten-Free Brioche (cuisine: french)
Section: Allergens
Contains egg and dairy. Gluten free, provided the flour blend is certified.
</context>

<context chunk_id="gf-brioche::structure::c000" recipe_id="gf-brioche" source_file="card-07-gluten-free-brioche.md" section="title" dietary_tags="gluten-free|contains-egg|contains-dairy">
Recipe: Gluten-Free Brioche (cuisine: french)
Section: Title
# Gluten-Free Brioche

An enriched overnight dough. Baker's percentages are relative to the 500 g flour blend.
</context>

<context chunk_id="classic-brioche::structure::c000" recipe_id="classic-brioche" source_file="card-08-classic-brioche.md" section="title" dietary_tags="contains-egg|contains-dairy|contains-gluten">
Recipe: Classic Brioche (cuisine: french)
Section: Title
# Classic Brioche

An enriched overnight dough. Baker's percentages are relative to the 500 g of flour.
</context>

<context chunk_id="classic-brioche::structure::c003" recipe_id="classic-brioche" source_file="card-08-classic-brioche.md" section="allergens" dietary_tags="contains-egg|contains-dairy|contains-gluten">
Recipe: Classic Brioche (cuisine: french)
Section: Allergens
Contains wheat (gluten), egg and dairy.
</context>

<context chunk_id="gf-brioche::structure::c002" recipe_id="gf-brioche" source_file="card-07-gluten-free-brioche.md" section="method" dietary_tags="gluten-free|contains-egg|contains-dairy">
Recipe: Gluten-Free Brioche (cuisine: french)
Section: Method
Whisk the flour blend, xanthan gum, sugar, yeast and salt together dry, so the gum disperses
before it meets any liquid. Lumped gum turns the crumb slimy and no amount of mixing later
will fix it.

Beat in the eggs and warm milk until the batter climbs the paddle, then add the softened
butter in five additions, waiting for each to disappear. The dough stays a thick batter
rather than a ball, which is normal without gluten.

Chill overnight at 4 C. Scale into a lined tin the next morning, prove until risen by half,
and bake at 180 C for 35 minutes.
</context>

<context chunk_id="classic-brioche::structure::c001" recipe_id="classic-brioche" source_file="card-08-classic-brioche.md" section="ingredients" dietary_tags="contains-egg|contains-dairy|contains-gluten">
Recipe: Classic Brioche (cuisine: french)
Section: Ingredients (rows 1-7 of 7)
| Ingredient | Weight | Baker's % |
| --- | --- | --- |
| Strong white bread flour | 500 g | 100% |
| Caster sugar | 60 g | 12% |
| Instant dried yeast | 8 g | 1.6% |
| Fine sea salt | 9 g | 1.8% |
| Whole eggs | 250 g | 50% |
| Whole milk (32 C) | 100 g | 20% |
| Unsalted butter, softened | 250 g | 50% |
</context>

<context chunk_id="chocolate-brioche::structure::c002" recipe_id="chocolate-brioche" source_file="card-09-chocolate-brioche.md" section="method" dietary_tags="contains-egg|contains-dairy|contains-gluten|contains-soy">
Recipe: Chocolate Chip Brioche (cuisine: french)
Section: Method
Whisk the flour, sugar, yeast and salt together dry, then beat in the eggs and warm milk
until the dough climbs the hook and cleans the bowl.

Add the softened butter in five additions, waiting for each to disappear before the next.
Fold the chocolate chips through by hand at the very end, or the paddle will smash them into
the crumb and grey the whole loaf.

Chill overnight at 4 C. Scale into a lined tin the next morning, prove until risen by half,
and bake at 180 C for 35 minutes.
</context>

<context chunk_id="gf-brioche::structure::c001" recipe_id="gf-brioche" source_file="card-07-gluten-free-brioche.md" section="ingredients" dietary_tags="gluten-free|contains-egg|contains-dairy">
Recipe: Gluten-Free Brioche (cuisine: french)
Section: Ingredients (rows 1-8 of 8)
| Ingredient | Weight | Baker's % |
| --- | --- | --- |
| Gluten-free flour blend | 500 g | 100% |
| Xanthan gum | 6 g | 1.2% |
| Caster sugar | 60 g | 12% |
| Instant dried yeast | 8 g | 1.6% |
| Fine sea salt | 9 g | 1.8% |
| Whole eggs | 250 g | 50% |
| Whole milk (32 C) | 150 g | 30% |
| Unsalted butter, softened | 175 g | 35% |
</context>

<context chunk_id="chocolate-brioche::structure::c003" recipe_id="chocolate-brioche" source_file="card-09-chocolate-brioche.md" section="allergens" dietary_tags="contains-egg|contains-dairy|contains-gluten|contains-soy">
Recipe: Chocolate Chip Brioche (cuisine: french)
Section: Allergens
Contains wheat (gluten), egg, dairy and soy (from the chocolate).
</context>

<context chunk_id="chocolate-brioche::structure::c000" recipe_id="chocolate-brioche" source_file="card-09-chocolate-brioche.md" section="title" dietary_tags="contains-egg|contains-dairy|contains-gluten|contains-soy">
Recipe: Chocolate Chip Brioche (cuisine: french)
Section: Title
# Chocolate Chip Brioche

An enriched overnight dough. Baker's percentages are relative to the 500 g of flour.
</context>
```

**output**:

```json
{
  "can_substitute": true,
  "base_recipe_id": "classic-brioche",
  "title": "Classic Brioche",
  "swaps": [
    {
      "removed": "Whole milk (32 C) | 100 g",
      "added": "Whole milk (32 C) | 150 g",
      "evidence_chunk_id": "gf-brioche::structure::c001"
    }
  ],
  "ingredients": [
    {
      "name": "Strong white bread flour",
      "amount": "500 g",
      "source_chunk_id": "classic-brioche::structure::c001"
    },
    {
      "name": "Caster sugar",
      "amount": "60 g",
      "source_chunk_id": "classic-brioche::structure::c001"
    },
    {
      "name": "Instant dried yeast",
      "amount": "8 g",
      "source_chunk_id": "classic-brioche::structure::c001"
    },
    {
      "name": "Fine sea salt",
      "amount": "9 g",
      "source_chunk_id": "classic-brioche::structure::c001"
    },
    {
      "name": "Whole eggs",
      "amount": "250 g",
      "source_chunk_id": "classic-brioche::structure::c001"
    },
    {
      "name": "Whole milk (32 C)",
      "amount": "150 g",
      "source_chunk_id": "gf-brioche::structure::c001"
    },
    {
      "name": "Unsalted butter, softened",
      "amount": "250 g",
      "source_chunk_id": "classic-brioche::structure::c001"
    }
  ],
  "method": "Whisk the flour, sugar, yeast and salt together dry, then beat in the eggs and warm milk until the dough climbs the hook and cleans the bowl. Add the softened butter in five additions, waiting for each to disappear before the next. The dough should end up glossy and slack enough to fall from the hook in a sheet. Chill overnight at 4 C. Scale into a lined tin the next morning, prove until risen by half, and bake at 180 C for 35 minutes.",
  "oven": "180 C",
  "allergen_warning": "Contains wheat (gluten), egg and dairy.",
  "unsupported": "The total flour weight is 500 g in both recipes, so no adjustment is needed."
}
```

`sound`: [ ] true   [ ] false

---

## c23

**request**: `2kg country sourdough` -> `raise the hydration to match the wettest loaf in the archive`

context blocks given (7):

```
<context chunk_id="sourdough-2kg::structure::c001" recipe_id="sourdough-2kg" source_file="card-01-country-sourdough-2kg.md" section="ingredients" dietary_tags="vegan|dairy-free|nut-free">
Recipe: 2kg Country Sourdough (cuisine: european)
Section: Ingredients (rows 1-5 of 5)
| Ingredient | Weight | Baker's % |
| --- | --- | --- |
| Strong white bread flour | 950 g | 95% |
| Wholemeal rye flour | 50 g | 5% |
| Water (28 C) | 760 g | 76% |
| Stiff sourdough starter | 200 g | 20% |
| Fine sea salt | 18 g | 1.8% |
</context>

<context chunk_id="sourdough-2kg::structure::c003" recipe_id="sourdough-2kg" source_file="card-01-country-sourdough-2kg.md" section="method" dietary_tags="vegan|dairy-free|nut-free">
Recipe: 2kg Country Sourdough (cuisine: european)
Section: Method
Bake straight from the fridge at 250 C with steam for twenty minutes, then vent the oven and
drop to 230 C for a further twenty-five minutes until the crust is deeply coloured.
</context>

<context chunk_id="sourdough-2kg::structure::c000" recipe_id="sourdough-2kg" source_file="card-01-country-sourdough-2kg.md" section="title" dietary_tags="vegan|dairy-free|nut-free">
Recipe: 2kg Country Sourdough (cuisine: european)
Section: Title
# 2kg Country Sourdough

A two-day naturally leavened loaf. Baker's percentages are relative to the total flour
weight of 1000 g, so the white and rye flours together make 100%.
</context>

<context chunk_id="sourdough-2kg::structure::c004" recipe_id="sourdough-2kg" source_file="card-01-country-sourdough-2kg.md" section="allergens" dietary_tags="vegan|dairy-free|nut-free">
Recipe: 2kg Country Sourdough (cuisine: european)
Section: Allergens
Contains wheat and rye (gluten). Made in a kitchen that also handles sesame and tree nuts.
</context>

<context chunk_id="sourdough-2kg::structure::c002" recipe_id="sourdough-2kg" source_file="card-01-country-sourdough-2kg.md" section="method" dietary_tags="vegan|dairy-free|nut-free">
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
</context>

<context chunk_id="wholemeal-sourdough::structure::c000" recipe_id="wholemeal-sourdough" source_file="card-11-wholemeal-sourdough.md" section="title" dietary_tags="vegan|dairy-free|nut-free|contains-gluten">
Recipe: Wholemeal Sourdough (cuisine: european)
Section: Title
# Wholemeal Sourdough

A high-extraction naturally leavened loaf. Baker's percentages are relative to the total
flour weight of 1000 g.
</context>

<context chunk_id="rye-sourdough::structure::c000" recipe_id="rye-sourdough" source_file="card-12-light-rye-sourdough.md" section="title" dietary_tags="vegan|dairy-free|nut-free|contains-gluten">
Recipe: Light Rye Sourdough (cuisine: european)
Section: Title
# Light Rye Sourdough

A twenty percent rye naturally leavened loaf. Baker's percentages are relative to the total
flour weight of 1000 g.
</context>
```

**output**:

```json
{
  "can_substitute": false,
  "base_recipe_id": "sourdough-2kg",
  "title": "2kg Country Sourdough",
  "swaps": [],
  "ingredients": [],
  "method": "",
  "oven": "",
  "allergen_warning": "",
  "unsupported": "The archive does not provide hydration percentages for other recipes to determine the wettest loaf, nor does it provide a method to adjust the water quantity in the base recipe."
}
```

`sound`: [ ] true   [ ] false

---

## c24

**request**: `(no recipe named)` -> `make it dairy free`

context blocks given (12):

```
<context chunk_id="milk-kefir::structure::c003" recipe_id="milk-kefir" source_file="card-05-milk-kefir.md" section="allergens" dietary_tags="contains-dairy|vegetarian|gluten-free">
Recipe: Milk Kefir (cuisine: caucasian)
Section: Allergens
Contains dairy (cow's milk). Not lactose-free, although fermentation reduces the lactose
load. Not suitable for anyone with a milk protein allergy.
</context>

<context chunk_id="milk-kefir::structure::c001" recipe_id="milk-kefir" source_file="card-05-milk-kefir.md" section="ingredients" dietary_tags="contains-dairy|vegetarian|gluten-free">
Recipe: Milk Kefir (cuisine: caucasian)
Section: Ingredients (rows 1-3 of 3)
| Ingredient | Weight | Baker's % |
| --- | --- | --- |
| Whole cow's milk | 1000 g | 100% |
| Live kefir grains | 50 g | 5% |
| Lemon peel, for the second ferment | 5 g | 0.5% |
</context>

<context chunk_id="milk-kefir::structure::c002" recipe_id="milk-kefir" source_file="card-05-milk-kefir.md" section="method" dietary_tags="contains-dairy|vegetarian|gluten-free">
Recipe: Milk Kefir (cuisine: caucasian)
Section: Method
Tip the live kefir grains into a clean jar and pour the whole milk over them. Cover with
cloth rather than a sealed lid, because the grains need to breathe and the jar will build
pressure otherwise.

Leave at 22 C for twenty-four hours. The kefir is ready when it coats the side of the jar
and pulls away from the glass in one sheet; past that point it splits into curd and whey and
turns aggressively sour.

Strain through a nylon sieve, never metal, and stir the grains straight into fresh milk to
begin the next batch. For a second ferment, seal the strained kefir with the lemon peel and
leave it at room temperature for a further twelve hours.
</context>

<context chunk_id="gf-brioche::structure::c003" recipe_id="gf-brioche" source_file="card-07-gluten-free-brioche.md" section="allergens" dietary_tags="gluten-free|contains-egg|contains-dairy">
Recipe: Gluten-Free Brioche (cuisine: french)
Section: Allergens
Contains egg and dairy. Gluten free, provided the flour blend is certified.
</context>

<context chunk_id="gf-brioche::structure::c001" recipe_id="gf-brioche" source_file="card-07-gluten-free-brioche.md" section="ingredients" dietary_tags="gluten-free|contains-egg|contains-dairy">
Recipe: Gluten-Free Brioche (cuisine: french)
Section: Ingredients (rows 1-8 of 8)
| Ingredient | Weight | Baker's % |
| --- | --- | --- |
| Gluten-free flour blend | 500 g | 100% |
| Xanthan gum | 6 g | 1.2% |
| Caster sugar | 60 g | 12% |
| Instant dried yeast | 8 g | 1.6% |
| Fine sea salt | 9 g | 1.8% |
| Whole eggs | 250 g | 50% |
| Whole milk (32 C) | 150 g | 30% |
| Unsalted butter, softened | 175 g | 35% |
</context>

<context chunk_id="gf-brioche::structure::c002" recipe_id="gf-brioche" source_file="card-07-gluten-free-brioche.md" section="method" dietary_tags="gluten-free|contains-egg|contains-dairy">
Recipe: Gluten-Free Brioche (cuisine: french)
Section: Method
Whisk the flour blend, xanthan gum, sugar, yeast and salt together dry, so the gum disperses
before it meets any liquid. Lumped gum turns the crumb slimy and no amount of mixing later
will fix it.

Beat in the eggs and warm milk until the batter climbs the paddle, then add the softened
butter in five additions, waiting for each to disappear. The dough stays a thick batter
rather than a ball, which is normal without gluten.

Chill overnight at 4 C. Scale into a lined tin the next morning, prove until risen by half,
and bake at 180 C for 35 minutes.
</context>

<context chunk_id="pad-thai::structure::c000" recipe_id="pad-thai" source_file="pad-thai.md" section="title" dietary_tags="gluten-free|contains-egg|contains-shellfish|contains-peanut">
Recipe: Prawn Pad Thai (cuisine: thai)
Section: Title
# Prawn Pad Thai
</context>

<context chunk_id="shakshuka::structure::c000" recipe_id="shakshuka" source_file="shakshuka.md" section="title" dietary_tags="vegetarian|gluten-free|contains-egg">
Recipe: Red Pepper Shakshuka (cuisine: middle-eastern)
Section: Title
# Red Pepper Shakshuka
</context>

<context chunk_id="chicken-tikka-masala::structure::c000" recipe_id="chicken-tikka-masala" source_file="chicken-tikka-masala.md" section="title" dietary_tags="gluten-free|contains-dairy">
Recipe: Chicken Tikka Masala (cuisine: indian)
Section: Title
# Chicken Tikka Masala
</context>

<context chunk_id="pad-thai::structure::c004" recipe_id="pad-thai" source_file="pad-thai.md" section="method" dietary_tags="gluten-free|contains-egg|contains-shellfish|contains-peanut">
Recipe: Prawn Pad Thai (cuisine: thai)
Section: Method
Get the wok properly hot. Fry the tofu until it takes colour, add the prawns and cook until
just opaque, then push everything to one side and scramble the eggs in the clear space.
Add the drained noodles and the sauce and toss hard for two minutes. Kill the heat, fold
through the beansprouts and chives so they stay crisp, and finish with the peanuts.
</context>

<context chunk_id="chana-masala::structure::c000" recipe_id="chana-masala" source_file="chana-masala.md" section="title" dietary_tags="vegan|gluten-free|dairy-free">
Recipe: Chana Masala (cuisine: indian)
Section: Title
# Chana Masala
</context>

<context chunk_id="congee::structure::c000" recipe_id="congee" source_file="congee.md" section="title" dietary_tags="vegan|gluten-free|dairy-free|nut-free">
Recipe: Ginger and Spring Onion Congee (cuisine: chinese)
Section: Title
# Ginger and Spring Onion Congee
</context>
```

**output**:

```json
{
  "can_substitute": false,
  "base_recipe_id": "milk-kefir",
  "title": "Milk Kefir",
  "swaps": [],
  "ingredients": [],
  "method": "",
  "oven": "",
  "allergen_warning": "",
  "unsupported": "There is no dairy-free alternative for whole cow's milk provided in the archive."
}
```

`sound`: [ ] true   [ ] false

---

## c25

**request**: `the loaf` -> `gluten free`

context blocks given (8):

```
<context chunk_id="gf-sandwich-loaf::structure::c003" recipe_id="gf-sandwich-loaf" source_file="card-10-gluten-free-sandwich-loaf.md" section="allergens" dietary_tags="gluten-free|vegan|dairy-free">
Recipe: Gluten-Free Sandwich Loaf (cuisine: european)
Section: Allergens
Gluten free, provided the flour blend is certified. No egg or dairy.
</context>

<context chunk_id="gf-sandwich-loaf::structure::c001" recipe_id="gf-sandwich-loaf" source_file="card-10-gluten-free-sandwich-loaf.md" section="ingredients" dietary_tags="gluten-free|vegan|dairy-free">
Recipe: Gluten-Free Sandwich Loaf (cuisine: european)
Section: Ingredients (rows 1-7 of 7)
| Ingredient | Weight | Baker's % |
| --- | --- | --- |
| Gluten-free flour blend | 500 g | 100% |
| Xanthan gum | 10 g | 2% |
| Psyllium husk | 15 g | 3% |
| Instant dried yeast | 7 g | 1.4% |
| Fine sea salt | 10 g | 2% |
| Water (30 C) | 400 g | 80% |
| Olive oil | 30 g | 6% |
</context>

<context chunk_id="gf-sandwich-loaf::structure::c000" recipe_id="gf-sandwich-loaf" source_file="card-10-gluten-free-sandwich-loaf.md" section="title" dietary_tags="gluten-free|vegan|dairy-free">
Recipe: Gluten-Free Sandwich Loaf (cuisine: european)
Section: Title
# Gluten-Free Sandwich Loaf

A lean tin loaf. Baker's percentages are relative to the 500 g flour blend.
</context>

<context chunk_id="gf-sandwich-loaf::structure::c002" recipe_id="gf-sandwich-loaf" source_file="card-10-gluten-free-sandwich-loaf.md" section="method" dietary_tags="gluten-free|vegan|dairy-free">
Recipe: Gluten-Free Sandwich Loaf (cuisine: european)
Section: Method
Whisk the flour blend, xanthan gum, psyllium husk, yeast and salt together dry so both gums
disperse before they meet water. Psyllium hydrates far faster than xanthan, so skipping the
dry mix leaves you picking gel lumps out of the batter.

Add the warm water and oil, beat for four minutes, then rest the batter for twenty so the
psyllium sets up. It should hold a peak rather than pour.

Scrape into a lined tin, prove until risen by half, and bake at 200 C for 45 minutes.
</context>

<context chunk_id="lemon-drizzle-cake::structure::c003" recipe_id="lemon-drizzle-cake" source_file="lemon-drizzle-cake.md" section="allergens" dietary_tags="vegetarian|contains-egg|contains-dairy">
Recipe: Lemon Drizzle Loaf (cuisine: british)
Section: Allergens
Contains wheat (gluten), egg and dairy.
</context>

<context chunk_id="lemon-drizzle-cake::structure::c000" recipe_id="lemon-drizzle-cake" source_file="lemon-drizzle-cake.md" section="title" dietary_tags="vegetarian|contains-egg|contains-dairy">
Recipe: Lemon Drizzle Loaf (cuisine: british)
Section: Title
# Lemon Drizzle Loaf
</context>

<context chunk_id="lemon-drizzle-cake::structure::c002" recipe_id="lemon-drizzle-cake" source_file="lemon-drizzle-cake.md" section="method" dietary_tags="vegetarian|contains-egg|contains-dairy">
Recipe: Lemon Drizzle Loaf (cuisine: british)
Section: Method
Beat the butter and caster sugar until the mixture turns pale and increases visibly in
volume — five minutes in a stand mixer, and no less. Add the eggs one at a time, beating
fully between each.

Fold in the flour, salt and zest with a spatula, stopping the moment the flour disappears.
Scrape into a lined 900 g loaf tin and bake at 170 C for 45 to 50 minutes.

Stir the granulated sugar into the lemon juice without heating it — the crust should end up
crunchy, not glazed. Spike the hot loaf all over with a skewer and spoon the drizzle over
while the cake is still in the tin. Let it cool completely before turning out.
</context>

<context chunk_id="sourdough-2kg::structure::c000" recipe_id="sourdough-2kg" source_file="card-01-country-sourdough-2kg.md" section="title" dietary_tags="vegan|dairy-free|nut-free">
Recipe: 2kg Country Sourdough (cuisine: european)
Section: Title
# 2kg Country Sourdough

A two-day naturally leavened loaf. Baker's percentages are relative to the total flour
weight of 1000 g, so the white and rye flours together make 100%.
</context>
```

**output**:

```json
{
  "can_substitute": false,
  "base_recipe_id": "lemon-drizzle-cake",
  "title": "Lemon Drizzle Loaf",
  "swaps": [],
  "ingredients": [],
  "method": "",
  "oven": "",
  "allergen_warning": "",
  "unsupported": "The archive does not contain a gluten-free version of the Lemon Drizzle Loaf, nor does it provide a method to substitute wheat flour with a gluten-free flour blend for this specific recipe."
}
```

`sound`: [ ] true   [ ] false

---

## r01

**request**: `chicken tikka masala` -> `can i use greek yoghurt in the tikka masala`

context blocks given (7):

```
<context chunk_id="chicken-tikka-masala::structure::c000" recipe_id="chicken-tikka-masala" source_file="chicken-tikka-masala.md" section="title" dietary_tags="gluten-free|contains-dairy">
Recipe: Chicken Tikka Masala (cuisine: indian)
Section: Title
# Chicken Tikka Masala
</context>

<context chunk_id="chicken-tikka-masala::structure::c001" recipe_id="chicken-tikka-masala" source_file="chicken-tikka-masala.md" section="ingredients" dietary_tags="gluten-free|contains-dairy">
Recipe: Chicken Tikka Masala (cuisine: indian)
Section: Ingredients (rows 1-8 of 13)
| Ingredient | Weight | Notes |
| --- | --- | --- |
| Chicken thigh, boneless | 900 g | 4 cm pieces |
| Full fat yoghurt | 250 g | for the marinade |
| Double cream | 150 g | |
| Tinned plum tomatoes | 400 g | |
| Brown onion | 250 g | diced |
| Ghee | 50 g | |
| Ginger, grated | 25 g | |
| Garlic, crushed | 20 g | |
</context>

<context chunk_id="chicken-tikka-masala::structure::c002" recipe_id="chicken-tikka-masala" source_file="chicken-tikka-masala.md" section="ingredients" dietary_tags="gluten-free|contains-dairy">
Recipe: Chicken Tikka Masala (cuisine: indian)
Section: Ingredients (rows 9-13 of 13)
| Ingredient | Weight | Notes |
| --- | --- | --- |
| Garam masala | 10 g | |
| Ground turmeric | 5 g | |
| Kashmiri chilli powder | 8 g | for colour |
| Fine sea salt | 12 g | |
| Kasoori methi | 4 g | crushed, at the end |
</context>

<context chunk_id="chicken-tikka-masala::structure::c004" recipe_id="chicken-tikka-masala" source_file="chicken-tikka-masala.md" section="allergens" dietary_tags="gluten-free|contains-dairy">
Recipe: Chicken Tikka Masala (cuisine: indian)
Section: Allergens
Contains dairy (yoghurt, cream, ghee). Naturally gluten free.
</context>

<context chunk_id="chicken-tikka-masala::structure::c003" recipe_id="chicken-tikka-masala" source_file="chicken-tikka-masala.md" section="method" dietary_tags="gluten-free|contains-dairy">
Recipe: Chicken Tikka Masala (cuisine: indian)
Section: Method
Marinate the chicken in the yoghurt with half the ginger, garlic and spices for at least
four hours, ideally overnight. The acid in the yoghurt does the tenderising; more than
twenty-four hours and the texture turns mealy.

Thread onto skewers and grill hard until the edges char in places. You want colour, not
doneness — the pieces finish in the sauce.

Soften the onion in the ghee, add the remaining ginger, garlic and spices, then the tomatoes.
Cook until thick and glossy, blend smooth, and return to the pan. Add the grilled chicken
and simmer for ten minutes, then stir in the cream and the crushed kasoori methi off the
heat.
</context>

<context chunk_id="chana-masala::structure::c001" recipe_id="chana-masala" source_file="chana-masala.md" section="ingredients" dietary_tags="vegan|gluten-free|dairy-free">
Recipe: Chana Masala (cuisine: indian)
Section: Ingredients (rows 1-8 of 11)
| Ingredient | Weight | Notes |
| --- | --- | --- |
| Dried chickpeas | 400 g | soaked overnight |
| Brown onion, diced | 300 g | |
| Tinned plum tomatoes | 400 g | crushed by hand |
| Sunflower oil | 45 g | |
| Ginger, grated | 25 g | |
| Garlic, crushed | 20 g | |
| Ground cumin | 8 g | |
| Ground coriander | 8 g | |
</context>

<context chunk_id="chana-masala::structure::c003" recipe_id="chana-masala" source_file="chana-masala.md" section="method" dietary_tags="vegan|gluten-free|dairy-free">
Recipe: Chana Masala (cuisine: indian)
Section: Method
Drain the soaked chickpeas, cover with fresh water and simmer for 50 minutes until they
give completely under a spoon. Keep the cooking liquor.

Fry the onion in the oil over medium heat for a full fifteen minutes, until it collapses and
takes on colour at the edges. Add the ginger and garlic, then the ground spices, and stir
for a minute so they toast rather than steam.

Add the tomatoes and cook until the oil separates and pools at the edge of the pan. Tip in
the chickpeas with enough of their liquor to loosen, season with the salt, and simmer for
twenty minutes. Stir the amchur through off the heat so its sourness stays bright.
</context>
```

**output**:

```json
{
  "can_substitute": false,
  "base_recipe_id": "chicken-tikka-masala",
  "title": "Chicken Tikka Masala",
  "swaps": [],
  "ingredients": [],
  "method": "",
  "oven": "",
  "allergen_warning": "",
  "unsupported": "The provided context does not contain information regarding the use of Greek yoghurt as a substitute for full fat yoghurt."
}
```

`sound`: [ ] true   [ ] false

---

## r02

**request**: `napa cabbage kimchi` -> `can i swap the fish sauce in the kimchi for soy sauce`

context blocks given (7):

```
<context chunk_id="napa-kimchi::structure::c002" recipe_id="napa-kimchi" source_file="card-02-napa-kimchi.md" section="ingredients" dietary_tags="contains-fish|contains-shellfish|gluten-free|dairy-free">
Recipe: Napa Cabbage Kimchi (cuisine: korean)
Section: Ingredients (rows 9-9 of 9)
| Ingredient | Weight | Baker's % |
| --- | --- | --- |
| Ginger, grated | 12 g | 1.2% |
</context>

<context chunk_id="napa-kimchi::structure::c003" recipe_id="napa-kimchi" source_file="card-02-napa-kimchi.md" section="method" dietary_tags="contains-fish|contains-shellfish|gluten-free|dairy-free">
Recipe: Napa Cabbage Kimchi (cuisine: korean)
Section: Method
Quarter the cabbage lengthways and work the coarse sea salt between every leaf, heaviest at
the stem end. Leave it to weep for two hours, turning the quarters once, then rinse three
times and drain stem-down for thirty minutes.

Stir the gochugaru into the cooled rice porridge and let it bloom for ten minutes before
adding the daikon, fish sauce, shrimp paste, garlic and ginger. Paste every leaf, then pack
into the jar and press down until the brine rises above the vegetables.

Keep the vegetables submerged below the brine for the whole ferment. Leave at 18 C for two
days until the jar smells sour and fizzes when tapped, then move it to the fridge.
</context>

<context chunk_id="napa-kimchi::structure::c004" recipe_id="napa-kimchi" source_file="card-02-napa-kimchi.md" section="allergens" dietary_tags="contains-fish|contains-shellfish|gluten-free|dairy-free">
Recipe: Napa Cabbage Kimchi (cuisine: korean)
Section: Allergens
Contains fish (fish sauce) and shellfish (salted shrimp paste). Not suitable for anyone with
a shellfish allergy. Gluten-free despite the name of the glutinous rice.
</context>

<context chunk_id="napa-kimchi::structure::c000" recipe_id="napa-kimchi" source_file="card-02-napa-kimchi.md" section="title" dietary_tags="contains-fish|contains-shellfish|gluten-free|dairy-free">
Recipe: Napa Cabbage Kimchi (cuisine: korean)
Section: Title
# Napa Cabbage Kimchi

A cold-fermented winter kimchi. Percentages are relative to the trimmed cabbage weight of
1000 g, not to the finished jar.
</context>

<context chunk_id="napa-kimchi::structure::c001" recipe_id="napa-kimchi" source_file="card-02-napa-kimchi.md" section="ingredients" dietary_tags="contains-fish|contains-shellfish|gluten-free|dairy-free">
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
</context>

<context chunk_id="red-sauerkraut::structure::c003" recipe_id="red-sauerkraut" source_file="card-04-red-cabbage-sauerkraut.md" section="allergens" dietary_tags="vegan|gluten-free|dairy-free">
Recipe: Red Cabbage Sauerkraut (cuisine: german)
Section: Allergens
No declared allergens. Made in a kitchen that also handles wheat, mustard and sesame.
</context>

<context chunk_id="pad-thai::structure::c003" recipe_id="pad-thai" source_file="pad-thai.md" section="method" dietary_tags="gluten-free|contains-egg|contains-shellfish|contains-peanut">
Recipe: Prawn Pad Thai (cuisine: thai)
Section: Method
Soak the noodles in warm water for thirty minutes until pliable but still firm at the core.
They finish cooking in the pan and will turn to paste if you soften them fully now.

Melt the palm sugar with the tamarind and fish sauce over low heat until it forms a smooth
syrup. This sauce is the whole dish; taste it and adjust before it goes near the wok.
</context>
```

**output**:

```json
{
  "can_substitute": false,
  "base_recipe_id": "napa-kimchi",
  "title": "Napa Cabbage Kimchi",
  "swaps": [],
  "ingredients": [],
  "method": "",
  "oven": "",
  "allergen_warning": "",
  "unsupported": "The archive does not contain a recipe or instruction that grounds the substitution of fish sauce with soy sauce."
}
```

`sound`: [ ] true   [ ] false

---

## r03

**request**: `gluten-free sandwich loaf` -> `what can i use instead of psyllium husk`

context blocks given (7):

```
<context chunk_id="gf-sandwich-loaf::structure::c003" recipe_id="gf-sandwich-loaf" source_file="card-10-gluten-free-sandwich-loaf.md" section="allergens" dietary_tags="gluten-free|vegan|dairy-free">
Recipe: Gluten-Free Sandwich Loaf (cuisine: european)
Section: Allergens
Gluten free, provided the flour blend is certified. No egg or dairy.
</context>

<context chunk_id="gf-sandwich-loaf::structure::c000" recipe_id="gf-sandwich-loaf" source_file="card-10-gluten-free-sandwich-loaf.md" section="title" dietary_tags="gluten-free|vegan|dairy-free">
Recipe: Gluten-Free Sandwich Loaf (cuisine: european)
Section: Title
# Gluten-Free Sandwich Loaf

A lean tin loaf. Baker's percentages are relative to the 500 g flour blend.
</context>

<context chunk_id="gf-sandwich-loaf::structure::c001" recipe_id="gf-sandwich-loaf" source_file="card-10-gluten-free-sandwich-loaf.md" section="ingredients" dietary_tags="gluten-free|vegan|dairy-free">
Recipe: Gluten-Free Sandwich Loaf (cuisine: european)
Section: Ingredients (rows 1-7 of 7)
| Ingredient | Weight | Baker's % |
| --- | --- | --- |
| Gluten-free flour blend | 500 g | 100% |
| Xanthan gum | 10 g | 2% |
| Psyllium husk | 15 g | 3% |
| Instant dried yeast | 7 g | 1.4% |
| Fine sea salt | 10 g | 2% |
| Water (30 C) | 400 g | 80% |
| Olive oil | 30 g | 6% |
</context>

<context chunk_id="gf-sandwich-loaf::structure::c002" recipe_id="gf-sandwich-loaf" source_file="card-10-gluten-free-sandwich-loaf.md" section="method" dietary_tags="gluten-free|vegan|dairy-free">
Recipe: Gluten-Free Sandwich Loaf (cuisine: european)
Section: Method
Whisk the flour blend, xanthan gum, psyllium husk, yeast and salt together dry so both gums
disperse before they meet water. Psyllium hydrates far faster than xanthan, so skipping the
dry mix leaves you picking gel lumps out of the batter.

Add the warm water and oil, beat for four minutes, then rest the batter for twenty so the
psyllium sets up. It should hold a peak rather than pour.

Scrape into a lined tin, prove until risen by half, and bake at 200 C for 45 minutes.
</context>

<context chunk_id="lemon-drizzle-cake::structure::c003" recipe_id="lemon-drizzle-cake" source_file="lemon-drizzle-cake.md" section="allergens" dietary_tags="vegetarian|contains-egg|contains-dairy">
Recipe: Lemon Drizzle Loaf (cuisine: british)
Section: Allergens
Contains wheat (gluten), egg and dairy.
</context>

<context chunk_id="sourdough-2kg::structure::c000" recipe_id="sourdough-2kg" source_file="card-01-country-sourdough-2kg.md" section="title" dietary_tags="vegan|dairy-free|nut-free">
Recipe: 2kg Country Sourdough (cuisine: european)
Section: Title
# 2kg Country Sourdough

A two-day naturally leavened loaf. Baker's percentages are relative to the total flour
weight of 1000 g, so the white and rye flours together make 100%.
</context>

<context chunk_id="gf-brioche::structure::c001" recipe_id="gf-brioche" source_file="card-07-gluten-free-brioche.md" section="ingredients" dietary_tags="gluten-free|contains-egg|contains-dairy">
Recipe: Gluten-Free Brioche (cuisine: french)
Section: Ingredients (rows 1-8 of 8)
| Ingredient | Weight | Baker's % |
| --- | --- | --- |
| Gluten-free flour blend | 500 g | 100% |
| Xanthan gum | 6 g | 1.2% |
| Caster sugar | 60 g | 12% |
| Instant dried yeast | 8 g | 1.6% |
| Fine sea salt | 9 g | 1.8% |
| Whole eggs | 250 g | 50% |
| Whole milk (32 C) | 150 g | 30% |
| Unsalted butter, softened | 175 g | 35% |
</context>
```

**output**:

```json
{
  "can_substitute": false,
  "base_recipe_id": "gf-sandwich-loaf",
  "title": "Gluten-Free Sandwich Loaf",
  "swaps": [],
  "ingredients": [],
  "method": "",
  "oven": "",
  "allergen_warning": "",
  "unsupported": "The provided context does not contain any information regarding a substitute for psyllium husk."
}
```

`sound`: [ ] true   [ ] false

