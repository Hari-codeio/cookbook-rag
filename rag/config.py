"""Central configuration.

Everything the two chunking strategies must SHARE lives here as a module-level
constant, so the bake-off can never accidentally vary two things at once. The
only values that differ between the two runs are the chunker-specific knobs at
the bottom, and the chunker function itself.
"""

from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# --------------------------------------------------------------------------
# Paths
# --------------------------------------------------------------------------
DATA_BASELINE = ROOT / "data" / "baseline"
DATA_NEW_DROP = ROOT / "data" / "new_drop"
OUT_DIR = ROOT / "out"
CHROMA_DIR = OUT_DIR / "chroma"
QUESTIONS_PATH = ROOT / "eval" / "questions.json"
QUESTIONS_LOCK = OUT_DIR / "questions.lock.json"

# --------------------------------------------------------------------------
# Embedding — HELD FIXED ACROSS BOTH CHUNKERS.
#
# This is the single most important line in the experiment. The rubric warns
# against changing the chunker and the embedding model in the same run, so the
# embedder is a constant, is asserted identical at query time, and is printed
# into every search dump header as evidence.
#
# chromadb's DefaultEmbeddingFunction is all-MiniLM-L6-v2 running under
# onnxruntime: 384 dims, no PyTorch dependency.
# --------------------------------------------------------------------------
EMBED_MODEL = "all-MiniLM-L6-v2 (chromadb ONNX DefaultEmbeddingFunction)"
EMBED_DIM = 384

# Cosine distance, so reported scores are comparable and bounded.
HNSW_SPACE = "cosine"

# Retrieval defaults — also held fixed across strategies.
TOP_K = 5

# --------------------------------------------------------------------------
# Week 4: THE ONE RETRIEVAL CHANGE — cross-encoder rerank over the top 25.
#
# Chosen from the failure tally, not from taste. Both R failures had the
# correct chunk inside the top 25 already (ranks 14 and 13 of 94), so
# reordering that window can reach both. See rag/rerank.py for why BM25+RRF
# was rejected: g09's key term "hydration" appears nowhere on the target
# card, so a lexical matcher has no bridge to cross.
#
# The dense stage is untouched. Same collection, same embedder, same cosine
# space. The reranker only reorders what dense retrieval already returned.
# --------------------------------------------------------------------------
RERANK_CANDIDATES = 25
RERANK_MODEL = "Xenova/ms-marco-MiniLM-L-6-v2"  # ONNX cross-encoder, ~80 MB, no torch

# Week 4 BONUS: MMR over the reranked window. 1.0 = pure relevance (identical
# to plain reranking), 0.0 = pure novelty. Tuned in one sweep, see results.md.
MMR_LAMBDA = 0.7


# --------------------------------------------------------------------------
# Strategy A: "baseline" — the chunker the app already had.
#
# A naive fixed-size character window with overlap. It has no idea what a
# markdown table is, so it will happily cut between a recipe title and the
# ingredient rows underneath it, or leave a "7 g | 0.7%" row stranded in a
# chunk that never names the recipe. That failure is the thing we are measuring.
# --------------------------------------------------------------------------
BASELINE_CHUNK_CHARS = 500
BASELINE_OVERLAP_CHARS = 80

# --------------------------------------------------------------------------
# Strategy B: "structure" — structure-aware.
#
# Splits on parsed document structure, never inside a table row, and re-prepends
# the recipe title + the table's column header to every ingredient chunk.
# The row budget is applied BEFORE the prefix is added, so the repeated prefix
# can never push rows out of a chunk.
# --------------------------------------------------------------------------
STRUCTURE_TABLE_ROWS_PER_CHUNK = 8
STRUCTURE_PROSE_CHARS = 700

STRATEGIES = ("baseline", "structure")

COLLECTION_NAMES = {
    "baseline": "recipes_baseline",
    "structure": "recipes_structure",
}

# --------------------------------------------------------------------------
# Generation
#
# GEN_PROVIDER selects the answering model. Retrieval never touches it — the
# whole hit-rate measurement runs with no key and no provider at all, so
# switching this cannot move any number in section 2 of results.md.
#
# "gemini"    Google AI Studio, free tier, no card required. The default.
# "anthropic" Claude. Needs paid API credit (a Claude Pro/Max subscription
#             does NOT include API credit — they are billed separately).
# --------------------------------------------------------------------------
GEN_PROVIDER = os.environ.get("GEN_PROVIDER", "gemini").strip().lower()

# Tried in order; the first model this API key can actually reach is used, so a
# model being retired does not break the run.
#
# Pinned rather than using the "gemini-flash-latest" alias, because the alias can
# silently move to a different model and the transcripts in results.md are
# supposed to be reproducible. The alias is kept last as a safety net.
#
# Verified reachable on a fresh free-tier key: gemini-2.5-flash and
# gemini-2.5-flash-lite are listed by models.list() but return 404 "no longer
# available to new users", so they are deliberately absent from this list.
GEMINI_MODELS = (
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-3.1-flash-lite",
    "gemini-flash-latest",
)

# Claude, used only when GEN_PROVIDER=anthropic.
ANTHROPIC_MODEL = "claude-opus-5"
GEN_EFFORT = "medium"

GEN_MAX_TOKENS = 4096

# Free-tier rate limits are per-minute, so a run of 9 calls can trip one.
# Retry rather than losing the run half way through.
GEN_RETRY_ATTEMPTS = 4
GEN_RETRY_WAIT_SECONDS = 20

# The exact token the app emits when it will not answer. The prompt gate asks
# for it and the code gate falls back to it, so every refusal in the transcripts
# is byte-identical and greppable.
REFUSAL_TOKEN = "INSUFFICIENT_CONTEXT"


def _read_env(name: str) -> str | None:
    """Environment first, then a local .env file at the project root."""
    value = os.environ.get(name)
    if value and value.strip():
        return value.strip()
    env_file = ROOT / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key_name, _, raw = line.partition("=")
            if key_name.strip() == name:
                cleaned = raw.strip().strip('"').strip("'")
                if cleaned:
                    return cleaned
    return None


def anthropic_api_key() -> str | None:
    return _read_env("ANTHROPIC_API_KEY")


def gemini_api_key() -> str | None:
    """AI Studio calls it GEMINI_API_KEY; GOOGLE_API_KEY is accepted too."""
    return _read_env("GEMINI_API_KEY") or _read_env("GOOGLE_API_KEY")


def api_key() -> str | None:
    """The key for whichever provider GEN_PROVIDER selects."""
    if GEN_PROVIDER == "anthropic":
        return anthropic_api_key()
    return gemini_api_key()


def gen_model_label() -> str:
    """What to print in the write-up as the answering model."""
    if GEN_PROVIDER == "anthropic":
        return ANTHROPIC_MODEL
    return GEMINI_MODELS[0]


# Kept so existing imports of GEN_MODEL keep working.
GEN_MODEL = gen_model_label()
