"""The output contract both systems must satisfy, and the grader for it.

This lives in its own module so neither the agent nor the workflow owns it. If
the contract were defined inside the agent, the workflow would be judged against
the agent's idea of done, and the race would be rigged before it started.

A run PASSES when all five hold:

  1. it names a recipe_id that exists in the archive
  2. that recipe_id is the one the case expects
  3. the scale factor matches the request
  4. every ingredient the case says must be substituted has been, and nothing
     that should have been left alone was touched
  5. the method is present and non-empty

Point 4 is the one the allergen-cascade cases turn on. If the swap introduced
by step 3 itself carries the banned allergen, a run that stops after one swap
fails, however fluent it reads.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

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


def check(answer: dict[str, Any], case: dict[str, Any]) -> tuple[bool, list[str]]:
    """Grade one answer against one case. Returns (passed, reasons_it_failed)."""
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

    method = str(answer.get("method") or "").strip()
    if not method:
        problems.append("method is empty")

    return (not problems), problems
