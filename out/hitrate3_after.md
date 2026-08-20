# hit-rate@3 - retriever=rerank

```
retriever        : rerank
strategy         : structure
embedding model  : all-MiniLM-L6-v2 (chromadb ONNX DefaultEmbeddingFunction)   (held fixed)
k                : 3
candidate window : 25
chunks in index  : 94
golden set       : eval/golden_set.jsonl  (12 questions)
golden sha256    : 24dda257f8b337d428710cd1f34a6def01a16f77cdc3a318b992351cc05d3cb7
timing samples   : 7 per query, 84 total
generated        : 2026-08-19T15:39:00+00:00
```

## Per-question record

| id | question | exact term? | expected chunk | hit@3 | rank of expected | in top-25 | ms |
|---|---|---|---|---|---|---|---|
| g01 | how much xanthan gum in the gluten free brioche | yes | `gf-brioche::structure::c001` | HIT | 1 of 94 | yes | 4249.8 |
| g02 | xanthan for the gf sandwich loaf | yes | `gf-sandwich-loaf::structure::c001` | HIT | 2 of 94 | yes | 4763.0 |
| g03 | psyllium husk amount | yes | `gf-sandwich-loaf::structure::c001` | HIT | 1 of 94 | yes | 4358.0 |
| g04 | how much saeujeot in the kimchi | yes | `napa-kimchi::structure::c001` | HIT | 1 of 94 | yes | 4656.6 |
| g05 | amchur amount chana masala | yes | `chana-masala::structure::c002` | HIT | 1 of 94 | yes | 4704.2 |
| g06 | what temp do i bake the 2kg sourdough at | yes | `sourdough-2kg::structure::c003` | HIT | 1 of 94 | yes | 4867.7 |
| g07 | how much butter in the chocolate brioche | no | `chocolate-brioche::structure::c001` | HIT | 1 of 94 | yes | 4682.9 |
| g08 | salt in the rye sourdough | no | `rye-sourdough::structure::c001` | HIT | 1 of 94 | yes | 4878.2 |
| g09 | hydration of the wholemeal loaf | no | `wholemeal-sourdough::structure::c001` | **MISS** | 5 of 94 | yes | 4825.5 |
| g10 | can i strain kefir with a metal sieve | no | `milk-kefir::structure::c002` | HIT | 1 of 94 | yes | 4891.3 |
| g11 | why do pickles turn soft | no | `dill-pickles::structure::c002` | HIT | 1 of 94 | yes | 4712.3 |
| g12 | is the kimchi ok if im allergic to prawns | no | `napa-kimchi::structure::c004` | HIT | 1 of 94 | yes | 4434.9 |

## Result

| metric | value |
|---|---|
| **hit-rate@3** | **11/12** |
| hit@1 | 10/12 |
| MRR | 0.892 |
| hit-rate@3, exact-term questions | 6/6 |
| hit-rate@3, paraphrase questions | 5/6 |
| **p50 latency per query** | **4722.4 ms** |
| p95 latency per query | 5568.3 ms |

## Misses

- **g09** `hydration of the wholemeal loaf` - retrieved but mis-ordered at rank 5
  - top-3 was: ['wholemeal-sourdough::structure::c000', 'gf-sandwich-loaf::structure::c002', 'wholemeal-sourdough::structure::c002']
