"""Tolerant recipe-card parser.

The 6 new cards are supplied by the test kitchen, so this parser is deliberately
forgiving about their exact shape. It accepts:

  * YAML-ish frontmatter (``---`` fenced) OR inline ``Cuisine:`` / ``Dietary:``
    lines OR neither (metadata then falls back to the filename, and the card is
    reported as incomplete rather than silently defaulted).
  * GFM pipe tables (``| Ingredient | Weight | Baker's % |``) OR
    whitespace-aligned columns.
  * Markdown headings for sections, OR no headings at all (in which case the
    table itself is used as the structural anchor).

Run ``python -m rag.inspect_cards`` to see exactly what came out of this for
every card before anything gets embedded.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

# --------------------------------------------------------------------------
# Section classification
# --------------------------------------------------------------------------
SECTION_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("ingredients", re.compile(r"ingredient|formula|dough\s+build|components", re.I)),
    ("method", re.compile(r"method|instruction|step|process|procedure|direction|technique|build", re.I)),
    ("allergens", re.compile(r"allerg|contains|intoleran", re.I)),
    ("notes", re.compile(r"note|tip|storage|serving|yield|variation", re.I)),
]

HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
INLINE_META_RE = re.compile(
    r"^\s*(?:[-*]\s*)?(?:\*\*)?(recipe[ _-]?id|id|title|name|cuisine|dietary(?:[ _-]tags)?|tags|diet)"
    r"(?:\*\*)?\s*[:：]\s*(.+?)\s*$",
    re.I,
)
PIPE_ROW_RE = re.compile(r"^\s*\|.*\|\s*$")
PIPE_SEP_RE = re.compile(r"^\s*\|(?:\s*:?-{2,}:?\s*\|)+\s*$")
ALIGNED_SEP_RE = re.compile(r"^\s*-{2,}(\s+-{2,})+\s*$")
INGREDIENT_HEADER_RE = re.compile(r"ingredient|item|component", re.I)


def slugify(value: str) -> str:
    out = re.sub(r"[^a-z0-9]+", "-", value.strip().lower()).strip("-")
    return out or "unknown"


def _split_list(value: str) -> list[str]:
    value = value.strip().strip("[]")
    parts = re.split(r"[,;|]", value)
    return [slugify(p) for p in parts if p.strip()]


@dataclass
class TableRow:
    cells: list[str]
    raw: str
    line_no: int

    def label(self) -> str:
        return self.cells[0] if self.cells else ""


@dataclass
class Table:
    header: list[str]
    header_raw: str
    rows: list[TableRow]
    kind: str
    line_start: int
    line_end: int

    def header_line(self) -> str:
        """The column header, normalised back to a pipe row for re-prepending."""
        return "| " + " | ".join(self.header) + " |"


@dataclass
class Section:
    kind: str
    heading: str
    text: str
    line_start: int
    line_end: int
    char_start: int
    char_end: int


@dataclass
class Card:
    source_file: str
    source_path: Path
    recipe_id: str
    title: str
    cuisine: str
    dietary_tags: list[str]
    raw: str
    sections: list[Section] = field(default_factory=list)
    table: Table | None = None
    warnings: list[str] = field(default_factory=list)

    def section(self, kind: str) -> Section | None:
        for s in self.sections:
            if s.kind == kind:
                return s
        return None

    def sections_of(self, kind: str) -> list[Section]:
        return [s for s in self.sections if s.kind == kind]


# --------------------------------------------------------------------------
# Frontmatter
# --------------------------------------------------------------------------
def _parse_frontmatter(lines: list[str]) -> tuple[dict[str, str], int]:
    """Return (metadata, index of first body line)."""
    if not lines or lines[0].strip() not in {"---", "+++"}:
        return {}, 0
    fence = lines[0].strip()
    meta: dict[str, str] = {}
    for i in range(1, len(lines)):
        if lines[i].strip() == fence:
            return meta, i + 1
        if ":" in lines[i]:
            key, _, value = lines[i].partition(":")
            meta[key.strip().lower().replace("_", "").replace("-", "").replace(" ", "")] = value.strip()
    # Unterminated fence — treat as no frontmatter rather than eating the card.
    return {}, 0


# --------------------------------------------------------------------------
# Table extraction
# --------------------------------------------------------------------------
def _split_pipe(line: str) -> list[str]:
    inner = line.strip()
    if inner.startswith("|"):
        inner = inner[1:]
    if inner.endswith("|"):
        inner = inner[:-1]
    return [c.strip() for c in inner.split("|")]


def _find_pipe_table(lines: list[str], lo: int, hi: int) -> Table | None:
    i = lo
    while i < hi:
        if PIPE_ROW_RE.match(lines[i]) and i + 1 < hi and PIPE_SEP_RE.match(lines[i + 1]):
            header = _split_pipe(lines[i])
            rows: list[TableRow] = []
            j = i + 2
            while j < hi and PIPE_ROW_RE.match(lines[j]):
                cells = _split_pipe(lines[j])
                if any(c for c in cells):
                    rows.append(TableRow(cells=cells, raw=lines[j].rstrip(), line_no=j))
                j += 1
            if rows:
                return Table(
                    header=header,
                    header_raw=lines[i].rstrip(),
                    rows=rows,
                    kind="pipe",
                    line_start=i,
                    line_end=j - 1,
                )
            i = j
        else:
            i += 1
    return None


def _find_aligned_table(lines: list[str], lo: int, hi: int) -> Table | None:
    """Whitespace-aligned columns: two or more columns separated by 2+ spaces."""
    i = lo
    while i < hi:
        line = lines[i]
        cols = re.split(r"\s{2,}", line.strip())
        if len(cols) >= 2 and INGREDIENT_HEADER_RE.search(cols[0]):
            header = cols
            j = i + 1
            if j < hi and ALIGNED_SEP_RE.match(lines[j]):
                j += 1
            rows: list[TableRow] = []
            while j < hi and lines[j].strip():
                cells = re.split(r"\s{2,}", lines[j].strip())
                if len(cells) < 2:
                    break
                rows.append(TableRow(cells=cells, raw=lines[j].rstrip(), line_no=j))
                j += 1
            if rows:
                return Table(
                    header=header,
                    header_raw=line.rstrip(),
                    rows=rows,
                    kind="aligned",
                    line_start=i,
                    line_end=j - 1,
                )
        i += 1
    return None


def _find_table(lines: list[str], lo: int, hi: int) -> Table | None:
    return _find_pipe_table(lines, lo, hi) or _find_aligned_table(lines, lo, hi)


# --------------------------------------------------------------------------
# Main entry point
# --------------------------------------------------------------------------
def parse_card(path: Path) -> Card:
    raw = path.read_text(encoding="utf-8-sig")
    lines = raw.splitlines()

    # Char offset of the start of each line, so chunks can carry real spans.
    offsets: list[int] = []
    pos = 0
    for line in lines:
        offsets.append(pos)
        pos += len(line) + 1
    offsets.append(pos)

    warnings: list[str] = []
    meta, body_start = _parse_frontmatter(lines)

    # Inline `Key: value` metadata anywhere in the card supplements frontmatter.
    for idx in range(body_start, len(lines)):
        m = INLINE_META_RE.match(lines[idx])
        if m:
            key = m.group(1).lower().replace("_", "").replace("-", "").replace(" ", "")
            meta.setdefault(key, m.group(2).strip())

    # ---- sections -------------------------------------------------------
    heading_idxs = [i for i in range(body_start, len(lines)) if HEADING_RE.match(lines[i])]
    sections: list[Section] = []

    def make_section(kind: str, heading: str, start: int, end: int) -> Section:
        text = "\n".join(lines[start:end]).strip("\n")
        return Section(
            kind=kind,
            heading=heading,
            text=text,
            line_start=start,
            line_end=end - 1,
            char_start=offsets[start],
            char_end=offsets[min(end, len(lines))],
        )

    if heading_idxs:
        if heading_idxs[0] > body_start:
            pre = make_section("header", "", body_start, heading_idxs[0])
            if pre.text.strip():
                sections.append(pre)
        for n, hi_idx in enumerate(heading_idxs):
            end = heading_idxs[n + 1] if n + 1 < len(heading_idxs) else len(lines)
            heading_text = HEADING_RE.match(lines[hi_idx]).group(2)
            kind = "other"
            for name, pattern in SECTION_PATTERNS:
                if pattern.search(heading_text):
                    kind = name
                    break
            # A top-level h1 that is just the recipe name is a title, not a body
            # section — treat it as the header block.
            if kind == "other" and n == 0 and len(HEADING_RE.match(lines[hi_idx]).group(1)) == 1:
                kind = "header"
            sections.append(make_section(kind, heading_text, hi_idx, end))
    else:
        warnings.append("no markdown headings found; sections inferred from table position")

    # ---- table ----------------------------------------------------------
    table = None
    ing_sections = [s for s in sections if s.kind == "ingredients"]
    for s in ing_sections:
        table = _find_table(lines, s.line_start, s.line_end + 1)
        if table:
            break
    if table is None:
        table = _find_table(lines, body_start, len(lines))
        if table is not None and ing_sections:
            warnings.append("ingredient table found outside the Ingredients heading")

    # No headings at all: synthesise sections around the table.
    if not sections:
        if table is not None:
            if table.line_start > body_start:
                sections.append(make_section("header", "", body_start, table.line_start))
            sections.append(make_section("ingredients", "Ingredients", table.line_start, table.line_end + 1))
            if table.line_end + 1 < len(lines):
                sections.append(make_section("method", "Method", table.line_end + 1, len(lines)))
        else:
            sections.append(make_section("other", "", body_start, len(lines)))

    if table is None:
        warnings.append("NO INGREDIENT TABLE FOUND — structure-aware chunking will fall back to prose")

    # ---- metadata resolution -------------------------------------------
    stem = path.stem
    recipe_id = meta.get("recipeid") or meta.get("id") or ""
    if not recipe_id:
        recipe_id = slugify(stem)
        warnings.append(f"recipe_id not declared; derived '{recipe_id}' from filename")
    else:
        recipe_id = slugify(recipe_id)

    title = meta.get("title") or meta.get("name") or ""
    if not title:
        for s in sections:
            if s.kind == "header" and s.heading:
                title = s.heading
                break
        if not title:
            for i in range(body_start, len(lines)):
                m = HEADING_RE.match(lines[i])
                if m:
                    title = m.group(2)
                    break
    if not title:
        title = stem.replace("-", " ").replace("_", " ").title()
        warnings.append(f"title not declared; derived '{title}' from filename")

    cuisine_raw = meta.get("cuisine") or ""
    if cuisine_raw:
        cuisine = slugify(cuisine_raw)
    else:
        cuisine = "unspecified"
        warnings.append("cuisine not declared — REQUIREMENT 1 metadata is incomplete")

    tags_raw = meta.get("dietarytags") or meta.get("dietary") or meta.get("tags") or meta.get("diet") or ""
    dietary_tags = _split_list(tags_raw) if tags_raw else []
    if not dietary_tags:
        warnings.append("dietary_tags not declared — REQUIREMENT 1 metadata is incomplete")

    return Card(
        source_file=path.name,
        source_path=path,
        recipe_id=recipe_id,
        title=title.strip(),
        cuisine=cuisine,
        dietary_tags=dietary_tags,
        raw=raw,
        sections=sections,
        table=table,
        warnings=warnings,
    )


# Files that live alongside the cards but are not cards.
NON_CARD_STEMS = {"readme", "notes", "index", "_index", "license", "changelog"}


def load_cards(directory: Path) -> list[Card]:
    if not directory.exists():
        raise FileNotFoundError(f"card directory does not exist: {directory}")
    paths = sorted(
        p
        for p in directory.iterdir()
        if p.is_file()
        and p.suffix.lower() in {".md", ".markdown", ".txt"}
        and p.stem.lower() not in NON_CARD_STEMS
        and not p.name.startswith(".")
    )
    return [parse_card(p) for p in paths]
