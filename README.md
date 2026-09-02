# Week 3 practical — Task Set B: recipes RAG, chunking bake-off

A retrieval-augmented recipe app that indexes the same cards under **two chunking
strategies** and measures which one actually finds the answer, plus a grounded answerer
that refuses what it cannot source.

## Setup

```bash
# Python 3.13
py -3.13 -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt

# Only needed for the generation step:
cp .env.example .env      # then put your GEMINI_API_KEY in it
```

Retrieval is entirely local — `chromadb`'s ONNX `all-MiniLM-L6-v2` embedder, no API key and
no PyTorch. Only `rag.generate` / `eval/run_generation.py` need a key.

**Answering model.** `GEN_PROVIDER` in `rag/config.py` selects it, default `gemini`:

| provider | model | key | cost |
|---|---|---|---|
| `gemini` (default) | `gemini-3.6-flash`, with newer fallbacks | `GEMINI_API_KEY` from [AI Studio](https://aistudio.google.com/apikey) | free tier, no card |
| `anthropic` | `claude-opus-5` | `ANTHROPIC_API_KEY` | needs paid API credit — a Claude Pro/Max subscription does **not** include it |

Switching provider cannot move any number in the chunking bake-off, because retrieval never
calls a provider. Both refusal gates work identically on either path.

## The experiment

| | Strategy A — `baseline` | Strategy B — `structure` |
|---|---|---|
| How it cuts | fixed 500-char window, 80-char overlap, snapped to whitespace | on parsed document structure |
| Knows about tables? | no | yes — groups whole rows, never cuts inside one |
| Ingredient chunks carry | whatever fell in the window | recipe title **+** table header row, re-prepended to every chunk |

**Held fixed across both**: the embedding model, top-k, the query strings, and the 8
questions. The embedder is stamped into each Chroma collection at creation and re-asserted
at query time, so a comparison across two different embedders cannot happen silently.

## Commands

```bash
PY=.venv/Scripts/python

# 0. See what the parser makes of a set of cards, before embedding anything
$PY -m rag.inspect_cards --dir data/new_drop

# 1. Prove the structural contract and measure the baseline's damage
$PY eval/test_chunk_invariants.py --dir data/new_drop

# 2. Ingest — APPEND-ONLY, reads only the directory you name
$PY -m rag.ingest --dir data/baseline --label baseline-corpus   # the pre-existing index
$PY -m rag.ingest --dir data/new_drop --label new-drop          # the 6 new cards ONLY

# 3. Search only (no LLM on this path at all)
$PY -m rag.search "how much salt is in the 2kg sourdough" --strategy both
$PY -m rag.search "..." --filter-tag vegan

# 4. The measurements
$PY eval/run_hitrate.py         # hit-in-top-5 for both chunkers, per-question record
$PY eval/run_filter_demo.py     # dietary_tags filter changing top-1, both lists + scores
$PY eval/run_generation.py      # 3 cited answers + 3 forced refusals   [needs API key]

# 5. One-off grounded answer
$PY -m rag.generate "how much salt is in the 2kg sourdough?" --show-context

# 6. Week 5 — traffic, traces, sampling, replay
$PY eval/run_traffic.py         # run the traffic pool, writing out/traces.jsonl [needs API key]
$PY eval/sample_traces.py       # draw the sample to open-code
$PY eval/trace_summary.py       # opinion-free descriptive summary
$PY eval/replay_trace.py --trace tr_xxxxxxxx   # replay one trace verbatim

# 7. Week 6 — the eval, and whether its judge can be trusted
$PY eval/test_assertions.py     # mutate a real output 7 ways, prove each check fires
$PY eval/run_eval.py --judge eval/judge_v2.txt   # THE one command: assertions,
                                                 # judge, pass rate by mode, agreement

# 7b. Week 6 bonus — RAGAS faithfulness + context precision
$PY eval/build_ragas_reference.py   # reconcile the 3 blind reference maps (no API)
$PY eval/run_ragas.py               # the two metrics + the free grounding check
```

The judge and the RAGAS metrics are both cached on the sha256 of their prompt and
their inputs, so re-running costs no API calls and cannot quietly return different
numbers. Editing a prompt changes the key and forces a genuine re-run.

Everything writes to `out/`: `ingest_*.md`, `search_dump_baseline.md`,
`search_dump_structure.md`, `hitrate.md`, `filter_demo.md`, `generation.md`.

## How a "hit" is decided

Not by section label — the two chunkers assign those differently, so scoring on them would
compare labels rather than retrieval. A hit requires a chunk in the top-k that

1. belongs to the **expected `recipe_id`**, and
2. **contains the answer strings** declared in `eval/questions.json`
   (`answer_must_contain`), matched case-insensitively and whitespace-tolerantly.

The questions are written from the cards **before** any search is run. `run_hitrate.py`
hashes `questions.json`, locks the hash on first run, and refuses to run against an edited
file unless you explicitly pass `--relock` — so the numbers cannot quietly become a measure
of question-tuning.

`hit-in-top-5` is the headline number the brief asks for. `hit@1`, `hit@3` and mean
reciprocal rank are reported next to it because on a small corpus of short cards top-5 can
cover most of a card whichever way it was cut, and both strategies then tie at 8/8 — a tie
that hides a real difference in rank.

## Refusal is forced, not suggested

`rag/generate.py` has two independent gates:

1. **Prompt + schema.** The system prompt forbids outside knowledge and forbids stating any
   quantity not written verbatim in context. The response is additionally constrained by
   `output_config.format` to a JSON schema with a required `can_answer` boolean, so the
   model cannot dodge the question of whether it had the facts. There is no
   "use your best judgement" clause — that sentence is how an invented gram weight ends up
   in a reader's dough.
2. **Code.** Every cited `chunk_id` is checked against the set actually retrieved for that
   question, then resolved against the store. A citation that was not retrieved, or that
   does not resolve, discards the answer and emits the refusal instead.

`--no-code-gate` disables gate 2 so the write-up can show gate 1 refusing on its own.

## Metadata

Every chunk carries `chunk_id`, `source_file`, `recipe_id`, `cuisine`, `dietary_tags`,
`title`, `section`, `strategy`, `char_start`, `char_end`. Ingest **hard-fails** if any chunk
lacks `source_file` or `recipe_id`, and (by default) if a card omits `cuisine` or
`dietary_tags`.

Chroma metadata values must be scalars, so `dietary_tags` is stored twice: as a
pipe-delimited string for display and citation, and exploded into one boolean per tag
(`tag_vegan: True`) so `where={"tag_vegan": True}` is a real indexed filter applied *before*
ranking rather than a substring hack applied after.

## Layout

```
rag/
  config.py              every shared constant, incl. the pinned embedder
  parse.py               tolerant card parser (frontmatter or inline; pipe or aligned tables)
  chunkers/baseline.py   strategy A
  chunkers/structure_aware.py  strategy B
  store.py               Chroma collections, cosine search, metadata filtering
  ingest.py              append-only ingest + proof block
  search.py              search-only CLI
  generate.py            grounded answerer, two gates
eval/
  questions.json         the 8 questions, with known-correct recipe/section
  test_chunk_invariants.py   asserts strategy B's contract; quantifies A's damage
  run_hitrate.py         the two numbers, with the per-question record
  run_filter_demo.py     unfiltered vs filtered, ranked by usefulness of the demo
  run_generation.py      cited answers, refusals, and the bonus comparison
data/baseline/           stand-in "already indexed" corpus (see results.md)
data/new_drop/           the 6 supplied cards go here
```
