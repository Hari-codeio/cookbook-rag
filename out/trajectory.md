# Week 8 - trajectory eval

Scored from `out/race_cache.json`. No API calls, so these numbers
cannot drift from the run that produced them.

## The four trajectory numbers

| system | tool-choice accuracy | argument validity | step efficiency | cost p50 | cost max |
|---|---|---|---|---|---|
| `agent_v1` | 10% | 100% | 0.60 | $0.000532 | $0.000615 |
| `agent_v2` | 100% | 100% | 1.02 | $0.001028 | $0.001311 |
| `workflow` | 100% | n/a | 1.00 | $0.000274 | $0.000310 |

Mean cost is shown only to make the point that it hides the tail:

| system | cost mean | cost p50 | cost max | max / p50 |
|---|---|---|---|---|
| `agent_v1` | $0.000543 | $0.000532 | $0.000615 | 1.16x |
| `agent_v2` | $0.001034 | $0.001028 | $0.001311 | 1.28x |
| `workflow` | $0.000271 | $0.000274 | $0.000310 | 1.13x |

## The gap

| system | outcome pass | trajectory pass | gap |
|---|---|---|---|
| `agent_v1` | 10/10 (100%) | 1/10 (10%) | **90 points** |
| `agent_v2` | 10/10 (100%) | 10/10 (100%) | **0 points** |
| `workflow` | 10/10 (100%) | 10/10 (100%) | **0 points** |

## Failure modes, per system

| mode | `agent_v1` | `agent_v2` | `workflow` |
|---|---|---|---|
| `skipped-allergen-check` | 9 | 0 | 0 |
| `unverified-substitute` | 0 | 0 | 0 |
| `hallucinated-argument` | 0 | 0 | 0 |
| `wrong-tool-order` | 9 | 0 | 0 |
| `redundant-call` | 0 | 0 | 0 |
| `unrequested-tool-use` | 0 | 0 | 0 |
| `budget-terminated` | 0 | 0 | 0 |
| `unparseable-final` | 0 | 0 | 0 |

## Right answer, wrong path

`agent_v1`: **9 of 10** passed the outcome eval while failing the trajectory eval.

- `c01` modes=['skipped-allergen-check', 'wrong-tool-order'] path=['search_recipes', 'scale_recipe']
- `c02` modes=['skipped-allergen-check', 'wrong-tool-order'] path=['search_recipes', 'scale_recipe']
- `c03` modes=['skipped-allergen-check', 'wrong-tool-order'] path=['search_recipes', 'scale_recipe']
- `c04` modes=['skipped-allergen-check', 'wrong-tool-order'] path=['search_recipes', 'scale_recipe']
- `s01` modes=['skipped-allergen-check', 'wrong-tool-order'] path=['search_recipes', 'scale_recipe']
- `s02` modes=['skipped-allergen-check', 'wrong-tool-order'] path=['search_recipes', 'scale_recipe']
- `s03` modes=['skipped-allergen-check', 'wrong-tool-order'] path=['search_recipes', 'scale_recipe']
- `s04` modes=['skipped-allergen-check', 'wrong-tool-order'] path=['search_recipes', 'scale_recipe']
- `s05` modes=['skipped-allergen-check', 'wrong-tool-order'] path=['search_recipes', 'scale_recipe']

`agent_v2`: none.

`workflow`: none.

## Per case

| system | case | outcome | trajectory | steps | eff | modes |
|---|---|---|---|---|---|---|
| `agent_v1` | `c01` | PASS | fail | 2/4 | 0.50 | skipped-allergen-check, wrong-tool-order |
| `agent_v1` | `c02` | PASS | fail | 2/4 | 0.50 | skipped-allergen-check, wrong-tool-order |
| `agent_v1` | `c03` | PASS | fail | 2/4 | 0.50 | skipped-allergen-check, wrong-tool-order |
| `agent_v1` | `c04` | PASS | fail | 2/4 | 0.50 | skipped-allergen-check, wrong-tool-order |
| `agent_v1` | `s01` | PASS | fail | 2/3 | 0.67 | skipped-allergen-check, wrong-tool-order |
| `agent_v1` | `s02` | PASS | fail | 2/3 | 0.67 | skipped-allergen-check, wrong-tool-order |
| `agent_v1` | `s03` | PASS | fail | 2/4 | 0.50 | skipped-allergen-check, wrong-tool-order |
| `agent_v1` | `s04` | PASS | fail | 2/4 | 0.50 | skipped-allergen-check, wrong-tool-order |
| `agent_v1` | `s05` | PASS | fail | 2/3 | 0.67 | skipped-allergen-check, wrong-tool-order |
| `agent_v1` | `s06` | PASS | PASS | 2/2 | 1.00 | - |
| `agent_v2` | `c01` | PASS | PASS | 4/4 | 1.00 | - |
| `agent_v2` | `c02` | PASS | PASS | 4/4 | 1.00 | - |
| `agent_v2` | `c03` | PASS | PASS | 4/4 | 1.00 | - |
| `agent_v2` | `c04` | PASS | PASS | 4/4 | 1.00 | - |
| `agent_v2` | `s01` | PASS | PASS | 3/3 | 1.00 | - |
| `agent_v2` | `s02` | PASS | PASS | 4/4 | 1.00 | - |
| `agent_v2` | `s03` | PASS | PASS | 4/4 | 1.00 | - |
| `agent_v2` | `s04` | PASS | PASS | 5/4 | 1.25 | - |
| `agent_v2` | `s05` | PASS | PASS | 4/4 | 1.00 | - |
| `agent_v2` | `s06` | PASS | PASS | 2/2 | 1.00 | - |
| `workflow` | `c01` | PASS | PASS | 4/4 | 1.00 | - |
| `workflow` | `c02` | PASS | PASS | 4/4 | 1.00 | - |
| `workflow` | `c03` | PASS | PASS | 4/4 | 1.00 | - |
| `workflow` | `c04` | PASS | PASS | 4/4 | 1.00 | - |
| `workflow` | `s01` | PASS | PASS | 4/4 | 1.00 | - |
| `workflow` | `s02` | PASS | PASS | 4/4 | 1.00 | - |
| `workflow` | `s03` | PASS | PASS | 4/4 | 1.00 | - |
| `workflow` | `s04` | PASS | PASS | 4/4 | 1.00 | - |
| `workflow` | `s05` | PASS | PASS | 4/4 | 1.00 | - |
| `workflow` | `s06` | PASS | PASS | 2/2 | 1.00 | - |

