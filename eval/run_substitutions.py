"""Generate one substitution per eval case. Writes out/substitutions_v1.jsonl.

This is the artefact-producing step and nothing else. It does not import the
judge, does not import the labels, and has no notion of pass or fail. The
outputs it writes are frozen and are what BOTH the hand labels and the judge are
applied to afterwards, so neither can be accused of having been graded against a
moving target.

    python eval/run_substitutions.py
    python eval/run_substitutions.py --limit 3 --out out/substitutions_smoke.jsonl
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rag import trace as trc  # noqa: E402
from rag.config import OUT_DIR  # noqa: E402
from rag.generate import build_client  # noqa: E402
from rag.substitute import PROMPT_SHA256, PROMPT_VERSION, build_context, substitute  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
CASES = ROOT / "eval" / "substitution_cases.jsonl"
DEFAULT_OUT = OUT_DIR / "substitutions_v1.jsonl"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def load_cases(path: Path = CASES) -> list[dict]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        obj = json.loads(line)
        if "_note" in obj:
            continue
        rows.append(obj)
    return rows


def main() -> None:
    ap = argparse.ArgumentParser(description="Generate substitutions for the eval cases.")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--out", default=None)
    ap.add_argument("--sleep", type=float, default=1.0)
    args = ap.parse_args()

    cases = load_cases()
    if args.limit:
        cases = cases[: args.limit]
    out_path = Path(args.out) if args.out else DEFAULT_OUT

    cases_sha = hashlib.sha256(CASES.read_bytes()).hexdigest()
    print(f"cases        : {len(cases)}  from {CASES.name}")
    print(f"cases sha256 : {cases_sha}")
    print(f"prompt       : {PROMPT_VERSION}  sha {PROMPT_SHA256[:16]}")
    print(f"out          : {out_path}")
    print()

    client = build_client()
    records = []
    started = time.time()

    # Written as we go, not at the end. The first attempt at this run hit a
    # per-DAY quota wall at case 9 and threw away eight completed generations,
    # each of which had cost an API call that does not come back.
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fh = out_path.open("w", encoding="utf-8")

    for i, case in enumerate(cases, start=1):
        result = substitute(
            case["recipe"],
            case["constraint"],
            request=f"{case['recipe']} -> {case['constraint']}",
            client=client,
            trace=True,
            trace_meta={
                "source": "week6-substitution-eval",
                "case_id": case["id"],
                "mode": case["mode"],
                "cases_sha256": cases_sha,
            },
        )
        rec = {
            "case_id": case["id"],
            "mode": case["mode"],
            "recipe": case["recipe"],
            "constraint": case["constraint"],
            "trace_id": result.trace_id,
            "model": result.usage.get("model"),
            "prompt_version": PROMPT_VERSION,
            "output": result.payload,
            "raw_text": result.raw_text,
            # The context is what a judge and a labeller both have to read to
            # decide whether a claim was supported, so it travels WITH the
            # output rather than being looked up later against a store that may
            # have been re-ingested in between.
            "context_chunk_ids": [h.chunk_id for h in result.hits],
            "context": build_context(result.hits),
            "usage": result.usage,
        }
        records.append(rec)
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
        fh.flush()
        verdict = "substituted" if result.can_substitute else "declined"
        print(f"[{i:>2}/{len(cases)}] {case['id']:<4} {verdict:<12} {case['recipe'][:26]:<26} -> {case['constraint'][:34]}")
        if args.sleep:
            time.sleep(args.sleep)

    fh.close()

    digest = hashlib.sha256(out_path.read_bytes()).hexdigest()
    n_sub = sum(1 for r in records if r["output"].get("can_substitute"))
    print()
    print(f"done in {(time.time() - started) / 60:.1f} min")
    print(f"substituted : {n_sub}/{len(records)}")
    print(f"declined    : {len(records) - n_sub}/{len(records)}")
    print(f"written     : {out_path}")
    print(f"sha256      : {digest}")
    print(json.dumps(trc.file_fingerprint(), indent=2))


if __name__ == "__main__":
    main()
