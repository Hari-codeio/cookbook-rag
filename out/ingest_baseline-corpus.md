### Ingest proof — baseline-corpus / strategy=baseline

```
timestamp            : 2026-08-12T12:57:40+00:00
directory read       : data\baseline   (ONLY this directory was read)
files read           : 9
  - beef-bourguignon.md  [recipe_id=beef-bourguignon]
  - chana-masala.md  [recipe_id=chana-masala]
  - chicken-tikka-masala.md  [recipe_id=chicken-tikka-masala]
  - classic-focaccia.md  [recipe_id=classic-focaccia]
  - congee.md  [recipe_id=congee]
  - lemon-drizzle-cake.md  [recipe_id=lemon-drizzle-cake]
  - pad-thai.md  [recipe_id=pad-thai]
  - sesame-soy-aubergine.md  [recipe_id=sesame-soy-aubergine]
  - shakshuka.md  [recipe_id=shakshuka]
embedding model      : all-MiniLM-L6-v2 (chromadb ONNX DefaultEmbeddingFunction)
chunks BEFORE        : 0
chunks ADDED         : 30
chunks AFTER         : 30
delta check          : 0 + 30 = 30 (OK)
pre-existing rewritten: 0 (append-only; ingest aborts on any id clash)
wall clock           : 13234 ms
assertions:
  - PASS  source_file present on all 30 chunks
  - PASS  recipe_id present on all 30 chunks
  - PASS  cuisine + dietary_tags present on all chunks
```

### Ingest proof — baseline-corpus / strategy=structure

```
timestamp            : 2026-08-12T12:57:43+00:00
directory read       : data\baseline   (ONLY this directory was read)
files read           : 9
  - beef-bourguignon.md  [recipe_id=beef-bourguignon]
  - chana-masala.md  [recipe_id=chana-masala]
  - chicken-tikka-masala.md  [recipe_id=chicken-tikka-masala]
  - classic-focaccia.md  [recipe_id=classic-focaccia]
  - congee.md  [recipe_id=congee]
  - lemon-drizzle-cake.md  [recipe_id=lemon-drizzle-cake]
  - pad-thai.md  [recipe_id=pad-thai]
  - sesame-soy-aubergine.md  [recipe_id=sesame-soy-aubergine]
  - shakshuka.md  [recipe_id=shakshuka]
embedding model      : all-MiniLM-L6-v2 (chromadb ONNX DefaultEmbeddingFunction)
chunks BEFORE        : 0
chunks ADDED         : 43
chunks AFTER         : 43
delta check          : 0 + 43 = 43 (OK)
pre-existing rewritten: 0 (append-only; ingest aborts on any id clash)
wall clock           : 2899 ms
assertions:
  - PASS  source_file present on all 43 chunks
  - PASS  recipe_id present on all 43 chunks
  - PASS  cuisine + dietary_tags present on all chunks
```
