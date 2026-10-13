"""Week 11: one trace per request, made of spans, for the production path.

WHY THIS EXISTS. The app Week 10 decided to keep is the kitchen squad
(rag/squad.py). Until now it wrote NOTHING per request. Its only record was
stdout, a race cache, or a .txt someone saved by hand (out/squad_demo.txt). The
Week 5 trace log (rag/trace.py, out/traces.jsonl) only ever covered the older
single-shot paths. So a complaint about a squad answer had no log to search.

WHAT A TRACE HOLDS. Everything a support drill can slice on, and everything a
replay needs:

    trace_id, ts            the unit you find, and when it happened (UTC)
    user, session           who asked; the "user" slice
    request.text            what they typed (indexed for search)
    request.input_type      allergen-swap / scale-only / unresolved; the "input type" slice
    release, prompts        which prompt version answered; the "prompt version" slice
    retrieval.context_ids   which recipe cards the answer was built from
    spans[]                 one per step: stage, start, latency, tokens, cost, model
    totals, cost_by_stage   per request; the "cost outlier" slice
    output.answer           the answer the user saw (indexed for search)

SPANS, NOT ONE LUMP. A request is a tree:

    request
      plan                       generation    1 model call
      recipe_search              retrieval     MCP, no model
      scale_recipe               tool          MCP, no model
      allergen_worker            worker        container
        lap 1                    generation
        get_allergen_profile     tool
        lap 2                    generation
      substitution_worker        worker        container
        ...
      synthesise                 generation

Only LEAF spans carry cost, so summing leaves by stage gives the
retrieval / generation / tool split without double counting the containers.

Writing is append-only and best-effort, like rag/trace.py: a logging failure
must never take down an answer, so write() swallows its own errors into
out/w11/trace_errors.log.
"""

from __future__ import annotations

import json
import os
import time
import uuid
from contextlib import contextmanager
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

from rag.config import OUT_DIR
from rag.llm import USD_PER_1M_INPUT, USD_PER_1M_OUTPUT, usd

TRACE_SCHEMA = "2.0"
W11_DIR = OUT_DIR / "w11"
ERROR_LOG = W11_DIR / "trace_errors.log"

# The stages the cost report splits on. "worker" is a container: it has
# children, carries no cost of its own, and is excluded from stage sums.
STAGES = ("retrieval", "generation", "tool")
CONTAINER = "worker"


def trace_path() -> Path:
    """OBS_TRACE_PATH lets the suite and the drill write somewhere else, so an
    eval run or a planted record never lands in the production log."""
    return Path(os.environ.get("OBS_TRACE_PATH") or (W11_DIR / "traces.jsonl"))


def new_trace_id() -> str:
    return "tr_" + uuid.uuid4().hex[:12]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass
class Span:
    span_id: str
    name: str
    stage: str  # retrieval | generation | tool | worker
    start_ms: float  # offset from the start of the request
    latency_ms: float = 0.0
    parent_id: str | None = None
    status: str = "ok"
    model: str = ""
    prompt_version: str = ""
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0
    attrs: dict[str, Any] = field(default_factory=dict)

    def tokens(self, input_tokens: int, output_tokens: int) -> None:
        self.input_tokens = int(input_tokens or 0)
        self.output_tokens = int(output_tokens or 0)
        self.cost_usd = usd(self.input_tokens, self.output_tokens)


class Recorder:
    """Collects the spans of ONE request. Times are offsets from its start."""

    def __init__(self) -> None:
        self.t0 = time.perf_counter()
        self.spans: list[Span] = []
        self._n = 0

    def now_ms(self) -> float:
        return (time.perf_counter() - self.t0) * 1000.0

    def _id(self) -> str:
        self._n += 1
        return f"s{self._n:02d}"

    @contextmanager
    def span(self, name: str, stage: str, parent: Span | None = None, **attrs: Any) -> Iterator[Span]:
        sp = Span(self._id(), name, stage, round(self.now_ms(), 1),
                  parent_id=parent.span_id if parent else None, attrs=dict(attrs))
        self.spans.append(sp)
        try:
            yield sp
        except Exception as exc:
            sp.status = f"error: {type(exc).__name__}: {exc}"
            raise
        finally:
            sp.latency_ms = round(self.now_ms() - sp.start_ms, 1)

    def add(self, name: str, stage: str, start_ms: float, latency_ms: float,
            parent: Span | None = None, **fields: Any) -> Span:
        """A span measured somewhere else (a lap inside the agent loop), placed
        on this request's clock after the fact."""
        sp = Span(self._id(), name, stage, round(start_ms, 1), round(latency_ms, 1),
                  parent_id=parent.span_id if parent else None)
        for k, v in fields.items():
            setattr(sp, k, v)
        self.spans.append(sp)
        return sp


