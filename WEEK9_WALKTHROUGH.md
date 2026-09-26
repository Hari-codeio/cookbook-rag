# Week 9, explained like a person would explain it

This is a teaching companion to `results_week9.md`. It walks through every
file Week 9 added or changed, block by block. For each block it says what the
code does and why, in plain words.

---

## Part 1. The whole idea in one picture

Before Week 9, your agent's tools were **glued in by hand**:

```
rag/agent.py  --imports-->  rag/tools.py  (search_recipes, scale_recipe, ...)
```

If the content team built a great ingredient database, you would have to
write new Python, import it, register it and redeploy. No other team could
reuse your tools either.

**MCP (Model Context Protocol) is a standard plug socket.** A tool that speaks
MCP can be plugged into any AI app that speaks MCP. Think of USB: your laptop
doesn't need new code for every mouse, because the mouse and the laptop agree
on the socket.

After Week 9:

```
                 YOUR APP (the "host")                          SEPARATE PROCESSES ("servers")
  ┌──────────────────────────────────────────────┐
  │  rag/agent.py   the loop (unchanged since W7) │     stdio pipe    ┌───────────────────────┐
  │  rag/llm.py     *** THE MODEL CALL ***        │ ◄──JSON-RPC────► │ recipe_search server   │ (yours)
  │  rag/mcp_host.py  reads mcp_config.json,      │                  └───────────────────────┘
  │                   one "client" per server     │     stdio pipe    ┌───────────────────────┐
  │                                               │ ◄──JSON-RPC────► │ ingredient_db server   │ (content team's)
  └──────────────────────────────────────────────┘                  └───────────────────────┘
                     ▲
                     │ the only file you edit to add a server
               mcp_config.json
```

### The three roles, in plain words

| Role | In this repo | What it does | Does it run the AI? |
|---|---|---|---|
| **Host** | `rag/mcp_host.py` + `rag/agent.py` | Owns the conversation and calls Gemini. Decides which tool to call, because the model decided. | **Yes, the only place** |
| **Client** | one `ClientSession` per server, inside the host | Speaks the MCP protocol to one server. Just a translator. | No |
| **Server** | `mcp_servers/recipe_search`, `mcp_servers/ingredient_db` | Offers tools. Gets "call tool X with these arguments" and answers with JSON. | **No, never** |

The one sentence to remember, and to say to your mentor:

> **The AI runs in my app (the host). The MCP server is just a menu of tools.
> It gets a tool name and some arguments, returns JSON, and has no idea a model
> exists.**

That is also why "does MCP make my AI smarter?" gets the answer **no**. MCP is
plumbing. The answers are just as good as before. What you gain is reuse: you
can plug tools in and out without touching code.

---

## Part 2. One request, start to finish

`python -m rag.mcp_host "Make the pad thai 1.5x ... tell me the swap's protein per 100 g"`

1. **Host starts.** It reads `mcp_config.json` and sees two servers.
2. **For each server, the host launches it as a child process** and opens a pipe to it.
3. **Handshake (`initialize`).** The host says "I speak MCP version 2025-11-25", and the server says "me too, and I offer tools and resources."
4. **Discovery (`tools/list`).** The host asks "what tools do you have?"
   - recipe_search replies with 3 tools.
   - ingredient_db replies with 3 tools.
   - The host now knows about **6 tools**, and nobody typed those names into the agent.
5. **The host gives those 6 tool descriptions to Gemini** along with the user's request.
6. **Gemini (running in the host) replies:** "call `search_recipes` with `{query: 'pad thai'}`."
7. **The host looks up which server owns `search_recipes`** (recipe_search) and sends it a `tools/call` message down the pipe.
8. **The server runs plain Python** (no AI) and sends back JSON.
9. The host gives that JSON to Gemini, and Gemini picks the next tool, e.g. `get_nutrition_per_100g`, which lives on ingredient_db.
10. The loop repeats until Gemini writes the final answer.

