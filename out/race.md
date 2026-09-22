# Week 7 race: agent vs fixed workflow

Same 10 requests, same tools, same pinned model, same output contract.

| system | pass rate | p50 latency | total tokens | cost / request |
|---|---|---|---|---|
| `agent_v2` | 10/10 (100%) | 20677 ms | 85,244 | $0.001034 |
| `workflow` | 10/10 (100%) | 9335 ms | 12,444 | $0.000271 |
| `agent_v1` | 10/10 (100%) | 12957 ms | 38,770 | $0.000543 |

Split by case type, which is where the average hides the answer:

| system | 6 straightforward | 4 cascade | mean laps |
|---|---|---|---|
| `agent_v2` | 6/6 | 4/4 | 4.8 |
| `workflow` | 6/6 | 4/4 | 2.0 |
| `agent_v1` | 6/6 | 4/4 | 3.0 |

## Per case

| system | case | cascade | result | laps | tokens | cost | latency |
|---|---|---|---|---|---|---|---|
| `agent_v2` | `s01` | no | PASS | 4 | 6473 | $0.000811 | 16356 ms |
| `agent_v2` | `s02` | no | PASS | 5 | 8258 | $0.001020 | 19636 ms |
| `agent_v2` | `s03` | no | PASS | 5 | 8391 | $0.001015 | 18845 ms |
| `agent_v2` | `s04` | no | PASS | 6 | 11241 | $0.001311 | 30237 ms |
| `agent_v2` | `s05` | no | PASS | 5 | 7383 | $0.000917 | 21604 ms |
| `agent_v2` | `s06` | no | PASS | 3 | 4586 | $0.000605 | 15553 ms |
| `agent_v2` | `c01` | yes | PASS | 5 | 9764 | $0.001142 | 19750 ms |
| `agent_v2` | `c02` | yes | PASS | 5 | 10108 | $0.001256 | 23057 ms |
| `agent_v2` | `c03` | yes | PASS | 5 | 10498 | $0.001222 | 37095 ms |
| `agent_v2` | `c04` | yes | PASS | 5 | 8542 | $0.001036 | 25522 ms |
| `workflow` | `s01` | no | PASS | 2 | 1198 | $0.000257 | 11130 ms |
| `workflow` | `s02` | no | PASS | 2 | 1287 | $0.000281 | 10318 ms |
| `workflow` | `s03` | no | PASS | 2 | 1278 | $0.000272 | 14322 ms |
| `workflow` | `s04` | no | PASS | 2 | 1294 | $0.000285 | 8046 ms |
| `workflow` | `s05` | no | PASS | 2 | 1134 | $0.000243 | 11282 ms |
| `workflow` | `s06` | no | PASS | 2 | 1220 | $0.000264 | 12810 ms |
| `workflow` | `c01` | yes | PASS | 2 | 1259 | $0.000276 | 6237 ms |
| `workflow` | `c02` | yes | PASS | 2 | 1391 | $0.000310 | 6680 ms |
| `workflow` | `c03` | yes | PASS | 2 | 1112 | $0.000240 | 7138 ms |
| `workflow` | `c04` | yes | PASS | 2 | 1271 | $0.000287 | 8351 ms |
| `agent_v1` | `s01` | no | PASS | 3 | 3626 | $0.000484 | 18766 ms |
| `agent_v1` | `s02` | no | PASS | 3 | 3545 | $0.000526 | 15313 ms |
| `agent_v1` | `s03` | no | PASS | 3 | 3575 | $0.000516 | 10226 ms |
| `agent_v1` | `s04` | no | PASS | 3 | 3867 | $0.000548 | 10774 ms |
| `agent_v1` | `s05` | no | PASS | 3 | 3197 | $0.000460 | 12928 ms |
| `agent_v1` | `s06` | no | PASS | 3 | 3854 | $0.000532 | 8067 ms |
| `agent_v1` | `c01` | yes | PASS | 3 | 4392 | $0.000611 | 10177 ms |
| `agent_v1` | `c02` | yes | PASS | 3 | 4314 | $0.000606 | 13574 ms |
| `agent_v1` | `c03` | yes | PASS | 3 | 4675 | $0.000615 | 15618 ms |
| `agent_v1` | `c04` | yes | PASS | 3 | 3725 | $0.000531 | 12985 ms |

## Failures, with the reason

