**Sunk-cost bias, named first:** I built the squad last week, so I want to keep it. A verdict that keeps it therefore has to rest on numbers that would hold if someone else had built it.
**Verdict: KEEP the squad, over the single agent we already had.**
Pass rate 10/10 vs 5/10. Total tokens 40,074 vs 170,939, a re-send multiplier of **0.2x**: the team re-sends less, because each worker gets ingredient names instead of the whole growing conversation.
p50 latency 23.5 s vs 32.9 s, and p99 44.9 s vs 50.3 s. Cost per question $0.000664 vs $0.001854.
The single agent did not lose to "teamwork". It lost to its own 6 tools: all 5 failures are max_laps spent re-checking substitutes on both allergen servers.
The control (same single agent with only server one's 3 tools) still loses: 9/10 at 97,580 tokens, so the squad is 0.4x even against the lean version.
Nothing here ran in parallel. The win is narrow prompts plus fewer tools per call, the one advantage the brief says is plausible, not the multi-agent pattern itself.
Keep it with one fix first: on an allergen-worker failure it must fail closed. Today it degrades to a guessed allergen check that the grader scores PASS (`failure_case.md`).
Next race, not this one: the Week 7 fixed workflow did the same 10 cases in 12,444 tokens (a different day, no MCP), so the squad may yet lose to plain code.