Steps 3, 4 and 7 are exactly the messages you can read in `wire.json`.

---

## Part 3. Every file, block by block

### 3.1 `mcp_config.json`: the "plug board" (the ONLY file the server swap changed)

```json
{
  "mcpServers": {
    "recipe_search": {                                   // a name I choose for this server
      "command": "python",                               // how to start it...
      "args": ["-m", "mcp_servers.recipe_search.server"] // ...with these arguments
    },
    "ingredient_db": {                                   // ← these 6 lines are the whole swap
      "command": "python",
      "args": ["mcp_servers/ingredient_db/server.py"],
      "env": {"INGREDIENT_DB_QUERY_LOG": "out/ingredient_db_queries.log"},  // settings passed to that server only
      "attach_resources": ["ingredients://allergen-flags"]                  // context the APP attaches (see 3.4)
    }
  }
}
```

It uses the same shape Claude Desktop and most MCP apps use. Adding server two
meant adding one entry here. `config_diff.txt` shows it: +6 lines, nothing else.

---

### 3.2 `mcp_servers/recipe_search/server.py`: YOUR server (server one)

This takes the Week 7 tools you already had in `rag/tools.py` and **puts them behind the MCP socket.**

| Lines | What it does, in plain words |
|---|---|
| 1-19 (docstring) | Explains that there's **no model and no API key** in this file, and that **the docstring becomes the prompt**. |
| `from mcp.server.fastmcp import FastMCP` | FastMCP is the helper library that turns ordinary Python functions into MCP tools. |
| `from rag import tools as archive` | Reuses your Week 7 logic. MCP doesn't change *what* the tools compute, only *how they are reached*. |
| `mcp = FastMCP("recipe-search")` (L32) | Creates the server and gives it a name. That name comes back in `serverInfo` during the handshake. |
| `Allergen = Literal[...]` (L34) | Lists the only allowed allergen values. FastMCP turns this into an `enum` in the JSON Schema, so the model can't make up `"dairy"` when the real value is `"contains-dairy"`. |
| `_unwrap(...)` (L47) | `rag/tools.py` reports failures as `ok=False`. MCP's way of saying "the tool failed" is to raise `ToolError`, which FastMCP turns into a reply with `isError: true`. The model sees that and can try again, instead of the program crashing. |
| `_closest_titles(...)` (L56) | **New in commit 1bd5043.** When a search misses, this finds recipe titles *spelled like* what the user typed (for example "shakshouka" matches "Shakshuka"). It uses Python's `difflib` and needs no AI. |
| `@mcp.tool()` above `search_recipes` (L72) | This decorator is the whole trick: "publish this function as an MCP tool." FastMCP reads the **type hints** (`query: str, limit: int = 5`) to build the `inputSchema`, and reads the **docstring** to build the `description`. |
| `search_recipes` docstring (L74-88) | **Rewritten as a prompt.** Before, it said "Name match over the 21 cards. No embedding call, so it is free and fast." That is useful to a developer and useless to the model. Now it tells the model **when** to call it (first), **what to pass** (only the dish name), **what comes back**, **what it doesn't do**, and **what to do when it fails**. |
| the two `raise ToolError(...)` (L95-104) | **The recoverable error.** There are two different messages for two different situations: "close spelling exists, retry with X" and "not in the archive, stop searching, say unsupported." Both end with "This is a no-match, not a server fault" so the model doesn't mistake it for a broken server. |
| `scale_recipe`, `get_allergen_profile` | Same pattern: a decorator, type hints, a prompt-style docstring, and a call into your Week 7 function. |
| `mcp.run()` (L125) | Starts the server on **stdio**: it reads JSON-RPC from stdin and writes to stdout. That is why a server must **never `print()`**, because any stray text would corrupt the pipe. |

**The before/after in one table:**

