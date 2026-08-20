# hit-rate@3 - retriever=dense

```
retriever        : dense
strategy         : structure
embedding model  : all-MiniLM-L6-v2 (chromadb ONNX DefaultEmbeddingFunction)   (held fixed)
k                : 3
candidate window : 25
chunks in index  : 70
golden set       : eval/golden_set.jsonl  (12 questions)
golden sha256    : d220d61de56b44aa0e877e28baa31ae12d94bc7390ab0db1f306f7af68c2bda8
generated        : 2026-08-19T14:54:53+00:00
```

## Per-question record

| id | question | exact term? | expected chunk | hit@3 | rank of expected | in top-25 | ms |
|---|---|---|---|---|---|---|---|
| g01 | how much saeujeot in the kimchi | yes | `napa-kimchi::structure::c001` | HIT | 3 of 70 | yes | 226.0 |
| g02 | amchur amount chana masala | yes | `chana-masala::structure::c002` | HIT | 1 of 70 | yes | 221.8 |
| g03 | what temp do i bake the 2kg sourdough at | yes | `sourdough-2kg::structure::c003` | HIT | 1 of 70 | yes | 1078.7 |
| g04 | rice to water ratio congee | yes | `congee::structure::c001` | HIT | 3 of 70 | yes | 1620.6 |
| g05 | how many g of juniper berries in the red kraut | yes | `red-sauerkraut::structure::c001` | HIT | 1 of 70 | yes | 1750.2 |
| g06 | koji weight for white miso | yes | `white-miso::structure::c001` | HIT | 2 of 70 | yes | 1573.0 |
| g07 | is the kimchi ok if im allergic to prawns | no | `napa-kimchi::structure::c004` | HIT | 1 of 70 | yes | 1543.6 |
| g08 | can i strain kefir with a metal sieve | no | `milk-kefir::structure::c002` | HIT | 1 of 70 | yes | 1260.4 |
| g09 | why do pickles turn soft | no | `dill-pickles::structure::c002` | HIT | 1 of 70 | yes | 1161.8 |
| g10 | how long until the sauerkraut is done | no | `red-sauerkraut::structure::c002` | HIT | 1 of 70 | yes | 1328.7 |
| g11 | does white miso contain gluten | no | `white-miso::structure::c004` | HIT | 1 of 70 | yes | 1375.9 |
| g12 | noodle soaking time pad thai | no | `pad-thai::structure::c003` | HIT | 1 of 70 | yes | 1211.8 |

## Result

| metric | value |
|---|---|
| **hit-rate@3** | **12/12** |
| hit@1 | 9/12 |
| MRR | 0.847 |
| hit-rate@3, exact-term questions | 6/6 |
| hit-rate@3, paraphrase questions | 6/6 |
| **p50 latency per query** | **1294.6 ms** |
| p95 latency per query | 1620.6 ms |

## Misses

None.
