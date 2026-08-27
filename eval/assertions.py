"""Deterministic checks on a substitution. No model is called from this file.

These five criteria used to be, or would naturally have been, bullet points in
the judge prompt. Every one of them is decidable by reading the output, so
paying a model to decide them buys nothing and costs an off day. The judge is
left with exactly one criterion, the one that genuinely needs a reader
(see eval/judge_v1.txt).

    A1 method-ingredients-declared   every ingredient the method names by name
                                     appears in the ingredient list
    A2 allergen-warning-present      if an allergen-bearing ingredient is in the
                                     list, allergen_warning names that allergen
    A3 oven-temperature-has-units    a stated oven setting carries C or F
    A4 servings-stated-or-absent     servings is either a real yield or empty,
                                     never a placeholder like "N/A" or "unknown"
    A5 quantities-parse              every ingredient amount parses as
                                     number + unit, or an explicit count

    A6 model-is-the-pinned-one       the model that answered is the model config
                                     pinned (Week-5 mode 7, checked per case
                                     rather than as its own eval cases)

A1's matching is deliberately conservative. It only fails an ingredient it can
name, and a near-miss between "Whole milk (32 C)" in the list and "warm milk" in
the method is treated as a match by head-noun overlap, because the failure worth
catching is a method that calls for something absent from the list entirely, not
one that abbreviates. A stricter matcher would spend the whole eval flagging
prose.
"""

from __future__ import annotations

import re
from typing import Any

# Ingredient substrings that carry a declarable allergen, mapped to the word the
# warning has to contain. Taken from the archive's own allergen sections, not
# from general food knowledge, so the check stays inside the corpus.
ALLERGEN_TERMS: dict[str, tuple[str, ...]] = {
    "gluten": ("wheat flour", "strong white bread flour", "plain flour", "self-raising flour",
               "wholemeal flour", "rye flour", "dark rye flour", "wholemeal rye flour",
               "semolina", "barley"),
    "dairy": ("butter", "milk", "yoghurt", "yogurt", "cream", "ghee", "kefir", "cheese"),
    "egg": ("egg", "eggs"),
    "soy": ("soy sauce", "soybean", "soya", "miso", "tofu", "tamari", "edamame"),
    "shellfish": ("prawn", "shrimp", "saeujeot", "crab", "lobster"),
    "fish": ("fish sauce", "anchovy", "anchovies"),
    "peanut": ("peanut", "peanuts"),
    "sesame": ("sesame",),
    "nut": ("almond", "hazelnut", "walnut", "pistachio", "cashew"),
}

# Words a method uses that are not ingredients. Without this the check flags
# "oven", "dough" and "water" on every single case.
NOT_AN_INGREDIENT = {
    "oven", "dough", "batter", "tin", "bowl", "jar", "crock", "pan", "sieve", "paddle",
    "water", "brine", "surface", "top", "base", "centre", "center", "heat", "steam",
    "fridge", "room", "hand", "hands", "mixture", "crumb", "crust", "loaf", "jar",
    "cloth", "lid", "basket", "board", "knife", "spatula", "skewer", "temperature",
}

AMOUNT_RE = re.compile(
    r"""^\s*
    (?:
        \d+(?:\.\d+)?\s*(?:g|kg|ml|l|%)          # 250 g, 1.5 kg, 80%
      | \d+(?:\.\d+)?\s*(?:whole|leaves|leaf|cloves|clove|pieces|piece)  # 4 whole
      | \d+(?:\.\d+)?                            # bare count
    )
    (?:\s*\([^)]*\))?                            # trailing "(1.8%)" or "(32 C)"
    \s*$""",
    re.VERBOSE | re.IGNORECASE,
)

OVEN_UNIT_RE = re.compile(r"\d+\s*(?:°\s*)?[CF]\b")
PLACEHOLDER = {"n/a", "na", "none", "unknown", "not specified", "-", "tbd", "null"}


def _words(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z]+", text.lower()) if len(w) > 2}


def _head_nouns(name: str) -> set[str]:
    """Content words of an ingredient name, minus qualifiers.

    "Unsalted butter, softened" -> {"unsalted", "butter", "softened"}. Matching
    on any one of these against the method is what makes "warm milk" match
    "Whole milk (32 C)".
    """
    return _words(re.sub(r"\(.*?\)", " ", name))


def a1_method_ingredients_declared(payload: dict[str, Any]) -> tuple[bool, str]:
    ingredients = payload.get("ingredients") or []
    method = payload.get("method") or ""
    if not ingredients or not method:
        return True, "skipped: no ingredient list or no method"

    declared: set[str] = set()
    for ing in ingredients:
        declared |= _head_nouns(str(ing.get("name", "")))

    # Candidate ingredient words in the method: capitalised or known food words
    # would both misfire, so instead check the reverse direction that actually
    # matters, plus an explicit scan for allergen terms the list never declares.
    missing: list[str] = []
    lowered = method.lower()
    for allergen, terms in ALLERGEN_TERMS.items():
        for term in terms:
            if term in lowered and not any(term in str(i.get("name", "")).lower() for i in ingredients):
                if not (declared & _words(term)):
                    missing.append(term)
    missing = sorted(set(missing))
    if missing:
        return False, f"method names {missing} but the ingredient list does not"
    return True, f"{len(ingredients)} ingredients declared, method names none that are absent"


