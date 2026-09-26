"""Server ONE: the recipe archive, exposed over MCP.

    python -m mcp_servers.recipe_search.server        (speaks JSON-RPC on stdin/stdout)

You never run this by hand. The host (rag/mcp_host.py) starts it as a child
process, because mcp_config.json tells it to, and talks to it over the pipes.

THERE IS NO MODEL IN THIS FILE, AND NO API KEY. This process receives a tool
name plus arguments and answers with JSON. It cannot tell which model, or
whether any model, is on the other end. The functions it wraps are the same
deterministic ones the Week 7 agent called directly from rag/tools.py; MCP only
changes how they are reached, not what they compute.

THE DOCSTRING IS THE PROMPT. FastMCP builds each tool's `inputSchema` from the
type hints and its `description` from the docstring, and that description is
what the model reads when it decides which tool to call. A docstring written
for a developer ("free and fast") is therefore a bad prompt, not a harmless
comment.
"""

from __future__ import annotations

import difflib
import re
from typing import Any, Literal

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.exceptions import ToolError

from rag import tools as archive

mcp = FastMCP("recipe-search")

Allergen = Literal[
    "contains-egg",
    "contains-dairy",
    "contains-gluten",
    "contains-soy",
    "contains-shellfish",
    "contains-sesame",
    "contains-peanut",
    "contains-fish",
    "contains-alcohol",
]


def _unwrap(result: archive.ToolResult) -> dict[str, Any]:
    """rag/tools.py reports failure as ok=False. Over MCP the equivalent is a
    ToolError, which FastMCP sends back as a result with isError=true, so the
    model sees it and can choose again instead of the run crashing."""
    if not result.ok:
        raise ToolError("Error: lookup failed")
    return result.data


def _closest_titles(query: str, n: int = 3) -> list[tuple[str, str]]:
    """(title, recipe_id) pairs whose words are spelled like the query's words."""
    words = [w for w in re.split(r"[^a-z0-9]+", query.lower()) if len(w) > 2]
    scored = []
    for card in archive._corpus().values():
        names = re.split(r"[^a-z0-9]+", f"{card.title} {card.recipe_id}".lower())
        best = max(
            (difflib.SequenceMatcher(None, w, name).ratio() for w in words for name in names if name),
            default=0.0,
        )
        if best >= 0.75:
            scored.append((best, card.title, card.recipe_id))
    scored.sort(key=lambda s: (-s[0], s[2]))
    return [(title, rid) for _, title, rid in scored[:n]]


@mcp.tool()
def search_recipes(query: str, limit: int = 5) -> dict[str, Any]:
    """FIND a recipe in the 21-card archive by dish name. Call this FIRST:
    scale_recipe and every later step need the recipe_id it returns.

    Pass only the dish name, e.g. "shakshuka" or "focaccia". Words from the
    request such as "double" or "without egg" are in no title and only
    weaken the match.

    Returns recipe_id, title, cuisine, dietary_tags and the ORIGINAL,
    unscaled ingredient names. Does not scale (use scale_recipe) and does not
    check allergens (use get_allergen_profile).

    If nothing matches, the error says whether a spelling variant exists and
    gives its exact query to retry with. If it says the dish is not in the
    archive, do not search again and do not adapt a different recipe: answer
    with that dish listed under "unsupported"."""
    result = archive.search_recipes(query, limit)
    if result.ok:
        return result.data
    close = _closest_titles(query)
    if close:
        options = "; ".join(f"'{t}' (recipe_id '{rid}')" for t, rid in close)
        raise ToolError(
            f"no recipe title matched {query!r}. Close spellings in the archive: {options}. "
            f"If that is the dish the user meant, call search_recipes again with "
            f"query='{close[0][1]}'. This is a no-match, not a server fault."
        )
    raise ToolError(
        f"no recipe title matched {query!r}, and no title is spelled like it: this dish is "
        f"not in the 21-card archive. Searching again will not find it. Answer now, with "
        f"{query!r} under \"unsupported\". This is a no-match, not a server fault."
    )


@mcp.tool()
def scale_recipe(recipe_id: str, scale_factor: float) -> dict[str, Any]:
    """MULTIPLY the amounts of one already-identified recipe by a factor, and
    return those scaled amounts plus the method text. Requires a recipe_id from
    search_recipes. Does not find recipes and does not assess allergens."""
    return _unwrap(archive.scale_recipe(recipe_id, scale_factor))


@mcp.tool()
def get_allergen_profile(ingredients: list[str], allergen: Allergen) -> dict[str, Any]:
    """REPORT which of the ingredient names you supply carry one specified
    allergen. Use it on the recipe's ingredients to find what must go, then again
    on any replacement you propose, to confirm the replacement is itself clear.
    Does not find recipes, does not scale, and does not choose a replacement."""
    return _unwrap(archive.get_allergen_profile(ingredients, allergen))


if __name__ == "__main__":
    mcp.run()  # stdio transport: JSON-RPC on stdin/stdout, logs on stderr
