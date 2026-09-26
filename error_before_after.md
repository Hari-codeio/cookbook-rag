# search_recipes: docstring as prompt, and a recoverable no-match

Server: **our own** `recipe-search` server (`mcp_servers/recipe_search/server.py`).
Tool: `search_recipes`. Only this tool's docstring and its no-match error path changed.

- Before = commit `7225574` (the Week 9 base server, both servers configured)
- After = commit `1bd5043`
- Agent module unchanged between them (`git diff 7225574 1bd5043 -- rag/` is empty).
- Model: `gemini-3.1-flash-lite`, temperature 0, same budgets for every run (8 laps).
- Full raw transcripts: `out/error_before.txt`, `out/error_after.txt`,
  `out/error_before_absent.txt`, `out/error_after_absent.txt`.

## What changed

### The docstring (FastMCP sends this to the model as the tool `description`)

Before, written for a developer:

```
Name match over the 21 cards. No embedding call, so it is free and fast.
```

After, written as a prompt for the model:

```
FIND a recipe in the 21-card archive by dish name. Call this FIRST:
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
with that dish listed under "unsupported".
```

The before text answers the developer's questions (is it cheap? does it embed?).
The after text answers the model's: when do I call this, what do I pass, what do I
get back, what is it NOT for, and what should I do when it fails.

### The error path

| Case | Before (what the model read) | After (what the model read) |
|---|---|---|
| misspelt | `Error: lookup failed` | `no recipe title matched 'shakshouka'. Close spellings in the archive: 'Red Pepper Shakshuka' (recipe_id 'shakshuka'). If that is the dish the user meant, call search_recipes again with query='shakshuka'. This is a no-match, not a server fault.` |
| not in archive | `Error: lookup failed` | `no recipe title matched 'moussaka', and no title is spelled like it: this dish is not in the 21-card archive. Searching again will not find it. Answer now, with 'moussaka' under "unsupported". This is a no-match, not a server fault.` |

"Error: lookup failed" leaves three questions open: was it a miss or a broken
server? is a retry worth it? with what? The new message answers all three.

## Transcript 1: the same failing call, `search_recipes("moussaka")`

Request: `Make the moussaka 2x`. There is no moussaka among the 21 cards.

**Before** (`out/error_before_absent.txt`)

```
lap 1  model -> search_recipes({"query": "moussaka"})
       tool  -> isError: "Error executing tool search_recipes: Error: lookup failed"
lap 2  model -> search_recipes({"query": "Moussaka"})
       tool  -> isError: "... Error: lookup failed"
lap 3  model -> search_recipes({"query": "moussaka"})
       tool  -> isError: "... Error: lookup failed"
lap 4..7  the same call, the same error, four more times
lap 8  budget_exceeded: max_laps
ok: False   answer: none   tokens: 11,800
```

The model treated the error like a flaky server: it retried the identical call
seven times (the only variation was capitalisation) until the lap budget ended the
run. From "lookup failed" it cannot tell that the dish does not exist.

**After** (`out/error_after_absent.txt`)

```
lap 1  model -> search_recipes({"query": "moussaka"})
       tool  -> isError: "no recipe title matched 'moussaka', and no title is spelled
                like it: this dish is not in the 21-card archive. Searching again will
                not find it. Answer now, with 'moussaka' under "unsupported". ..."
lap 2  model -> final answer  {"substitutions": [], "unsupported": "moussaka", ...}
ok: True   tokens: 3,113
```

It stopped after one call and said honestly that it could not do this.

## Transcript 2: the same failing call, `search_recipes("shakshouka")`

Request: `Make the shakshouka 1.5x and take out the egg` (misspelt; the card is `shakshuka`).

**Before** (`out/error_before.txt`)

```
lap 1  model -> search_recipes({"query": "shakshouka"})
       tool  -> isError: "Error executing tool search_recipes: Error: lookup failed"
lap 2  model -> search_recipes({"query": "shakshuka"})      <- respelt from its own memory
       tool  -> ok
lap 3  scale_recipe  ->  lap 4..8  get_allergens / lookup_ingredient on egg substitutes
lap 8  budget_exceeded: max_laps
ok: False   tokens: 16,432
```

**After** (`out/error_after.txt`)

```
lap 1  model -> search_recipes({"query": "shakshouka"})
       tool  -> isError: "... Close spellings in the archive: 'Red Pepper Shakshuka'
                (recipe_id 'shakshuka'). ... call search_recipes again with query='shakshuka'. ..."
lap 2  model -> search_recipes({"query": "shakshuka"})      <- the query the error gave it
       tool  -> ok
lap 3  scale_recipe  ->  lap 4  get_allergen_profile(contains-egg)  ->  lap 5  answer
ok: True   tokens: 10,722
```

Read this pair carefully. The search step takes 2 laps both times. Before, the
model **guessed** the right spelling. That worked only because shakshuka is a famous
dish it already knows. After, it **was told** the spelling by the archive itself. On a
dish the model does not know, the guess has nothing to go on. That is transcript 1.

The lap difference after the search (8 vs 5) is mostly NOT the error rewrite. In
the before run the model spent laps 4 to 8 exploring egg substitutes on the
ingredient server, and in the after run it went straight to `get_allergen_profile`.
That is path variance between runs, and I do not claim it for this change.

## Numbers

| Failing call | Before | After |
|---|---|---|
| `moussaka` (not in archive) | 8 laps, **no answer** (max_laps), 11,800 tokens, 7 identical retries | **2 laps**, answered `unsupported: moussaka`, 3,113 tokens, 0 retries |
| `shakshouka` (misspelt) | retry was a guess from model memory; run hit max_laps | retry used the query the error supplied; answered in 5 laps |

One run per cell. At temperature 0 the moussaka pair is the clean result: the
same first call, the same model, and the error message is the only thing that differs.