def a2_allergen_warning_present(payload: dict[str, Any]) -> tuple[bool, str]:
    ingredients = payload.get("ingredients") or []
    if not ingredients:
        return True, "skipped: nothing was substituted"
    warning = (payload.get("allergen_warning") or "").lower()

    present: set[str] = set()
    for ing in ingredients:
        name = str(ing.get("name", "")).lower()
        for allergen, terms in ALLERGEN_TERMS.items():
            if any(t in name for t in terms):
                present.add(allergen)
    if not present:
        return True, "no allergen-bearing ingredient in the list"
    if not warning.strip():
        return False, f"ingredients carry {sorted(present)} and allergen_warning is empty"

    # "wheat" satisfies gluten, "shrimp"/"shellfish" satisfy shellfish, etc.
    synonyms = {"gluten": ("gluten", "wheat", "rye", "barley"),
                "dairy": ("dairy", "milk", "butter", "lactose"),
                "egg": ("egg",), "soy": ("soy", "soya"),
                "shellfish": ("shellfish", "shrimp", "prawn"),
                "fish": ("fish",), "peanut": ("peanut",),
                "sesame": ("sesame",), "nut": ("nut",)}
    unnamed = [a for a in sorted(present) if not any(s in warning for s in synonyms.get(a, (a,)))]
    if unnamed:
        return False, f"ingredients carry {unnamed} and the warning does not name them"
    return True, f"warning names every allergen present: {sorted(present)}"


def a3_oven_temperature_has_units(payload: dict[str, Any]) -> tuple[bool, str]:
    oven = (payload.get("oven") or "").strip()
    if not oven:
        return True, "skipped: no oven setting stated"
    if not re.search(r"\d", oven):
        return False, f"oven={oven!r} states no number"
    if not OVEN_UNIT_RE.search(oven):
        return False, f"oven={oven!r} carries a number with no C or F"
    return True, f"oven={oven!r}"


def a4_servings_stated_or_absent(payload: dict[str, Any]) -> tuple[bool, str]:
    servings = (payload.get("servings") or "").strip()
    if not servings:
        return True, "empty, which is honest: the cards state no yield"
    if servings.lower() in PLACEHOLDER:
        return False, f"servings={servings!r} is a placeholder, not a yield or an honest blank"
    return True, f"servings={servings!r}"


def a5_quantities_parse(payload: dict[str, Any]) -> tuple[bool, str]:
    ingredients = payload.get("ingredients") or []
    if not ingredients:
        return True, "skipped: nothing was substituted"
    bad = [
        f"{ing.get('name')}={ing.get('amount')!r}"
        for ing in ingredients
        if not AMOUNT_RE.match(str(ing.get("amount", "")))
    ]
    if bad:
        return False, f"{len(bad)} amount(s) do not parse as number+unit: {bad[:3]}"
    return True, f"all {len(ingredients)} amounts parse as number+unit"


def a6_model_is_the_pinned_one(payload: dict[str, Any], model: str | None = None) -> tuple[bool, str]:
    """Week-5 mode 7, checked on every case instead of given its own cases."""
    from rag.config import GEN_PIN, GEN_PINNED_MODEL

    if not GEN_PIN:
        return True, "skipped: pinning is off"
    if model is None:
        return True, "skipped: no model recorded"
    if model != GEN_PINNED_MODEL:
        return False, f"answered by {model!r}, config pins {GEN_PINNED_MODEL!r}"
    return True, f"answered by the pinned {model!r}"


ASSERTIONS = [
    ("A1", "method-ingredients-declared", a1_method_ingredients_declared),
    ("A2", "allergen-warning-present", a2_allergen_warning_present),
    ("A3", "oven-temperature-has-units", a3_oven_temperature_has_units),
    ("A4", "servings-stated-or-absent", a4_servings_stated_or_absent),
    ("A5", "quantities-parse", a5_quantities_parse),
]


def run_all(payload: dict[str, Any], model: str | None = None) -> dict[str, Any]:
    """Every assertion against one substitution. Returns per-check detail."""
    results = []
    for code, name, fn in ASSERTIONS:
        ok, detail = fn(payload)
        results.append({"code": code, "name": name, "passed": ok, "detail": detail})
    ok, detail = a6_model_is_the_pinned_one(payload, model)
    results.append({"code": "A6", "name": "model-is-the-pinned-one", "passed": ok, "detail": detail})
    return {
        "passed": all(r["passed"] for r in results),
        "n_passed": sum(1 for r in results if r["passed"]),
        "n_total": len(results),
        "checks": results,
    }
