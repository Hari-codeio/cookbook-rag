# Week 9: MCP. Bolt on the ingredient database without touching the agent (Set B)

## The numbers

| | Value | Evidence |
|---|---|---|
| Agent-module lines changed, server one -> one + two | **0 added, 0 deleted** | `agent_diff.txt` |
| Files the server swap touched | **1** (`mcp_config.json`, +6 lines) | `config_diff.txt` |
| Tools from `tools/list` | **3 -> 6** | `out/tool_counts_before.txt`, `out/tool_counts_after.txt` |
| `search_recipes("moussaka")`, before -> after the error rewrite | **8 laps, no answer -> 2 laps, answered "unsupported"** | `error_before_after.md` |
| Gateway: nutrition calls denied under the `menu-bot` token | **2 of 2 denied, 0 invented numbers** | `out/gateway_audit.log`, `out/gateway_run.txt` |

**Tool count line:** 3 before -> 6 after.
- Before (`search_recipes`, `scale_recipe`, `get_allergen_profile`), all from server `recipe_search`.
- After adds `lookup_ingredient`, `get_allergens`, `get_nutrition_per_100g` from server `ingredient_db`.
- Both lists are printed by `python -m rag.mcp_host --list-tools`, which prints `ListToolsResult.tools` as the server returned it.

## Commit trail

```
f499c39  week 9 base: recipe-search MCP server + host that discovers tools   <- SERVER ONE
f0e0497  vendor the content team's ingredient-db server (not in config yet)
7225574  add ingredient-db to mcp_config.json, and nothing else               <- SERVER ONE + TWO
1bd5043  search_recipes docstring as prompt + recoverable no-match
b40505e  deliverables
0e38d7e  bonus: gateway, scoped token, audit line
```

`git diff f499c39 HEAD -- rag/` is empty. The agent module has not changed
since the Week 9 base, not even for the gateway.

## 1. Config-only server swap (30)

- `agent_diff.txt`: `git diff --numstat f499c39 7225574` over `rag/agent.py`,
  `rag/mcp_host.py`, `rag/llm.py`, `rag/tools.py`, `rag/contract.py` gives 0 / 0.
- `config_diff.txt`: the whole swap is six added lines in `mcp_config.json`.
- A query that provably used server two (`out/server_two_query.txt`), with the
  server name next to each call in the host trace:

```
[recipe_search] search_recipes({"query": "pad thai"}) -> ok
[recipe_search] scale_recipe({"scale_factor": 1.5, "recipe_id": "pad-thai"}) -> ok
[ingredient_db] get_allergens({"ingredient": "Roasted sunflower seeds"}) -> ERROR  (no match, "Try: 'sunflower-seeds-roasted'")
[ingredient_db] get_allergens({"ingredient": "sunflower-seeds-roasted"}) -> ok
[ingredient_db] get_nutrition_per_100g({"ingredient": "sunflower-seeds-roasted"}) -> ok
```

The model named "Roasted sunflower seeds", the third-party server replied with
a spelling hint, and the model used it. The protein figure in the answer
(19.3 g) is the database's own number.

Why it can work with no code change: `rag/mcp_host.py` never names a tool. It
builds the model's tool list from `tools/list` and routes each call by the
name it discovered. `run_agent` already took `tool_schemas` and `registry` as
parameters in Week 7, so the host passes those in and `agent.py` stays untouched.

## 2. Raw wire capture (25)

`wire.json`: 9 messages (initialize, the initialized notification, tools/list,
and two tools/call, one a hit and one a miss). They were captured by
`eval/capture_wire.py`, which writes JSON lines to the server's stdin by hand
with no MCP library. Every top-level field is annotated.

> **Where the model runs:** only in the host process (`rag/mcp_host.py` ->
> `rag/agent.py` -> `rag/llm.py` -> Gemini). It never runs in the ingredient-db
> server, which only receives a tool name and JSON arguments and never sees a
> prompt, a model name or an API key.

## 3. Docstring as prompt + recoverable error (20)

See `error_before_after.md`. The clean result is `moussaka`, a dish not in the
archive:

- **Before:** "Error: lookup failed" led to 7 identical retries and then max_laps, with no answer.
- **After:** "not in the 21-card archive... answer unsupported" led to a stop after one call and an honest answer.

The shakshouka pair is reported too, with what it does NOT show.

## 4. Tool counts (15)

3 -> 6, names above, from `tools/list` output files, not notes.

## 5. Risk note (10)

`risk_note.md`, 5 lines. Verdict: **ship behind the gateway, not as the sole allergen source.**

## Bonus: gateway

`mcp_config.gateway.json` points the host at ONE server, `mcp_servers/gateway`.
The gateway connects to both real servers and re-exports their 6 tools and the
allergen-flags resource unchanged. For each call it:

1. checks the token scope,
2. forwards the call,
3. appends one audit line.

The `menu-bot` token (only its sha256 is in `tokens.json`) is denied
`get_nutrition_per_100g`:

```
{"caller": "menu-bot", "tool": "get_allergens", "upstream": "ingredient_db", "ingredient_queried": "Sunflower seeds, roasted", "decision": "allow", ...}
{"caller": "menu-bot", "tool": "get_nutrition_per_100g", "upstream": "ingredient_db", "ingredient_queried": "Sunflower seeds, roasted", "decision": "deny", ...}
```

The model's answer says *"I am unable to provide the protein content per 100g
for this substitute."* It did not invent a number.

**One finding against my own message:** the model still retried the denied
tool once, with a shorter ingredient name, even though the denial said retries
would be denied. Stating "retry will fail" in the error was not enough to
prevent one wasted lap. Hiding denied tools from `tools/list` for that caller
would prevent it. I did not do that here, because the brief asks to show the
denial reaching the model.

## Environment notes

- `mcp` is pinned `>=1.9,<2`. mcp 2.x renamed FastMCP to MCPServer, and the
  course material uses the FastMCP API.
- The local `.venv` pointed at a Python install under another Windows user.
  `pyvenv.cfg` was repointed to this machine's Python 3.13 (backup:
  `.venv/pyvenv.cfg.bak`, not committed).
- The ingredient-db server is a stand-in built to the brief's description,
  because its code was not supplied. See `mcp_servers/ingredient_db/README.md`.
