# Week 6 bonus - RAGAS faithfulness and context precision

```
substitutions     : out/substitutions_v1.jsonl  (25 cases)
substitutions sha : f50218d27cf5bf2e00ab641c2c3242001e8a5fe415e7e2eb7ef3720343ba6849
reference         : eval/ragas_reference.json
reference sha     : 5a0faeb1a4366d7ea47d7c842405662943bfc10870b6ead7db3263ab4d673bc0
metric model      : gemini-3.1-flash-lite  (pinned)
llm calls made    : 0   cache hits: 50
```

## The two averages, which is all a dashboard would show you

```
mean faithfulness      : 0.859   (n=25)
mean context precision : 0.989   (n=25)
```

## Per case

| case | mode | faithfulness | context precision | grounded on | rank | in base? | declined w/ donor? |
|---|---|---|---|---|---|---|---|
| `c01` | `refuses-swap-instead-of-quoting-card` | 0.700 | 0.932 | `classic-brioche` | 3 | yes | no |
| `c02` | `refuses-swap-instead-of-quoting-card` | 1.000 | 1.000 | `chocolate-brioche` | 1 | yes | no |
| `c03` | `refuses-swap-instead-of-quoting-card` | 1.000 | 1.000 | `napa-kimchi` | 1 | yes | no |
| `c04` | `refuses-swap-instead-of-quoting-card` | 0.588 | 1.000 | `sourdough-2kg` | 1 | yes | no |
| `c05` | `refuses-swap-instead-of-quoting-card` | 1.000 | 1.000 | `gf-sandwich-loaf` | 1 | yes | **YES** |
| `c06` | `refuses-swap-instead-of-quoting-card` | 0.429 | 1.000 | `chicken-tikka-masala` | 1 | yes | no |
| `c09` | `refuses-swap-instead-of-quoting-card` | 1.000 | 1.000 | `rye-sourdough` | 1 | yes | no |
| `c11` | `refuses-arithmetic-with-table-on-screen` | 0.625 | 0.986 | `classic-brioche` | 5 | yes | **YES** |
| `c12` | `refuses-arithmetic-with-table-on-screen` | 1.000 | 1.000 | `sourdough-2kg` | 2 | yes | **YES** |
| `c13` | `refuses-arithmetic-with-table-on-screen` | 0.750 | 1.000 | `gf-sandwich-loaf` | 1 | yes | no |
| `c14` | `refuses-arithmetic-with-table-on-screen` | 0.667 | 1.000 | `red-sauerkraut` | 1 | yes | no |
| `c15` | `drops-bakers-percentage` | 0.733 | 1.000 | `chocolate-brioche` | 1 | yes | no |
| `c16` | `drops-bakers-percentage` | 0.625 | 1.000 | `wholemeal-sourdough` | 3 | yes | no |
| `c17` | `drops-bakers-percentage` | 1.000 | 0.854 | `gf-brioche` | 1 | yes | no |
| `c18` | `drops-bakers-percentage` | 0.842 | 1.000 | `classic-brioche` | 5 | yes | no |
| `c19` | `compares-only-retrieved-cards` | 1.000 | 1.000 | `gf-brioche` | 1 | yes | no |
| `c20` | `compares-only-retrieved-cards` | 0.947 | 1.000 | `sourdough-2kg` | 1 | yes | no |
| `c21` | `compares-only-retrieved-cards` | 1.000 | 1.000 | `gf-sandwich-loaf` | 1 | yes | no |
| `c22` | `says-missing-while-on-screen` | 0.571 | 0.986 | `classic-brioche` | 1 | yes | no |
| `c23` | `says-missing-while-on-screen` | 1.000 | 1.000 | `sourdough-2kg` | 1 | yes | **YES** |
| `c24` | `refuses-when-no-recipe-named` | 1.000 | 0.968 | `milk-kefir` | 1 | yes | no |
| `c25` | `refuses-when-no-recipe-named` | 1.000 | 1.000 | `lemon-drizzle-cake` | 5 | yes | **YES** |
| `r01` | `refuses-swap-instead-of-quoting-card` | 1.000 | 1.000 | `chicken-tikka-masala` | 1 | yes | no |
| `r02` | `refuses-swap-instead-of-quoting-card` | 1.000 | 1.000 | `napa-kimchi` | 1 | yes | no |
| `r03` | `refuses-swap-instead-of-quoting-card` | 1.000 | 1.000 | `gf-sandwich-loaf` | 1 | yes | no |

