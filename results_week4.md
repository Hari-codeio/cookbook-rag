# Week 4 · Task Set B — label the failures, then buy back hit-rate@3 with one change

Week 3's report is `results.md`. This is the Week 4 extension and it reuses that app,
that index, and that chunker. Nothing about the Week 3 numbers changed.

```
retriever before : dense only (all-MiniLM-L6-v2, cosine, Chroma HNSW)
retriever after  : dense -> cross-encoder rerank over the top 25
embedding model  : all-MiniLM-L6-v2 (chromadb ONNX)   HELD FIXED across both runs
reranker         : Xenova/ms-marco-MiniLM-L-6-v2 (ONNX, ~80 MB, no PyTorch)
chunker          : structure-aware (the one that shipped in Week 3)   HELD FIXED
k                : 3
candidate window : 25
chunks in index  : 94   (21 recipes)
golden set       : eval/golden_set.jsonl, sha256 24dda257f8b337d428710cd1f34a6def01a16f77cdc3a318b992351cc05d3cb7
```

**Exactly one variable moved between the before and after runs**: whether the dense
result list is reordered by a cross-encoder. Same 12 questions, same embedder, same
collection, same chunker, same k. The embedding model was *not* swapped, and section 4
explains why that was the right call and where I disagree with the brief about it.

---

## 0. Three things I changed about my own setup first, and why

These are disclosed up front because two of them affect how the numbers should be read.

### 0.1 My first golden set scored 12/12 and measured nothing

I wrote 12 questions, ran them, and got **12/12**. That is the exact failure the brief
lists: *"A golden set that only contains questions you already pass measures nothing."*

The cause was structural, not laziness. Every question named a unique dish, and my
Week 3 corpus had no two recipes of the same type. Name the dish and its 4 or 5 chunks
cluster together, so the right one is nearly always inside the top 3. The brief's own
example only bites because naming the dish *doesn't* narrow it down — there are three
brioches.

The rejected set is kept at `eval/golden_set_v1_rejected.jsonl` and its run at
`out/hitrate3_v1golden_rejected.md`, so the rewrite is auditable rather than hidden.

### 0.2 I added 6 near-duplicate recipes to the index

The brief's scenario requires near-copies, and the MMR bonus is undemonstrable without
them. My corpus had none. So I added `data/variations/`:

| recipe | why it is there |
|---|---|
| `gf-brioche` | xanthan gum **6 g** |
| `gf-sandwich-loaf` | xanthan gum **10 g** — same rare term, different answer |
| `classic-brioche` | near-copy of gf-brioche's method prose |
| `chocolate-brioche` | third brioche, butter 225 g against 175 g and 250 g |
| `wholemeal-sourdough` | second sourdough, 80% hydration, 240 C |
| `rye-sourdough` | third sourdough, 19 g salt against 18 g and 20 g |

Index went 70 → 94 chunks, 15 → 21 recipes, appended with the same append-only proof
block as Week 3 (`out/ingest_variations.md`: `70 + 24 = 94 (OK)`, `pre-existing
rewritten: 0`). `fine sea salt` now appears in **20 of 94 chunks**.

**The obvious objection**: did I add documents until the baseline looked bad? No, and
here is the check. The additions were made *before* the golden set was rewritten and
*before* any retrieval change existed or was chosen. They were chosen to reproduce the
brief's stated scenario (near-copies plus a shared rare term at different values), not
to break any particular query. The rewritten questions were then written from the cards,
validated against the index, and frozen by hash before the baseline was run.

**What this costs in credibility, stated plainly**: I authored the corpus and the
questions. This measures my pipeline on my own data. The mechanism is real and
reproducible; the specific numbers are not a benchmark.

### 0.3 A bug in my own scoring produced a false G failure

