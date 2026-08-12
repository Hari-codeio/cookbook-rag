# hit-in-top-5 — same 8 questions, two chunkers

```
embedding model : all-MiniLM-L6-v2 (chromadb ONNX DefaultEmbeddingFunction)   (identical for both strategies)
top-k           : 5
questions file  : eval/questions.json
questions sha256: 5dc74b03fbf46ccbf1fbdbb6aff5a338d9e9e7053fef0b6dcaf71d1e0f1d8d27
questions locked: 2026-08-12T13:01:22+00:00
chunk counts    : baseline=30, structure=43
generated       : 2026-08-12T13:18:07+00:00
```

## Per-question record

| # | question | expected recipe / section | table row? | baseline | structure |
|---|---|---|---|---|---|
| q1 | How much fine sea salt is in the beef bourguignon? | beef-bourguignon / ingredients table | yes | HIT (rank 2) | HIT (rank 1) |
| q2 | What is the hydration percentage of the classic rosemary focaccia? | classic-focaccia / ingredients table (water row, baker's %) | yes | HIT (rank 1) | HIT (rank 1) |
| q3 | How much amchur goes into the chana masala? | chana-masala / ingredients table | yes | HIT (rank 4) | HIT (rank 1) |
| q4 | How much double cream is in the chicken tikka masala? | chicken-tikka-masala / ingredients table | yes | HIT (rank 1) | HIT (rank 1) |
| q5 | At what temperature and for how long is the lemon drizzle loaf baked? | lemon-drizzle-cake / method | no | HIT (rank 1) | HIT (rank 1) |
| q6 | How long should the pad thai rice noodles soak before they go in the wok? | pad-thai / method | no | HIT (rank 1) | HIT (rank 1) |
| q7 | What allergens does the prawn pad thai contain? | pad-thai / allergens | no | HIT (rank 1) | HIT (rank 1) |
| q8 | What is the rice to water ratio for the ginger and spring onion congee? | congee / ingredients table (water row note) | yes | HIT (rank 1) | HIT (rank 1) |

## Result

| chunking strategy | **hit-in-top-5** | hit@3 | hit@1 | mean reciprocal rank |
|---|---|---|---|---|
| A — baseline fixed-window (30 chunks) | **8/8** | 7/8 | 6/8 | 0.844 |
| B — structure-aware (43 chunks) | **8/8** | 8/8 | 8/8 | 1.000 |

> **Saturation warning.** Both strategies hit on every question, so hit-in-top-5 alone cannot separate them here: with a small corpus of short cards, top-5 covers most of a card whichever way it was cut. Read hit@1 and MRR for the difference, and see the measured row-stranding figure from `eval/test_chunk_invariants.py` for the mechanism.
