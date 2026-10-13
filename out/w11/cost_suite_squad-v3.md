# Cost per query, `suite, squad-v3`

log `suite_traces.jsonl`, source `suite`, release squad-v3. Prices: $0.25/1M in, $1.5/1M out.

## By stage, then by step

11 requests.  mean cost/request **$0.001739**  median $0.001720  max $0.002179  mean model calls 3.91  p50 6.0 s  p95 34.3 s

| stage | mean cost $/request | share of $ | mean latency ms | share of summed span time |
|---|---|---|---|---|
| retrieval | 0.000000 | 0.0% | 13 | 0.1% |
| generation | 0.001739 | 100.0% | 9279 | 99.5% |
| tool | 0.000000 | 0.0% | 37 | 0.4% |

| step | stage | calls/request | in tok/request | out tok/request | $/request | share of $ |
|---|---|---|---|---|---|---|
| synthesise | generation | 1.00 | 923 | 579 | 0.001099 | 63.2% |
| substitution_worker | generation | 1.91 | 1013 | 192 | 0.000541 | 31.1% |
| plan | generation | 1.00 | 168 | 38 | 0.000099 | 5.7% |
| recipe_search | retrieval | 1.00 | 0 | 0 | 0.000000 | 0.0% |
| scale_recipe | tool | 1.00 | 0 | 0 | 0.000000 | 0.0% |
| allergen_step | tool | 0.91 | 0 | 0 | 0.000000 | 0.0% |
| get_allergen_profile | tool | 1.09 | 0 | 0 | 0.000000 | 0.0% |

Input tokens 23136 ($0.005784, 30% of $) vs output tokens 8898 ($0.013347, 70% of $). Output is 2.6x fewer tokens and costs 6x more per token.

### only `allergen-swap` (10 requests)

10 requests.  mean cost/request **$0.001818**  median $0.001755  max $0.002179  mean model calls 4.10  p50 6.0 s  p95 34.3 s

### only `scale-only` (1 requests)

1 requests.  mean cost/request **$0.000946**  median $0.000946  max $0.000946  mean model calls 2.00  p50 2.8 s  p95 2.8 s

## 10x

| at | requests/day | model calls/day | peak calls/min | $/day (list price) | p50 latency |
|---|---|---|---|---|---|
| 1x (busiest day, 2026-10-13) | 11 | 43 | 21 | 0.0191 | 6.0 s |
| 10x | 110 | 430 | 210 | 0.1913 | 6.0 s if nothing queues |
| limit | | **500/day** | **15/min** | none | |

Per-minute cap (named by a real 429 in this log: GenerateRequestsPerMinutePerProjectPerModel-FreeTier=15): the busiest minute made **21** model calls, already over the cap at 1x, and 1 call(s) drew a 429, costing 23 s of back-off between them. Daily cap (third-party free-tier table (tilnote.io), not confirmed on an official page; check AI Studio): reached at **11.6x** today's volume.

**At 10x the per-minute rate limit breaks first, and it already bit at 1x: the busiest minute made 21 model calls against the 15/min cap the API named in its own 429, so 10x is 210 calls/min (14x the cap); the 500/day cap follows at 11.6x, and cost at 10x is only $0.19/day.**