The first tally reported `G: 1` against **g01**, with the answer *"The recipe calls for
6 g (1.2%) of xanthan gum"* — which is correct. My answer key listed `"2%"` as a wrong
value (it is the sandwich loaf's figure), and a plain substring test finds `"2%"` inside
`"1.2%"`.

That single mislabel pointed at the model when every real failure was in retrieval. It
is precisely the trap the brief describes, arriving from my measurement code rather than
my judgement. `contains()` in `eval/run_answer_eval.py` is now boundary-aware — a needle
starting with a digit may not be preceded by a digit or a decimal point — with 12 unit
cases covering `2%` vs `1.2%`, `6 g` vs `16 g`, and `80%` vs `180%`.

---

## 1. The 12-question golden set

Written from the cards before either index state was queried, validated against the live
index (every `expected_chunk_id` exists, belongs to the stated recipe, and contains the
discriminating term), then frozen by sha256.

Questions are written the way people actually type into a recipe app: lowercase, terse,
no punctuation, sometimes not naming the dish at all. **6 of 12 contain an exact term
dense retrieval is structurally bad at** — the requirement is at least 4.

| id | question | expected chunk | known answer | exact term | why it is hard |
|---|---|---|---|---|---|
| g01 | how much xanthan gum in the gluten free brioche | `gf-brioche::structure::c001` | 6 g (1.2%) | **rare ingredient** | two recipes use xanthan gum at different amounts |
| g02 | xanthan for the gf sandwich loaf | `gf-sandwich-loaf::structure::c001` | 10 g (2%) | **rare ingredient** | same term as g01, other recipe — the term alone cannot disambiguate |
| g03 | psyllium husk amount | `gf-sandwich-loaf::structure::c001` | 15 g (3%) | **rare ingredient** | rare term, no dish named at all |
| g04 | how much saeujeot in the kimchi | `napa-kimchi::structure::c001` | 20 g (2%) | **rare ingredient** | loanword that subword tokenisation destroys |
| g05 | amchur amount chana masala | `chana-masala::structure::c002` | 6 g | **rare ingredient** | rare term in the second half of a split table |
| g06 | what temp do i bake the 2kg sourdough at | `sourdough-2kg::structure::c003` | 250 C then 230 C | **oven temperature** | three sourdoughs bake at 240, 250 and 250 C |
| g07 | how much butter in the chocolate brioche | `chocolate-brioche::structure::c001` | 225 g (45%) | near-duplicate | three brioches use 175, 250 and 225 g butter |
| g08 | salt in the rye sourdough | `rye-sourdough::structure::c001` | 19 g (1.9%) | near-duplicate | `fine sea salt` is in 20 chunks; three sourdoughs use 18, 19, 20 g |
| g09 | hydration of the wholemeal loaf | `wholemeal-sourdough::structure::c001` | 80% | near-duplicate | three sourdoughs at 76, 78, 80 percent |
| g10 | can i strain kefir with a metal sieve | `milk-kefir::structure::c002` | no, use nylon | paraphrase | no shared vocabulary with the card |
| g11 | why do pickles turn soft | `dill-pickles::structure::c002` | the blossom end enzyme | paraphrase | the card never uses "soft" in this sense |
| g12 | is the kimchi ok if im allergic to prawns | `napa-kimchi::structure::c004` | no, shrimp paste and fish sauce | paraphrase | "prawns" never appears; "shrimp" and "shellfish" do |

A hit means **that exact chunk_id is inside the top 3**. Not the right recipe, not a
chunk that looks close. Retrieving the right card but the wrong section scores a miss,
which is stricter than recipe-level recall and is the point — the question is whether
the number arrived.

---

## 2. Baseline hit-rate@3, written down before anything changed

`out/hitrate3_before.md`, generated 2026-08-19T15:02:31Z.

| metric | value |
|---|---|
| **hit-rate@3** | **10 / 12** |
| hit@1 | 6 / 12 |
| MRR | 0.651 |
| hit-rate@3, exact-term questions | 5 / 6 |
| hit-rate@3, paraphrase questions | 5 / 6 |
| **p50 latency per query** | **1400.6 ms** |
| p95 latency per query | 1723.1 ms |

Latency is the retrieval call only, 7 samples per question, 84 samples total, median of
all of them, embedder warmed first. A single sample swung by a factor of seven on the
first attempt, which is why it is sampled rather than timed once.

---

## 3. The failure tally: R / G / Not-In-Corpus

`out/answer_eval_before.md`. hit-rate@3 measures retrieval only, so it *cannot* surface
a G failure by construction — G means retrieval worked and the model still got it wrong.
So all 12 questions were also run through full generation at k=3, and every wrong answer
labelled by this tree:

```
wrong answer + correct chunk NOT in top-3   -> R              (retrieval fetched bad context)
wrong answer + correct chunk IS  in top-3   -> G              (model misused good context)
wrong answer + no chunk holds the answer    -> Not-In-Corpus
```

### Tally

| label | count |
|---|---|
| PASS | 9 |
| **R** — retrieval fetched bad context | **2** |
| **G** — model misused good context | **1** |
| Not-In-Corpus | 0 |

### One line of real evidence per labelled failure

**g03 — R.** `psyllium husk amount`
> Correct chunk `gf-sandwich-loaf::structure::c001` was at **rank 14 of 94**, not in the
> top 3. Retrieved instead: `red-sauerkraut::structure::c001`,
> `gf-sandwich-loaf::structure::c002`, `red-sauerkraut::structure::c002`. Top-1 score
> was 0.2743 — dense retrieval had almost no signal and put an unrelated cabbage recipe
> first. The model then refused: *"INSUFFICIENT_CONTEXT: The amount or weight of
> psyllium husk required in the recipe."* An honest output, but the retrieval caused it.

**g09 — R.** `hydration of the wholemeal loaf`
> Correct chunk `wholemeal-sourdough::structure::c001` was at **rank 13 of 94**. The
> right *recipe* was retrieved — its title chunk at rank 2 and its method chunk at rank
> 3 — but the ingredients chunk holding `| Water (28 C) | 800 g | 80% |` ranked below
> both. The model refused. Retrieval found the document and missed the section.

**g12 — G.** `is the kimchi ok if im allergic to prawns`
> Correct chunk `napa-kimchi::structure::c004` was at **rank 1**, and the model refused
> anyway: *"INSUFFICIENT_CONTEXT: The context does not state whether a prawn allergy is
> a shellfish allergy."* The card says *"Contains fish (fish sauce) and shellfish (salted
> shrimp paste)"*. Rule 1 of my Week 3 grounding prompt forbids outside knowledge, so the
> model would not make the prawn → shellfish inference. **Perfect retrieval, wrong
> answer. No retrieval change can touch this one.**

### An instability I have to report

g12 is **not stable across runs**. It passed on one execution and produced the G refusal
on another, with the same retrieval and the same rank-1 chunk. Two causes, both mine:
the grounding prompt sits right at the edge of refusing this inference, and my Gemini
model fallback means a 503 on `gemini-3.6-flash` silently serves the call from
`gemini-3.5-flash` instead.

So `G: 1` is a real failure mode I can reproduce and diagnose, but it is not a stable
count. It is one flaky question, not a measured G-rate. The R labels are stable, because
they come from retrieval, which is deterministic here.

---

## 4. The single change, and why the tally chose it

**The change: a cross-encoder rerank of the top 25 dense results.** `rag/rerank.py`.

Both R failures had the correct chunk **already inside the candidate window** — rank 14
and rank 13 of 94. Nothing was unreachable; both were retrieved and then mis-ordered,
and in both cases the right recipe was in the top 3 while the section carrying the
number was not. Reordering the top 25 is the only operation that addresses that, and it
reaches both. That is why I picked reranking over BM25 + RRF, and the tally is the whole
argument: BM25 earns its keep when the correct chunk is *absent* from the candidate list
because a rare term was blurred away, and neither of my failures is that shape. BM25 would
very likely have fixed **g03**, since `psyllium husk` appears verbatim in the target chunk
— but it structurally cannot fix **g09**, because that query's key term is *hydration* and
the word hydration appears **nowhere** on the wholemeal sourdough card; the card states the
fact as `| Water (28 C) | 800 g | 80% |`, so there is no lexical bridge for a term matcher
to cross. One change had to cover both R failures, and only reranking could reach both. The
single G failure (g12) is outside the reach of either option and I am not counting it as
something retrieval can fix.

### Where I disagree with the brief about swapping the embedding model

The brief primes you to reject the team lead's suggestion. I am rejecting it, but not for
the reason given, because that reason does not hold on my data. The brief's argument is
that a denser embedding structurally cannot help exact-term R-failures where the correct
chunk is unreachable. **Mine are not that shape.** Both correct chunks were retrieved and
merely mis-ordered inside the window, and a stronger embedder could plausibly reorder them.
It is still the worse choice, for reasons that are about blast radius rather than
structure: it re-embeds all 94 chunks, invalidates every number in the Week 3 report,
changes the representation for the 9 questions that already pass, and cannot be undone
without a re-index. Reranking leaves the index untouched and only reorders. Same target,
smaller risk. Pretending the brief's structural argument applied to my tally when it
doesn't would be exactly the kind of unexamined agreement it warns against.

---

## 5. Before → after, both numbers

`out/hitrate3_before.md` and `out/hitrate3_after.md`.

| metric | before (dense) | after (rerank top-25) | change |
|---|---|---|---|
| **hit-rate@3** | **10 / 12** | **11 / 12** | **+1** |
| hit@1 | 6 / 12 | 10 / 12 | **+4** |
| MRR | 0.651 | 0.892 | +0.241 |
| exact-term questions | 5 / 6 | **6 / 6** | +1 |
| paraphrase questions | 5 / 6 | 5 / 6 | 0 |
| **p50 latency per query** | **1400.6 ms** | **4722.4 ms** | **+3321.8 ms (3.37×)** |
| p95 latency per query | 1723.1 ms | 5568.3 ms | +3845.2 ms (3.23×) |

The answer-level tally moved with it: **PASS 9 → 11, R 2 → 1, G 1 → 0**
(`out/answer_eval_after.md`). But see the honesty note in section 3 — the G going to zero
is g12 flipping on a rerun, not the reranker fixing it. Its chunk was at rank 1 both
times, so reranking could not have been the cause, and I am not claiming it.

### A caveat on the latency numbers

The **ratio** is the trustworthy part. The absolute figures are inflated: this runs
onnxruntime on CPU with per-call overhead, and 1400 ms for a local dense query over 94
chunks is already far slower than any real deployment, where the same query is tens of
milliseconds. Read 3.37× as the price, not "+3.3 seconds" as a production figure.

---

## 6. Which failures the change fixed, and which it did not touch

Per-question rank of the expected chunk, out of 94.

| id | before | after | hit@3 before | hit@3 after | verdict |
|---|---|---|---|---|---|
| g01 | 2 | 1 | HIT | HIT | already passing, improved |
| g02 | 2 | 2 | HIT | HIT | already passing, unchanged |
| **g03** | **14** | **1** | **MISS** | **HIT** | **FIXED** |
| g04 | 3 | 1 | HIT | HIT | already passing, improved |
| g05 | 1 | 1 | HIT | HIT | already passing, unchanged |
| g06 | 1 | 1 | HIT | HIT | already passing, unchanged |
| g07 | 3 | 1 | HIT | HIT | already passing, improved |
| g08 | 1 | 1 | HIT | HIT | already passing, unchanged |
| **g09** | **13** | **5** | **MISS** | **MISS** | **STILL BROKEN** — improved 13 → 5, not enough |
| g10 | 1 | 1 | HIT | HIT | already passing, unchanged |
| g11 | 1 | 1 | HIT | HIT | already passing, unchanged |
| g12 | 1 | 1 | HIT | HIT | retrieval was never the problem here |

**Named explicitly, as the brief asks:**

- **R-failure FIXED: g03.** The correct chunk went from rank 14 to **rank 1**, cross-encoder
  score +0.1551 against −0.0790 for the sibling method chunk. The reranker recognised
  that a query asking for an *amount* is answered by the ingredient table row, not by the
  method prose that merely mentions psyllium husk.

- **R-failure NOT FIXED: g09.** Still a miss. It improved from rank 13 to rank 5, so the
  reranker moved it in the right direction and then stopped short. The cross-encoder still
  ranks `wholemeal-sourdough::structure::c000` (the title chunk) above the ingredients
  chunk. **My prediction here was wrong.** I argued in section 4 that a cross-encoder
  would bridge *hydration* → `800 g / 80%` where BM25 could not. It did not. A
  22-million-parameter MS MARCO cross-encoder has no more idea that hydration is
  water-over-flour than the embedder did. Neither offered option fixes g09; what it
  actually needs is either a domain synonym expansion (hydration → water percentage) or
  the word "hydration" written on the card.

- **G-failure NOT TOUCHED: g12.** Untouched by construction. Its chunk was at rank 1
  before and after. A retrieval change cannot fix a grounding-prompt problem, and this is
  the question that proves the labelling exercise was worth doing — had I labelled it R
  on the strength of "the answer was wrong", I would have spent the whole week building a
  reranker to fix a question that reranking cannot affect.

---

## 7. Shipping decision

**I would not ship this configuration. The number does not justify the cost.**

The honest arithmetic on the metric the brief asked me to move: **+1 question out of 12
for 3.37× latency.** One question is 8.3 percentage points on a 12-question set, which is
inside the noise of a set this small — a single question is worth 8.3 points, so "+1" and
"no real change" are not distinguishable here. Paying 3.4× query latency for a result
that thin is not a trade I would defend in review.

The counter-argument, stated fairly, is that **hit@1 went 6/12 → 10/12 and MRR 0.651 →
0.892.** Those are large and they are not noise-sized. But they are the wrong metric for
*this* app: it feeds the top 3 into the model, so being right at rank 1 rather than rank 3
buys nothing downstream. hit@1 would matter if I were showing a single source to the user
or cutting k to 1 to save tokens. I am not, so I decline to bank it as a win.

**What I would do instead**, in order:

1. **Fix g09 without a reranker.** It is a vocabulary gap, not a ranking failure. Writing
   the word "hydration" beside the water row, or expanding the query term, costs no
   latency at all and targets the one failure that survived.
2. **Keep the reranker behind a flag, off by default.** `GEN_PROVIDER`-style switching
   already exists; `--retriever rerank` is one argument. It costs nothing to keep and it is
   the right tool the moment the corpus grows enough that in-window mis-ordering becomes
   the dominant failure. At 94 chunks it is not.
3. **Re-measure on a corpus 10× larger before revisiting.** The reranker's whole value is
   reordering a candidate window. With 94 chunks and k=3, dense retrieval already lands
   the right recipe in the top 3 on 11 of 12 questions, so there is very little for a
   reranker to win. That headroom grows with the index.

### Could the gain be bought cheaper? Measured, and no

The obvious objection to "too slow" is "then shrink the candidate window". I measured it
rather than assuming. Separate timing pass, 5 samples per question, so these figures are
comparable to each other but not to the p50 table in section 5, which used 7 samples and
its own warmup.

| config | hit-rate@3 | p50 | fixes g03? |
|---|---|---|---|
| dense, no rerank | 10/12 | 1021.5 ms | n/a |
| rerank, window=5 | 10/12 | 3134.5 ms | no |
| rerank, window=10 | 10/12 | 3568.1 ms | no |
| **rerank, window=14** | **11/12** | **3725.5 ms** | **YES** |
| rerank, window=25 (shipped config) | 11/12 | 4234.5 ms | YES |

Two things fall out of this, and both argue against shipping.

**The window cannot go below 14.** g03's correct chunk sat at rank 14, so any smaller
window literally cannot see it, and windows of 5 and 10 duly score 10/12 — the entire
gain vanishes. The boundary is exactly where the arithmetic said it would be.

**Shrinking the window barely helps anyway, because the cost is not the pairs.** A
window of 5 scores five pairs and still costs 3134 ms against dense's 1021 ms — 3.1×
already. Going from 5 pairs to 25 adds only about 35% on top. So most of the price is
the fixed cost of invoking the cross-encoder at all, not the size of the window. The
cheapest configuration that keeps the one fixed question is window=14 at 3725 ms, a 12%
saving over the shipped 25.

There is no configuration of this change that is both cheap and useful. That is what
turns "expensive" into "don't ship" rather than "tune it".

---

## 8. Bonus — MMR over the reranked candidate list

`out/mmr_bonus.md`. `rag/mmr.py`.

The premise holds, in a sharper form than the brief describes. Reranked top-5 for
`gluten free brioche`:

```text
  1.   +9.028  gf-brioche             title
  2.   +8.512  gf-brioche             allergens
  3.   +8.413  gf-brioche             method
  4.   +7.877  gf-brioche             ingredients     <- the chunk with the xanthan weight
  5.   +3.879  classic-brioche        allergens
```

Not three near-copies of the same dough — **four sections of the same recipe**, with the
one section carrying the number sitting at rank 4, just outside the top 3. Part of why
they look alike to an embedder is my own Week 3 chunker, which stamps the same
`Recipe: ... (cuisine: ...)` prefix on every chunk of a card.

MMR selects iteratively, maximising `lambda * relevance - (1 - lambda) * max_similarity_to_already_picked`.
Relevance is the cross-encoder score, min-max normalised across the window so it mixes
sanely with a cosine similarity in [-1, 1]. Similarity reuses the embeddings already in
Chroma, so there is no second model and no extra inference.

### The sweep — one tuning pass, every value reported

| lambda | hit-rate@3 | mean distinct recipes in top-3 | questions missed |
|---|---|---|---|
| 1.0 (= plain rerank, control) | 11/12 | 1.50 | g09 |
| 0.9 | 11/12 | 1.50 | g09 |
| 0.8 | 11/12 | 1.67 | g09 |
| **0.7** | **11/12** | **2.00** | g09 |
| 0.5 | 11/12 | 2.08 | g09 |
| 0.3 | **10/12** | 2.75 | g09, **g02** |
| 0.0 | **10/12** | 3.00 | g09, **g02** |

### What it did, and whether I would ship it

Down to lambda 0.5, diversity is **free**: distinct recipes in the top 3 rises 1.50 →
2.08 with hit-rate@3 unmoved at 11/12. Below that the warning in the bonus comes true
exactly as advertised — at lambda 0.3, **g02 breaks**, because `xanthan for the gf
sandwich loaf` has its answer and its supporting method chunk in the *same* recipe, and a
novelty penalty strong enough to prefer variety evicts one of them for a chunk from a
different bread that does not contain the answer. MMR pushed the correct chunk out of the
top 3 in the name of variety, on a question that was passing.

**I would not ship MMR either, and the reason is not the risk — it is that there is no
benefit to buy.** At lambda 0.7 it is nearly free: hit-rate@3 unchanged, latency
unchanged to within noise (the embeddings are already stored, and the selection is a
few dozen dot products), and top-3 diversity meaningfully better. But diversity is not
a goal for this app. Every question in the golden set is a single-fact lookup with one
correct chunk, and for those the ideal top-3 is *three chunks from the right recipe* —
exactly the redundancy MMR is built to destroy. It optimises a property I do not want.

MMR is the right tool for a different product: "show me some gluten-free bread recipes",
where three near-identical brioches genuinely is a bad answer. If this app grows a
browse or recommend surface, lambda 0.7 is where I would start, and I would keep it off
the factual-lookup path.

---

## 9. Code diff — exactly one retrieval change

New files:

```
rag/rerank.py                 THE ONE CHANGE: cross-encoder rerank over the top 25
rag/mmr.py                    bonus only, not in the measured path
rag/inspect.py                inspection view (read-only, no API calls)
eval/golden_set.jsonl         the 12 questions
eval/answer_keys.json         answer-correctness keys, kept separate so the golden hash stays valid
eval/run_hitrate3.py          hit-rate@3 + p50 latency, --retriever dense|rerank
eval/run_answer_eval.py       answer-level pass + the R/G/Not-In-Corpus tally
eval/run_mmr_bonus.py         the lambda sweep
eval/run_window_sweep.py      candidate-window cost curve behind the ship decision
data/variations/card-07..12   the 6 near-duplicate recipes
```

The retrieval change itself, in full:

```python
# rag/rerank.py
def rerank_search(collection, query, k=TOP_K, where=None, candidates=RERANK_CANDIDATES):
    pool_size = max(candidates, k)
    pool = search(collection, query, k=pool_size, where=where)   # <- dense stage UNCHANGED
    if not pool:
        return []

    head = pool[:candidates]
    tail = pool[candidates:]

    scores = list(get_encoder().rerank(query, [h.text for h in head]))
    order = sorted(range(len(head)), key=lambda i: scores[i], reverse=True)

    out = []
    for new_rank, i in enumerate(order, start=1):
        out.append(replace(head[i], rank=new_rank, score=float(scores[i])))
    for offset, h in enumerate(tail, start=len(out) + 1):
        out.append(replace(h, rank=offset))     # tail keeps dense order, so whole-collection rank stays defined

    return out[:k]
```

Config added:

```python
RERANK_CANDIDATES = 25
RERANK_MODEL = "Xenova/ms-marco-MiniLM-L-6-v2"   # ONNX cross-encoder, ~80 MB, no torch
MMR_LAMBDA = 0.7                                  # bonus only
```

Existing files touched, and how:

| file | change | affects the measurement? |
|---|---|---|
| `rag/config.py` | added the three constants above | no |
| `rag/generate.py` | `answer(..., retriever="dense")` param; dense is still the default | no, dense path unchanged |
| `rag/generate.py` | 503/overloaded added to the transient-retry set, and a 503 now tries the next model instead of sleeping | no, generation only |
| `eval/run_answer_eval.py` | `contains()` made boundary-aware (the false-G bug in 0.3) | yes — it corrected a wrong label |

Nothing in `rag/store.py`, `rag/parse.py`, or either chunker was modified. The dense
retrieval path is byte-identical between the before and after runs; the reranker is
bolted on after it.

---

## 10. Reproducing this

```bash
PY=.venv/Scripts/python
$PY -m pip install -r requirements.txt      # adds fastembed for the cross-encoder

# free, no API key, retrieval only
$PY -m rag.ingest --dir data/variations --label variations   # once; append-only, refuses a second run
$PY -m rag.inspect --all --out inspection_before.md
$PY eval/run_hitrate3.py --retriever dense  --label before
$PY eval/run_hitrate3.py --retriever rerank --label after
$PY eval/run_mmr_bonus.py
$PY eval/run_window_sweep.py                                  # -> out/window_sweep.txt

# needs GEMINI_API_KEY, 12 calls each
$PY eval/run_answer_eval.py --retriever dense  --label before
$PY eval/run_answer_eval.py --retriever rerank --label after
```

### Deliverable checklist

| item | where |
|---|---|
| `golden_set.jsonl`, 12 real-style questions with known-correct chunk_ids | `eval/golden_set.jsonl`, §1 |
| Baseline hit-rate@3, recorded before any change | §2, `out/hitrate3_before.md` |
| R / G / Not-In-Corpus tally, one line of evidence each | §3, `out/answer_eval_before.md` |
| Before → after hit-rate@3 and p50 latency in one table | §5 |
| Per-question fixed / unfixed table | §6 |
| Code diff showing exactly one retrieval change | §9 |
| Shipping decision with the number behind it | §7 |
| Bonus: MMR, hit-rate@3 and diversity, ship decision | §8, `out/mmr_bonus.md` |
| Candidate-window sweep behind the ship decision | §7, `out/window_sweep.txt` |
| Inspection view used for every label | `out/inspection_before.md`, `rag/inspect.py` |
| Rejected golden set v1 (12/12) kept for audit | `eval/golden_set_v1_rejected.jsonl` |
