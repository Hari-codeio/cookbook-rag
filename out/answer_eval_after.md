# Answer-level evaluation and failure tally - retriever=rerank

```
retriever   : rerank
k           : 3
provider    : gemini
model       : gemini-3.6-flash
generated   : 2026-08-19T15:42:29+00:00
```

## Tally

| label | count |
|---|---|
| PASS | 11 |
| R (retrieval fetched bad context) | 1 |
| G (model misused good context) | 0 |
| Not-In-Corpus | 0 |

## Per-question, with one line of evidence each

| id | question | expected chunk in top-3? | refused? | label | evidence |
|---|---|---|---|---|---|
| g01 | how much xanthan gum in the gluten free brioche | yes | no | **PASS** | answer contains '6 g' |
| g02 | xanthan for the gf sandwich loaf | yes | no | **PASS** | answer contains '10 g' |
| g03 | psyllium husk amount | yes | no | **PASS** | answer contains '15 g' |
| g04 | how much saeujeot in the kimchi | yes | no | **PASS** | answer contains '20 g' |
| g05 | amchur amount chana masala | yes | no | **PASS** | answer contains '6 g' |
| g06 | what temp do i bake the 2kg sourdough at | yes | no | **PASS** | answer contains '250 C' |
| g07 | how much butter in the chocolate brioche | yes | no | **PASS** | answer contains '225 g' |
| g08 | salt in the rye sourdough | yes | no | **PASS** | answer contains '19 g' |
| g09 | hydration of the wholemeal loaf | **no** | yes | **R** | correct chunk wholemeal-sourdough::structure::c001 was NOT in the top-3; retrieved ['wholemeal-sourdough::structure::c000', 'gf-sandwich-loaf::structure::c002', 'wholemeal-sourdough::structure::c002'] |
| g10 | can i strain kefir with a metal sieve | yes | no | **PASS** | answer contains 'nylon' |
| g11 | why do pickles turn soft | yes | no | **PASS** | answer contains 'blossom' |
| g12 | is the kimchi ok if im allergic to prawns | yes | no | **PASS** | answer contains 'shrimp' |

## Transcripts

### g01 - how much xanthan gum in the gluten free brioche

known-correct: 6 g (1.2%)   expected chunk: `gf-brioche::structure::c001`

```text
top-3: ['gf-brioche::structure::c001', 'gf-brioche::structure::c002', 'gf-sandwich-loaf::structure::c001']

The gluten-free brioche recipe requires 6 g (1.2%) of xanthan gum.

  - The gluten-free brioche recipe requires 6 g (1.2%) of xanthan gum.  [gf-brioche::structure::c001]
```

label: **PASS** - answer contains '6 g'

### g02 - xanthan for the gf sandwich loaf

known-correct: 10 g (2%)   expected chunk: `gf-sandwich-loaf::structure::c001`

```text
top-3: ['gf-sandwich-loaf::structure::c002', 'gf-sandwich-loaf::structure::c001', 'gf-sandwich-loaf::structure::c003']

For the Gluten-Free Sandwich Loaf, the recipe requires 10 g (2% Baker's) of xanthan gum. It should be whisked dry with the flour blend, psyllium husk, yeast, and salt before meeting water so that both gums disperse properly; skipping this dry mix results in gel lumps in the batter because psyllium hydrates far faster than xanthan.

  - For the Gluten-Free Sandwich Loaf, the recipe requires 10 g (2% Baker's) of xanthan gum.  [gf-sandwich-loaf::structure::c001]
  - It should be whisked dry with the flour blend, psyllium husk, yeast, and salt before meeting water so that both gums disperse properly; skipping this dry mix results in gel lumps in the batter because psyllium hydrates far faster than xanthan.  [gf-sandwich-loaf::structure::c002]
```

label: **PASS** - answer contains '10 g'

### g03 - psyllium husk amount

known-correct: 15 g (3%)   expected chunk: `gf-sandwich-loaf::structure::c001`

```text
top-3: ['gf-sandwich-loaf::structure::c001', 'gf-sandwich-loaf::structure::c002', 'chana-masala::structure::c003']

The amount of psyllium husk required is 15 g (or 3% baker's percentage).

  - The amount of psyllium husk required is 15 g (or 3% baker's percentage).  [gf-sandwich-loaf::structure::c001]
```

label: **PASS** - answer contains '15 g'

### g04 - how much saeujeot in the kimchi

known-correct: 20 g (2%)   expected chunk: `napa-kimchi::structure::c001`

```text
top-3: ['napa-kimchi::structure::c001', 'napa-kimchi::structure::c000', 'napa-kimchi::structure::c003']

The recipe requires 20 g (2%) of salted shrimp paste (saeujeot).

  - The recipe requires 20 g (2%) of salted shrimp paste (saeujeot).  [napa-kimchi::structure::c001]
```

