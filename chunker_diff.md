# Code diff â€” the second chunker and the metadata fields

Submission-checklist item: *"Code diff showing the second chunker and the metadata fields."*

**An honest note on what kind of diff this is.** Both chunkers, and all the metadata plumbing,
landed in this repo's initial commit (`914fefc`), because the app was built for this task set
with the bake-off already in mind. There is therefore no before/after commit pair to show. What
follows instead is a real, machine-generated diff of **strategy A against strategy B** â€”
`git diff --no-index rag/chunkers/baseline.py rag/chunkers/structure_aware.py` â€” which is the
diff that actually answers the question "what does the second chunker do differently?". It is
verbatim command output, not a hand-written summary.

Reproduce it with:

```bash
git diff --no-index --unified=2 rag/chunkers/baseline.py rag/chunkers/structure_aware.py
```

## 1. Strategy A â†’ Strategy B

The three lines that carry the whole requirement-3 contract are, in the added side:

- `prefix = _recipe_prefix(card)` â€” built once per card as
  `Recipe: {title} (cuisine: {cuisine})`
- `header_line = table.header_line()` â€” the table's own `| Ingredient | Weight | Baker's % |`
- the `emit(...)` body that re-prepends **both** to every ingredient chunk:
  `f"{prefix}\nSection: Ingredients (rows N-M of T)\n{header_line}\n{separator}\n{row_lines}"`

and the loop bound that makes a mid-row cut impossible:

```python
for start in range(0, total, STRUCTURE_TABLE_ROWS_PER_CHUNK):
    group = rows[start : start + STRUCTURE_TABLE_ROWS_PER_CHUNK]
```

`rows` is a list of parsed `TableRow` objects, so the unit of division is a whole row. The row
budget is applied *before* the prefix is concatenated, so the repeated title and header can
never push a row out of its chunk.

Contrast the removed side, which slices on raw character offsets and knows nothing about rows:

```python
step = max(1, BASELINE_CHUNK_CHARS - BASELINE_OVERLAP_CHARS)   # 500 - 80 = 420
end = min(start + BASELINE_CHUNK_CHARS, n)
snap = max(text.rfind(" ", start, end), text.rfind("\n", start, end))
```

The whitespace snap is the only structural courtesy baseline extends â€” it protects words, not
rows, and not the title/row relationship.

```diff
diff --git a/rag/chunkers/baseline.py b/rag/chunkers/structure_aware.py
index 90334f6..bb080b1 100644
--- a/rag/chunkers/baseline.py
+++ b/rag/chunkers/structure_aware.py
@@ -1,85 +1,186 @@
-"""Strategy A — the chunker the app already had.
-
-A fixed-size sliding character window with overlap. It has no model of the
-document: no headings, no tables, no rows. It snaps cut points back to the
-nearest whitespace so it does not slice words in half, which is about as much
-sophistication as a naive splitter ever has.
-
-Deliberate fairness note: this runs over the FULL raw card text, frontmatter
-included. Stripping the frontmatter would have hidden the recipe title and
-cuisine from the baseline's first chunk and made the structure-aware chunker
-look better for a reason that has nothing to do with chunking. Baseline gets
-every character the other strategy gets.
+"""Strategy B — structure-aware.
+
+The contract from requirement 3: *never separate an ingredient row from its
+table header or its parent recipe title*. That is enforced structurally, not by
+tuning a size:
+
+  * Ingredient rows are grouped as whole ``TableRow`` objects, so a cut can
+    never land inside a row.
+  * Every ingredient chunk re-prepends the recipe title AND the table's column
+    header row. A chunk holding rows 9-12 of a table carries the same title and
+    the same ``| Ingredient | Weight | Baker's % |`` line as the chunk holding
+    rows 1-8.
+  * The row budget is applied before the prefix is added, so the repeated
+    prefix can never push rows out of a chunk.
+  * Method prose and the allergen note become their own title-prefixed chunks,
+    split on paragraph boundaries.
+
+Deliberate omission: ``dietary_tags`` are NOT written into the chunk text, only
+into metadata. If the tags were in the text they would move the embedding too,
+and the requirement-4 filter demo could no longer show that the *metadata
+filter* is what changed the ranking.
 """
 
 from __future__ import annotations
 
-from ..config import BASELINE_CHUNK_CHARS, BASELINE_OVERLAP_CHARS
-from ..parse import Card
-from .base import Chunk
+import re
 
-STRATEGY = "baseline"
+from ..config import STRUCTURE_PROSE_CHARS, STRUCTURE_TABLE_ROWS_PER_CHUNK
+from ..parse import Card, Section
+from .base import Chunk, line_offsets
 
+STRATEGY = "structure"
 
-def _label_section(card: Card, char_mid: int) -> str:
-    """Best-effort section label for the dump only.
 
