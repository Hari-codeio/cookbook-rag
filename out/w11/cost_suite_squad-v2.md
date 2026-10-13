# Cost per query, `suite, squad-v2`

log `suite_traces.jsonl`, source `suite`, release squad-v2. Prices: $0.25/1M in, $1.5/1M out.

## By stage, then by step

11 requests.  mean cost/request **$0.002329**  median $0.002272  max $0.002899  mean model calls 5.73  p50 9.9 s  p95 48.9 s

| stage | mean cost $/request | share of $ | mean latency ms | share of summed span time |
|---|---|---|---|---|
| retrieval | 0.000000 | 0.0% | 50 | 0.3% |
| generation | 0.002329 | 100.0% | 15816 | 99.1% |
| tool | 0.000000 | 0.0% | 86 | 0.5% |

| step | stage | calls/request | in tok/request | out tok/request | $/request | share of $ |
|---|---|---|---|---|---|---|
| synthesise | generation | 1.00 | 927 | 589 | 0.001115 | 47.9% |
| allergen_worker | generation | 1.82 | 1249 | 172 | 0.000571 | 24.5% |
| substitution_worker | generation | 1.91 | 1022 | 193 | 0.000545 | 23.4% |
| plan | generation | 1.00 | 168 | 38 | 0.000099 | 4.2% |
| recipe_search | retrieval | 1.00 | 0 | 0 | 0.000000 | 0.0% |
| scale_recipe | tool | 1.00 | 0 | 0 | 0.000000 | 0.0% |
| get_allergen_profile | tool | 2.00 | 0 | 0 | 0.000000 | 0.0% |

Input tokens 37025 ($0.009256, 36% of $) vs output tokens 10906 ($0.016359, 64% of $). Output is 3.4x fewer tokens and costs 6x more per token.

### only `allergen-swap` (10 requests)

10 requests.  mean cost/request **$0.002467**  median $0.002341  max $0.002899  mean model calls 6.10  p50 9.9 s  p95 48.9 s

### only `scale-only` (1 requests)

1 requests.  mean cost/request **$0.000946**  median $0.000946  max $0.000946  mean model calls 2.00  p50 2.9 s  p95 2.9 s

## 10x

| at | requests/day | model calls/day | peak calls/min | $/day (list price) | p50 latency |
|---|---|---|---|---|---|
| 1x (busiest day, 2026-10-13) | 11 | 63 | 24 | 0.0256 | 9.9 s |
| 10x | 110 | 630 | 240 | 0.2562 | 9.9 s if nothing queues |
| limit | | **500/day** | **15/min** | none | |

Per-minute cap (named by a real 429 in this log: GenerateRequestsPerMinutePerProjectPerModel-FreeTier=15): the busiest minute made **24** model calls, already over the cap at 1x, and 4 call(s) drew a 429, costing 86 s of back-off between them. Daily cap (third-party free-tier table (tilnote.io), not confirmed on an official page; check AI Studio): reached at **7.9x** today's volume.

**At 10x the per-minute rate limit breaks first, and it already bit at 1x: the busiest minute made 24 model calls against the 15/min cap the API named in its own 429, so 10x is 240 calls/min (16x the cap); the 500/day cap follows at 7.9x, and cost at 10x is only $0.26/day.**
