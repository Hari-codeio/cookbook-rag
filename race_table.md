# Race: kitchen squad vs single agent

Same 10 cases (s01, s02, s03, s04, s05, s06, c01, c02, c03, c04) from `eval/race_cases.jsonl`,
graded by `rag/contract.check`, same pinned model, same MCP servers, arms interleaved per case.

| arm | pass rate | p50 latency | p99 latency | total tokens | cost / question |
|---|---|---|---|---|---|
| single agent (6 MCP tools) | 5/10 | 32.9 s | 50.3 s | 170,939 | $0.001854 |
| squad (orchestrator + 2 workers) | 10/10 | 23.5 s | 44.9 s | 40,074 | $0.000664 |
| *control:* single agent, 3 tools (server one only) | 9/10 | 21.1 s | 51.7 s | 97,580 | $0.001161 |

Control multiplier, squad / 3-tool single: 40,074 / 97,580 = 0.4x. The control ran after the race, not interleaved with it.

Mean model calls per question: single 6.6, squad 5.6.
p99 over 10 runs is nearest-rank, i.e. the slowest run.

**Context re-send multiplier: 40,074 / 170,939 = 0.2x.**
Largest squad token share: `orchestrator -> allergen_worker`, 35% of all squad tokens.

## Per case

| case | cascade | single | squad | single tokens | squad tokens | single s | squad s |
|---|---|---|---|---|---|---|---|
| `s01` | no | PASS | PASS | 9,337 | 4,215 | 17.0 | 21.8 |
| `s02` | no | PASS | PASS | 14,319 | 4,279 | 48.8 | 22.3 |
| `s03` | no | fail | PASS | 19,876 | 4,481 | 38.7 | 44.9 |
| `s04` | no | fail | PASS | 20,907 | 4,492 | 31.5 | 23.5 |
| `s05` | no | PASS | PASS | 16,055 | 3,990 | 50.3 | 27.0 |
| `s06` | no | PASS | PASS | 6,641 | 1,286 | 13.2 | 9.0 |
| `c01` | yes | fail | PASS | 22,778 | 4,236 | 32.7 | 25.2 |
| `c02` | yes | fail | PASS | 22,541 | 4,844 | 33.0 | 24.2 |
| `c03` | yes | fail | PASS | 23,668 | 4,112 | 29.9 | 21.3 |
| `c04` | yes | PASS | PASS | 14,817 | 4,139 | 45.6 | 23.5 |

## Failures, with the grader's reason

- single `s03`: no answer produced (terminated_by max_laps)
- single `s04`: no answer produced (terminated_by max_laps)
- single `c01`: no answer produced (terminated_by max_laps)
- single `c02`: no answer produced (terminated_by max_laps)
- single `c03`: no answer produced (terminated_by max_laps)
- single_3tools `s03`: no answer produced (terminated_by max_laps)
