# Substitution eval

```
cases             : 25   (substitutions_v1.jsonl)
substitutions sha : f50218d27cf5bf2e00ab641c2c3242001e8a5fe415e7e2eb7ef3720343ba6849
model pinned      : True  (gemini-3.1-flash-lite)
assertions        : 6   (A1-A6)
judged criteria   : 1   (soundness, one binary field)
```


judge: `judge_v2`  prompt sha `c2477d2d2f6fee5d`

## Pass rate by Week-5 mode

| mode | n | assertions pass | judged SOUND | case PASS | pass % |
|---|---|---|---|---|---|
| `compares-only-retrieved-cards` | 3 | 3/3 | 1/3 | 1/3 | 33% |
| `drops-bakers-percentage` | 4 | 4/4 | 3/4 | 3/4 | 75% |
| `refuses-arithmetic-with-table-on-screen` | 4 | 4/4 | 3/4 | 3/4 | 75% |
| `refuses-swap-instead-of-quoting-card` | 10 | 10/10 | 6/10 | 6/10 | 60% |
| `refuses-when-no-recipe-named` | 2 | 2/2 | 2/2 | 2/2 | 100% |
| `says-missing-while-on-screen` | 2 | 2/2 | 2/2 | 2/2 | 100% |
| **all** | 25 | 25/25 | 17/25 | 17/25 | **68%** |

The overall row is last on purpose. It is the number most likely to sit still
while one mode regresses and another carries it.

## Assertion failures

None. All six assertions pass on all cases.

## Agreement, hand labels vs `judge_v2`

```
n compared                 : 25
agree                      : 21
AGREEMENT                  : 84.0%

both SOUND                 : 16
both UNSOUND               : 5
human SOUND, judge UNSOUND : 3
human UNSOUND, judge SOUND : 1
```

| case | disagreement | judge's reason |
|---|---|---|
| `c11` | human SOUND / judge UNSOUND | The assistant incorrectly claimed it could not ground the request to make the recipe glu |
| `c16` | human SOUND / judge UNSOUND | The assistant proposed a substitution by mixing ingredients from two different recipes,  |
| `c19` | human SOUND / judge UNSOUND | The assistant failed to answer the user's request to identify which of the brioche recip |
| `c25` | human UNSOUND / judge SOUND | The assistant correctly identified that the archive does not contain a gluten-free versi |

