# Cost per query, `production traffic, squad-v1`

log `traces.jsonl`, source `w11-traffic`. Prices: $0.25/1M in, $1.5/1M out.

## By stage, then by step

36 requests.  mean cost/request **$0.002016**  median $0.002194  max $0.002896  mean model calls 5.25  p50 14.4 s  p95 28.7 s

| stage | mean cost $/request | share of $ | mean latency ms | share of summed span time |
|---|---|---|---|---|
| retrieval | 0.000000 | 0.0% | 21 | 0.1% |
| generation | 0.002016 | 100.0% | 15142 | 99.6% |
| tool | 0.000000 | 0.0% | 42 | 0.3% |

| step | stage | calls/request | in tok/request | out tok/request | $/request | share of $ |
|---|---|---|---|---|---|---|
| synthesise | generation | 1.00 | 789 | 524 | 0.000982 | 48.7% |
| allergen_worker | generation | 1.56 | 1056 | 138 | 0.000470 | 23.3% |
| substitution_worker | generation | 1.69 | 915 | 160 | 0.000469 | 23.3% |
| plan | generation | 1.00 | 161 | 36 | 0.000094 | 4.7% |
| recipe_search | retrieval | 1.00 | 0 | 0 | 0.000000 | 0.0% |
| scale_recipe | tool | 1.00 | 0 | 0 | 0.000000 | 0.0% |
| get_allergen_profile | tool | 1.81 | 0 | 0 | 0.000000 | 0.0% |

Input tokens 105130 ($0.026283, 36% of $) vs output tokens 30870 ($0.046305, 64% of $). Output is 3.4x fewer tokens and costs 6x more per token.

### only `allergen-swap` (28 requests)

28 requests.  mean cost/request **$0.002339**  median $0.002222  max $0.002896  mean model calls 6.18  p50 16.5 s  p95 28.7 s

### only `scale-only` (8 requests)

8 requests.  mean cost/request **$0.000888**  median $0.000896  max $0.001056  mean model calls 2.00  p50 5.6 s  p95 27.4 s

## 10x

| at | requests/day | model calls/day | peak calls/min | $/day (list price) | p50 latency |
|---|---|---|---|---|---|
| 1x (busiest day, 2026-10-13) | 36 | 189 | 18 | 0.0726 | 14.4 s |
| 10x | 360 | 1890 | 180 | 0.7259 | 14.4 s if nothing queues |
| limit | | **500/day** | **15/min** | none | |

Per-minute cap (named by a real 429 in this log: GenerateRequestsPerMinutePerProjectPerModel-FreeTier=15): the busiest minute made **18** model calls, already over the cap at 1x, and 2 call(s) drew a 429, costing 43 s of back-off between them. Daily cap (third-party free-tier table (tilnote.io), not confirmed on an official page; check AI Studio): reached at **2.6x** today's volume.

**At 10x the per-minute rate limit breaks first, and it already bit at 1x: the busiest minute made 18 model calls against the 15/min cap the API named in its own 429, so 10x is 180 calls/min (12x the cap); the 500/day cap follows at 2.6x, and cost at 10x is only $0.73/day.**