-    The baseline chunker does not know about sections — this label is derived
-    afterwards, purely so the search dumps are readable and the failure
-    diagnosis can say which part of the card a chunk landed in. It is never
-    used for retrieval or for scoring.
-    """
-    for section in card.sections:
-        if section.char_start <= char_mid < section.char_end:
-            return f"~{section.kind}"
-    return "~unknown"
+def _recipe_prefix(card: Card) -> str:
+    return f"Recipe: {card.title} (cuisine: {card.cuisine})"
 
 
-def chunk_card(card: Card) -> list[Chunk]:
-    text = card.raw
-    n = len(text)
-    if n == 0:
-        return []
+def _split_paragraphs(text: str) -> list[str]:
+    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
+    return paras
+
+
+def _pack_paragraphs(paras: list[str], budget: int) -> list[str]:
+    """Pack whole paragraphs up to the budget; only split a paragraph that
+    exceeds the budget on its own, and then only on sentence boundaries."""
+    packed: list[str] = []
+    current: list[str] = []
+    size = 0
+
+    def flush() -> None:
+        nonlocal current, size
+        if current:
+            packed.append("\n\n".join(current))
+            current = []
+            size = 0
+
+    for para in paras:
+        if len(para) > budget:
+            flush()
+            sentences = re.split(r"(?<=[.!?])\s+", para)
+            buf: list[str] = []
+            buf_len = 0
+            for sentence in sentences:
+                if buf and buf_len + len(sentence) + 1 > budget:
+                    packed.append(" ".join(buf))
+                    buf, buf_len = [], 0
+                buf.append(sentence)
+                buf_len += len(sentence) + 1
+            if buf:
+                packed.append(" ".join(buf))
+            continue
+        if size + len(para) + 2 > budget and current:
+            flush()
+        current.append(para)
+        size += len(para) + 2
+
+    flush()
+    return packed
+
 
-    step = max(1, BASELINE_CHUNK_CHARS - BASELINE_OVERLAP_CHARS)
+def chunk_card(card: Card) -> list[Chunk]:
+    offsets = line_offsets(card.raw)
+    prefix = _recipe_prefix(card)
     chunks: list[Chunk] = []
-    start = 0
-    index = 0
-
-    while start < n:
-        end = min(start + BASELINE_CHUNK_CHARS, n)
-
-        # Snap the cut back to the last whitespace so words survive. This is
-        # the only structural courtesy the baseline extends — it knows nothing
-        # about table rows, so it will still cut straight through one.
-        if end < n:
-            snap = text.rfind(" ", start, end)
-            snap_nl = text.rfind("\n", start, end)
-            snap = max(snap, snap_nl)
-            if snap > start + step // 2:
-                end = snap
-
-        body = text[start:end].strip()
-        if body:
-            chunks.append(
-                Chunk(
-                    chunk_id=f"{card.recipe_id}::{STRATEGY}::c{index:03d}",
-                    text=body,
-                    strategy=STRATEGY,
-                    section=_label_section(card, (start + end) // 2),
-                    recipe_id=card.recipe_id,
-                    source_file=card.source_file,
-                    cuisine=card.cuisine,
-                    dietary_tags=list(card.dietary_tags),
-                    title=card.title,
-                    char_start=start,
-                    char_end=end,
-                )
+    counter = 0
+
+    def emit(text: str, section: str, char_start: int, char_end: int) -> None:
+        nonlocal counter
+        if not text.strip():
+            return
+        chunks.append(
+            Chunk(
+                chunk_id=f"{card.recipe_id}::{STRATEGY}::c{counter:03d}",
+                text=text.strip(),
+                strategy=STRATEGY,
+                section=section,
+                recipe_id=card.recipe_id,
+                source_file=card.source_file,
+                cuisine=card.cuisine,
+                dietary_tags=list(card.dietary_tags),
+                title=card.title,
+                char_start=char_start,
+                char_end=char_end,
+            )
+        )
+        counter += 1
+
+    # ---- 1. title / header block ---------------------------------------
+    header_sections = card.sections_of("header")
+    header_body = "\n\n".join(s.text for s in header_sections if s.text.strip())
+    header_start = header_sections[0].char_start if header_sections else 0
+    header_end = header_sections[-1].char_end if header_sections else 0
+    emit(
+        f"{prefix}\nSection: Title\n{header_body}".strip(),
+        "title",
+        header_start,
+        header_end,
+    )
+
+    # ---- 2. ingredient table -------------------------------------------
+    table = card.table
+    if table is not None:
+        rows = table.rows
+        total = len(rows)
+        header_line = table.header_line()
+        separator = "| " + " | ".join("---" for _ in table.header) + " |"
+
+        for start in range(0, total, STRUCTURE_TABLE_ROWS_PER_CHUNK):
+            group = rows[start : start + STRUCTURE_TABLE_ROWS_PER_CHUNK]
+            first, last = group[0], group[-1]
+            row_lines = "\n".join(
+                "| " + " | ".join(r.cells) + " |" if table.kind == "aligned" else r.raw.strip()
+                for r in group
+            )
+            body = (
+                f"{prefix}\n"
+                f"Section: Ingredients (rows {start + 1}-{start + len(group)} of {total})\n"
+                f"{header_line}\n{separator}\n{row_lines}"
+            )
+            emit(
+                body,
+                "ingredients",
+                offsets[first.line_no],
+                offsets[min(last.line_no + 1, len(offsets) - 1)],
             )
-            index += 1
 
-        if end >= n:
-            break
-        start += step
+    # ---- 3. every other section, as prose ------------------------------
+    table_lines: set[int] = set()
+    if table is not None:
+        table_lines = set(range(table.line_start, table.line_end + 1))
+
+    def section_prose(section: Section) -> str:
+        """Section text with the table's own lines removed."""
+        if not table_lines:
+            return section.text
+        kept = [
+            line
+            for i, line in enumerate(
+                card.raw.splitlines()[section.line_start : section.line_end + 1],
+                start=section.line_start,
+            )
+            if i not in table_lines
+        ]
+        return "\n".join(kept)
+
+    for section in card.sections:
+        if section.kind == "header":
+            continue
+        body = section_prose(section)
+        # Drop the heading line itself from the body; it is restated in the prefix.
+        body = re.sub(r"^#{1,6}\s+.*\n?", "", body, count=1)
+        paras = _split_paragraphs(body)
+        if not paras:
+            continue
+
+        label = section.heading or section.kind.title()
+        for part in _pack_paragraphs(paras, STRUCTURE_PROSE_CHARS):
+            emit(
+                f"{prefix}\nSection: {label}\n{part}",
+                section.kind if section.kind != "other" else "notes",
+                section.char_start,
+                section.char_end,
+            )
 
     return chunks
