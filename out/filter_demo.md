# Metadata filter on dietary_tags — unfiltered vs filtered

```
strategy        : structure
embedding model : all-MiniLM-L6-v2 (chromadb ONNX DefaultEmbeddingFunction)
top-k           : 5
dietary tags    : ['contains-alcohol', 'contains-dairy', 'contains-egg', 'contains-peanut', 'contains-sesame', 'contains-shellfish', 'contains-soy', 'dairy-free', 'gluten-free', 'nut-free', 'vegan', 'vegetarian']
generated       : 2026-08-12T13:29:14+00:00
```

Swept 16 quer(y/ies) x 12 tag(s) = 192 comparisons; **141** of them changed the top-1 result.

## Cases where the filter changed top-1

**Query:** `How much double cream is in the chicken tikka masala?`
**Filter:** `where={'tag_dairy_free': True}`  (dietary_tags contains `dairy-free`)

```text
UNFILTERED  (top-5)
  1. score=0.7079  chicken-tikka-masala::structure::c001
     recipe_id=chicken-tikka-masala  section=ingredients  dietary_tags=[gluten-free|contains-dairy]
  2. score=0.6636  chicken-tikka-masala::structure::c002
     recipe_id=chicken-tikka-masala  section=ingredients  dietary_tags=[gluten-free|contains-dairy]
  3. score=0.6205  chicken-tikka-masala::structure::c000
     recipe_id=chicken-tikka-masala  section=title  dietary_tags=[gluten-free|contains-dairy]
  4. score=0.6106  chicken-tikka-masala::structure::c003
     recipe_id=chicken-tikka-masala  section=method  dietary_tags=[gluten-free|contains-dairy]
  5. score=0.6071  chicken-tikka-masala::structure::c004
     recipe_id=chicken-tikka-masala  section=allergens  dietary_tags=[gluten-free|contains-dairy]

FILTERED    (top-5)  where={'tag_dairy_free': True}
  1. score=0.5479  chana-masala::structure::c002
     recipe_id=chana-masala  section=ingredients  dietary_tags=[vegan|gluten-free|dairy-free]
  2. score=0.5440  chana-masala::structure::c001
     recipe_id=chana-masala  section=ingredients  dietary_tags=[vegan|gluten-free|dairy-free]
  3. score=0.5179  chana-masala::structure::c003
     recipe_id=chana-masala  section=method  dietary_tags=[vegan|gluten-free|dairy-free]
  4. score=0.4667  chana-masala::structure::c000
     recipe_id=chana-masala  section=title  dietary_tags=[vegan|gluten-free|dairy-free]
  5. score=0.4311  chana-masala::structure::c004
     recipe_id=chana-masala  section=allergens  dietary_tags=[vegan|gluten-free|dairy-free]

top-1 unfiltered : chicken-tikka-masala::structure::c001 (recipe_id=chicken-tikka-masala, score=0.7079)
top-1 filtered   : chana-masala::structure::c002 (recipe_id=chana-masala, score=0.5479)
TOP-1 CHANGED    : YES
```

**Query:** `How much double cream is in the chicken tikka masala?`
**Filter:** `where={'tag_vegan': True}`  (dietary_tags contains `vegan`)

```text
UNFILTERED  (top-5)
  1. score=0.7079  chicken-tikka-masala::structure::c001
     recipe_id=chicken-tikka-masala  section=ingredients  dietary_tags=[gluten-free|contains-dairy]
  2. score=0.6636  chicken-tikka-masala::structure::c002
     recipe_id=chicken-tikka-masala  section=ingredients  dietary_tags=[gluten-free|contains-dairy]
  3. score=0.6205  chicken-tikka-masala::structure::c000
     recipe_id=chicken-tikka-masala  section=title  dietary_tags=[gluten-free|contains-dairy]
  4. score=0.6106  chicken-tikka-masala::structure::c003
     recipe_id=chicken-tikka-masala  section=method  dietary_tags=[gluten-free|contains-dairy]
  5. score=0.6071  chicken-tikka-masala::structure::c004
     recipe_id=chicken-tikka-masala  section=allergens  dietary_tags=[gluten-free|contains-dairy]

FILTERED    (top-5)  where={'tag_vegan': True}
  1. score=0.5479  chana-masala::structure::c002
     recipe_id=chana-masala  section=ingredients  dietary_tags=[vegan|gluten-free|dairy-free]
  2. score=0.5440  chana-masala::structure::c001
     recipe_id=chana-masala  section=ingredients  dietary_tags=[vegan|gluten-free|dairy-free]
  3. score=0.5179  chana-masala::structure::c003
     recipe_id=chana-masala  section=method  dietary_tags=[vegan|gluten-free|dairy-free]
  4. score=0.4667  chana-masala::structure::c000
     recipe_id=chana-masala  section=title  dietary_tags=[vegan|gluten-free|dairy-free]
  5. score=0.4311  chana-masala::structure::c004
     recipe_id=chana-masala  section=allergens  dietary_tags=[vegan|gluten-free|dairy-free]

top-1 unfiltered : chicken-tikka-masala::structure::c001 (recipe_id=chicken-tikka-masala, score=0.7079)
top-1 filtered   : chana-masala::structure::c002 (recipe_id=chana-masala, score=0.5479)
TOP-1 CHANGED    : YES
```

