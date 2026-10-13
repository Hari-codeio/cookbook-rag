# Suite run `red`

```
release   : squad-v1
cases     : 11  (10 race + 1 regression)
started   : 2026-10-13T01:05:16+00:00
traces    : C:\Hari\Python\AI\cookbook-rag\out\w11\suite_traces.jsonl
```

| case | kind | w10 grader (1-5) | **now (1-6)** | trace | why it failed |
|---|---|---|---|---|---|
| `s01` | race | PASS | **PASS** | `tr_c4519a0e51ba` |  |
| `s02` | race | PASS | **PASS** | `tr_c2bc48fd1a3c` |  |
| `s03` | race | PASS | **FAIL** | `tr_0a6ebf388361` | method still tells the cook to use contains-alcohol: ['over the reserved wine'] |
| `s04` | race | PASS | **PASS** | `tr_9a30c32d0aa2` |  |
| `s05` | race | PASS | **PASS** | `tr_9e655d5ae16d` |  |
| `s06` | race | PASS | **PASS** | `tr_e4523576fa99` |  |
| `c01` | race | PASS | **PASS** | `tr_745200998555` |  |
| `c02` | race | PASS | **FAIL** | `tr_5b08a77ab490` | method still tells the cook to use contains-dairy: ['chicken in the yoghurt', 'onion in the ghee,', 'stir in the cream'] |
| `c03` | race | PASS | **FAIL** | `tr_a0cb684bdf79` | method still tells the cook to use contains-dairy: ['Add the softened butter', 'eggs and warm milk'] |
| `c04` | race | PASS | **FAIL** | `tr_c13b3cb8a45f` | method still tells the cook to use contains-dairy: ['Beat the butter'] |
| `w11-r01` | regression | PASS | **FAIL** | `tr_cf4384faefa8` | method still tells the cook to use contains-dairy: ['acid in the yoghurt', 'chicken in the yoghurt', 'onion in the ghee,', 'stir in the cream'] |

```
SUITE RED: 6/11 pass   (release squad-v1)
same answers, Week 10 grader: 11/11
tokens 46651   cost $0.024919   model calls 63
```
