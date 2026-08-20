# Answer-level evaluation and failure tally - retriever=dense

```
retriever   : dense
k           : 3
provider    : gemini
model       : gemini-3.6-flash
generated   : 2026-08-19T15:28:44+00:00
```

## Tally

| label | count |
|---|---|
| PASS | 9 |
| R (retrieval fetched bad context) | 2 |
| G (model misused good context) | 1 |
| Not-In-Corpus | 0 |

## Per-question, with one line of evidence each

| id | question | expected chunk in top-3? | refused? | label | evidence |
|---|---|---|---|---|---|
| g01 | how much xanthan gum in the gluten free brioche | yes | no | **PASS** | answer contains '6 g' |
| g02 | xanthan for the gf sandwich loaf | yes | no | **PASS** | answer contains '10 g' |
| g03 | psyllium husk amount | **no** | yes | **R** | correct chunk gf-sandwich-loaf::structure::c001 was NOT in the top-3; retrieved ['red-sauerkraut::structure::c001', 'gf-sandwich-loaf::structure::c002', 'red-sauerkraut::structure::c002'] |
| g04 | how much saeujeot in the kimchi | yes | no | **PASS** | answer contains '20 g' |
| g05 | amchur amount chana masala | yes | no | **PASS** | answer contains '6 g' |
| g06 | what temp do i bake the 2kg sourdough at | yes | no | **PASS** | answer contains '250 C' |
| g07 | how much butter in the chocolate brioche | yes | no | **PASS** | answer contains '225 g' |
| g08 | salt in the rye sourdough | yes | no | **PASS** | answer contains '19 g' |
| g09 | hydration of the wholemeal loaf | **no** | yes | **R** | correct chunk wholemeal-sourdough::structure::c001 was NOT in the top-3; retrieved ['gf-sandwich-loaf::structure::c002', 'wholemeal-sourdough::structure::c000', 'wholemeal-sourdough::structure::c002'] |
| g10 | can i strain kefir with a metal sieve | yes | no | **PASS** | answer contains 'nylon' |
| g11 | why do pickles turn soft | yes | no | **PASS** | answer contains 'blossom' |
| g12 | is the kimchi ok if im allergic to prawns | yes | yes | **G** | correct chunk napa-kimchi::structure::c004 WAS in the top-3 and the model refused anyway |

## Transcripts

### g01 - how much xanthan gum in the gluten free brioche

known-correct: 6 g (1.2%)   expected chunk: `gf-brioche::structure::c001`

```text
top-3: ['gf-brioche::structure::c002', 'gf-brioche::structure::c001', 'gf-brioche::structure::c000']

The Gluten-Free Brioche recipe uses 6 g (1.2%) of xanthan gum.

  - The Gluten-Free Brioche recipe uses 6 g (1.2%) of xanthan gum.  [gf-brioche::structure::c001]
```

label: **PASS** - answer contains '6 g'

### g02 - xanthan for the gf sandwich loaf

known-correct: 10 g (2%)   expected chunk: `gf-sandwich-loaf::structure::c001`

```text
top-3: ['gf-sandwich-loaf::structure::c002', 'gf-sandwich-loaf::structure::c001', 'gf-sandwich-loaf::structure::c003']

For the Gluten-Free Sandwich Loaf, 10 g (2%) of xanthan gum is used. It is whisked dry together with the flour blend, psyllium husk, yeast, and salt so both gums disperse before meeting water.

  - For the Gluten-Free Sandwich Loaf, 10 g (2%) of xanthan gum is used.  [gf-sandwich-loaf::structure::c001]
  - It is whisked dry together with the flour blend, psyllium husk, yeast, and salt so both gums disperse before meeting water.  [gf-sandwich-loaf::structure::c002]
```

label: **PASS** - answer contains '10 g'

### g03 - psyllium husk amount

known-correct: 15 g (3%)   expected chunk: `gf-sandwich-loaf::structure::c001`

```text
top-3: ['red-sauerkraut::structure::c001', 'gf-sandwich-loaf::structure::c002', 'red-sauerkraut::structure::c002']

INSUFFICIENT_CONTEXT: The amount or weight of psyllium husk required in the recipe.
```

label: **R** - correct chunk gf-sandwich-loaf::structure::c001 was NOT in the top-3; retrieved ['red-sauerkraut::structure::c001', 'gf-sandwich-loaf::structure::c002', 'red-sauerkraut::structure::c002']

### g04 - how much saeujeot in the kimchi

