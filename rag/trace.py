"""Trace log for the answering path.

Before this week the only record of a run was a markdown transcript in ``out/``
(``generation.md``, ``answer_eval_before.md``). Those are readable but not
replayable: they carry the question, the top-k chunk_ids and the *rendered*
answer, and nothing else. Missing were the prompt version, the retrieval
scores, the model parameters, the raw model output, the token usage, and the
timing. You cannot re-run a markdown table.

This module writes one JSON object per answered question to ``out/traces.jsonl``
containing everything ``eval/replay_trace.py`` needs to reconstruct the call
without touching the vector store:

    trace_id        stable id, the unit the random sample draws from
    ts              UTC timestamp
    prompt          version label, sha256, and the full system prompt text
    request         query, strategy, retriever, k, metadata filter
    retrieval       embedder, collection, and every hit with rank/score/text
    context.sha256  fingerprint of the exact context string that was sent
    model           provider, model name, and every generation parameter
    output.raw_text the model's response BEFORE any parsing or gating
    gates           what the two refusal gates did
    usage           tokens, stop reason, wall-clock latency

The context TEXT is deliberately not stored. It is rebuilt from the hits at
replay time and checked against ``context.sha256``, which proves the stored
hits are sufficient to reconstruct the call rather than merely asserting it.

Writing is append-only and best-effort: a tracing failure must never take down
an answer, so :func:`write` swallows its own errors and records them in
``out/trace_errors.log``.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

from .config import OUT_DIR

TRACE_SCHEMA = "1.0"
TRACE_PATH = OUT_DIR / "traces.jsonl"
TRACE_ERROR_LOG = OUT_DIR / "trace_errors.log"


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def new_trace_id() -> str:
    """Opaque and unique. Sorting by it is stable, which the sampler relies on."""
    return "tr_" + uuid.uuid4().hex[:12]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


_GIT_SHA: str | None = None


def git_sha() -> str:
    """Short HEAD sha, so a trace names the code that produced it."""
    global _GIT_SHA
    if _GIT_SHA is None:
        try:
            _GIT_SHA = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                cwd=str(Path(__file__).resolve().parent.parent),
                capture_output=True,
                text=True,
                timeout=10,
            ).stdout.strip() or "unknown"
        except Exception:  # noqa: BLE001 - tracing must never raise
            _GIT_SHA = "unknown"
    return _GIT_SHA


def write(record: dict[str, Any], path: Path | None = None) -> str | None:
    """Append one trace. Returns the trace_id, or None if tracing failed."""
    path = path or TRACE_PATH
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        line = json.dumps(record, ensure_ascii=False, sort_keys=False)
        with path.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")
        return str(record.get("trace_id"))
    except Exception as exc:  # noqa: BLE001 - an answer must survive a bad disk
        try:
            TRACE_ERROR_LOG.parent.mkdir(parents=True, exist_ok=True)
            with TRACE_ERROR_LOG.open("a", encoding="utf-8") as fh:
                fh.write(f"{utc_now()}\t{type(exc).__name__}\t{exc}\n")
        except Exception:  # noqa: BLE001
            pass
        return None


def read_all(path: Path | None = None) -> list[dict[str, Any]]:
    return list(iter_traces(path))


def iter_traces(path: Path | None = None) -> Iterator[dict[str, Any]]:
    path = path or TRACE_PATH
    if not path.exists():
        return
    with path.open("r", encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError as exc:
                raise RuntimeError(f"{path}:{lineno} is not valid JSON: {exc}") from exc


def load_trace(trace_id: str, path: Path | None = None) -> dict[str, Any]:
    for rec in iter_traces(path):
        if rec.get("trace_id") == trace_id:
            return rec
    raise KeyError(f"no trace with trace_id={trace_id!r} in {path or TRACE_PATH}")


def file_fingerprint(path: Path | None = None) -> dict[str, Any]:
    """Size, line count and sha256 of the trace log, for the write-up."""
    path = path or TRACE_PATH
    if not path.exists():
        return {"path": str(path), "exists": False}
    raw = path.read_bytes()
    return {
        "path": str(path),
        "exists": True,
        "bytes": len(raw),
        "lines": raw.count(b"\n"),
        "sha256": hashlib.sha256(raw).hexdigest(),
    }


def tracing_enabled() -> bool:
    """``RAG_TRACE=0`` turns it off; anything else leaves it on."""
    return os.environ.get("RAG_TRACE", "1").strip() not in {"0", "false", "off", ""}
