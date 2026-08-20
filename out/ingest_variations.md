### Ingest proof — variations / strategy=baseline

```
timestamp            : 2026-08-19T14:58:09+00:00
directory read       : data\variations   (ONLY this directory was read)
files read           : 6
  - card-07-gluten-free-brioche.md  [recipe_id=gf-brioche]
  - card-08-classic-brioche.md  [recipe_id=classic-brioche]
  - card-09-chocolate-brioche.md  [recipe_id=chocolate-brioche]
  - card-10-gluten-free-sandwich-loaf.md  [recipe_id=gf-sandwich-loaf]
  - card-11-wholemeal-sourdough.md  [recipe_id=wholemeal-sourdough]
  - card-12-light-rye-sourdough.md  [recipe_id=rye-sourdough]
embedding model      : all-MiniLM-L6-v2 (chromadb ONNX DefaultEmbeddingFunction)
chunks BEFORE        : 52
chunks ADDED         : 18
chunks AFTER         : 70
delta check          : 52 + 18 = 70 (OK)
pre-existing rewritten: 0 (append-only; ingest aborts on any id clash)
wall clock           : 933 ms
assertions:
  - PASS  source_file present on all 18 chunks
  - PASS  recipe_id present on all 18 chunks
  - PASS  cuisine + dietary_tags present on all chunks
```

### Ingest proof — variations / strategy=structure

```
timestamp            : 2026-08-19T14:58:10+00:00
directory read       : data\variations   (ONLY this directory was read)
files read           : 6
  - card-07-gluten-free-brioche.md  [recipe_id=gf-brioche]
  - card-08-classic-brioche.md  [recipe_id=classic-brioche]
  - card-09-chocolate-brioche.md  [recipe_id=chocolate-brioche]
  - card-10-gluten-free-sandwich-loaf.md  [recipe_id=gf-sandwich-loaf]
  - card-11-wholemeal-sourdough.md  [recipe_id=wholemeal-sourdough]
  - card-12-light-rye-sourdough.md  [recipe_id=rye-sourdough]
embedding model      : all-MiniLM-L6-v2 (chromadb ONNX DefaultEmbeddingFunction)
chunks BEFORE        : 70
chunks ADDED         : 24
chunks AFTER         : 94
delta check          : 70 + 24 = 94 (OK)
pre-existing rewritten: 0 (append-only; ingest aborts on any id clash)
wall clock           : 803 ms
assertions:
  - PASS  source_file present on all 24 chunks
  - PASS  recipe_id present on all 24 chunks
  - PASS  cuisine + dietary_tags present on all chunks
```
