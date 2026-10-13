"""Week 11: the SQUADMATE's half of the drill. Plant one bad answer in a copy of the log.

    python eval/w11_plant.py --random                    # pick a dairy-free answer, make one swap dairy
    python eval/w11_plant.py --from-trace tr_x --swap-to "Ghee" --reason "ghee has no milk solids"
    python eval/w11_plant.py --random --append           # bonus: a SECOND plant, same drill copy
    python eval/w11_plant.py --random --receipt          # also print the planted trace_id (planter's eyes only)

What it does, in order:
  1. copies the production log (out/w11/traces.jsonl) to out/w11/drill/traces.jsonl,
     stripping test-harness fields (meta.pool_id, meta.pool_sha256) from EVERY
     record, so the copy only carries what production would carry
  2. takes a real dairy-free answer and clones it as a new request: new
     trace_id, a different existing user, a time inside the traffic window,
     span latencies jittered so no two traces share exact timings
  3. corrupts ONE substitution so the replacement is itself dairy, in the
     answer, the ingredient list and the substitution worker's report
  4. writes a SEAL: salt + sha256(salt:trace_id). eval/drill.py `found` can
     check a candidate against it; nobody can read the trace_id off it

The production log is never written. The planted record exists only in the
drill copy, which is what makes it safe to commit the production log as-is.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import random
import re
import secrets
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from rag import obs  # noqa: E402

PROD = obs.W11_DIR / "traces.jsonl"
DRILL_DIR = obs.W11_DIR / "drill"
DRILL_LOG = DRILL_DIR / "traces.jsonl"
SEAL = DRILL_DIR / "plant.sealed.json"
HARNESS_META = ("pool_id", "pool_sha256")

# The replacement a careless rewrite reaches for, keyed on what it replaces,
# with the wrong belief that makes it look dairy-free. Every one is dairy.
DECOYS = (
    (r"butter|ghee", "Ghee", "Clarified, so the milk solids are gone: a dairy-free fat with the same richness."),
    (r"cream", "Creme fraiche", "Cultured, so it is gentler than cream and suits a dairy-free sauce."),
    (r"yoghurt|yogurt", "Greek yoghurt", "Strained, so most of the dairy is removed; keeps the marinade's tang."),
    (r"milk", "Lactose-free milk", "No lactose, so it is suitable for a dairy-free diet."),
)

rng = random.SystemRandom()


def _read(path: Path) -> list[dict[str, Any]]:
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]


def _strip_harness(rec: dict[str, Any]) -> dict[str, Any]:
    rec = copy.deepcopy(rec)
    for k in HARNESS_META:
        (rec.get("meta") or {}).pop(k, None)
    return rec


def _decoy_for(removed: str) -> tuple[str, str] | None:
    for pattern, to, reason in DECOYS:
        if re.search(pattern, removed, re.I):
            return to, reason
    return None


def _candidates(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for r in rows:
        ans = (r.get("output") or {}).get("answer") or {}
        if (r.get("request") or {}).get("allergen") == "contains-dairy" and r.get("status") == "ok" \
                and any(_decoy_for(str(s.get("from", ""))) for s in ans.get("substitutions") or []):
            out.append(r)
    return out


def corrupt(rec: dict[str, Any], swap_to: str | None, reason: str | None) -> dict[str, Any]:
    ans = rec["output"]["answer"]
    subs = [s for s in ans.get("substitutions") or [] if _decoy_for(str(s.get("from", "")))]
    target = rng.choice(subs)
    old_to = str(target.get("to", ""))
    decoy_to, decoy_reason = _decoy_for(str(target["from"]))  # type: ignore[misc]
    new_to, new_reason = swap_to or decoy_to, reason or decoy_reason
    target["to"], target["reason"] = new_to, new_reason
    for ing in ans.get("ingredients") or []:
        if str(ing.get("ingredient", "")).strip().lower() == old_to.strip().lower():
            ing["ingredient"] = new_to
    # Keep the substitution worker's report consistent with the answer, as it
    # would be if the model had really proposed this.
    for sp in rec.get("spans") or []:
        out = (sp.get("attrs") or {}).get("output")
        if sp.get("name") == "substitution_worker" and isinstance(out, dict):
            for s in out.get("substitutions") or []:
                if str(s.get("to", "")).strip().lower() == old_to.strip().lower():
                    s["to"], s["reason"] = new_to, new_reason
    rec["output"]["answer_text"] = obs.flatten_answer(ans)
    return rec


def clone(base: dict[str, Any], users: list[str], window: tuple[datetime, datetime],
          user: str | None, request: str | None) -> dict[str, Any]:
    rec = copy.deepcopy(base)
    rec["trace_id"] = obs.new_trace_id()
    lo, hi = window
    ts = lo + timedelta(seconds=rng.uniform(0, max(1.0, (hi - lo).total_seconds())))
    rec["ts"] = ts.isoformat(timespec="seconds")
    pick = user or rng.choice([u for u in users if u != base["user"]["user_id"]] or users)
    rec["user"] = {"user_id": pick, "session_id": f"s_{pick[2:]}{rng.choice('cdefg')}"}
    if request:
        rec["request"]["text"] = request
    jitter = rng.uniform(0.9, 1.1)
    for sp in rec.get("spans") or []:
        sp["start_ms"] = round(sp["start_ms"] * jitter, 1)
        sp["latency_ms"] = round(sp["latency_ms"] * jitter * rng.uniform(0.97, 1.03), 1)
    rec["totals"]["latency_ms"] = round(rec["totals"]["latency_ms"] * jitter, 1)
    rec["cost_by_stage"] = obs.stage_totals(rec["spans"])
    return rec


def main() -> None:
    ap = argparse.ArgumentParser(description="Plant one bad answer for the support drill.")
    ap.add_argument("--random", action="store_true", help="pick the base answer at random")
    ap.add_argument("--from-trace", help="the real trace to clone and corrupt")
    ap.add_argument("--swap-to", help="the dairy replacement to plant (default: matched to what it replaces)")
    ap.add_argument("--reason", help="the wrong justification to plant with it")
    ap.add_argument("--user", help="the user the planted request appears to come from")
    ap.add_argument("--request", help="rephrase the request text")
    ap.add_argument("--append", action="store_true", help="add to the existing drill copy (second plant)")
    ap.add_argument("--receipt", action="store_true", help="print the planted trace_id")
    args = ap.parse_args()

    prod = _read(PROD)
    if args.append and DRILL_LOG.exists():
        rows = _read(DRILL_LOG)
    else:
        rows = [_strip_harness(r) for r in prod]

    pool = _candidates(prod)
    if args.from_trace:
        base = next((r for r in prod if r["trace_id"] == args.from_trace), None)
        if base is None:
            raise SystemExit(f"{args.from_trace} is not in {PROD}")
        if base not in pool:
            raise SystemExit(f"{args.from_trace} is not a dairy-free answer with a dairy row swapped")
    elif args.random:
        if not pool:
            raise SystemExit("no dairy-free answer with a swappable row in the production log")
        base = rng.choice(pool)
    else:
        raise SystemExit("pass --random or --from-trace")

    stamps = sorted(datetime.fromisoformat(r["ts"]) for r in prod)
    users = sorted({r["user"]["user_id"] for r in prod})
    plant = corrupt(clone(_strip_harness(base), users, (stamps[0], stamps[-1]), args.user, args.request),
                    args.swap_to, args.reason)

    rows.append(plant)
    rows.sort(key=lambda r: r["ts"])
    DRILL_DIR.mkdir(parents=True, exist_ok=True)
    DRILL_LOG.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")

    salt = secrets.token_hex(16)
    SEAL.write_text(json.dumps({
        "salt": salt,
        "sealed": hashlib.sha256(f"{salt}:{plant['trace_id']}".encode()).hexdigest(),
        "planted_at": obs.utc_now(),
        "log": str(DRILL_LOG),
        "rows": len(rows),
        "complaint": "someone said it recommended a dairy-free substitution that wasn't dairy-free, sometime last week",
    }, indent=2), encoding="utf-8")

    print(f"planted 1 record into {DRILL_LOG}  ({len(rows)} rows)")
    print(f"seal written to {SEAL}")
    print('hand the finder ONLY the complaint: "someone said it recommended a dairy-free '
          "substitution that wasn't dairy-free, sometime last week.\"")
    if args.receipt:
        print(f"RECEIPT (planter only): {plant['trace_id']}")


if __name__ == "__main__":
    main()