## Confidently, faithfully wrong

Cases scoring faithfulness >= 0.9 that still answered about a dish the request could not defensibly name, or declined with a donor card sitting in their own retrieved context: **4 of 25**.

### `c05` - gluten-free sandwich loaf / enriched, like a brioche

```
faithfulness      : 1.000   (4/4 claims entailed)
context precision : 1.000
grounded on       : gf-sandwich-loaf   at rank 1
in reference base : True
declined          : True
donors on screen  : gf-brioche   (best at rank 5)
walked past       : -
```

Retrieved context, in rank order:

| rank | chunk | relevant | P@k | contributes |
|---|---|---|---|---|
| 1 | `gf-sandwich-loaf::structure::c003` | 1 | 1.0000 | 1.0000 |
| 2 | `gf-sandwich-loaf::structure::c000` | 1 | 1.0000 | 1.0000 |
| 3 | `gf-sandwich-loaf::structure::c001` | 1 | 1.0000 | 1.0000 |
| 4 | `gf-sandwich-loaf::structure::c002` | 1 | 1.0000 | 1.0000 |
| 5 | `gf-brioche::structure::c001` | 1 | 1.0000 | 1.0000 |
| 6 | `gf-brioche::structure::c000` | 1 | 1.0000 | 1.0000 |
| 7 | `lemon-drizzle-cake::structure::c003` | 0 | 0.8571 | 0.0000 |
| 8 | `sourdough-2kg::structure::c000` | 0 | 0.7500 | 0.0000 |

Claims and their verdicts:

- `1` The result is titled Gluten-Free Sandwich Loaf.
  - The title is explicitly stated in the context for the Gluten-Free Sandwich Loaf.
- `1` The result is based on the recipe gf-sandwich-loaf.
  - The context explicitly identifies the recipe ID as gf-sandwich-loaf.
- `1` The archive does not provide a method to transform a lean sandwich loaf into an enriched brioche-style dough.
  - The provided context contains methods for both recipes separately but does not contain instructions for transforming one into the other.
- `1` The archive does not provide an ingredient list to transform a lean sandwich loaf into an enriched brioche-style dough.
  - The provided context contains ingredient lists for both recipes separately but does not contain a list for transforming one into the other.

### `c12` - 2kg country sourdough / wholemeal, scaled to 500 g total flour

```
faithfulness      : 1.000   (4/4 claims entailed)
context precision : 1.000
grounded on       : sourdough-2kg   at rank 2
in reference base : True
declined          : True
donors on screen  : wholemeal-sourdough   (best at rank 1)
walked past       : wholemeal-sourdough
```

Retrieved context, in rank order:

| rank | chunk | relevant | P@k | contributes |
|---|---|---|---|---|
| 1 | `wholemeal-sourdough::structure::c001` | 1 | 1.0000 | 1.0000 |
| 2 | `sourdough-2kg::structure::c001` | 1 | 1.0000 | 1.0000 |
| 3 | `sourdough-2kg::structure::c003` | 1 | 1.0000 | 1.0000 |
| 4 | `sourdough-2kg::structure::c000` | 1 | 1.0000 | 1.0000 |
| 5 | `wholemeal-sourdough::structure::c000` | 1 | 1.0000 | 1.0000 |
| 6 | `sourdough-2kg::structure::c004` | 1 | 1.0000 | 1.0000 |
| 7 | `sourdough-2kg::structure::c002` | 1 | 1.0000 | 1.0000 |
| 8 | `wholemeal-sourdough::structure::c002` | 1 | 1.0000 | 1.0000 |

Claims and their verdicts:

- `1` The result is titled 2kg Country Sourdough.
  - The context explicitly lists a recipe titled 2kg Country Sourdough.
- `1` The result is based on the recipe sourdough-2kg.
  - The context identifies the recipe ID for 2kg Country Sourdough as sourdough-2kg.
- `1` The archive does not contain instructions to scale the recipe to 500 g total flour weight.
  - The provided context contains no instructions for scaling the recipes.
- `1` The archive does not contain a mechanism to scale the recipe to 500 g total flour weight.
  - The provided context contains no mechanism for scaling the recipes.

### `c23` - 2kg country sourdough / raise the hydration to match the wettest loaf in the archive