| | Before | After |
|---|---|---|
| Docstring (what the model reads) | "Name match... free and fast." | When to call it, what to pass, what it returns, what it's not for, what to do on failure |
| Miss message | `Error: lookup failed` | "not in the 21-card archive... answer unsupported", or "close spelling 'X', retry with query='X'" |
| `moussaka` run | 7 identical retries, then out of laps, **no answer** | 1 call, then an honest "unsupported" in **2 laps** |

Why it matters: "Error: lookup failed" could mean *typo*, *doesn't exist*, or
*server on fire*. The model can't tell which, so it either keeps retrying (what
we saw) or makes up an answer (the brief's warning). A good error message tells
the model **what went wrong and what to do next.**

---

### 3.3 `rag/mcp_host.py`: the host (the heart of the week)

This is the file that makes "add a server with only config" possible. **It
never mentions a single tool by name.**

| Lines | What it does, in plain words |
|---|---|
| 1-21 (docstring) | The three roles and where the model runs. |
| `CONFIG_PATH`, `TRACE_PATH`, ... (L44-48) | Where to read the config, and where to write the log of every tool call (`out/mcp_trace.jsonl`). |
| `_expand` (L52) | Lets the config say `"${MENU_BOT_TOKEN}"` and fills it in from `.env`. **Secrets stay out of the committed config.** |
| `load_config` (L58) | Reads `mcp_config.json` and returns the `mcpServers` section. |
| `_server_params` (L68) | Turns one config entry into "how to launch this server." Two details matter: `"python"` becomes *this* interpreter, so the config works on any machine. And `get_default_environment()` passes only safe variables like PATH, so **your GEMINI_API_KEY is never handed to a tool server.** |
| `DiscoveredTool` (L86) | A little record for each discovered tool: which server owns it, its name, its description and its schema. |
| `class MCPHost` (L93) | The host object. Its docstring explains a real engineering problem: `run_agent` is normal synchronous Python, but MCP sessions are `async`. So the sessions live on a **background event loop in its own thread**, and each tool becomes a small sync function that sends the call to that loop and waits for the answer. |
| `__enter__` / `__exit__` (L123-141) | `with MCPHost() as host:` starts every server, and leaving the `with` block shuts them all down cleanly. |
| `_lifecycle` (L143) | Opens **all** connections in **one** async task and keeps them open until shutdown. (anyio, the async library underneath, refuses to close a pipe from a different task than the one that opened it. That is why it is structured this way.) |
| `_connect` (L157) | **The discovery code.** For one server it: 1) launches the process (`stdio_client`), 2) opens a `ClientSession`, 3) runs `initialize()`, the handshake, 4) runs `list_tools()`, **discovery**, 5) records every tool it got back, 6) **refuses to start** if two servers offer the same tool name (so it never silently calls the wrong one), and 7) reads any `attach_resources` the config asked for. |
| `tool_schemas` (L189) | Turns the discovered tools into what Gemini wants. MCP's `inputSchema` is standard JSON Schema, and Gemini accepts JSON Schema directly through `parameters_json_schema`, so **nothing is translated by hand, tool by tool.** |
| `registry` (L198) | A dict from tool name to a function that calls it over MCP. This is the same shape as `REGISTRY_V1` in Week 7, which is why `agent.py` didn't need to change. |
| `system_prompt` (L202) | Your Week 7 system prompt, plus any attached resources (the allergen legend) pasted in as reference text. |
| `call` (L219) | **One `tools/call`.** It finds the owning server, sends the call, and waits up to 30 s. Then there are three outcomes: **success** gives `ToolResult(ok=True, data)`; **the tool said isError** gives `ToolResult(ok=False, error=<the server's message>)`, so the model reads the real reason; **the server didn't answer at all** gives a message that explicitly says "connection failure, not an empty result; do not guess." That last one is what stops the model from treating a dead server as "no allergens found." |
| `_trace` (L244) | Writes one JSON line per call: which server, which tool, the arguments, the error flag, and the result. This is how the `[ingredient_db] get_nutrition_per_100g` proof lines were produced. |
| `run` (L261) | Calls **the unchanged Week 7 `run_agent`**, handing it the discovered schemas, the registry and the prompt. |
| `main` (L284) | The command line. `--list-tools` prints what `tools/list` returned (the 3 -> 6 evidence), `--config` picks a different plug board (used by the gateway), and otherwise it runs the agent and prints the trace. |

