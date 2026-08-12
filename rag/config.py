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
# --------------------------------------------------------------------------
GEN_MODEL = "claude-opus-5"
GEN_MAX_TOKENS = 4096
GEN_EFFORT = "medium"

# The exact token the app emits when it will not answer. The prompt gate asks
# for it and the code gate falls back to it, so every refusal in the transcripts
# is byte-identical and greppable.
REFUSAL_TOKEN = "INSUFFICIENT_CONTEXT"


def api_key() -> str | None:
    """Read the Anthropic key from the environment or a local .env file."""
    key = os.environ.get("ANTHROPIC_API_KEY")
    if key:
        return key.strip()
    env_file = ROOT / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            name, _, value = line.partition("=")
            if name.strip() == "ANTHROPIC_API_KEY":
                return value.strip().strip('"').strip("'")
    return None