def stage_totals(spans: list[dict[str, Any]] | list[Span]) -> dict[str, dict[str, Any]]:
    """Sum LEAF spans by stage. A container's cost is its children's cost, so
    adding both would count every worker twice."""
    rows = [asdict(s) if isinstance(s, Span) else s for s in spans]
    out = {st: {"spans": 0, "model_calls": 0, "latency_ms": 0.0, "input_tokens": 0,
                "output_tokens": 0, "cost_usd": 0.0} for st in STAGES}
    for s in rows:
        if s["stage"] not in out:
            continue
        t = out[s["stage"]]
        t["spans"] += 1
        t["model_calls"] += 1 if s["stage"] == "generation" else 0
        t["latency_ms"] = round(t["latency_ms"] + s["latency_ms"], 1)
        t["input_tokens"] += s["input_tokens"]
        t["output_tokens"] += s["output_tokens"]
        t["cost_usd"] = round(t["cost_usd"] + s["cost_usd"], 8)
    return out


def flatten_answer(answer: dict[str, Any] | None) -> str:
    """The answer as ONE searchable string, in the order a user reads it.

    The complaint describes the OUTPUT ("it recommended a dairy-free swap that
    wasn't"), so the output has to be searchable, not just the request.
    Indexing only the input is the mistake the brief warns costs four of the
    five minutes.
    """
    if not answer:
        return ""
    parts = [str(answer.get("title") or "")]
    for ing in answer.get("ingredients") or []:
        if isinstance(ing, dict):
            parts.append(f"{ing.get('ingredient') or ing.get('name')}: {ing.get('amount')}")
    for s in answer.get("substitutions") or []:
        if isinstance(s, dict):
            parts.append(f"swap {s.get('from')} -> {s.get('to')} ({s.get('reason') or ''})")
    parts.append(str(answer.get("method") or ""))
    parts.append(str(answer.get("unsupported") or ""))
    return "\n".join(p for p in parts if p.strip())


def pricing() -> dict[str, Any]:
    """Stamped into every trace, so a cost figure always says what it assumed."""
    return {"usd_per_1m_input": USD_PER_1M_INPUT, "usd_per_1m_output": USD_PER_1M_OUTPUT,
            "source": "ai.google.dev/pricing, gemini-3.1-flash-lite paid tier, checked 2026-10-13",
            "note": "free tier invoices $0; this is the paid-tier cost of the same tokens"}


def write(record: dict[str, Any], path: Path | None = None) -> str | None:
    """Append one trace. Returns the trace_id, or None if logging failed."""
    path = path or trace_path()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
        return str(record.get("trace_id"))
    except Exception as exc:  # noqa: BLE001 - an answer must survive a bad disk
        try:
            ERROR_LOG.parent.mkdir(parents=True, exist_ok=True)
            with ERROR_LOG.open("a", encoding="utf-8") as fh:
                fh.write(f"{utc_now()}\t{type(exc).__name__}\t{exc}\n")
        except Exception:  # noqa: BLE001
            pass
        return None


def iter_traces(path: Path | None = None) -> Iterator[dict[str, Any]]:
    path = path or trace_path()
    if not path.exists():
        return
    with path.open("r", encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, start=1):
            if line.strip():
                try:
                    yield json.loads(line)
                except json.JSONDecodeError as exc:
                    raise RuntimeError(f"{path}:{lineno} is not valid JSON: {exc}") from exc


def load(trace_id: str, path: Path | None = None) -> dict[str, Any]:
    for rec in iter_traces(path):
        if rec.get("trace_id") == trace_id:
            return rec
    raise KeyError(f"no trace {trace_id!r} in {path or trace_path()}")


def tracing_enabled() -> bool:
    return os.environ.get("RAG_TRACE", "1").strip() not in {"0", "false", "off", ""}
