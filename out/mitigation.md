# Week 8 - the one mitigation, and what it cost

before : `agent_v1`
after  : `workflow`
target : `skipped-allergen-check`

## The targeted mode

```
skipped-allergen-check
  before : 9 / 10
  after  : 0 / 10
```

## Regression check, every mode

| mode | before | after | verdict |
|---|---|---|---|
| `skipped-allergen-check` | 9 | 0 | improved |
| `unverified-substitute` | 0 | 0 | unchanged |
| `hallucinated-argument` | 0 | 0 | unchanged |
| `wrong-tool-order` | 9 | 0 | improved |
| `redundant-call` | 0 | 0 | unchanged |
| `unrequested-tool-use` | 0 | 0 | unchanged |
| `budget-terminated` | 0 | 0 | unchanged |
| `unparseable-final` | 0 | 0 | unchanged |

No mode got worse and no new mode appeared. Modes checked: `skipped-allergen-check`, `unverified-substitute`, `hallucinated-argument`, `wrong-tool-order`, `redundant-call`, `unrequested-tool-use`, `budget-terminated`, `unparseable-final`.

## Outcome and trajectory

| | outcome pass | trajectory pass | gap |
|---|---|---|---|
| `agent_v1` | 10/10 | 1/10 | 90 points |
| `workflow` | 10/10 | 10/10 | 0 points |

## The price

| measure | before | after | change |
|---|---|---|---|
| cost / request, p50 | $0.000532 | $0.000274 | -48% |
| cost / request, max | $0.000615 | $0.000310 | -50% |
| latency, p50 | 12957 ms | 9335 ms | -28% |
| latency, max | 18766 ms | 14322 ms | -24% |
| tokens, p50 | 3790 | 1265 | -67% |
| tokens, total | 38770 | 12444 | -68% |

| measure | before | after | change |
|---|---|---|---|
| step efficiency | 0.60 | 1.00 | +67% |

## The price that is not cost: flexibility

Every cost column above moved the right way, so the price is not latency,
tokens or money. It is the ability to take a different route. Distinct tool
sequences actually observed over the same 10 inputs:

| system | distinct routes taken | routes |
|---|---|---|
| `agent_v1` | 1 | `search_recipes -> scale_recipe` |
| `workflow` | 2 | `search_recipes -> scale_recipe`<br>`search_recipes -> scale_recipe -> get_allergen_profile` |

