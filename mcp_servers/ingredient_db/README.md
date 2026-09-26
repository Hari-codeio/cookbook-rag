# ingredient-db (content team)

MCP server over the content team's ingredient sample. Vendored into this repo
unchanged for Week 9. **Not written by the recipe-assistant team.**

> Stand-in note: the brief describes this server but did not ship its code, so
> this is a stand-in built to the brief's description (lookup by name, allergen
> flags, per-100g nutrition). The Week 9 point is that the recipe agent can use
> it **without a code change**, and that we audit it before trusting it. The
> audit is in `risk_note.md`.

| Kind | Name | What it does |
|---|---|---|
| tool | `lookup_ingredient(name)` | fuzzy search, returns candidate ids |
| tool | `get_allergens(ingredient)` | EU-14 `contains` / `may_contain` flags |
| tool | `get_nutrition_per_100g(ingredient)` | kcal, protein, fat, carbs, sugars, fibre, salt |
| resource | `ingredients://allergen-flags` | legend of the 14 flag codes (app-attached) |

Transport: stdio. Reads `ingredients.json` (read-only). Appends every query to
`INGREDIENT_DB_QUERY_LOG` (default `out/ingredient_db_queries.log`). No network
access, no authentication of its own.
