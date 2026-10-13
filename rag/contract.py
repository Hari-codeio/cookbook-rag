"""The output contract both systems must satisfy, and the grader for it.

This lives in its own module so neither the agent nor the workflow owns it. If
the contract were defined inside the agent, the workflow would be judged against
the agent's idea of done, and the race would be rigged before it started.

A run PASSES when all six hold:

  1. it names a recipe_id that exists in the archive
  2. that recipe_id is the one the case expects
  3. the scale factor matches the request
  4. every ingredient the case says must be substituted has been, and nothing
     that should have been left alone was touched
  5. the method is present and non-empty
  6. (Week 11) nothing in the answer puts the avoided allergen back: not a
     replacement, not a row in the ingredient list, and not the METHOD

Point 4 is the one the allergen-cascade cases turn on. If the swap introduced
by step 3 itself carries the banned allergen, a run that stops after one swap
fails, however fluent it reads.

Point 6 exists because points 1-5 never read the method, and the method is
what a cook follows. Week 10 scored the squad 10/10 while its "completely dairy
free" tikka masala still said "soften the onion in the ghee" and "stir in the
cream" (out/squad_demo.txt). The swap list was right and the recipe was not.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

# Words in front of an allergen word that turn an instruction into a mention:
# "use oil instead of ghee" names ghee without telling anyone to use it.
_MENTION_ONLY = re.compile(
    r"\b(instead of|in place of|rather than|without|omit|omitting|leave out|no|"
    r"replace|replaces|replacing|replaced|swap|swapping|substitute for)\b", re.I)
_NONE_LIKE = {"", "none", "-", "n/a", "omit", "removed"}

REQUIRED_KEYS = ("recipe_id", "scale_factor", "ingredients", "substitutions", "method")


@dataclass
class RunResult:
    """What one system returns for one request. Identical for agent and workflow."""

    answer: dict[str, Any] = field(default_factory=dict)
    ok: bool = False
    error: str = ""

    # Accounting. Summed across every model call the run made, not just the last.
    laps: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0
    latency_ms: float = 0.0

    terminated_by: str = ""  # "" = ran to completion; otherwise the budget that fired
    log: list[dict[str, Any]] = field(default_factory=list)

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens


def check(answer: dict[str, Any], case: dict[str, Any], residue: bool = True) -> tuple[bool, list[str]]:
    """Grade one answer against one case. Returns (passed, reasons_it_failed).

    residue=False grades on points 1-5 only, the grader Week 10 reported, so a
    suite run can show both numbers for the same answers."""
    problems: list[str] = []

    if not isinstance(answer, dict) or not answer:
        return False, ["no answer produced"]

    for key in REQUIRED_KEYS:
        if key not in answer:
            problems.append(f"missing key {key!r}")
    if problems:
        return False, problems

    got_id = str(answer.get("recipe_id") or "").strip()
    if got_id != case["expect_recipe_id"]:
        problems.append(f"recipe_id {got_id!r} != expected {case['expect_recipe_id']!r}")

    try:
        got_factor = float(answer.get("scale_factor"))
    except (TypeError, ValueError):
        got_factor = None
    if got_factor is None or abs(got_factor - float(case["scale_factor"])) > 1e-6:
        problems.append(f"scale_factor {answer.get('scale_factor')!r} != {case['scale_factor']}")

    # Substitutions: compare the SET of ingredients removed, case-insensitively
    # and on a substring basis, because "Whole milk" and "whole milk (250 g)"
    # are the same removal and the contract is about which ingredient went, not
    # how it was spelled.
    subs = answer.get("substitutions") or []
    removed = []
    for s in subs:
        if isinstance(s, dict):
            removed.append(str(s.get("from") or s.get("ingredient") or "").lower())
        else:
            removed.append(str(s).lower())
    removed_blob = " | ".join(removed)

    for needed in case.get("expect_substituted", []):
        if needed.lower() not in removed_blob:
            problems.append(f"did not substitute {needed!r}")

    for forbidden in case.get("expect_untouched", []):
        if forbidden.lower() in removed_blob:
            problems.append(f"substituted {forbidden!r}, which should have been left alone")

    # THE CASCADE TEST. Checking only that the banned ingredient left is not
    # enough: swapping light soy sauce for tamari removes the row and still
    # serves soy. So every replacement is put through the same allergen check
    # the original ingredients went through. This is the one assertion the four
    # cascade cases turn on, and it is deterministic - no model is asked.
    avoid = case.get("avoid_allergen") or ""
    if avoid:
        from rag.tools import ALLERGENS, _carries

        if avoid in ALLERGENS:
            for s in subs:
                if not isinstance(s, dict):
                    continue
                replacement = str(s.get("to") or "").strip()
                if not replacement or replacement.lower() in {"none", "-", "n/a", "omit", "removed"}:
                    continue  # straight removal is a valid answer
                if _carries(replacement, avoid):
                    problems.append(
                        f"replacement {replacement!r} still carries {avoid}"
                    )

    method = str(answer.get("method") or "").strip()
    if not method:
        problems.append("method is empty")

    # 6. THE RESIDUE TEST (Week 11). Replacements are point 4's job; this adds
    # the two places point 4 never looked.
    if avoid and residue:
        from rag.tools import ALLERGENS

        if avoid in ALLERGENS:
            res = allergen_residue(answer, avoid)
            if res["ingredients"]:
                problems.append(f"ingredient list still carries {avoid}: {res['ingredients']}")
            if res["method"]:
                problems.append(f"method still tells the cook to use {avoid}: {res['method']}")

    return (not problems), problems


def allergen_residue(answer: dict[str, Any], allergen: str) -> dict[str, list[str]]:
    """Where an answer to an `allergen`-free request still carries it.

        swaps        replacements that themselves carry it      ("Ghee" for butter)
        ingredients  rows of the final list that carry it       ("Double cream", left in)
        method       method phrases that tell the cook to use it ("soften the onion in the ghee")

    Deterministic, and it reuses the matcher the allergen tool uses
    (rag.tools._carries), so "coconut cream" and "vegan butter" stay clear in
    the method for the same reason they are clear in the ingredient list.

    A method hit is judged on the two words in front of it, so "the vegan
    butter" is clear and "the butter" is not. A hit after "instead of",
    "without", "no" and similar is a mention, not an instruction, and is
    skipped: "use oil instead of ghee" is a correct sentence.
    """
    from rag.tools import ALLERGEN_MARKERS, _carries

    swaps = [str(s.get("to") or "").strip() for s in answer.get("substitutions") or []
             if isinstance(s, dict) and str(s.get("to") or "").strip().lower() not in _NONE_LIKE
             and _carries(str(s.get("to")), allergen)]
    ingredients = [str(i.get("ingredient") or i.get("name") or "").strip()
                   for i in answer.get("ingredients") or []
                   if isinstance(i, dict) and _carries(str(i.get("ingredient") or i.get("name") or ""), allergen)]

    method_hits: list[str] = []
    method = str(answer.get("method") or "")
    for sentence in re.split(r"(?<=[.!?])\s+|\n+", method):
        words = sentence.split()
        for i, w in enumerate(words):
            core = re.sub(r"[^\w-]", "", w).lower()
            if not core or not any(re.fullmatch(rf"{re.escape(m)}(s|es)?", core)
                                   for m in ALLERGEN_MARKERS[allergen] if " " not in m):
                continue
            before2 = " ".join(words[max(0, i - 2):i + 1])
            before4 = " ".join(words[max(0, i - 4):i])
            if _MENTION_ONLY.search(before4):
                continue
            if _carries(before2, allergen):
                method_hits.append(" ".join(words[max(0, i - 3):i + 1]))
    return {"swaps": swaps, "ingredients": ingredients, "method": sorted(set(method_hits))}
