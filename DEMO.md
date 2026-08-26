# Live demo script

Keep this open on a second screen. Every command below is fast and needs no API key,
except the two marked **[key]** at the end.

## Prep, before he arrives (2 minutes)

```powershell
cd c:\Hari\Python\AI\cookbook-rag
$env:HF_HUB_DISABLE_SYMLINKS_WARNING=1
.\.venv\Scripts\python.exe demo.py g03
```

That throwaway run loads both models into memory. **Do not skip it.** The first
cross-encoder call is slow because it loads an 80 MB model, and you do not want that
happening while he watches.

Then clear the screen and start.

---

## Step 1 — the corpus (10 seconds)

```powershell
ls data/baseline, data/new_drop, data/variations
```

Say: *"21 recipes, 94 chunks. Nine from Week 3, six fermentation cards, and six
near-duplicates I added in Week 4 because the failure I needed to study only happens when
two recipes look alike."*

## Step 2 — the golden set (20 seconds)

Open `eval/golden_set.jsonl`.

Say: *"12 questions written before I ran anything, each tagged with the exact chunk that
answers it. Six contain a rare term or a number, which is what meaning-based search is
bad at. The file is fingerprinted, so I can prove the questions didn't change between my
two measurements."*

## Step 3 — the failure, and the fix (30 seconds) ⭐ the main event

```powershell
.\.venv\Scripts\python.exe demo.py g03
```

Point at the output:

- Before: the top 3 are two cabbage recipes and the wrong section of the right one. The
  correct chunk was at **rank 14 of 94**.
- After: **rank 1**.

Say: *"This is an R failure. Retrieval fetched bad context. The chunk with psyllium husk
15 g existed the whole time, it just ranked 14th, so the model never saw it."*

## Step 4 — the failure it did NOT fix (30 seconds)

```powershell
.\.venv\Scripts\python.exe demo.py g09
```

Say: *"Still broken. It moved from rank 13 to rank 5 and stopped. The question asks about
hydration, and the word hydration appears nowhere on that card. The card says Water 800 g,
80%. I predicted a cross-encoder would bridge that. It didn't. That's in my report."*

Volunteering a wrong prediction scores better than hiding it.

## Step 5 — the G failure (30 seconds)

```powershell
.\.venv\Scripts\python.exe demo.py g12
```

Say: *"Retrieval was perfect here, before and after. The right chunk was rank 1 both
times. But the answer was still wrong on one run, because the card says shellfish and the
user asked about prawns, and my prompt forbids outside knowledge. That's a G failure. No
retrieval change can fix it. If I'd labelled this R, I'd have built the reranker to fix a
question the reranker cannot touch."*

## Step 6 — the numbers (30 seconds)

These are pre-computed. **Do not re-run them live**, they take minutes.

```powershell
cat out/hitrate3_before.md
cat out/hitrate3_after.md
```

Point at: **10/12 → 11/12**, and **1400 ms → 4722 ms**.

Say: *"Plus one question, times 3.4 latency. I chose not to ship it. One question on a
12-question set is 8 percentage points, which is inside the noise."*

## Step 7 — the window sweep, if he asks why 25 (15 seconds)

```powershell
cat out/window_sweep.txt
```

Say: *"g03 sat at rank 14, so a window under 14 can't see it and the gain disappears. And
shrinking barely saves anything, because the cost is invoking the model at all, not the
number of pairs."*

---

## Optional, if he wants to see the app answer **[key]**

```powershell
.\.venv\Scripts\python.exe -m rag.generate "how much xanthan gum in the gluten free brioche" --k 3
```

Expect `6 g (1.2%)` with a chunk ID in brackets.

Then the Week 3 refusal, which is the best single thing to show:

```powershell
.\.venv\Scripts\python.exe -m rag.generate "what percentage of caraway seed is in the kimchi?"
```

Expect `INSUFFICIENT_CONTEXT`. Say: *"Caraway is real, but it's on the sauerkraut card, not
the kimchi card. It refuses instead of inventing a number."*

---

## Do NOT run these live

| command | why |
|---|---|
| `eval/run_hitrate3.py` | 2 to 5 minutes |
| `eval/run_answer_eval.py` | 12 API calls, can hit a 503 |
| `eval/run_mmr_bonus.py` | several minutes |
| `rag.ingest` | refuses on purpose (append-only). Looks like a crash unless you explain it |

Show the saved files in `out/` instead. That is what they are for.

## If something breaks

- **Gemini 503.** It auto-retries and falls back to another model. If every model is busy,
  stop using live generation and show `out/answer_eval_before.md` instead.
- **First rerank is slow.** You skipped the warm-up. Say so and carry on.
- **`golden_set.jsonl` throws a JSON error.** Your IDE reformatted it. It is JSONL, one
  object per line, so format-on-save breaks it. Turn formatting off for that file.
