# Cost per query, `suite, squad-v1`

log `suite_traces.jsonl`, source `suite`, release squad-v1. Prices: $0.25/1M in, $1.5/1M out.

## By stage, then by step

11 requests.  mean cost/request **$0.002265**  median $0.002239  max $0.002886  mean model calls 5.73  p50 10.0 s  p95 27.9 s

| stage | mean cost $/request | share of $ | mean latency ms | share of summed span time |
|---|---|---|---|---|
| retrieval | 0.000000 | 0.0% | 111 | 0.7% |
| generation | 0.002265 | 100.0% | 14893 | 97.6% |
| tool | 0.000000 | 0.0% | 250 | 1.6% |

| step | stage | calls/request | in tok/request | out tok/request | $/request | share of $ |
|---|---|---|---|---|---|---|
| synthesise | generation | 1.00 | 838 | 561 | 0.001051 | 46.4% |
| allergen_worker | generation | 1.82 | 1249 | 172 | 0.000571 | 25.2% |
| substitution_worker | generation | 1.91 | 1022 | 193 | 0.000545 | 24.0% |
| plan | generation | 1.00 | 168 | 38 | 0.000099 | 4.4% |
| recipe_search | retrieval | 1.00 | 0 | 0 | 0.000000 | 0.0% |
| scale_recipe | tool | 1.00 | 0 | 0 | 0.000000 | 0.0% |
| get_allergen_profile | tool | 2.00 | 0 | 0 | 0.000000 | 0.0% |

Input tokens 36046 ($0.009012, 36% of $) vs output tokens 10605 ($0.015907, 64% of $). Output is 3.4x fewer tokens and costs 6x more per token.

### only `allergen-swap` (10 requests)

10 requests.  mean cost/request **$0.002400**  median $0.002249  max $0.002886  mean model calls 6.10  p50 9.4 s  p95 27.9 s

### only `scale-only` (1 requests)

1 requests.  mean cost/request **$0.000924**  median $0.000924  max $0.000924  mean model calls 2.00  p50 25.3 s  p95 25.3 s

## 10x

| at | requests/day | model calls/day | peak calls/min | $/day (list price) | p50 latency |
|---|---|---|---|---|---|
| 1x (busiest day, 2026-10-13) | 11 | 63 | 18 | 0.0249 | 10.0 s |
| 10x | 110 | 630 | 180 | 0.2492 | 10.0 s if nothing queues |
| limit | | **500/day** | **15/min** | none | |

Per-minute cap (named by a real 429 in this log: GenerateRequestsPerMinutePerProjectPerModel-FreeTier=15): the busiest minute made **18** model calls, already over the cap at 1x, and 3 call(s) drew a 429, costing 67 s of back-off between them. Daily cap (third-party free-tier table (tilnote.io), not confirmed on an official page; check AI Studio): reached at **7.9x** today's volume.

**At 10x the per-minute rate limit breaks first, and it already bit at 1x: the busiest minute made 18 model calls against the 15/min cap the API named in its own 429, so 10x is 180 calls/min (12x the cap); the 500/day cap follows at 7.9x, and cost at 10x is only $0.25/day.**