```

## 2. The metadata fields (requirement 1)

`rag/chunkers/base.py` â€” both chunkers emit exactly this shape, so the only variable between
the two indexes is where the text was cut, never what metadata rides along with it.

```python
@dataclass
class Chunk:
    chunk_id: str
    text: str
    strategy: str
    section: str
    recipe_id: str
    source_file: str
    cuisine: str
    dietary_tags: list[str]
    title: str
    char_start: int
    char_end: int

    def metadata(self) -> dict[str, str | int | bool]:
        md: dict[str, str | int | bool] = {
            "chunk_id": self.chunk_id,
            "source_file": self.source_file,
            "recipe_id": self.recipe_id,
            "cuisine": self.cuisine,
            "title": self.title,
            "dietary_tags": "|".join(self.dietary_tags),
            "section": self.section,
            "strategy": self.strategy,
            "char_start": self.char_start,
            "char_end": self.char_end,
        }
        for tag in self.dietary_tags:
            md[tag_key(tag)] = True
        return md


def tag_key(tag: str) -> str:
    """Chroma metadata keys must be plain identifiers."""
    return "tag_" + re.sub(r"[^a-z0-9]+", "_", tag.lower()).strip("_")
```

The four fields requirement 1 names â€” `source_file`, `recipe_id`, `cuisine`, `dietary_tags` â€”
are all present, plus `chunk_id` so citations can be resolved back to stored text.

**Why `dietary_tags` is stored twice.** Chroma metadata values must be scalars, so a list is
not storable. It is written once as a pipe-delimited string (`vegan|gluten-free|dairy-free`)
for display and citation, and exploded into one boolean per tag (`tag_vegan: True`) so that
`where={"tag_vegan": True}` is a genuine indexed filter applied **before** ranking, rather than
a substring match applied to an already-ranked list. `rag/store.py::search` passes `where`
straight through to `collection.query`, and its docstring states the consequence:

```python
"""Search-only. No LLM is involved on this path at all.

``where`` is applied by Chroma BEFORE ranking, so a filtered query re-ranks
the surviving subset rather than trimming an unfiltered top-k.
"""
```

That distinction is what makes the requirement-4 demo meaningful: filtered survivors keep their
exact unfiltered scores (0.1819 stays 0.1819), which proves the filter restricted the candidate
set rather than re-scoring it.

**Ingest refuses incomplete metadata.** `rag/ingest.py` asserts `source_file` and `recipe_id`
on every chunk and aborts the ingest if either is missing â€” "a chunk with no `source_file` is a
failed ingest", as the brief puts it â€” and by default also requires `cuisine` and
`dietary_tags`. The assertions print into every ingest proof in `out/ingest_new-drop.md`.

## 3. This measurement run's own changes

New, untracked â€” the corpus and the question set:

```
data/new_drop/card-01-country-sourdough-2kg.md
data/new_drop/card-02-napa-kimchi.md
data/new_drop/card-03-half-sour-dill-pickles.md
data/new_drop/card-04-red-cabbage-sauerkraut.md
data/new_drop/card-05-milk-kefir.md
data/new_drop/card-06-white-rice-miso.md
out/ingest_new-drop.md
out/ingest_new-drop_baseline.md
out/ingest_new-drop_structure.md
```

Modified:

```
eval/questions.json          50 insertions(+), 39 deletions(-)   placeholder set -> the 8 measured questions
out/questions.lock.json      new sha256 locked at the first measured run
out/hitrate.md               the two numbers, regenerated
out/search_dump_baseline.md  all 8 top-5 lists, baseline
out/search_dump_structure.md all 8 top-5 lists, structure-aware
out/filter_demo.md           208-comparison filter sweep
```

No file under `rag/` was touched during the measurement. The chunkers, the metadata shape and
the embedding config are byte-identical to the committed versions, which is the point: the only
things that changed between the placeholder run and this one are the corpus and the questions.
