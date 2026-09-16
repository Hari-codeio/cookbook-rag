# Week 7 race: agent vs fixed workflow

Same 10 requests, same tools, same pinned model, same output contract.

| system | pass rate | p50 latency | total tokens | cost / request |
|---|---|---|---|---|
| `agent_v2` | 10/10 (100%) | 8013 ms | 85,244 | $0.001034 |
| `workflow` | 10/10 (100%) | 3006 ms | 12,444 | $0.000271 |
| `agent_v1` | 10/10 (100%) | 4580 ms | 38,770 | $0.000543 |

Split by case type, which is where the average hides the answer:

| system | 6 straightforward | 4 cascade | mean laps |
|---|---|---|---|
| `agent_v2` | 6/6 | 4/4 | 4.8 |
| `workflow` | 6/6 | 4/4 | 2.0 |
| `agent_v1` | 6/6 | 4/4 | 3.0 |

## Per case

| system | case | cascade | result | laps | tokens | cost | latency |
|---|---|---|---|---|---|---|---|
| `agent_v2` | `s01` | no | PASS | 4 | 6473 | $0.000811 | 7907 ms |
| `agent_v2` | `s02` | no | PASS | 5 | 8258 | $0.001020 | 12214 ms |
| `agent_v2` | `s03` | no | PASS | 5 | 8391 | $0.001015 | 11873 ms |
| `agent_v2` | `s04` | no | PASS | 6 | 11241 | $0.001311 | 30420 ms |
| `agent_v2` | `s05` | no | PASS | 5 | 7383 | $0.000917 | 8120 ms |
| `agent_v2` | `s06` | no | PASS | 3 | 4586 | $0.000605 | 4224 ms |
| `agent_v2` | `c01` | yes | PASS | 5 | 9764 | $0.001142 | 46692 ms |
| `agent_v2` | `c02` | yes | PASS | 5 | 10108 | $0.001256 | 5683 ms |
| `agent_v2` | `c03` | yes | PASS | 5 | 10498 | $0.001222 | 5551 ms |
| `agent_v2` | `c04` | yes | PASS | 5 | 8542 | $0.001036 | 5165 ms |
| `workflow` | `s01` | no | PASS | 2 | 1198 | $0.000257 | 43318 ms |
| `workflow` | `s02` | no | PASS | 2 | 1287 | $0.000281 | 3083 ms |
| `workflow` | `s03` | no | PASS | 2 | 1278 | $0.000272 | 2779 ms |
| `workflow` | `s04` | no | PASS | 2 | 1294 | $0.000285 | 3774 ms |
| `workflow` | `s05` | no | PASS | 2 | 1134 | $0.000243 | 2414 ms |
| `workflow` | `s06` | no | PASS | 2 | 1220 | $0.000264 | 2650 ms |
| `workflow` | `c01` | yes | PASS | 2 | 1259 | $0.000276 | 2928 ms |
| `workflow` | `c02` | yes | PASS | 2 | 1391 | $0.000310 | 2808 ms |
| `workflow` | `c03` | yes | PASS | 2 | 1112 | $0.000240 | 43920 ms |
| `workflow` | `c04` | yes | PASS | 2 | 1271 | $0.000287 | 3504 ms |
| `agent_v1` | `s01` | no | PASS | 3 | 3626 | $0.000484 | 3696 ms |
| `agent_v1` | `s02` | no | PASS | 3 | 3545 | $0.000526 | 4298 ms |
| `agent_v1` | `s03` | no | PASS | 3 | 3575 | $0.000516 | 3453 ms |
| `agent_v1` | `s04` | no | PASS | 3 | 3867 | $0.000548 | 6965 ms |
| `agent_v1` | `s05` | no | PASS | 3 | 3197 | $0.000460 | 4652 ms |
| `agent_v1` | `s06` | no | PASS | 3 | 3854 | $0.000532 | 46046 ms |
| `agent_v1` | `c01` | yes | PASS | 3 | 4392 | $0.000611 | 7451 ms |
| `agent_v1` | `c02` | yes | PASS | 3 | 4314 | $0.000606 | 4403 ms |
| `agent_v1` | `c03` | yes | PASS | 3 | 4675 | $0.000615 | 4580 ms |
| `agent_v1` | `c04` | yes | PASS | 3 | 3725 | $0.000531 | 4579 ms |

## Failures, with the reason

