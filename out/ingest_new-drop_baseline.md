### Ingest proof — new-drop / strategy=baseline

```
timestamp            : 2026-08-13T01:56:44+00:00
directory read       : data\new_drop   (ONLY this directory was read)
files read           : 6
  - card-01-country-sourdough-2kg.md  [recipe_id=sourdough-2kg]
  - card-02-napa-kimchi.md  [recipe_id=napa-kimchi]
  - card-03-half-sour-dill-pickles.md  [recipe_id=dill-pickles]
  - card-04-red-cabbage-sauerkraut.md  [recipe_id=red-sauerkraut]
  - card-05-milk-kefir.md  [recipe_id=milk-kefir]
  - card-06-white-rice-miso.md  [recipe_id=white-miso]
embedding model      : all-MiniLM-L6-v2 (chromadb ONNX DefaultEmbeddingFunction)
chunks BEFORE        : 30
chunks ADDED         : 22
chunks AFTER         : 52
delta check          : 30 + 22 = 52 (OK)
pre-existing rewritten: 0 (append-only; ingest aborts on any id clash)
wall clock           : 1314 ms
assertions:
  - PASS  source_file present on all 22 chunks
  - PASS  recipe_id present on all 22 chunks
  - PASS  cuisine + dietary_tags present on all chunks
```
