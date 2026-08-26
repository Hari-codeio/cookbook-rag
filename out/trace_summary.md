# Trace log - descriptive summary

```
file          : C:\Hari\Python\AI\cookbook-rag\out\traces.jsonl
bytes         : 1,303,661
lines         : 163   (one JSON object per line)
sha256        : e58151f7a61b69accc754641931496afb2d1695861a5282c6d9c284700317520
traces        : 163
```

| source | traces |
|---|---|
| `curated-demo` | 12 |
| `random-traffic` | 150 |
| `schema-1.1-proof` | 1 |

## `curated-demo` - 12 traces

```
raised an exception : 0
answered            : 10  (83%)
refused             : 2  (17%)
model latency ms    : p50 3623  p90 4188  max 6287
tokens in / out     : 14,341 / 1,203
models              : {'gemini-3.1-flash-lite': 12}
prompt versions     : {'grounded-recipe-v1': 12}
trace schemas       : {'1.0': 12}
```

## `random-traffic` - 150 traces

```
raised an exception : 0
answered            : 86  (57%)
refused             : 64  (43%)
model latency ms    : p50 2350  p90 9197  max 41094
tokens in / out     : 177,034 / 14,446
models              : {'gemini-3.5-flash': 18, 'gemini-3.6-flash': 18, 'gemini-3.1-flash-lite': 109, 'gemini-flash-latest': 5}
prompt versions     : {'grounded-recipe-v1': 150}
trace schemas       : {'1.0': 150}
```

| question shape | traces | refused |
|---|---|---|
| allergen | 12 | 4 (33%) |
| comparison | 12 | 6 (50%) |
| conversion | 8 | 8 (100%) |
| lookup | 45 | 1 (2%) |
| method | 21 | 3 (14%) |
| out-of-scope | 7 | 6 (86%) |
| scaling | 15 | 15 (100%) |
| substitution | 12 | 12 (100%) |
| technique | 8 | 3 (38%) |
| underspecified | 10 | 6 (60%) |

## `schema-1.1-proof` - 1 traces

```
raised an exception : 0
answered            : 1  (100%)
refused             : 0  (0%)
model latency ms    : p50 1920  p90 1920  max 1920
tokens in / out     : 1,199 / 102
models              : {'gemini-3.1-flash-lite': 1}
prompt versions     : {'grounded-recipe-v1': 1}
trace schemas       : {'1.1': 1}
```

