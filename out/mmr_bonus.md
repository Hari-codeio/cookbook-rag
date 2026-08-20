# Bonus - MMR over the reranked candidate list

```
strategy         : structure
embedding model  : all-MiniLM-L6-v2 (chromadb ONNX DefaultEmbeddingFunction)
reranker         : Xenova/ms-marco-MiniLM-L-6-v2
candidate window : 25
k                : 3
questions        : 12 (the same golden set)
generated        : 2026-08-19T15:43:58+00:00
```

`lambda = 1.0` is pure relevance and reduces exactly to plain reranking, so that
row is the control and should match the after-run in the main experiment.

## The lambda sweep, all values reported

| lambda | hit-rate@3 | mean distinct recipes in top-3 | questions missed |
|---|---|---|---|
| 1.0 | 11/12 | 1.50 | g09 |
| 0.9 | 11/12 | 1.50 | g09 |
| 0.8 | 11/12 | 1.67 | g09 |
| 0.7 | 11/12 | 2.00 | g09 |
| 0.5 | 11/12 | 2.08 | g09 |
| 0.3 | 10/12 | 2.75 | g02, g09 |
| 0.0 | 10/12 | 3.00 | g02, g09 |

## Per-question, hit or miss at each lambda

| id | 1.0 | 0.9 | 0.8 | 0.7 | 0.5 | 0.3 | 0.0 |
|---|---|---|---|---|---|---|---|
| g01 | Y | Y | Y | Y | Y | Y | Y |
| g02 | Y | Y | Y | Y | Y | **n** | **n** |
| g03 | Y | Y | Y | Y | Y | Y | Y |
| g04 | Y | Y | Y | Y | Y | Y | Y |
| g05 | Y | Y | Y | Y | Y | Y | Y |
| g06 | Y | Y | Y | Y | Y | Y | Y |
| g07 | Y | Y | Y | Y | Y | Y | Y |
| g08 | Y | Y | Y | Y | Y | Y | Y |
| g09 | **n** | **n** | **n** | **n** | **n** | **n** | **n** |
| g10 | Y | Y | Y | Y | Y | Y | Y |
| g11 | Y | Y | Y | Y | Y | Y | Y |
| g12 | Y | Y | Y | Y | Y | Y | Y |

## The showcase query: `gluten free brioche`

This is the case the bonus describes. Watch the ingredients chunk, which is the
one carrying the xanthan gum weight.

**lambda = 1.0**  (distinct recipes in top-3: 1)

```text
  1.   +9.028  gf-brioche             title
  2.   +8.512  gf-brioche             allergens
  3.   +8.413  gf-brioche             method
  4.   +7.877  gf-brioche             ingredients
  5.   +3.879  classic-brioche        allergens
```

**lambda = 0.9**  (distinct recipes in top-3: 1)

```text
  1.   +9.028  gf-brioche             title
  2.   +8.413  gf-brioche             method
  3.   +8.512  gf-brioche             allergens
  4.   +7.877  gf-brioche             ingredients
  5.   +3.879  classic-brioche        allergens
```

**lambda = 0.8**  (distinct recipes in top-3: 1)

```text
  1.   +9.028  gf-brioche             title
  2.   +8.413  gf-brioche             method
  3.   +8.512  gf-brioche             allergens
  4.   +7.877  gf-brioche             ingredients
  5.   +3.879  classic-brioche        allergens
```

**lambda = 0.7**  (distinct recipes in top-3: 1)

```text
  1.   +9.028  gf-brioche             title
  2.   +8.413  gf-brioche             method
  3.   +7.877  gf-brioche             ingredients
  4.   +8.512  gf-brioche             allergens
  5.   +3.879  classic-brioche        allergens
```

**lambda = 0.5**  (distinct recipes in top-3: 1)

```text
  1.   +9.028  gf-brioche             title
  2.   +8.413  gf-brioche             method
  3.   +7.877  gf-brioche             ingredients
  4.   +8.512  gf-brioche             allergens
  5.   -3.045  congee                 allergens
```

**lambda = 0.3**  (distinct recipes in top-3: 3)

```text
  1.   +9.028  gf-brioche             title
  2.   -3.045  congee                 allergens
  3.   -0.960  gf-sandwich-loaf       method
  4.   -7.520  beef-bourguignon       allergens
  5.   +8.413  gf-brioche             method
```

**lambda = 0.0**  (distinct recipes in top-3: 3)

```text
  1.   +9.028  gf-brioche             title
  2.   -3.045  congee                 allergens
  3.   -7.520  beef-bourguignon       allergens
  4.   -8.943  lemon-drizzle-cake     allergens
  5.   -0.960  gf-sandwich-loaf       method
```

