# Support drill: "the dairy-free swap that wasn't"

> *"someone said it recommended a dairy-free substitution that wasn't
> dairy-free, sometime last week."*

| | drill 1 | drill 2 (bonus) |
|---|---|---|
| **time-to-find** | **00:17** | **00:11** |
| **slice that found it** | **input type** (`allergen-swap`, `contains-dairy`) + **time** (7d), then reading the swap lines | the new **residue** field: `--residue swap` + `--asked contains-dairy` + time 7d |
| rows a person had to read | 10 answers, 22 swap lines | **1** |
| found | `tr_93031da07c32`, u_0107, tikka masala: *Double cream -> Creme fraiche, "suits a dairy-free sauce"* | `tr_8c2f07583608`, u_0134, milk kefir: *Whole cow's milk -> Lactose-free milk* |
| checked against the seal | MATCH | MATCH |
| tooling | `rag/obs_index.py` at `00ed2cb` | `rag/obs_index.py` at `0a00a4f` |
| raw record | `out/w11/drill/drill_log.jsonl` line 1 | line 2 |
| haystack | `out/w11/drill/run1/traces.jsonl` (36 real + 1 planted) | `out/w11/drill/run2/traces.jsonl` (36 real + 1 planted) |

## Read this first: these two times are a REHEARSAL, not the graded drill

- **No squadmate held the stopwatch.** `eval/drill.py` timed it: `start`
  writes the clock, `found` stops it and checks the guess against the
  planter's seal. The `timer` field says so.
- **The finder wrote the planter.** I did not know which trace, user, time or
  swap was planted (`--random`, no receipt), but I knew the KIND of corruption
  the tool makes. A real finder knows only the complaint.
- **The finder reads at machine speed.** 22 swap lines took me seconds; they
  would take a person a couple of minutes. That is why the column that matters
  is **rows a person had to read: 22 -> 1**, not 17 s -> 11 s.

So both rehearsals are evidence that the **tooling** works end to end, not a
human time. **The graded run is yours, with a named squadmate, on Monday**;
the commands are at the bottom and the result goes in the table below.

## Drill 1, step by step

```
python eval/w11_plant.py --random                       # planter: 37 rows, seal written, no receipt
python eval/drill.py start --finder "..."               # 01:03:35 UTC
python eval/drill.py slice --since 7d --type allergen-swap --allergen contains-dairy
    -> 10 of 37 requests
python eval/drill.py slice --since 7d --type allergen-swap --allergen contains-dairy --show-answer --grep "swap "
    -> 22 swap lines; one reads "Double cream -> Creme fraiche (Cultured, so it is gentler
       than cream and suits a dairy-free sauce.)". Creme fraiche is cultured cream.
python eval/drill.py found tr_93031da07c32 --slice "..." --timer "..."
    -> MATCH: this is the planted answer.  time-to-find 00:17
```

**Why input type first, not text.** The complaint describes the OUTPUT. A
full-text search for "dairy" hits nearly every dairy request's answer, because
legitimate answers say "without dairy" and "dairy-free". Slicing on what the
request was (input type + allergen) cut 37 rows to 10. Reading the replacements
is what found it.

**Under 5 minutes, and the field whose absence cost the time anyway.** All of
drill 1's time went into reading. Nothing in the log answered the complaint's
actual question: *did this answer's replacement carry the allergen the user
asked to avoid?* The log held the answer and the allergen, but no field joined
them.

## Drill 2 (bonus): the field that closed the gap

`rag/obs_index.py` now DERIVES that field from every logged answer, using the
same deterministic check the suite grades with (`rag/contract.allergen_residue`).
It backfills every old trace when the index rebuilds:

| column | answers |
|---|---|
| `asked` | what the user's own words asked to avoid ("no dairy", "lactose free", "milk allergy") |
| `missed` | which of those the planner dropped |
| `residue_swaps` | **replacements that carry an avoided allergen** <- the one that closed the gap |
| `residue_rows`, `residue_method` | ingredient rows / method phrases that still carry it |

```
python eval/w11_plant.py --random                       # a second, fresh plant
python eval/drill.py start --finder "..."               # 01:10:01 UTC
python eval/drill.py slice --since 7d --asked contains-dairy --residue swap
    -> 1 of 37 requests: tr_8c2f07583608, "Whole cow's milk -> Lactose-free milk"
python eval/drill.py found tr_8c2f07583608 ...
    -> MATCH.  time-to-find 00:11
```

**The one field that closed the gap: `residue_swaps`.** On the real production
log it returns **0 of 36** (the substitution worker's allergen check holds), so
anything it returns is the needle.

## What the slices found that nobody planted

A drill that only finds the plant has missed the point. The same slices on the
real production log (`out/w11/traces.jsonl`, no plant):

| slice | rows | what it is |
|---|---|---|
| `--residue method --asked contains-dairy` | **8 of 9** dairy answers | the method still says "soften the onion in the ghee", "beat the butter", "warm milk" after the swap. **The real bug**, and what the regression case and the fix are about. |
| `--residue any` | 17 of 36 | the same, across all allergens (wine, prawns, flour) |
| `--plan-mismatch` | 3 of 36 | the user asked for dairy-free and the planner did not pick dairy. One matters: "Gluten-free brioche but dairy free too" was planned as gluten only, so its answer kept the milk and butter. |
| input type vs request text | 3 of 3 "half" requests | the planner invented an allergen nobody asked for: half sourdough -> gluten removed, half bourguignon -> wine removed, half miso -> soy removed |

The last two are logged as backlog in `results_week11.md`, not fixed this week:
one fix per week, so the fix can be attributed.

## The graded drill, for Monday

| | |
|---|---|
| finder | Hari |
| timed by (squadmate) | _______ |
| planted by (squadmate) | _______ |
| time-to-find (mm:ss) | _______ |
| slice that found it | _______ |
| missing field (only if over 5:00) | _______ |

```
# squadmate (Hari looks away):
python eval/w11_plant.py --random            # or --from-trace / --swap-to / --request to pick their own
# Hari, with the squadmate holding the stopwatch:
python eval/drill.py start --finder Hari
python eval/drill.py slice ...               # any slices; no diffing the drill copy against the production log
python eval/drill.py found tr_xxxxxxxxxxxx --slice "<which slice found it>" --timer "<squadmate's name>"
```

`found` prints MATCH or NO MATCH and appends the attempt to
`out/w11/drill/drill_log.jsonl`, so a wrong guess is on the record too.

Two things that would make the time meaningless, from the brief: recognising
the recipe you demoed on Friday (memory, not tooling), and diffing the drill
copy against `out/w11/traces.jsonl` (the plant is the only line that differs).
