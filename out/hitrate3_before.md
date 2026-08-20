# hit-rate@3 - retriever=dense

```
retriever        : dense
strategy         : structure
embedding model  : all-MiniLM-L6-v2 (chromadb ONNX DefaultEmbeddingFunction)   (held fixed)
k                : 3
candidate window : 25
chunks in index  : 94
golden set       : eval/golden_set.jsonl  (12 questions)
golden sha256    : 24dda257f8b337d428710cd1f34a6def01a16f77cdc3a318b992351cc05d3cb7
timing samples   : 7 per query, 84 total
generated        : 2026-08-19T15:02:31+00:00
```

## Per-question record

| id | question | exact term? | expected chunk | hit@3 | rank of expected | in top-25 | ms |
|---|---|---|---|---|---|---|---|
| g01 | how much xanthan gum in the gluten free brioche | yes | `gf-brioche::structure::c001` | HIT | 2 of 94 | yes | 1302.1 |
| g02 | xanthan for the gf sandwich loaf | yes | `gf-sandwich-loaf::structure::c001` | HIT | 2 of 94 | yes | 1474.3 |
| g03 | psyllium husk amount | yes | `gf-sandwich-loaf::structure::c001` | **MISS** | 14 of 94 | yes | 1473.0 |
| g04 | how much saeujeot in the kimchi | yes | `napa-kimchi::structure::c001` | HIT | 3 of 94 | yes | 1390.8 |
| g05 | amchur amount chana masala | yes | `chana-masala::structure::c002` | HIT | 1 of 94 | yes | 1478.5 |
| g06 | what temp do i bake the 2kg sourdough at | yes | `sourdough-2kg::structure::c003` | HIT | 1 of 94 | yes | 1417.8 |
| g07 | how much butter in the chocolate brioche | no | `chocolate-brioche::structure::c001` | HIT | 3 of 94 | yes | 1575.8 |
| g08 | salt in the rye sourdough | no | `rye-sourdough::structure::c001` | HIT | 1 of 94 | yes | 1360.6 |
| g09 | hydration of the wholemeal loaf | no | `wholemeal-sourdough::structure::c001` | **MISS** | 13 of 94 | yes | 1408.4 |
| g10 | can i strain kefir with a metal sieve | no | `milk-kefir::structure::c002` | HIT | 1 of 94 | yes | 1374.2 |
| g11 | why do pickles turn soft | no | `dill-pickles::structure::c002` | HIT | 1 of 94 | yes | 1260.1 |
| g12 | is the kimchi ok if im allergic to prawns | no | `napa-kimchi::structure::c004` | HIT | 1 of 94 | yes | 1270.0 |

## Result

| metric | value |
|---|---|
| **hit-rate@3** | **10/12** |
| hit@1 | 6/12 |
| MRR | 0.651 |
| hit-rate@3, exact-term questions | 5/6 |
| hit-rate@3, paraphrase questions | 5/6 |
| **p50 latency per query** | **1400.6 ms** |
| p95 latency per query | 1723.1 ms |

## Misses

- **g03** `psyllium husk amount` - retrieved but mis-ordered at rank 14
  - top-3 was: ['red-sauerkraut::structure::c001', 'gf-sandwich-loaf::structure::c002', 'red-sauerkraut::structure::c002']
- **g09** `hydration of the wholemeal loaf` - retrieved but mis-ordered at rank 13
  - top-3 was: ['gf-sandwich-loaf::structure::c002', 'wholemeal-sourdough::structure::c000', 'wholemeal-sourdough::structure::c002']