```
faithfulness      : 1.000   (4/4 claims entailed)
context precision : 1.000
grounded on       : sourdough-2kg   at rank 1
in reference base : True
declined          : True
donors on screen  : wholemeal-sourdough   (best at rank 6)
walked past       : -
```

Retrieved context, in rank order:

| rank | chunk | relevant | P@k | contributes |
|---|---|---|---|---|
| 1 | `sourdough-2kg::structure::c001` | 1 | 1.0000 | 1.0000 |
| 2 | `sourdough-2kg::structure::c003` | 1 | 1.0000 | 1.0000 |
| 3 | `sourdough-2kg::structure::c000` | 1 | 1.0000 | 1.0000 |
| 4 | `sourdough-2kg::structure::c004` | 1 | 1.0000 | 1.0000 |
| 5 | `sourdough-2kg::structure::c002` | 1 | 1.0000 | 1.0000 |
| 6 | `wholemeal-sourdough::structure::c000` | 1 | 1.0000 | 1.0000 |
| 7 | `rye-sourdough::structure::c000` | 0 | 0.8571 | 0.0000 |

Claims and their verdicts:

- `1` The result is titled 2kg Country Sourdough.
  - The title is explicitly stated in the context for the 2kg Country Sourdough recipe.
- `1` The result is based on the recipe sourdough-2kg.
  - The context explicitly identifies the recipe ID as sourdough-2kg.
- `1` The archive does not provide hydration percentages for other recipes to determine the wettest loaf.
  - The provided context only contains ingredient tables for the 2kg Country Sourdough recipe, lacking ingredient data for the other listed recipes.
- `1` The archive does not provide a method to adjust the water quantity in the base recipe.
  - The method section for the 2kg Country Sourdough recipe does not contain instructions for adjusting water quantities.

### `c25` - the loaf / gluten free

```
faithfulness      : 1.000   (4/4 claims entailed)
context precision : 1.000
grounded on       : lemon-drizzle-cake   at rank 5
in reference base : True
declined          : True
donors on screen  : gf-sandwich-loaf   (best at rank 1)
walked past       : gf-sandwich-loaf
```

Retrieved context, in rank order:

| rank | chunk | relevant | P@k | contributes |
|---|---|---|---|---|
| 1 | `gf-sandwich-loaf::structure::c003` | 1 | 1.0000 | 1.0000 |
| 2 | `gf-sandwich-loaf::structure::c001` | 1 | 1.0000 | 1.0000 |
| 3 | `gf-sandwich-loaf::structure::c000` | 1 | 1.0000 | 1.0000 |
| 4 | `gf-sandwich-loaf::structure::c002` | 1 | 1.0000 | 1.0000 |
| 5 | `lemon-drizzle-cake::structure::c003` | 1 | 1.0000 | 1.0000 |
| 6 | `lemon-drizzle-cake::structure::c000` | 1 | 1.0000 | 1.0000 |
| 7 | `lemon-drizzle-cake::structure::c002` | 1 | 1.0000 | 1.0000 |
| 8 | `sourdough-2kg::structure::c000` | 1 | 1.0000 | 1.0000 |

Claims and their verdicts:

- `1` The result is titled Lemon Drizzle Loaf.
  - The title is explicitly stated in the context for the Lemon Drizzle Loaf recipe.
- `1` The result is based on the recipe lemon-drizzle-cake.
  - The context identifies the recipe ID as lemon-drizzle-cake.
- `1` The archive does not contain a gluten-free version of the Lemon Drizzle Loaf.
  - The provided context only contains a standard Lemon Drizzle Loaf recipe which contains wheat.
- `1` The archive does not provide a method to substitute wheat flour with a gluten-free flour blend for the Lemon Drizzle Loaf recipe.
  - The method section for the Lemon Drizzle Loaf does not mention any substitution instructions.

## Why the average hides it

```
flagged cases   n=4   mean faithfulness 1.000  mean context precision 1.000
everything else n=21  mean faithfulness 0.832  mean context precision 0.987
```

The flagged cases score AT OR ABOVE the run average on both metrics. They do not drag either mean down, so no threshold on either number can separate them out. Averaging is not what hides them - they are invisible at the per-case level too, because neither metric ever forms the pair (claim, chunk that supported it). Faithfulness joins every chunk into one premise, so support by ANY chunk reads the same as support by the RIGHT chunk. Context precision never looks at the answer at all. The failure lives in the gap between them, and the free deterministic check in the `declined w/ donor?` column is what finds it - no model call, no threshold to tune.

