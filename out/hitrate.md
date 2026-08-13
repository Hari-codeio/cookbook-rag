# hit-in-top-5 — same 8 questions, two chunkers

```
embedding model : all-MiniLM-L6-v2 (chromadb ONNX DefaultEmbeddingFunction)   (identical for both strategies)
top-k           : 5
questions file  : eval/questions.json
questions sha256: 07436a98184885aa00ba0fe92a1046322e5e4ca05753c3546ae5676eb64c80e5
questions locked: 2026-08-13T01:56:59+00:00
chunk counts    : baseline=52, structure=70
generated       : 2026-08-13T02:46:10+00:00
```

## Per-question record

| # | question | expected recipe / section | table row? | baseline | structure |
|---|---|---|---|---|---|
| q1 | How much fine sea salt goes into the 2kg country sourdough? | sourdough-2kg / ingredients table (fine sea salt row) | yes | MISS | HIT (rank 1) |
| q2 | What hydration percentage does the 2kg country sourdough run at? | sourdough-2kg / ingredients table (water row, baker's %) | yes | HIT (rank 1) | HIT (rank 1) |
| q3 | How much gochugaru goes into the napa cabbage kimchi? | napa-kimchi / ingredients table (gochugaru row) | yes | HIT (rank 3) | HIT (rank 3) |
| q4 | How much coarse sea salt do the half-sour dill pickles need? | dill-pickles / ingredients table (coarse sea salt row) | yes | HIT (rank 1) | HIT (rank 2) |
| q5 | How many grams of live kefir grains go into one litre of milk? | milk-kefir / ingredients table (kefir grains row) | yes | HIT (rank 1) | HIT (rank 1) |
| q6 | How long does the red cabbage sauerkraut ferment, and at what temperature? | red-sauerkraut / method | no | MISS | HIT (rank 1) |
| q7 | Is the napa cabbage kimchi safe for someone with a shellfish allergy? | napa-kimchi / allergens | no | HIT (rank 2) | HIT (rank 1) |
| q8 | At what temperature and for how long is the white rice miso fermented? | white-miso / method | no | HIT (rank 2) | HIT (rank 1) |

## Result

| chunking strategy | **hit-in-top-5** | hit@3 | hit@1 | mean reciprocal rank |
|---|---|---|---|---|
| A — baseline fixed-window (52 chunks) | **6/8** | 6/8 | 3/8 | 0.542 |
| B — structure-aware (70 chunks) | **8/8** | 8/8 | 6/8 | 0.854 |
