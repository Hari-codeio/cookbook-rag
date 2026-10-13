# Cost per query, by stage

Every number below is summed from spans in the trace log by
`eval/w11_cost.py`, never estimated. Prices are gemini-3.1-flash-lite's
paid-tier list price, **$0.25 / 1M input tokens and $1.50 / 1M output tokens**
(ai.google.dev/pricing, checked 2026-10-13), stamped into every trace. The free
tier invoices $0, so these are what the same traffic costs once it outgrows it.

## 1. That request: the one the drill found

`tr_93031da07c32`, *"Tikka masala with no dairy, my son has a milk allergy"*,
squad-v1:

| stage | spans | model calls | latency | input tok | output tok | cost | share |
|---|---|---|---|---|---|---|---|
| **retrieval** (recipe_search over MCP) | 1 | 0 | 300 ms | 0 | 0 | **$0.000000** | 0% |
| **generation** (6 model calls) | 6 | 6 | 25,497 ms | 3,731 | 1,302 | **$0.002886** | 100% |
| **tools** (scale_recipe, 2x get_allergen_profile) | 3 | 0 | 86 ms | 0 | 0 | **$0.000000** | 0% |
| **request** | 10 | 6 | 25,920 ms wall | 3,731 | 1,302 | **$0.002886** | 100% |

Inside generation, by step:

| step | calls | latency | input tok | output tok | cost | share |
|---|---|---|---|---|---|---|
| plan | 1 | 4,456 ms | 165 | 36 | $0.000095 | 3% |
| allergen_worker | 2 | 6,807 ms | 1,463 | 236 | $0.000720 | 25% |
| substitution_worker | 2 | 8,551 ms | 1,106 | 306 | $0.000735 | 25% |
| synthesise | 1 | 5,683 ms | 997 | 724 | $0.001335 | **46%** |

That trace is the planted clone of a real request, so its **tokens and cost
are real**, and its latencies were jittered by +-10% by the planter so it would
not stand out. The untouched original, `tr_919c9b03134d` (same request from
u_0121), has identical tokens and cost and 23,853 ms wall time. Both tables are
in `out/w11/cost_found_request.md`.

## 2. Across all 36 production requests (squad-v1)

**$0.002016 per request** on average; $0.002339 for an allergen rewrite (6.18
model calls), $0.000888 for a plain scale (2 calls). p50 14.4 s, p95 28.7 s.

| stage | $/request | share of $ | latency/request | share of span time |
|---|---|---|---|---|
| retrieval | $0.000000 | 0.0% | 21 ms | 0.1% |
| generation | $0.002016 | **100.0%** | 15,142 ms | 99.6% |
| tools | $0.000000 | 0.0% | 42 ms | 0.3% |

| step | stage | calls/request | $/request | share of $ |
|---|---|---|---|---|
| synthesise | generation | 1.00 | $0.000982 | **48.7%** |
| allergen_worker | generation | 1.56 | $0.000470 | 23.3% |
| substitution_worker | generation | 1.69 | $0.000469 | 23.3% |
| plan | generation | 1.00 | $0.000094 | 4.7% |
| recipe_search | retrieval | 1.00 | $0 | 0% |
| scale_recipe, get_allergen_profile | tool | 2.81 | $0 | 0% |

**Output tokens are 64% of the bill** (30,870 output vs 105,130 input tokens)
because they cost 6x more. Synthesis is the dearest step because it writes the
whole recipe back out.

**What the split says before anything is changed:** retrieval and tools are
free and fast (local MCP over 21 cards), so optimising them cannot save a cent.
Every dollar and 99.6% of the time is model calls. Full report:
`out/w11/cost_report_traffic.md`.

## 3. The one improvement, and where the saving came from

**Chosen from the table above, not from taste.** The binding limit at 10x is
model calls per minute (`tenx.md`), so the change that matters most is fewer
calls per request, not fewer tokens. Of the four model steps, one needs no
judgement: the allergen worker's whole job is a single `get_allergen_profile`
call and a copy of the answer. In 27 of 28 production requests its report WAS
the tool's answer (the 28th added a shrimp-paste caveat from its own knowledge,
which its prompt forbids). So `squad-v3` routes that step to code: model
routing in its cheapest form.

**Measured on the same 11 suite requests, live, squad-v2 (GREEN) vs squad-v3**
(`out/w11/cost_suite_squad-v2.md`, `out/w11/cost_suite_squad-v3.md`):

| per request | squad-v2 | squad-v3 | change |
|---|---|---|---|
| **cost** | **$0.002329** | **$0.001739** | **-$0.000590 (-25.3%)** |
| model calls | 5.73 | 3.91 | -1.82 |
| tokens | 4,357 | 2,912 | -1,445 (-33%) |
| p50 latency | 9.9 s | 6.0 s | see note |
| suite | 11/11 | **11/11** | no regression |

Where the saving came from, step by step:

| step | stage | squad-v2 $/request | squad-v3 $/request | change |
|---|---|---|---|---|
| allergen_worker -> allergen_step | generation -> **tool** | $0.000571 (1.82 calls, 2,413 ms) | **$0** (0 calls, 11 ms) | **-$0.000571** |
| synthesise | generation | $0.001115 | $0.001099 | -$0.000016 |
| substitution_worker | generation | $0.000545 | $0.000541 | -$0.000004 |
| plan | generation | $0.000099 | $0.000099 | 0 |

**97% of the saving ($0.000571 of $0.000590) is the stage that changed**, and
the 1.82 calls removed are exactly the allergen worker's 1.82. The other 3% is
run-to-run noise in steps whose prompts did not change.

**Latency, honestly:** p50 fell 9.9 s -> 6.0 s, but per-step latency on the
free tier moves between runs with no change at all (`plan` went 1.3 s -> 3.4 s
with an identical prompt). Only the allergen step's 2.4 s -> 11 ms is
attributable.

**On the production mix** (36 requests, 5.25 calls each), removing the
allergen worker's 1.56 calls/request would leave about 3.7 calls/request: the
busiest minute would carry about 13 calls instead of 18 (under the 15/min cap
at 1x), and the 500/day cap would move from 2.6x to about 3.8x. That is a
projection from the measured attribution, not a production measurement.

**Not shipped yet, on purpose.** squad-v3 is validated 11/11 but the default
stays squad-v2 until squad-v2's canary finishes. Two changes in one canary
cannot be told apart. squad-v3 then gets its own canary against squad-v2
(`release_notes.md`).

## 4. What the fix itself cost (squad-v1 -> squad-v2)

Same 11 requests: $0.002265 -> $0.002329 per request (**+2.8%**), all of it in
`synthesise` (+116 tokens/request: a longer prompt and a method that is now
rewritten instead of pasted). Correctness first: a cheaper answer that tells a
milk-allergic child's parent to use ghee is not a saving.

## 5. Levers deliberately not pulled

| lever | why not |
|---|---|
| prompt caching | It pays on long, repeated prefixes; every one of the 189 production model calls sent between 156 and 1,001 input tokens, and the pricing page lists context caching as unavailable on the free tier. |
| semantic caching | It would have served this week's bad dairy answer instantly to every near-identical request: caching the failure, plus a staleness risk on an allergy answer. |
| a cheaper model | Already on the cheapest flash model; the cheaper "model" for the allergen step was code. |
| trimming retrieval or tools | They cost $0 and under 1% of the time. Optimising them first is the mistake section 2 exists to prevent. |
| fine-tuning | The course calls it the last resort, and a prompt change fixed the failure. |

