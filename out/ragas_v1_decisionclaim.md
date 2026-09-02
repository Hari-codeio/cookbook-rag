# Week 6 bonus - RAGAS faithfulness and context precision

```
substitutions     : out/substitutions_v1.jsonl  (25 cases)
substitutions sha : f50218d27cf5bf2e00ab641c2c3242001e8a5fe415e7e2eb7ef3720343ba6849
reference         : eval/ragas_reference.json
reference sha     : 5a0faeb1a4366d7ea47d7c842405662943bfc10870b6ead7db3263ab4d673bc0
metric model      : gemini-3.1-flash-lite  (pinned)
llm calls made    : 44   cache hits: 6
```

## The two averages, which is all a dashboard would show you

```
mean faithfulness      : 0.699   (n=25)
mean context precision : 0.989   (n=25)
```

## Per case

| case | mode | faithfulness | context precision | grounded on | rank | in base? | declined w/ donor? |
|---|---|---|---|---|---|---|---|
| `c01` | `refuses-swap-instead-of-quoting-card` | 0.650 | 0.932 | `classic-brioche` | 3 | yes | no |
| `c02` | `refuses-swap-instead-of-quoting-card` | 0.750 | 1.000 | `chocolate-brioche` | 1 | yes | no |
| `c03` | `refuses-swap-instead-of-quoting-card` | 0.750 | 1.000 | `napa-kimchi` | 1 | yes | no |
| `c04` | `refuses-swap-instead-of-quoting-card` | 0.579 | 1.000 | `sourdough-2kg` | 1 | yes | no |
| `c05` | `refuses-swap-instead-of-quoting-card` | 0.750 | 1.000 | `gf-sandwich-loaf` | 1 | yes | **YES** |
| `c06` | `refuses-swap-instead-of-quoting-card` | 0.133 | 1.000 | `chicken-tikka-masala` | 1 | yes | no |
| `c09` | `refuses-swap-instead-of-quoting-card` | 0.750 | 1.000 | `rye-sourdough` | 1 | yes | no |
| `c11` | `refuses-arithmetic-with-table-on-screen` | 0.444 | 0.986 | `classic-brioche` | 5 | yes | **YES** |
| `c12` | `refuses-arithmetic-with-table-on-screen` | 0.750 | 1.000 | `sourdough-2kg` | 2 | yes | **YES** |
| `c13` | `refuses-arithmetic-with-table-on-screen` | 0.750 | 1.000 | `gf-sandwich-loaf` | 1 | yes | no |
| `c14` | `refuses-arithmetic-with-table-on-screen` | 0.500 | 1.000 | `red-sauerkraut` | 1 | yes | no |
| `c15` | `drops-bakers-percentage` | 0.688 | 1.000 | `chocolate-brioche` | 1 | yes | no |
| `c16` | `drops-bakers-percentage` | 0.500 | 1.000 | `wholemeal-sourdough` | 3 | yes | no |
| `c17` | `drops-bakers-percentage` | 0.833 | 0.854 | `gf-brioche` | 1 | yes | no |
| `c18` | `drops-bakers-percentage` | 0.667 | 1.000 | `classic-brioche` | 5 | yes | no |
| `c19` | `compares-only-retrieved-cards` | 0.947 | 1.000 | `gf-brioche` | 1 | yes | no |
| `c20` | `compares-only-retrieved-cards` | 0.955 | 1.000 | `sourdough-2kg` | 1 | yes | no |
| `c21` | `compares-only-retrieved-cards` | 0.944 | 1.000 | `gf-sandwich-loaf` | 1 | yes | no |
| `c22` | `says-missing-while-on-screen` | 0.533 | 0.986 | `classic-brioche` | 1 | yes | no |
| `c23` | `says-missing-while-on-screen` | 0.800 | 1.000 | `sourdough-2kg` | 1 | yes | **YES** |
| `c24` | `refuses-when-no-recipe-named` | 0.750 | 0.968 | `milk-kefir` | 1 | yes | no |
| `c25` | `refuses-when-no-recipe-named` | 0.800 | 1.000 | `lemon-drizzle-cake` | 5 | yes | **YES** |
| `r01` | `refuses-swap-instead-of-quoting-card` | 0.750 | 1.000 | `chicken-tikka-masala` | 1 | yes | no |
| `r02` | `refuses-swap-instead-of-quoting-card` | 0.750 | 1.000 | `napa-kimchi` | 1 | yes | no |
| `r03` | `refuses-swap-instead-of-quoting-card` | 0.750 | 1.000 | `gf-sandwich-loaf` | 1 | yes | no |

## Confidently, faithfully wrong

Cases scoring faithfulness >= 0.9 that still answered about a dish the request could not defensibly name, or declined with a donor card sitting in their own retrieved context: **0 of 25**.

## Why the average hides it

No case matched the pattern on this run.

