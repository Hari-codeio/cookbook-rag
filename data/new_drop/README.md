# Drop the 6 fermentation-chapter cards here

Put the 6 supplied recipe cards in this directory as `.md` (or `.txt`) files, one per
recipe. **Delete this README first** — the loader treats every `.md`/`.txt` file in the
directory as a card, and this file would be ingested as a tenth recipe.

Then run:

```bash
.venv/Scripts/python -m rag.inspect_cards --dir data/new_drop
```

and check each card shows a real `cuisine`, non-empty `dietary_tags`, and a parsed table
with the row count you expect. Fix anything the parser flags **before** ingesting.

## What the parser looks for

It is deliberately tolerant, but it can only find metadata that is actually written down.
The shape below is what it reads most reliably:

```markdown
---
recipe_id: sourdough-2kg
title: 2kg Country Sourdough
cuisine: european
dietary_tags: [vegan, dairy-free]
---

# 2kg Country Sourdough

## Ingredients

| Ingredient | Weight | Baker's % |
| --- | --- | --- |
| Strong white flour | 1000 g | 100% |
| Fine sea salt | 7 g | 0.7% |

## Method

Loose method prose...

## Allergens

Contains wheat (gluten).
```

Accepted variations:

- **Metadata** — frontmatter as above, *or* inline lines anywhere in the card
  (`Cuisine: European`, `Dietary: vegan, dairy-free`), *or* neither, in which case
  `recipe_id` falls back to the filename and the card is reported as incomplete.
- **Tables** — GFM pipe tables as above, *or* whitespace-aligned columns
  (`Ingredient    Weight    Baker's %`). Any column headers work; nothing assumes
  the word "Baker's".
- **Sections** — headings matching ingredient / method / allergen / note are
  classified automatically. A card with no headings at all still parses: the table
  is used as the anchor, and prose after it is treated as method.

`cuisine` and `dietary_tags` are required by requirement 1, so ingest **fails** if a card
omits them. That is deliberate. Use `--allow-incomplete-metadata` to override if you
genuinely need to.