label: **PASS** - answer contains '20 g'

### g05 - amchur amount chana masala

known-correct: 6 g   expected chunk: `chana-masala::structure::c002`

```text
top-3: ['chana-masala::structure::c002', 'chana-masala::structure::c003', 'chana-masala::structure::c001']

The recipe for Chana Masala requires 6 g of Amchur (dried mango powder).

  - The recipe for Chana Masala requires 6 g of Amchur (dried mango powder).  [chana-masala::structure::c002]
```

label: **PASS** - answer contains '6 g'

### g06 - what temp do i bake the 2kg sourdough at

known-correct: 250 C with steam for 20 min, then 230 C for 25 min   expected chunk: `sourdough-2kg::structure::c003`

```text
top-3: ['sourdough-2kg::structure::c003', 'sourdough-2kg::structure::c002', 'sourdough-2kg::structure::c001']

You bake the sourdough straight from the fridge at 250 C with steam for twenty minutes, and then drop the temperature to 230 C for a further twenty-five minutes.

  - Bake straight from the fridge at 250 C with steam for twenty minutes, then vent the oven and drop to 230 C for a further twenty-five minutes until the crust is deeply coloured.  [sourdough-2kg::structure::c003]
```

label: **PASS** - answer contains '250 C'

### g07 - how much butter in the chocolate brioche

known-correct: 225 g (45%)   expected chunk: `chocolate-brioche::structure::c001`

```text
top-3: ['chocolate-brioche::structure::c001', 'classic-brioche::structure::c001', 'chocolate-brioche::structure::c002']

The Chocolate Chip Brioche recipe requires 225 g of softened unsalted butter.

  - The Chocolate Chip Brioche recipe requires 225 g of softened unsalted butter.  [chocolate-brioche::structure::c001]
```

label: **PASS** - answer contains '225 g'

### g08 - salt in the rye sourdough

known-correct: 19 g (1.9%)   expected chunk: `rye-sourdough::structure::c001`

```text
top-3: ['rye-sourdough::structure::c001', 'rye-sourdough::structure::c002', 'sourdough-2kg::structure::c001']

The Light Rye Sourdough recipe requires 19 g (1.9%) of fine sea salt.

  - The Light Rye Sourdough recipe requires 19 g (1.9%) of fine sea salt.  [rye-sourdough::structure::c001]
```

label: **PASS** - answer contains '19 g'

### g09 - hydration of the wholemeal loaf

known-correct: 80% (800 g water to 1000 g flour)   expected chunk: `wholemeal-sourdough::structure::c001`

```text
top-3: ['wholemeal-sourdough::structure::c000', 'gf-sandwich-loaf::structure::c002', 'wholemeal-sourdough::structure::c002']

INSUFFICIENT_CONTEXT: The hydration percentage or the specific weights of water, starter, and flour for the Wholemeal Sourdough recipe.
```

label: **R** - correct chunk wholemeal-sourdough::structure::c001 was NOT in the top-3; retrieved ['wholemeal-sourdough::structure::c000', 'gf-sandwich-loaf::structure::c002', 'wholemeal-sourdough::structure::c002']

### g10 - can i strain kefir with a metal sieve

known-correct: No, use nylon, never metal   expected chunk: `milk-kefir::structure::c002`

```text
top-3: ['milk-kefir::structure::c002', 'milk-kefir::structure::c000', 'milk-kefir::structure::c003']

No, you should strain the kefir through a nylon sieve and never use metal.

  - Strain through a nylon sieve, never metal  [milk-kefir::structure::c002]
```

label: **PASS** - answer contains 'nylon'

### g11 - why do pickles turn soft

known-correct: The enzyme in the blossom end, so trim it off   expected chunk: `dill-pickles::structure::c002`

```text
top-3: ['dill-pickles::structure::c002', 'dill-pickles::structure::c000', 'dill-pickles::structure::c003']

Pickles turn soft because of an enzyme that lives in the blossom end of the cucumber.

  - Pickles turn soft because of an enzyme that lives in the blossom end of the cucumber.  [dill-pickles::structure::c002]
```

label: **PASS** - answer contains 'blossom'

### g12 - is the kimchi ok if im allergic to prawns

known-correct: No, it contains salted shrimp paste and fish sauce   expected chunk: `napa-kimchi::structure::c004`

```text
top-3: ['napa-kimchi::structure::c004', 'pad-thai::structure::c005', 'pad-thai::structure::c000']

No, the Napa Cabbage Kimchi is not suitable for anyone with a shellfish allergy, as it contains salted shrimp paste.

  - The Napa Cabbage Kimchi contains shellfish (salted shrimp paste).  [napa-kimchi::structure::c004]
  - The Napa Cabbage Kimchi is not suitable for anyone with a shellfish allergy.  [napa-kimchi::structure::c004]
```

label: **PASS** - answer contains 'shrimp'