known-correct: 20 g (2%)   expected chunk: `napa-kimchi::structure::c001`

```text
top-3: ['napa-kimchi::structure::c002', 'napa-kimchi::structure::c000', 'napa-kimchi::structure::c001']

The recipe calls for 20 g (or 2%) of salted shrimp paste (saeujeot).

  - The recipe calls for 20 g (or 2%) of salted shrimp paste (saeujeot).  [napa-kimchi::structure::c001]
```

label: **PASS** - answer contains '20 g'

### g05 - amchur amount chana masala

known-correct: 6 g   expected chunk: `chana-masala::structure::c002`

```text
top-3: ['chana-masala::structure::c002', 'chana-masala::structure::c000', 'chana-masala::structure::c001']

The amount of amchur (dried mango powder) required for the Chana Masala recipe is 6 g.

  - The amount of amchur (dried mango powder) required for the Chana Masala recipe is 6 g.  [chana-masala::structure::c002]
```

label: **PASS** - answer contains '6 g'

### g06 - what temp do i bake the 2kg sourdough at

known-correct: 250 C with steam for 20 min, then 230 C for 25 min   expected chunk: `sourdough-2kg::structure::c003`

```text
top-3: ['sourdough-2kg::structure::c003', 'sourdough-2kg::structure::c000', 'sourdough-2kg::structure::c002']

You bake the sourdough straight from the fridge at 250 C with steam for twenty minutes, then drop the temperature to 230 C for a further twenty-five minutes.

  - Bake straight from the fridge at 250 C with steam for twenty minutes, then vent the oven and drop to 230 C for a further twenty-five minutes until the crust is deeply coloured.  [sourdough-2kg::structure::c003]
```

label: **PASS** - answer contains '250 C'

### g07 - how much butter in the chocolate brioche

known-correct: 225 g (45%)   expected chunk: `chocolate-brioche::structure::c001`

```text
top-3: ['chocolate-brioche::structure::c002', 'chocolate-brioche::structure::c000', 'chocolate-brioche::structure::c001']

The recipe requires 225 g of softened unsalted butter.

  - The recipe requires 225 g of softened unsalted butter.  [chocolate-brioche::structure::c001]
```

label: **PASS** - answer contains '225 g'

### g08 - salt in the rye sourdough

known-correct: 19 g (1.9%)   expected chunk: `rye-sourdough::structure::c001`

```text
top-3: ['rye-sourdough::structure::c001', 'rye-sourdough::structure::c002', 'rye-sourdough::structure::c003']

The Light Rye Sourdough recipe requires 19 g of fine sea salt, which is 1.9% in baker's percentage. The method instructions direct to add the salt and pinch it through after the autolyse.

  - The Light Rye Sourdough recipe requires 19 g of fine sea salt, which is 1.9% in baker's percentage.  [rye-sourdough::structure::c001]
  - The method instructions direct to add the salt and pinch it through.  [rye-sourdough::structure::c002]
```

label: **PASS** - answer contains '19 g'

### g09 - hydration of the wholemeal loaf

known-correct: 80% (800 g water to 1000 g flour)   expected chunk: `wholemeal-sourdough::structure::c001`

```text
top-3: ['gf-sandwich-loaf::structure::c002', 'wholemeal-sourdough::structure::c000', 'wholemeal-sourdough::structure::c002']

INSUFFICIENT_CONTEXT: The hydration percentage or the specific amount of water for the wholemeal sourdough loaf is not mentioned in the context.
```

label: **R** - correct chunk wholemeal-sourdough::structure::c001 was NOT in the top-3; retrieved ['gf-sandwich-loaf::structure::c002', 'wholemeal-sourdough::structure::c000', 'wholemeal-sourdough::structure::c002']

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

  - The enzyme that lives in the blossom end of the cucumber is what turns a jar of pickles soft.  [dill-pickles::structure::c002]
```

label: **PASS** - answer contains 'blossom'

### g12 - is the kimchi ok if im allergic to prawns

known-correct: No, it contains salted shrimp paste and fish sauce   expected chunk: `napa-kimchi::structure::c004`

```text
top-3: ['napa-kimchi::structure::c004', 'pad-thai::structure::c005', 'pad-thai::structure::c003']

INSUFFICIENT_CONTEXT: The context does not state whether a prawn allergy is a shellfish allergy, or whether the kimchi is safe for someone with a prawn allergy.
```

label: **G** - correct chunk napa-kimchi::structure::c004 WAS in the top-3 and the model refused anyway