**Why `agent.py` never changed:** back in Week 7, `run_agent(...)` already
accepted `tool_schemas=` and `registry=` as parameters. The host just fills
them from `tools/list` instead of from a hard-coded Python list. That is what
"discovered, not hard-coded" looks like in code.

---

### 3.4 `mcp_servers/ingredient_db/`: the content team's server (server two)

| File / lines | What it does |
|---|---|
| `ingredients.json` | The database: 56 ingredients, each with aliases, EU-14 allergen flags (`contains` / `may_contain`) and nutrition per 100 g. |
| `README.md` | Who owns it and what it touches. It is honest that this is a stand-in, since the brief didn't ship the real code. |
| `server.py` `_norm` (L38) | Cleans up names: `"Crème fraîche, full fat (UK)"` becomes `"creme fraiche"`. Recipe cards write "Ginger, grated", so it drops everything after the comma. |
| `_INDEX` (L47) | A lookup table from every id, name and alias to its record. |
| `_log` (L53) | **Writes every query to a log file.** Pay attention to this line: it means *a third party is recording what your users ask about.* It is why the risk note exists. |
| `_resolve` (L66) | Finds an ingredient, or raises a helpful error: `"no ingredient matched 'creme fraiche lite'. Try: 'creme-fraiche'."` That is the brief's own example, and you can see the model use a hint like this live in `out/server_two_query.txt`. |
| 3 × `@mcp.tool()` | `lookup_ingredient`, `get_allergens`, `get_nutrition_per_100g`: the things the **model** decides to call. |
| `@mcp.resource("ingredients://allergen-flags")` (L111) | **A resource, not a tool.** The legend of the 14 allergen codes never changes, so the **app attaches it once** (via `attach_resources` in the config) instead of the model spending a tool call to fetch it every turn. That is the brief's "common mistake #3", avoided. |

**Tools, resources, prompts (the three things a server can offer):**
- **Tool:** the *model* decides to call it (for example "get allergens for tahini").
- **Resource:** the *app* decides to attach it as context (for example the allergen legend).
- **Prompt:** a reusable prompt template the *user* picks (not used this week).

---

### 3.5 `eval/capture_wire.py` + `wire.json`: taking the mystery out of MCP

| Lines | What it does |
|---|---|
| `MESSAGES` (L29) | Five JSON messages **typed by hand**: `initialize`, `notifications/initialized`, `tools/list`, and two `tools/call`. |
| `main` (L46) | Starts the ingredient server with plain `subprocess.Popen`, **with no MCP library**, writes each message as one line to its stdin, and reads the reply line from stdout. |

What you learn from reading `wire.json`:
- MCP over stdio is literally **one JSON object per line**.
- A **request** has an `id`, and the **response** carries the **same `id`**. That is how replies get matched.
- A **notification** has **no `id`**, and nobody replies to it.
- A tool that fails still comes back as a normal `result` with `isError: true`. That is *not* the same as a JSON-RPC `error`, which is reserved for protocol-level problems like an unknown method.
- None of the 9 messages contains a prompt, a model name or an API key. **That is the proof the AI isn't on the server.**

---

### 3.6 Bonus: `mcp_servers/gateway/`: one front door

```
host ──► gateway ──┬──► recipe_search
                   └──► ingredient_db
```

