"""Ingredient database MCP server (content team).

    python mcp_servers/ingredient_db/server.py        (stdio)

Lookup by ingredient name, EU-14 allergen flags, and nutrition per 100 g, over
a read-only JSON file shipped next to this script.

Tools (model-invoked):   lookup_ingredient, get_allergens, get_nutrition_per_100g
Resource (app-attached): ingredients://allergen-flags, the standing legend of
                         flag codes. It is the same on every turn, so it is a
                         resource the host attaches, not a tool to call.

Every tool call is appended to a query log (INGREDIENT_DB_QUERY_LOG, default
out/ingredient_db_queries.log under the working directory) for the content
team's usage reporting.
"""

from __future__ import annotations

import difflib
import json
import os
import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.exceptions import ToolError

DATA = json.loads((Path(__file__).parent / "ingredients.json").read_text(encoding="utf-8"))
QUERY_LOG = Path(os.environ.get("INGREDIENT_DB_QUERY_LOG", "out/ingredient_db_queries.log"))

mcp = FastMCP("ingredient-db")


def _norm(text: str) -> str:
    """'Crème fraîche, full fat (UK)' -> 'creme fraiche'. Accents folded,
    anything after a comma or inside brackets dropped, as recipe cards write
    'Ginger, grated' and 'Red wine (Burgundy)'."""
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    text = re.sub(r"\(.*?\)", " ", text.lower()).split(",")[0]
    return re.sub(r"[^a-z0-9' -]+", " ", text).strip()


_INDEX: dict[str, dict[str, Any]] = {}
for _item in DATA["ingredients"]:
    for _key in [_item["id"], _item["name"], *_item["aliases"]]:
        _INDEX.setdefault(_norm(_key), _item)


def _log(tool: str, query: str, matched: str | None) -> None:
    QUERY_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(QUERY_LOG, "a", encoding="utf-8") as fh:
        fh.write(json.dumps({
            "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "tool": tool, "query": query, "matched": matched,
        }) + "\n")


def _close(name: str, n: int = 3) -> list[str]:
    return difflib.get_close_matches(_norm(name), list(_INDEX), n=n, cutoff=0.6)


def _resolve(tool: str, name: str) -> dict[str, Any]:
    item = _INDEX.get(_norm(name))
    _log(tool, name, item["id"] if item else None)
    if item is None:
        near = sorted({_INDEX[k]["id"] for k in _close(name)})
        hint = f" Try: {', '.join(repr(n) for n in near)}." if near else " Use lookup_ingredient to search."
        raise ToolError(f"no ingredient matched {name!r}.{hint}")
    return item


@mcp.tool()
def lookup_ingredient(name: str) -> dict[str, Any]:
    """Search the ingredient database by name and return candidate records
    (id, canonical name, aliases). Use the returned id or name with
    get_allergens or get_nutrition_per_100g."""
    exact = _INDEX.get(_norm(name))
    hits = [exact] if exact else [_INDEX[k] for k in _close(name, n=5)]
    unique = list({h["id"]: h for h in hits}.values())
    _log("lookup_ingredient", name, ",".join(h["id"] for h in unique) or None)
    return {
        "query": name,
        "exact": bool(exact),
        "matches": [{"id": h["id"], "name": h["name"], "aliases": h["aliases"]} for h in unique],
    }


@mcp.tool()
def get_allergens(ingredient: str) -> dict[str, Any]:
    """Return the EU-14 allergen flags for one ingredient: `contains` (present
    by recipe) and `may_contain` (cross-contact risk declared by the supplier).
    An empty `contains` list with a non-empty `may_contain` is NOT allergen-free."""
    item = _resolve("get_allergens", ingredient)
    return {"id": item["id"], "name": item["name"],
            "contains": item["contains"], "may_contain": item["may_contain"]}


@mcp.tool()
def get_nutrition_per_100g(ingredient: str) -> dict[str, Any]:
    """Return nutrition per 100 g for one ingredient: kcal, protein, fat,
    carbohydrate, sugars, fibre and salt, all in grams except kcal."""
    item = _resolve("get_nutrition_per_100g", ingredient)
    return {"id": item["id"], "name": item["name"], "per_100g": item["per_100g"],
            "source": DATA["source"]}


@mcp.resource("ingredients://allergen-flags", mime_type="text/plain")
def allergen_flags() -> str:
    """The standing legend of allergen flag codes used by every record."""
    return "\n".join(f"{code}: {meaning}" for code, meaning in DATA["flags"].items())


if __name__ == "__main__":
    mcp.run()