**Query:** `a dish finished with fresh herbs`
**Filter:** `where={'tag_contains_egg': True}`  (dietary_tags contains `contains-egg`)

```text
UNFILTERED  (top-5)
  1. score=0.4981  classic-focaccia::structure::c001
     recipe_id=classic-focaccia  section=ingredients  dietary_tags=[vegan|dairy-free|nut-free]
  2. score=0.4828  shakshuka::structure::c002
     recipe_id=shakshuka  section=ingredients  dietary_tags=[vegetarian|gluten-free|contains-egg]
  3. score=0.4663  congee::structure::c001
     recipe_id=congee  section=ingredients  dietary_tags=[vegan|gluten-free|dairy-free|nut-free]
  4. score=0.4659  classic-focaccia::structure::c003
     recipe_id=classic-focaccia  section=allergens  dietary_tags=[vegan|dairy-free|nut-free]
  5. score=0.4659  chana-masala::structure::c001
     recipe_id=chana-masala  section=ingredients  dietary_tags=[vegan|gluten-free|dairy-free]

FILTERED    (top-5)  where={'tag_contains_egg': True}
  1. score=0.4828  shakshuka::structure::c002
     recipe_id=shakshuka  section=ingredients  dietary_tags=[vegetarian|gluten-free|contains-egg]
  2. score=0.4594  shakshuka::structure::c001
     recipe_id=shakshuka  section=ingredients  dietary_tags=[vegetarian|gluten-free|contains-egg]
  3. score=0.4211  shakshuka::structure::c003
     recipe_id=shakshuka  section=method  dietary_tags=[vegetarian|gluten-free|contains-egg]
  4. score=0.4203  shakshuka::structure::c000
     recipe_id=shakshuka  section=title  dietary_tags=[vegetarian|gluten-free|contains-egg]
  5. score=0.4112  pad-thai::structure::c002
     recipe_id=pad-thai  section=ingredients  dietary_tags=[gluten-free|contains-egg|contains-shellfish|contains-peanut]

top-1 unfiltered : classic-focaccia::structure::c001 (recipe_id=classic-focaccia, score=0.4981)
top-1 filtered   : shakshuka::structure::c002 (recipe_id=shakshuka, score=0.4828)
TOP-1 CHANGED    : YES
```

**Query:** `a dish finished with fresh herbs`
**Filter:** `where={'tag_gluten_free': True}`  (dietary_tags contains `gluten-free`)

```text
UNFILTERED  (top-5)
  1. score=0.4981  classic-focaccia::structure::c001
     recipe_id=classic-focaccia  section=ingredients  dietary_tags=[vegan|dairy-free|nut-free]
  2. score=0.4828  shakshuka::structure::c002
     recipe_id=shakshuka  section=ingredients  dietary_tags=[vegetarian|gluten-free|contains-egg]
  3. score=0.4663  congee::structure::c001
     recipe_id=congee  section=ingredients  dietary_tags=[vegan|gluten-free|dairy-free|nut-free]
  4. score=0.4659  classic-focaccia::structure::c003
     recipe_id=classic-focaccia  section=allergens  dietary_tags=[vegan|dairy-free|nut-free]
  5. score=0.4659  chana-masala::structure::c001
     recipe_id=chana-masala  section=ingredients  dietary_tags=[vegan|gluten-free|dairy-free]

FILTERED    (top-5)  where={'tag_gluten_free': True}
  1. score=0.4828  shakshuka::structure::c002
     recipe_id=shakshuka  section=ingredients  dietary_tags=[vegetarian|gluten-free|contains-egg]
  2. score=0.4663  congee::structure::c001
     recipe_id=congee  section=ingredients  dietary_tags=[vegan|gluten-free|dairy-free|nut-free]
  3. score=0.4659  chana-masala::structure::c001
     recipe_id=chana-masala  section=ingredients  dietary_tags=[vegan|gluten-free|dairy-free]
  4. score=0.4594  shakshuka::structure::c001
     recipe_id=shakshuka  section=ingredients  dietary_tags=[vegetarian|gluten-free|contains-egg]
  5. score=0.4325  congee::structure::c000
     recipe_id=congee  section=title  dietary_tags=[vegan|gluten-free|dairy-free|nut-free]

top-1 unfiltered : classic-focaccia::structure::c001 (recipe_id=classic-focaccia, score=0.4981)
top-1 filtered   : shakshuka::structure::c002 (recipe_id=shakshuka, score=0.4828)
TOP-1 CHANGED    : YES
```

