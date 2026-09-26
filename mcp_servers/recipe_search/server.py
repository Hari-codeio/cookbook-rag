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


@mcp.tool()
def search_recipes(query: str, limit: int = 5) -> dict[str, Any]:
    """Name match over the 21 cards. No embedding call, so it is free and fast."""
    return _unwrap(archive.search_recipes(query, limit))


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