| Lines | What it does |
|---|---|
| `_TOKEN` / `_GRANT` / `CALLER` (L48-52) | Reads the token the host passed in (`GATEWAY_TOKEN`), hashes it, and looks the hash up in `tokens.json`. Only the **hash** is committed; the real token is in your `.env`. The match says the caller is `menu-bot` and it is denied `get_nutrition_per_100g`. |
| `lifespan` (L68) | When the gateway starts, it **becomes a client** of both real servers, connects, and collects their tools and resources. |
| `Server(...)` (L88) | Uses the *low-level* server instead of FastMCP. A proxy has no Python function signature to read, so it passes each upstream's schema through **unchanged**. |
| `_allowed` (L91) | Answers "is this caller allowed this tool?" That is policy, not AI. |
| `_audit` (L107) | **One line per call:** time, caller, tool, upstream, ingredient queried, allow/deny. |
| `list_tools` (L121) | Returns all 6 upstream tools as if they were its own. |
| `call_tool` (L126) | Unknown tool gives an error. Out of scope gives a **recoverable denial**: "permission denied... this is policy, not a fault, retrying will be denied again, here's what you *can* use, tell the user it's unavailable, don't estimate." Otherwise it forwards the call and passes the answer back untouched. |
| `mcp_config.gateway.json` | A different plug board with **one** server: the gateway. Switching to it is `--config mcp_config.gateway.json`, and still zero agent code changes. |

What happened when it ran (`out/gateway_audit.log`): allergen lookup was
**allowed**, nutrition was **denied twice**, and the final answer said *"I am
unable to provide the protein content"*. The model **did not make up a
number.** The honest wrinkle is that it retried the denied tool once, with a
different ingredient spelling, even though the message said not to.

---

## Part 4. What each deliverable proves

| Deliverable | The question it answers |
|---|---|
| `agent_diff.txt` | "Did you really add a server without touching the agent?" Yes: 0 lines in `rag/`. |
| `config_diff.txt` | "Then what *did* change?" 6 lines of JSON. |
| tool counts 3 -> 6 | "Was the discovery real?" The names came from the server's own `tools/list`, not from your notes. |
| `wire.json` | "Do you understand what's on the wire, and where the model is?" |
| `error_before_after.md` | "Do you understand that a docstring is a prompt, and that error text is too?" |
| `risk_note.md` | "Did you think before trusting someone else's code inside your app?" |

## Part 5. The brief's five "common mistakes" and where the code avoids them

1. **Hard-coding the tool list.** `mcp_host.py` never names a tool; it uses `tools/list`.
2. **Putting an LLM inside the MCP server.** None of the three servers imports a model SDK or holds a key. The host even strips API keys from their environment.
3. **Exposing the standing allergen matrix as a tool.** It is a **resource**, attached by the app.
4. **Swallowing errors into "lookup failed".** This was fixed on `search_recipes`, and the host separately labels a dead server as "connection failure, do not guess."
5. **Adding the third-party server just because it worked.** `risk_note.md` covers who wrote it, what it reaches, what it logs, what a stolen token could do, and whether to ship.

## Part 6. Mentor's Friday questions, answered in plain words

- **Does the agent use a tool through MCP, discovered rather than hard-coded?**
  Yes. Run `python -m rag.mcp_host --list-tools`: the names come from each server's `tools/list` reply.
- **Can you add a second tool without changing the agent's code?**
  Yes. I added a whole second server, 3 tools, with 6 lines of config. `git diff` on `rag/` is empty.
- **Did you build your own server another person's agent could call?**
  Yes. `mcp_servers/recipe_search` is a standard MCP server. Anyone's MCP host (Claude Desktop, Claude Code, another team's agent) can launch it with `python -m mcp_servers.recipe_search.server` and call its 3 tools.
- **Where does the AI run, and where doesn't it?**
  It runs in my app, the host, in `rag/llm.py`. It never runs in the MCP servers; they just execute tools and return JSON.
