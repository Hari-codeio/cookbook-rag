"""Run an LLM judge over frozen substitutions. One binary criterion.

The prompt is READ FROM A FILE (eval/judge_v1.txt, eval/judge_v2.txt) rather
than living in this module. Two reasons, both about being able to trust the
before/after number:

* the two versions can be diffed as text, which is what the write-up has to show
* iterating the judge cannot accidentally change the harness at the same time,
  so a moved agreement figure is attributable to the prompt and nothing else

The judge sees the request, the CONTEXT blocks the assistant was given, and the
assistant's output. It does not see the hand labels, the case's `groundable`
field, or the other cases' verdicts.

    python eval/judge.py --prompt eval/judge_v1.txt --out out/judge_v1_verdicts.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rag.config import OUT_DIR  # noqa: E402
from rag.generate import build_client, call_model  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SUBSTITUTIONS = OUT_DIR / "substitutions_v1.jsonl"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

VERDICT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "sound": {
            "type": "boolean",
            "description": "True if the output is SOUND by the single criterion. No middle value.",
        },
        "reason": {
            "type": "string",
            "description": "One sentence naming the specific evidence that decided it.",
        },
    },
    "required": ["sound", "reason"],
}


def load_prompt(path: Path) -> tuple[str, str]:
    """Everything after the SYSTEM PROMPT banner, plus the file's sha256.

    The header above that banner is commentary for humans - which criteria were
    moved to assertions, when the file was written - and must not be sent to the
    model, or the judge would be reading notes about itself.
    """
    text = path.read_text(encoding="utf-8")
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if line.strip() == "SYSTEM PROMPT":
            start = i + 1
            if start < len(lines) and set(lines[start].strip()) <= {"-"}:
                start += 1
            return "\n".join(lines[start:]).strip(), digest
    raise SystemExit(f"{path} has no 'SYSTEM PROMPT' banner line")


def build_user_turn(rec: dict[str, Any]) -> str:
    out = rec["output"]
    rendered = json.dumps(
        {
            "can_substitute": out.get("can_substitute"),
            "base_recipe_id": out.get("base_recipe_id"),
            "title": out.get("title"),
            "swaps": out.get("swaps"),
            "ingredients": out.get("ingredients"),
            "method": out.get("method"),
            "oven": out.get("oven"),
            "allergen_warning": out.get("allergen_warning"),
            "unsupported": out.get("unsupported"),
        },
        indent=2,
        ensure_ascii=False,
    )
    return (
        f"REQUEST\n=======\n"
        f"base recipe: {rec['recipe'] or '(none named)'}\n"
        f"requested change: {rec['constraint']}\n\n"
        f"CONTEXT BLOCKS THE ASSISTANT WAS GIVEN\n"
        f"======================================\n{rec['context']}\n\n"
        f"THE ASSISTANT'S OUTPUT\n======================\n{rendered}\n\n"
        f"Is this output SOUND? Answer the single criterion only."
    )


def judge_one(client, system_prompt: str, rec: dict[str, Any]) -> dict[str, Any]:
    reply = call_model(
        client,
        "",
        build_user_turn(rec),
        system_prompt=system_prompt,
        schema=VERDICT_SCHEMA,
        max_tokens=4096,
        prefer_no_thinking=True,
    )
    try:
        payload = json.loads(reply.text)
    except json.JSONDecodeError:
        payload = {"sound": False, "reason": "judge returned unparseable JSON"}
    return {
        "sound": bool(payload.get("sound")),
        "reason": str(payload.get("reason") or ""),
        "model": reply.model,
        "raw_text": reply.text,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="Run the judge over frozen substitutions.")
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--substitutions", default=str(SUBSTITUTIONS))
    ap.add_argument("--out", required=True)
    ap.add_argument("--sleep", type=float, default=1.0)
    args = ap.parse_args()

    prompt_path = Path(args.prompt)
    system_prompt, prompt_sha = load_prompt(prompt_path)
    version = re.sub(r"\.txt$", "", prompt_path.name)

    recs = [
        json.loads(l)
        for l in Path(args.substitutions).read_text(encoding="utf-8").splitlines()
        if l.strip()
    ]
    subs_sha = hashlib.sha256(Path(args.substitutions).read_bytes()).hexdigest()

    print(f"judge prompt      : {prompt_path}  ({version})")
    print(f"judge prompt sha  : {prompt_sha}")
    print(f"substitutions     : {args.substitutions}  ({len(recs)} cases)")
    print(f"substitutions sha : {subs_sha}")
    print()

    client = build_client()
    verdicts = {}
    started = time.time()
    for i, rec in enumerate(recs, start=1):
        v = judge_one(client, system_prompt, rec)
        verdicts[rec["case_id"]] = v
        print(f"[{i:>2}/{len(recs)}] {rec['case_id']:<4} sound={str(v['sound']):<5} {v['reason'][:74]}")
        if args.sleep:
            time.sleep(args.sleep)

    record = {
        "judge_version": version,
        "judge_prompt_path": str(prompt_path),
        "judge_prompt_sha256": prompt_sha,
        "substitutions_sha256": subs_sha,
        "n": len(recs),
        "verdicts": verdicts,
    }
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    n_sound = sum(1 for v in verdicts.values() if v["sound"])
    print()
    print(f"done in {(time.time() - started) / 60:.1f} min")
    print(f"judged SOUND   : {n_sound}/{len(recs)}")
    print(f"judged UNSOUND : {len(recs) - n_sound}/{len(recs)}")
    print(f"written        : {out_path}")


if __name__ == "__main__":
    main()
