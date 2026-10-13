# At 10x today's query volume, what breaks first?

**The per-minute rate limit, and it already bit at 1x: the busiest minute of today's 36 requests made 18 model calls against the 15/min cap the API named in its own 429 (`GenerateRequestsPerMinutePerProjectPerModel-FreeTier=15`), so 10x is 180 calls/min, 12x the cap; cost at 10x is only $0.73/day.**

| | requests/day | model calls/day | busiest minute | $/day at list price | p50 / p95 latency |
|---|---|---|---|---|---|
| today (1x) | 36 | 189 | **18 calls** | $0.073 | 14.4 s / 28.7 s |
| 10x | 360 | 1,890 | **180 calls** | $0.73 | unchanged until requests queue |
| the cap | | 500/day (third-party table, unconfirmed) | **15/min (named by a real 429)** | none | |

Where each number comes from (`python eval/w11_cost.py`, over `out/w11/traces.jsonl`):

- **calls and the busiest minute** are counted from generation spans, placed on
  the clock by each trace's `ts` plus the span's `start_ms`. Each request makes
  5.25 model calls on average (6.18 for an allergen rewrite, 2 for a plain scale).
- **15/min is not a guess.** Two requests at 1x drew a 429 whose body named the
  quota, recorded on the span by the Week 11 change to `rag/llm.py`
  (`tr_97e37bd61449` at 00:58:15 and `tr_4fc7e6848e15` at 01:00:09). Each lost
  about 20 s to back-off, which is already visible in the p95.
- **500/day is the weaker number.** It comes from a third-party table, and no
  429 in this log has named a daily quota. On it, the daily cap falls at 2.6x
  today's volume. Even if it is wrong, the per-minute cap is hit first.
- **cost** is the paid-tier list price ($0.25 / $1.50 per 1M tokens). On the
  free tier the invoice is $0; at 10x on the paid tier it is $0.73/day. Cost is
  the last of the three to matter.
- **latency** per request does not change with volume until calls queue behind
  the cap; then every throttled call adds a 20 s retry wait (`GEN_RETRY_WAIT_SECONDS`).

## The 10x plan, in the order it would be needed

1. **Fewer model calls per request**: what `squad-v3` does (allergen step
   in code), measured in `cost_by_stage.md`. Cuts allergen requests from 6.2
   calls to about 4, so the same cap carries more requests.
2. **Paid tier or a second model quota** for the per-minute cap, once (1) is
   spent. The quota is per project per model.
3. **A queue with a per-minute budget** in front of the squad, so a burst
   waits its turn instead of each call sleeping 20 s and retrying blind.
4. **Not semantic caching.** It would serve a cached bad answer, like the dairy
   one this week found, instantly to everyone who asks something similar.
