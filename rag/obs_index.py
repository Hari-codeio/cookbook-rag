"""Week 11: a searchable index over the trace log, for the support drill.

A JSONL file is a fine place to WRITE traces and a terrible place to FIND one.
A complaint arrives as a sentence, not a trace_id, so finding the answer means
slicing: by time, by user, by prompt version, by input type, by cost, and by
words in what the user typed AND in what the app answered. This module builds
one SQLite file with a row per request, a row per span, and an FTS5 full-text
index over both the request and the answer.

    python -m rag.obs_index                        # (re)build from out/w11/traces.jsonl
    python -m rag.obs_index --log out/w11/drill/traces.jsonl

The index is DERIVED. It is rebuilt from the log whenever the log's size or
mtime changes, so it can never disagree with the log for long, and deleting it
loses nothing. That is also why it is gitignored.

WHAT IS INDEXED, AND THE ONE THING THAT IS NOT (YET)
  requests   ts, day, user_id, session_id, input_type, allergen, recipe_id,
             prompt_version, model, status, latency_ms, model_calls, tokens,
             cost_usd, rate_limited
  spans      every span, with stage, latency, tokens, cost
  fts        request_text and answer_text, porter-stemmed

THE WEEK 11 BONUS: the field whose absence cost the drill its time. Drill 1
was spent reading 22 swap lines by eye, because nothing in the index answered
"did this answer put back the allergen the user asked to avoid?". These
DERIVED columns answer it, computed from the logged answer with the same
deterministic check the suite grades with (rag.contract.allergen_residue), so
every old trace is backfilled the moment the index rebuilds:

  asked             allergens the user's OWN WORDS ask to avoid ("no dairy",
                    "lactose free", "milk allergy"), read from the request,
                    not from the planner
  missed            asked allergens the planner did NOT pick: the planner
                    dropped what the user asked for
  residue_swaps     replacements that carry an avoided allergen
  residue_rows      ingredient rows that still carry it
  residue_method    method phrases that still tell the cook to use it
  residue           1 if any of the three is non-empty

`eval/drill.py slice --residue swap` is then one query, not a reading task.
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
from pathlib import Path
from typing import Any

from rag import obs

# What a request's own words ask to avoid. Phrases, not bare nouns, so "Make
# the milk kefir 2x" is not read as a dairy-free request.
ASKED: dict[str, str] = {
    "contains-dairy": r"\bdairy|\blactose|\bmilk[- ]free|\bmilk allerg|\bno (butter|milk|cream)\b|\bwithout (any )?(milk|butter|cream)\b",
    "contains-egg": r"\begg[- ]free|\bno eggs?\b|\bwithout (any )?eggs?\b|\begg allerg|\banything with egg",
    "contains-gluten": r"\bgluten|\bcoeliac|\bceliac",
    "contains-soy": r"\bsoy[- ]free|\bno soy\b|\bwithout (any )?soy\b",
    "contains-sesame": r"\bsesame[- ]free|\bno sesame\b|\bwithout sesame\b|\bremove sesame\b|\banything containing sesame",
    "contains-fish": r"\bfish[- ]free|\bfree of fish\b|\bno fish\b|\bwithout (the )?fish\b",
    "contains-shellfish": r"\bshellfish",
    "contains-alcohol": r"\balcohol|\bwithout (the )?wine\b|\bno wine\b",
    "contains-peanut": r"\bpeanut|\bnut[- ]free|\bnut allerg",
}


def asked_allergens(text: str) -> list[str]:
    low = text.lower()
    return sorted(a for a, pat in ASKED.items() if re.search(pat, low))


def residue_for(rec: dict[str, Any]) -> dict[str, Any]:
    """Residue against every allergen the user asked about OR the planner chose."""
    from rag.contract import allergen_residue

    req = rec.get("request") or {}
    answer = (rec.get("output") or {}).get("answer") or {}
    asked = asked_allergens(req.get("text", ""))
    targets = sorted(set(asked) | ({req["allergen"]} if req.get("allergen") else set()))
    swaps, rows, method = [], [], []
    for a in targets if answer else []:
        r = allergen_residue(answer, a)
        swaps += [f"{a}: {x}" for x in r["swaps"]]
        rows += [f"{a}: {x}" for x in r["ingredients"]]
        method += [f"{a}: {x}" for x in r["method"]]
    missed = [a for a in asked if a != req.get("allergen")]
    return {"asked": ",".join(asked), "missed": ",".join(missed), "residue_swaps": " | ".join(swaps),
            "residue_rows": " | ".join(rows), "residue_method": " | ".join(method),
            "residue": int(bool(swaps or rows or method))}

SCHEMA = """
CREATE TABLE meta (k TEXT PRIMARY KEY, v TEXT);
CREATE TABLE requests (
    trace_id TEXT PRIMARY KEY, ts TEXT, day TEXT, user_id TEXT, session_id TEXT,
    input_type TEXT, allergen TEXT, recipe_id TEXT, prompt_version TEXT, model TEXT,
    status TEXT, latency_ms REAL, model_calls INTEGER, tokens INTEGER, cost_usd REAL,
    rate_limited INTEGER, request_text TEXT, answer_text TEXT,
    asked TEXT, missed TEXT, residue_swaps TEXT, residue_rows TEXT, residue_method TEXT, residue INTEGER
);
CREATE TABLE spans (
    trace_id TEXT, span_id TEXT, parent_id TEXT, name TEXT, stage TEXT, start_ms REAL,
    latency_ms REAL, input_tokens INTEGER, output_tokens INTEGER, cost_usd REAL, status TEXT
);
CREATE VIRTUAL TABLE requests_fts USING fts5(
    trace_id UNINDEXED, request_text, answer_text, tokenize='porter unicode61'
);
CREATE INDEX ix_ts ON requests(ts);
CREATE INDEX ix_user ON requests(user_id);
CREATE INDEX ix_type ON requests(input_type, allergen);
CREATE INDEX ix_prompt ON requests(prompt_version);
CREATE INDEX ix_cost ON requests(cost_usd);
CREATE INDEX ix_residue ON requests(residue);
"""


def db_path_for(log: Path) -> Path:
    return log.with_name(log.stem + ".index.sqlite")


INDEX_VERSION = "3"  # bump when the schema changes, so an old index file is rebuilt


def _fingerprint(log: Path) -> str:
    st = log.stat()
    return f"v{INDEX_VERSION}:{st.st_size}:{st.st_mtime_ns}"


def row_for(rec: dict[str, Any]) -> dict[str, Any]:
    req = rec.get("request") or {}
    out = rec.get("output") or {}
    tot = rec.get("totals") or {}
    used = (rec.get("model") or {}).get("used") or []
    return {
        "trace_id": rec["trace_id"],
        "ts": rec.get("ts", ""),
        "day": str(rec.get("ts", ""))[:10],
        "user_id": (rec.get("user") or {}).get("user_id", ""),
        "session_id": (rec.get("user") or {}).get("session_id", ""),
        "input_type": req.get("input_type", ""),
        "allergen": req.get("allergen", ""),
        "recipe_id": (rec.get("retrieval") or {}).get("used", ""),
        "prompt_version": rec.get("prompt_version", ""),
        "model": ",".join(used),
        "status": rec.get("status", ""),
        "latency_ms": tot.get("latency_ms", 0.0),
        "model_calls": tot.get("model_calls", 0),
        "tokens": int(tot.get("input_tokens", 0)) + int(tot.get("output_tokens", 0)),
        "cost_usd": tot.get("cost_usd", 0.0),
        "rate_limited": tot.get("rate_limited", 0),
        "request_text": req.get("text", ""),
        "answer_text": out.get("answer_text") or obs.flatten_answer(out.get("answer")),
        **residue_for(rec),
    }


def build(log: Path, db: Path | None = None) -> Path:
    db = db or db_path_for(log)
    if db.exists():
        db.unlink()
    con = sqlite3.connect(db)
    con.executescript(SCHEMA)
    n = 0
    for rec in obs.iter_traces(log):
        row = row_for(rec)
        cols = ", ".join(row)
        con.execute(f"INSERT INTO requests ({cols}) VALUES ({', '.join('?' * len(row))})", list(row.values()))
        con.execute("INSERT INTO requests_fts (trace_id, request_text, answer_text) VALUES (?, ?, ?)",
                    (row["trace_id"], row["request_text"], row["answer_text"]))
        for s in rec.get("spans") or []:
            con.execute("INSERT INTO spans VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                        (row["trace_id"], s["span_id"], s.get("parent_id"), s["name"], s["stage"],
                         s["start_ms"], s["latency_ms"], s["input_tokens"], s["output_tokens"],
                         s["cost_usd"], s["status"]))
        n += 1
    con.execute("INSERT INTO meta VALUES ('log', ?), ('fingerprint', ?), ('rows', ?)",
                (str(log), _fingerprint(log), str(n)))
    con.commit()
    con.close()
    return db


def connect(log: Path | None = None) -> sqlite3.Connection:
    """Open the index for this log, rebuilding it first if the log has moved on."""
    log = Path(log or obs.trace_path())
    if not log.exists():
        raise SystemExit(f"no trace log at {log}")
    db = db_path_for(log)
    fresh = False
    if db.exists():
        try:
            con = sqlite3.connect(db)
            got = con.execute("SELECT v FROM meta WHERE k='fingerprint'").fetchone()
            con.close()
            fresh = bool(got) and got[0] == _fingerprint(log)
        except sqlite3.DatabaseError:
            fresh = False
    if not fresh:
        build(log, db)
    con = sqlite3.connect(db)
    con.row_factory = sqlite3.Row
    return con


def main() -> None:
    ap = argparse.ArgumentParser(description="Build the trace index.")
    ap.add_argument("--log", default=str(obs.trace_path()))
    args = ap.parse_args()
    db = build(Path(args.log))
    con = sqlite3.connect(db)
    n = con.execute("SELECT COUNT(*) FROM requests").fetchone()[0]
    s = con.execute("SELECT COUNT(*) FROM spans").fetchone()[0]
    print(f"indexed {n} requests, {s} spans -> {db}")


if __name__ == "__main__":
    main()