**Query:** `a dish finished with fresh herbs`
**Filter:** `where={'tag_vegetarian': True}`  (dietary_tags contains `vegetarian`)

```text
UNFILTERED  (top-5)
  1. score=0.4981  classic-focaccia::structure::c001
     recipe_id=classic-focaccia  section=ingredients  dietary_tags=[vegan|dairy-free|nut-free]
  2. score=0.4828  shakshuka::structure::c002
     recipe_id=shakshuka  section=ingredients  dietary_tags=[vegetarian|gluten-free|contains-egg]
  3. score=0.4663  congee::structure::c001
     recipe_id=congee  section=ingredients  dietary_tags=[vegan|gluten-free|dairy-free|nut-free]
  4. score=0.4659  classic-focaccia::structure::c003
     recipe_id=classic-focaccia  section=allergens  dietary_tags=[vegan|dairy-free|nut-free]
  5. score=0.4659  chana-masala::structure::c001
     recipe_id=chana-masala  section=ingredients  dietary_tags=[vegan|gluten-free|dairy-free]

FILTERED    (top-5)  where={'tag_vegetarian': True}
  1. score=0.4828  shakshuka::structure::c002
     recipe_id=shakshuka  section=ingredients  dietary_tags=[vegetarian|gluten-free|contains-egg]
  2. score=0.4594  shakshuka::structure::c001
     recipe_id=shakshuka  section=ingredients  dietary_tags=[vegetarian|gluten-free|contains-egg]
  3. score=0.4211  shakshuka::structure::c003
     recipe_id=shakshuka  section=method  dietary_tags=[vegetarian|gluten-free|contains-egg]
  4. score=0.4203  shakshuka::structure::c000
     recipe_id=shakshuka  section=title  dietary_tags=[vegetarian|gluten-free|contains-egg]
  5. score=0.3421  shakshuka::structure::c004
     recipe_id=shakshuka  section=allergens  dietary_tags=[vegetarian|gluten-free|contains-egg]

top-1 unfiltered : classic-focaccia::structure::c001 (recipe_id=classic-focaccia, score=0.4981)
top-1 filtered   : shakshuka::structure::c002 (recipe_id=shakshuka, score=0.4828)
TOP-1 CHANGED    : YES
```

**Query:** `a creamy spiced dish with tomatoes and onion`
**Filter:** `where={'tag_dairy_free': True}`  (dietary_tags contains `dairy-free`)

```text
UNFILTERED  (top-5)
  1. score=0.4964  shakshuka::structure::c003
     recipe_id=shakshuka  section=method  dietary_tags=[vegetarian|gluten-free|contains-egg]
  2. score=0.4953  shakshuka::structure::c001
     recipe_id=shakshuka  section=ingredients  dietary_tags=[vegetarian|gluten-free|contains-egg]
  3. score=0.4801  congee::structure::c001
     recipe_id=congee  section=ingredients  dietary_tags=[vegan|gluten-free|dairy-free|nut-free]
  4. score=0.4789  beef-bourguignon::structure::c002
     recipe_id=beef-bourguignon  section=ingredients  dietary_tags=[dairy-free|contains-alcohol]
  5. score=0.4544  chana-masala::structure::c001
     recipe_id=chana-masala  section=ingredients  dietary_tags=[vegan|gluten-free|dairy-free]

FILTERED    (top-5)  where={'tag_dairy_free': True}
  1. score=0.4801  congee::structure::c001
     recipe_id=congee  section=ingredients  dietary_tags=[vegan|gluten-free|dairy-free|nut-free]
  2. score=0.4789  beef-bourguignon::structure::c002
     recipe_id=beef-bourguignon  section=ingredients  dietary_tags=[dairy-free|contains-alcohol]
  3. score=0.4544  chana-masala::structure::c001
     recipe_id=chana-masala  section=ingredients  dietary_tags=[vegan|gluten-free|dairy-free]
  4. score=0.4377  congee::structure::c000
     recipe_id=congee  section=title  dietary_tags=[vegan|gluten-free|dairy-free|nut-free]
  5. score=0.4199  sesame-soy-aubergine::structure::c002
     recipe_id=sesame-soy-aubergine  section=ingredients  dietary_tags=[vegan|dairy-free|contains-soy|contains-sesame]

top-1 unfiltered : shakshuka::structure::c003 (recipe_id=shakshuka, score=0.4964)
top-1 filtered   : congee::structure::c001 (recipe_id=congee, score=0.4801)
TOP-1 CHANGED    : YES
```
