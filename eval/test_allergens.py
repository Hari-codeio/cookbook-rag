"""Regression tests for the allergen matcher, which has been wrong twice.

    python eval/test_allergens.py

Both bugs were SILENT and both changed race results:

  1. substring matching flagged "Tamarind paste" as soy, because the soy marker
     "tamari" is a prefix of it, and flagged "Gluten-free flour blend" as gluten
     because it contains "flour".
  2. after the boundary fix, the plant-based replacements a model actually
     reaches for - "Coconut yoghurt", "Coconut cream", "Vegan butter block" -
     were all still flagged dairy on the words yoghurt / cream / butter. That
     failed three of the four cascade cases in the first race for a reason that
     had nothing to do with either system.

The matcher decides pass and fail for the whole week, so it gets its own test.
Every row below is a case one of those bugs got wrong, plus the traps that must
keep firing.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rag.tools import _carries  # noqa: E402

# (ingredient, allergen, should_it_carry)
CASES: list[tuple[str, str, bool]] = [
    # --- bug 1: substring false positives -------------------------------
    ("Tamarind paste", "contains-soy", False),
    ("Gluten-free flour blend", "contains-gluten", False),
    ("Aubergine", "contains-egg", False),
    # --- bug 2: plant-based replacements read as the thing they replace --
    ("Coconut yoghurt", "contains-dairy", False),
    ("Coconut cream", "contains-dairy", False),
    ("Coconut creme", "contains-dairy", False),
    ("Vegan butter block, softened", "contains-dairy", False),
    ("Almond milk", "contains-dairy", False),
    ("Oat milk", "contains-dairy", False),
    ("Soya milk", "contains-dairy", False),
    ("Cashew cream", "contains-dairy", False),
    ("Plant-based cream", "contains-dairy", False),
    ("Olive oil", "contains-dairy", False),
    # --- the traps, which must keep firing ------------------------------
    ("Greek yoghurt", "contains-dairy", True),
    ("Full fat yoghurt", "contains-dairy", True),
    ("Double cream", "contains-dairy", True),
    ("Buttermilk", "contains-dairy", True),
    ("Creme fraiche", "contains-dairy", True),
    ("Ghee", "contains-dairy", True),
    ("Paneer", "contains-dairy", True),
    ("Whole milk", "contains-dairy", True),
    ("Unsalted butter, softened", "contains-dairy", True),
    ("Tamari", "contains-soy", True),
    ("Light soy sauce", "contains-soy", True),
    ("Firm tofu", "contains-soy", True),
    ("Strong white bread flour", "contains-gluten", True),
    ("Self-raising flour", "contains-gluten", True),
    ("Eggs", "contains-egg", True),
    ("Whole eggs", "contains-egg", True),
    ("Fish sauce", "contains-fish", True),
    ("Raw prawns", "contains-shellfish", True),
    ("Roasted peanuts", "contains-peanut", True),
    ("Toasted sesame oil", "contains-sesame", True),
    ("Red wine (Burgundy)", "contains-alcohol", True),
    # --- cross-allergen: a dairy-free swap can still carry something else
    ("Soya milk", "contains-soy", True),
]


def main() -> None:
    width = max(len(c[0]) for c in CASES) + 2
    failures = 0
    print(f"{'ingredient':<{width}} {'allergen':<22} got    want")
    print("-" * (width + 40))
    for name, allergen, want in CASES:
        got = _carries(name, allergen)
        flag = "" if got == want else "   <-- MISMATCH"
        if got != want:
            failures += 1
        print(f"{name:<{width}} {allergen:<22} {str(got):<6} {str(want):<6}{flag}")
    print("-" * (width + 40))
    if failures:
        print(f"{failures} of {len(CASES)} MISMATCHED")
        raise SystemExit(1)
    print(f"all {len(CASES)} correct; the matcher is not decorative")


if __name__ == "__main__":
    main()
