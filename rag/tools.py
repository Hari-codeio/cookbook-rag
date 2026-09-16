"""The tools the recipe agent can call, and the schemas it sees.

Every tool is DETERMINISTIC PYTHON. No tool calls a model. That split is the
whole point of the week: if the work a step does is fixed, it belongs in code,
and the only question left is whether choosing the ORDER of those steps needs a
model. An agent that calls a model inside its own tools cannot answer that
question, because the cost of the loop and the cost of the work are mixed.

Scaling in particular is arithmetic, and it is done here with Decimal rather
than asked of the model. Weeks 5 and 6 spent a lot of effort proving the model
must not do arithmetic (taxonomy mode `refuses-arithmetic-with-table-on-screen`,
judge v2 Example 1). Nothing about adding an agent loop changes that.

TOOL DESCRIPTIONS ARE v1 HERE, AND THEY ARE DELIBERATELY OVERLAPPING.
`search_recipes` and `scale_recipe` both claim to return the ingredient list.
That is the bug this week is supposed to find by racing, not by taste, and the
fix has to be a sharper description rather than a sterner system prompt or a
bigger model. The v1 -> v2 diff is a deliverable.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from functools import lru_cache
from pathlib import Path
from typing import Any

from rag.config import DATA_BASELINE, DATA_NEW_DROP, ROOT, TOP_K
from rag.parse import Card, load_cards

DATA_VARIATIONS = ROOT / "data" / "variations"
CORPUS_DIRS = (DATA_BASELINE, DATA_NEW_DROP, DATA_VARIATIONS)

# Taken from the cards' own frontmatter, not invented. Every value below
# appears as a dietary_tag on at least one of the 21 cards, so a caller cannot
# name an allergen the corpus has no opinion about.
ALLERGENS = (
    "contains-egg",
    "contains-dairy",
    "contains-gluten",
    "contains-soy",
    "contains-shellfish",
    "contains-sesame",
    "contains-peanut",
    "contains-fish",
    "contains-alcohol",
)

DIETS = ("vegan", "vegetarian", "dairy-free", "gluten-free", "nut-free")

# Which ingredient words carry which allergen. Deterministic, auditable, and
# deliberately narrow: a word not on this list does not silently become safe,
# it becomes UNKNOWN, which the caller can see.
ALLERGEN_MARKERS: dict[str, tuple[str, ...]] = {
    "contains-egg": ("egg", "eggs"),
    # buttermilk / creme / curd are here as whole words because the boundary
    # match on "butter" and "cream" does not reach them, and they are exactly
    # the substitutes a model reaches for when told to replace butter or cream.
    "contains-dairy": (
        "milk", "butter", "buttermilk", "yoghurt", "yogurt", "cream", "creme",
        "kefir", "ghee", "cheese", "curd", "paneer", "mascarpone", "custard",
    ),
    "contains-gluten": ("flour", "wheat", "rye", "barley", "semolina", "breadcrumb"),
    "contains-soy": ("soy", "soya", "miso", "tofu", "tamari"),
    "contains-shellfish": ("shrimp", "prawn", "crab", "lobster"),
    "contains-sesame": ("sesame", "tahini"),
    "contains-peanut": ("peanut",),
    "contains-fish": ("fish sauce", "anchovy", "anchovies", "fish"),
    "contains-alcohol": ("wine", "brandy", "beer", "rum"),
}

QTY_RE = re.compile(r"^\s*([0-9]+(?:\.[0-9]+)?)\s*([a-zA-Z%]*)\s*$")


def _fmt(value: Decimal) -> str:
    """2dp, trailing zeros stripped, and never scientific notation.

    Decimal.normalize() turns 300.00 into 3E+2, which is arithmetically right
    and useless on a recipe card. format(..., "f") forces plain notation.
    """
    return format(value.quantize(Decimal("0.01")).normalize(), "f")


@dataclass
class ToolResult:
    """What a tool hands back to the loop.

    `ok` is separate from the payload on purpose. A tool that cannot answer
    returns ok=False with a reason, and the loop is allowed to see that and
    choose again. A tool that raises would end the run instead, which would
    hide exactly the retry behaviour the race is meant to measure.
    """

    ok: bool
    data: dict[str, Any] = field(default_factory=dict)
    error: str = ""


@lru_cache(maxsize=1)
def _corpus() -> dict[str, Card]:
    cards: dict[str, Card] = {}
    for directory in CORPUS_DIRS:
        if not directory.exists():
            continue
        for card in load_cards(directory):
            cards[card.recipe_id] = card
    return cards


def _ingredient_rows(card: Card) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for section in card.sections_of("ingredients"):
        table = getattr(section, "table", None) or card.table
        if not table:
            continue
        for row in table.rows:
            cells = row.cells
            if not cells or not cells[0].strip():
                continue
            rows.append(
                {
                    "ingredient": cells[0].strip(),
                    "amount": cells[1].strip() if len(cells) > 1 else "",
                    "note": cells[2].strip() if len(cells) > 2 else "",
                }
            )
    if not rows and card.table:
        for row in card.table.rows:
            cells = row.cells
            if cells and cells[0].strip():
                rows.append(
                    {
                        "ingredient": cells[0].strip(),
                        "amount": cells[1].strip() if len(cells) > 1 else "",
                        "note": cells[2].strip() if len(cells) > 2 else "",
                    }
                )
    return rows


def _method_text(card: Card) -> str:
    parts = [s.text.strip() for s in card.sections_of("method") if s.text.strip()]
    return "\n\n".join(parts)


def _servings(card: Card) -> str:
    for section in card.sections:
        m = re.search(r"(serves|makes|yield[s]?)\s*[:\-]?\s*([0-9]+)", section.text, re.I)
        if m:
            return m.group(2)
    m = re.search(r"(serves|makes|yield[s]?)\s*[:\-]?\s*([0-9]+)", card.raw, re.I)
    return m.group(2) if m else ""


# Phrases that CLEAR an allergen even though a marker word is present. Without
# these, "Gluten-free flour blend" reads as gluten because it contains "flour",
# which would fail every gluten case in the race for the wrong reason.
ALLERGEN_EXCLUSIONS: dict[str, tuple[str, ...]] = {
    "contains-gluten": ("gluten-free", "gluten free", "gf "),
    # The dairy list is the long one because dairy words are also the NAMES of
    # the plant-based products that replace them. "Coconut yoghurt", "Coconut
    # cream" and "Vegan butter block" are all dairy free, and the first pass of
    # this file failed all three on the words yoghurt / cream / butter. That was
    # a bug in the grader, not a finding about either system, and it failed
    # three of the four cascade cases for the wrong reason.
    "contains-dairy": (
        "dairy-free", "dairy free", "non-dairy", "nondairy", "plant-based",
        "plant based", "vegan", "coconut", "almond", "oat ", "oat-", "soya",
        "soy ", "soy-", "cashew", "rice milk", "hemp", "olive oil",
    ),
    "contains-egg": ("egg-free", "egg free", "eggless", "eggplant", "aubergine", "egg replacer", "vegan egg"),
    "contains-fish": ("fish-free", "fish free", "vegan fish", "vegetarian fish"),
    "contains-soy": ("soy-free", "soy free"),
}


def _carries(name: str, allergen: str) -> bool:
    """Does this ingredient name carry this allergen?

    Substring matching was wrong twice on the real corpus and both were silent:
    "Tamarind paste" matched the soy marker "tamari", and "Gluten-free flour
    blend" matched the gluten marker "flour". So markers now match on a word
    boundary with an optional plural - \btamari(s)?\b does not match tamarind,
    while \begg(s)?\b still matches "Eggs" - and an exclusion phrase clears the
    allergen outright.
    """
    low = name.lower()
    for phrase in ALLERGEN_EXCLUSIONS.get(allergen, ()):
        if phrase in low:
            return False
    for word in ALLERGEN_MARKERS[allergen]:
        if re.search(rf"\b{re.escape(word)}(s|es)?\b", low):
            return True
    return False


def allergens_for_ingredient(name: str) -> list[str]:
    return sorted(a for a in ALLERGEN_MARKERS if _carries(name, a))


# ---------------------------------------------------------------------------
# TOOL 1 - search_recipes
# ---------------------------------------------------------------------------

def search_recipes(query: str, limit: int = TOP_K) -> ToolResult:
    """Name match over the 21 cards. No embedding call, so it is free and fast."""
    if not query or not query.strip():
        return ToolResult(False, error="query was empty")

    terms = [t for t in re.split(r"[^a-z0-9]+", query.lower()) if len(t) > 2]
    scored: list[tuple[int, Card]] = []
    for card in _corpus().values():
        hay = f"{card.recipe_id} {card.title} {card.cuisine}".lower()
        score = sum(1 for t in terms if t in hay)
        if score:
            scored.append((score, card))
    scored.sort(key=lambda p: (-p[0], p[1].recipe_id))

    matches = [
        {
            "recipe_id": c.recipe_id,
            "title": c.title,
            "cuisine": c.cuisine,
            "dietary_tags": c.dietary_tags,
            "ingredients": _ingredient_rows(c),
        }
        for _, c in scored[:limit]
    ]
    if not matches:
        return ToolResult(False, error=f"no recipe in the archive matches {query!r}")
    return ToolResult(True, {"matches": matches, "n": len(matches)})


# ---------------------------------------------------------------------------
# TOOL 2 - scale_recipe
# ---------------------------------------------------------------------------

def scale_recipe(recipe_id: str, scale_factor: float) -> ToolResult:
    """Multiply every parseable amount by a factor.

    DEVIATION FROM THE BRIEF, STATED RATHER THAN HIDDEN. The brief says "scale
    it to the requested servings". Not one of the 21 cards states a serving
    count - `grep -rliE "(serves|makes|yields)[^a-z]*[0-9]" data/*/*.md` returns
    zero files. Eleven cards carry a baker's-percentage basis row (100%) and ten
    do not, so that is not a universal anchor either. The only scaling basis
    every card supports is a multiplier, so the requests ask for "1.5x" or
    "double" and this takes a factor. Inventing a servings number per card would
    have been fabricating corpus data to make a tool signature look tidier.

    Decimal, not float, and quantised to 2dp, so a third of 100 g is 33.33 g
    rather than 33.333333333333336.
    """
    card = _corpus().get(recipe_id)
    if card is None:
        return ToolResult(False, error=f"unknown recipe_id {recipe_id!r}")
    try:
        factor = Decimal(str(scale_factor))
    except (InvalidOperation, TypeError, ValueError):
        return ToolResult(False, error=f"scale_factor {scale_factor!r} is not a number")
    if factor <= 0:
        return ToolResult(False, error="scale_factor must be greater than zero")

    base = _servings(card)
    scaled: list[dict[str, str]] = []
    unscalable: list[str] = []

    for row in _ingredient_rows(card):
        m = QTY_RE.match(row["amount"])
        if not m:
            unscalable.append(row["ingredient"])
            scaled.append({**row, "scaled_amount": row["amount"], "scaled": False})
            continue
        try:
            value = Decimal(m.group(1)) * factor
        except InvalidOperation:
            unscalable.append(row["ingredient"])
            scaled.append({**row, "scaled_amount": row["amount"], "scaled": False})
            continue
        unit = m.group(2)
        scaled.append({**row, "scaled_amount": f"{_fmt(value)} {unit}".strip(), "scaled": True})

    return ToolResult(
        True,
        {
            "recipe_id": recipe_id,
            "title": card.title,
            "base_servings": base or "not stated on the card",
            "factor": format(factor.quantize(Decimal("0.0001")).normalize(), "f"),
            "ingredients": scaled,
            "unscalable": unscalable,
            "method": _method_text(card),
        },
    )


# ---------------------------------------------------------------------------
# The schemas the model actually sees. v1: TWO tools, overlapping descriptions.
# ---------------------------------------------------------------------------

TOOL_SCHEMAS_V1: list[dict[str, Any]] = [
    {
        "name": "search_recipes",
        "description": (
            "Search the recipe archive and return matching recipes with their "
            "ingredient lists, amounts and dietary tags. Use this to look up a "
            "recipe and see what is in it."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "What to search for."},
                "limit": {"type": "integer", "description": "How many to return."},
            },
            "required": ["query"],
        },
    },
    {
        "name": "scale_recipe",
        "description": (
            "Get a recipe's ingredient list with the amounts adjusted for a "
            "different number of servings. Returns the ingredients and the method."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "recipe_id": {"type": "string", "description": "The recipe to scale."},
                "scale_factor": {"type": "number", "description": "Multiplier, e.g. 2 to double."},
            },
            "required": ["recipe_id", "scale_factor"],
        },
    },
]

REGISTRY_V1 = {"search_recipes": search_recipes, "scale_recipe": scale_recipe}


# ---------------------------------------------------------------------------
# TOOL 3 - get_allergen_profile
# ---------------------------------------------------------------------------

def get_allergen_profile(ingredients: list[str], allergen: str) -> ToolResult:
    """Which of the named ingredients carry one named allergen. That is its
    whole job.

    It takes a LIST OF INGREDIENT NAMES rather than a recipe_id on purpose.
    Keyed on recipe_id it could only ever answer "what is wrong with the
    original", and the cascade cases need the other question too: is the
    replacement I just thought of also unsafe? One signature answers both, and
    the tool still does exactly one thing.

    It deliberately does NOT choose a replacement. Choosing is the model's job
    and is the only part of this task that is not fixed. A tool that both
    detected and replaced would hide that, and the verdict this week turns on
    being able to see it.

    An ingredient no marker matches comes back under `unknown`, never under
    `safe`. Silence is not a clearance.
    """
    if not isinstance(ingredients, (list, tuple)) or not ingredients:
        return ToolResult(False, error="ingredients must be a non-empty list of names")
    if allergen not in ALLERGENS:
        return ToolResult(
            False,
            error=f"unknown allergen {allergen!r}; expected one of {', '.join(ALLERGENS)}",
        )

    carries, safe, unknown = [], [], []
    for raw in ingredients:
        name = str(raw).strip()
        if not name:
            continue
        if _carries(name, allergen):
            carries.append({"ingredient": name, "allergen": allergen})
        elif allergens_for_ingredient(name):
            safe.append(name)
        else:
            unknown.append(name)

    return ToolResult(
        True,
        {
            "allergen": allergen,
            "carries_allergen": carries,
            "clear_of_this_allergen": safe,
            "unknown_to_the_archive": unknown,
            "any_found": bool(carries),
        },
    )


# ---------------------------------------------------------------------------
# v2 SCHEMAS. Three tools, one job each, no overlapping claim.
#
# The v1 pair both promised the ingredient list, which is the whole description
# bug. v2 fixes it by giving each tool a single verb and an explicit "does not"
# line, so the boundary is stated rather than inferred. The enum on `allergen`
# means a wrong value is rejected by the schema instead of being silently
# matched against nothing and coming back clean.
# ---------------------------------------------------------------------------

TOOL_SCHEMAS_V2: list[dict[str, Any]] = [
    {
        "name": "search_recipes",
        "description": (
            "FIND a recipe in the archive by name and return its recipe_id, title "
            "and original unscaled ingredient names. Call this FIRST, to learn the "
            "recipe_id. Does not scale amounts and does not assess allergens."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Recipe name to look for."},
                "limit": {"type": "integer", "description": "Maximum matches to return."},
            },
            "required": ["query"],
        },
    },
    {
        "name": "scale_recipe",
        "description": (
            "MULTIPLY the amounts of one already-identified recipe by a factor, and "
            "return those scaled amounts plus the method text. Requires a recipe_id "
            "from search_recipes. Does not find recipes and does not assess allergens."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "recipe_id": {"type": "string", "description": "recipe_id from search_recipes."},
                "scale_factor": {"type": "number", "description": "Multiplier, e.g. 2 to double."},
            },
            "required": ["recipe_id", "scale_factor"],
        },
    },
    {
        "name": "get_allergen_profile",
        "description": (
            "REPORT which of the ingredient names you supply carry one specified "
            "allergen. Use it on the recipe's ingredients to find what must go, then "
            "again on any replacement you propose, to confirm the replacement is "
            "itself clear. Does not find recipes, does not scale, and does not choose "
            "a replacement for you."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "ingredients": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Ingredient names to check. May be one proposed substitute.",
                },
                "allergen": {
                    "type": "string",
                    "enum": list(ALLERGENS),
                    "description": "The single allergen to test for.",
                },
            },
            "required": ["ingredients", "allergen"],
        },
    },
]

REGISTRY_V2 = {
    "search_recipes": search_recipes,
    "scale_recipe": scale_recipe,
    "get_allergen_profile": get_allergen_profile,
}
