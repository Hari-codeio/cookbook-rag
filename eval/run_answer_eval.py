"""Answer-level evaluation, and the R / G / Not-In-Corpus tally.

Week 4 requirement 3. hit-rate@3 measures retrieval only, so it can never
surface a G failure by construction: G means retrieval worked and the model
still got it wrong. That can only be seen by reading the answer.

So this runs all 12 golden questions through the full pipeline at k=3 - the same
k the hit-rate uses - and then labels every wrong answer with the decision tree
the brief asks for:

    wrong answer + correct chunk NOT in top-3   -> R   (retrieval fetched bad context)
    wrong answer + correct chunk IS  in top-3   -> G   (model misused good context)
    wrong answer + no chunk holds the answer    -> Not-In-Corpus

The middle branch is the one the brief warns about: labelling something R
without checking whether the right chunk was sitting in the top-3 all along. If
it was there and the number is still wrong, no retrieval change on earth fixes
it, so calling it R would send you off to build the wrong thing.

A refusal is never scored correct. It is recorded as refused and then labelled
by the same tree, because a refusal caused by missing context is an R failure
even though it is an honest output.

    python eval/run_answer_eval.py --retriever dense  --label before
    python eval/run_answer_eval.py --retriever rerank --label after
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rag.config import GEN_MODEL, GEN_PROVIDER, OUT_DIR, ROOT  # noqa: E402
from rag.store import get_collection, search  # noqa: E402

GOLDEN_PATH = ROOT / "eval" / "golden_set.jsonl"
KEYS_PATH = ROOT / "eval" / "answer_keys.json"


def norm(text: str) -> str:
    """Lowercase, collapse runs of whitespace to one space."""
    return re.sub(r"\s+", " ", (text or "").lower()).strip()


def contains(haystack: str, needle: str) -> bool:
    """Boundary-aware match, so a number cannot match inside a bigger number.

    A plain substring test is wrong here and it bit me. The first run of this
    script labelled g01 a G failure because the answer key listed '2%' as a
    wrong value and the CORRECT answer was '1.2%' - and '2%' is a substring of
    '1.2%'. That false label pointed at the model when the real failures were
    all in retrieval, which is precisely the mislabelling the brief warns about.

    So: a needle beginning with a digit may not be preceded by a digit or a
    decimal point, and one ending in a digit may not be followed by a digit.
    Word-like needles get ordinary word boundaries. Spaces in the needle match
    optional whitespace, so '6 g' still matches '6g'.
    """
    h = norm(haystack)
    n = norm(needle)
    if not n:
        return False

    left = r"(?<![0-9.])" if n[0].isdigit() else r"(?<![a-z0-9])"
    if n[-1].isdigit():
        right = r"(?![0-9])"
    elif n[-1].isalnum():
        right = r"(?![a-z0-9])"
    else:
        right = ""

    body = re.escape(n).replace(r"\ ", r"\s*")
    return re.search(left + body + right, h) is not None


def load_golden() -> list[dict]:
    raw = GOLDEN_PATH.read_text(encoding="utf-8")
    return [json.loads(l) for l in raw.splitlines() if l.strip()]


def whole_corpus_has_answer(collection, key: dict) -> bool:
    """Is any chunk in the index carrying one of the required strings at all?"""
    got = collection.get(include=["documents"])
    for doc in got.get("documents") or []:
        for need in key.get("any_of", []):
            if contains(doc, need):
                return True
    return False


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--retriever", default="dense", choices=["dense", "rerank"])
    ap.add_argument("--label", default=None)
    ap.add_argument("--k", type=int, default=3)
    ap.add_argument("--strategy", default="structure")
    args = ap.parse_args()
    label = args.label or args.retriever

    from rag.generate import answer as generate_answer

    golden = load_golden()
    keys = json.loads(KEYS_PATH.read_text(encoding="utf-8"))["keys"]
    collection = get_collection(args.strategy)

    if args.retriever == "rerank":
        from rag.rerank import rerank_search

        def top_ids(q, k):
            return [h.chunk_id for h in rerank_search(collection, q, k=k)]
    else:
        def top_ids(q, k):
            return [h.chunk_id for h in search(collection, q, k=k)]

    rows = []
    for g in golden:
        qid = g["id"]
        key = keys.get(qid, {})
        top3 = top_ids(g["question"], args.k)
        expected_in_top = g["expected_chunk_id"] in top3

        print("[gen] " + qid + ": " + g["question"], file=sys.stderr)
        res = generate_answer(
            g["question"], args.strategy, k=args.k, retriever=args.retriever
        )
        text = "" if res.refused else res.answer_text
        shown = res.rendered()

        hit_any = any(contains(text, n) for n in key.get("any_of", []))
        hit_wrong = [n for n in key.get("wrong_if", []) if contains(text, n)]
        correct = (not res.refused) and hit_any and not hit_wrong

        if correct:
            lab = "PASS"
            evidence = "answer contains " + repr(
                next(n for n in key["any_of"] if contains(text, n))
            )
        elif not whole_corpus_has_answer(collection, key):
            lab = "Not-In-Corpus"
            evidence = "no chunk anywhere in the index contains " + str(key.get("any_of"))
        elif expected_in_top:
            lab = "G"
            if res.refused:
                evidence = (
                    "correct chunk " + g["expected_chunk_id"] + " WAS in the top-"
                    + str(args.k) + " and the model refused anyway"
                )
            elif hit_wrong:
                evidence = (
                    "correct chunk " + g["expected_chunk_id"] + " WAS in the top-"
                    + str(args.k) + " but the answer quotes " + str(hit_wrong)
                    + " from a sibling recipe"
                )
            else:
                evidence = (
                    "correct chunk " + g["expected_chunk_id"] + " WAS in the top-"
                    + str(args.k) + " but the answer omits " + str(key.get("any_of"))
                )
        else:
            lab = "R"
            evidence = (
                "correct chunk " + g["expected_chunk_id"] + " was NOT in the top-"
                + str(args.k) + "; retrieved " + str(top3)
            )

        rows.append(
            {
                "id": qid,
                "question": g["question"],
                "expected": g["expected_chunk_id"],
                "top3": top3,
                "expected_in_top": expected_in_top,
                "refused": res.refused,
                "answer": shown,
                "label": lab,
                "evidence": evidence,
                "known": g["known_answer"],
                "exact_token": g.get("exact_token", False),
            }
        )

    tally = {}
    for r in rows:
        tally[r["label"]] = tally.get(r["label"], 0) + 1

    out = [
        "# Answer-level evaluation and failure tally - retriever=" + args.retriever,
        "",
        "```",
        "retriever   : " + args.retriever,
        "k           : " + str(args.k),
        "provider    : " + GEN_PROVIDER,
        "model       : " + GEN_MODEL,
        "generated   : " + datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "```",
        "",
        "## Tally",
        "",
        "| label | count |",
        "|---|---|",
        "| PASS | " + str(tally.get("PASS", 0)) + " |",
        "| R (retrieval fetched bad context) | " + str(tally.get("R", 0)) + " |",
        "| G (model misused good context) | " + str(tally.get("G", 0)) + " |",
        "| Not-In-Corpus | " + str(tally.get("Not-In-Corpus", 0)) + " |",
        "",
        "## Per-question, with one line of evidence each",
        "",
        "| id | question | expected chunk in top-" + str(args.k) + "? | refused? | label | evidence |",
        "|---|---|---|---|---|---|",
    ]
    for r in rows:
        out.append(
            "| " + r["id"]
            + " | " + r["question"]
            + " | " + ("yes" if r["expected_in_top"] else "**no**")
            + " | " + ("yes" if r["refused"] else "no")
            + " | **" + r["label"] + "**"
            + " | " + r["evidence"]
            + " |"
        )

    out += ["", "## Transcripts", ""]
    for r in rows:
        out += [
            "### " + r["id"] + " - " + r["question"],
            "",
            "known-correct: " + r["known"] + "   expected chunk: `" + r["expected"] + "`",
            "",
            "```text",
            "top-" + str(args.k) + ": " + str(r["top3"]),
            "",
            r["answer"],
            "```",
            "",
            "label: **" + r["label"] + "** - " + r["evidence"],
            "",
        ]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / ("answer_eval_" + label + ".md")
    path.write_text("\n".join(out) + "\n", encoding="utf-8")

    print()
    for r in rows:
        print(
            "  " + r["id"] + "  " + r["label"].ljust(14)
            + ("top3:y " if r["expected_in_top"] else "top3:N ")
            + ("refused " if r["refused"] else "        ")
            + r["question"]
        )
    print()
    print("TALLY: " + str(tally))
    print("[written] out/" + path.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
