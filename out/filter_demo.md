# Metadata filter on dietary_tags — unfiltered vs filtered

```
strategy        : structure
embedding model : all-MiniLM-L6-v2 (chromadb ONNX DefaultEmbeddingFunction)
top-k           : 5
dietary tags    : ['contains-alcohol', 'contains-dairy', 'contains-egg', 'contains-fish', 'contains-peanut', 'contains-sesame', 'contains-shellfish', 'contains-soy', 'dairy-free', 'gluten-free', 'nut-free', 'vegan', 'vegetarian']
generated       : 2026-08-13T01:59:47+00:00
```

Swept 16 quer(y/ies) x 13 tag(s) = 208 comparisons; **156** of them changed the top-1 result.

## Cases where the filter changed top-1

**Query:** `How long does the red cabbage sauerkraut ferment, and at what temperature?`
**Filter:** `where={'tag_contains_fish': True}`  (dietary_tags contains `contains-fish`)

```text
UNFILTERED  (top-5)
  1. score=0.7252  red-sauerkraut::structure::c002
     recipe_id=red-sauerkraut  section=method  dietary_tags=[vegan|gluten-free|dairy-free]
  2. score=0.6638  red-sauerkraut::structure::c001
     recipe_id=red-sauerkraut  section=ingredients  dietary_tags=[vegan|gluten-free|dairy-free]
  3. score=0.6401  red-sauerkraut::structure::c003
     recipe_id=red-sauerkraut  section=allergens  dietary_tags=[vegan|gluten-free|dairy-free]
  4. score=0.5369  red-sauerkraut::structure::c000
     recipe_id=red-sauerkraut  section=title  dietary_tags=[vegan|gluten-free|dairy-free]
  5. score=0.5053  napa-kimchi::structure::c003
     recipe_id=napa-kimchi  section=method  dietary_tags=[contains-fish|contains-shellfish|gluten-free|dairy-free]

FILTERED    (top-5)  where={'tag_contains_fish': True}
  1. score=0.5053  napa-kimchi::structure::c003
     recipe_id=napa-kimchi  section=method  dietary_tags=[contains-fish|contains-shellfish|gluten-free|dairy-free]
  2. score=0.4896  napa-kimchi::structure::c001
     recipe_id=napa-kimchi  section=ingredients  dietary_tags=[contains-fish|contains-shellfish|gluten-free|dairy-free]
  3. score=0.4659  napa-kimchi::structure::c002
     recipe_id=napa-kimchi  section=ingredients  dietary_tags=[contains-fish|contains-shellfish|gluten-free|dairy-free]
  4. score=0.3605  napa-kimchi::structure::c000
     recipe_id=napa-kimchi  section=title  dietary_tags=[contains-fish|contains-shellfish|gluten-free|dairy-free]
  5. score=0.3506  napa-kimchi::structure::c004
     recipe_id=napa-kimchi  section=allergens  dietary_tags=[contains-fish|contains-shellfish|gluten-free|dairy-free]

top-1 unfiltered : red-sauerkraut::structure::c002 (recipe_id=red-sauerkraut, score=0.7252)
top-1 filtered   : napa-kimchi::structure::c003 (recipe_id=napa-kimchi, score=0.5053)
TOP-1 CHANGED    : YES
```

**Query:** `How long does the red cabbage sauerkraut ferment, and at what temperature?`
**Filter:** `where={'tag_contains_shellfish': True}`  (dietary_tags contains `contains-shellfish`)

```text
UNFILTERED  (top-5)
  1. score=0.7252  red-sauerkraut::structure::c002
     recipe_id=red-sauerkraut  section=method  dietary_tags=[vegan|gluten-free|dairy-free]
  2. score=0.6638  red-sauerkraut::structure::c001
     recipe_id=red-sauerkraut  section=ingredients  dietary_tags=[vegan|gluten-free|dairy-free]
  3. score=0.6401  red-sauerkraut::structure::c003
     recipe_id=red-sauerkraut  section=allergens  dietary_tags=[vegan|gluten-free|dairy-free]
  4. score=0.5369  red-sauerkraut::structure::c000
     recipe_id=red-sauerkraut  section=title  dietary_tags=[vegan|gluten-free|dairy-free]
  5. score=0.5053  napa-kimchi::structure::c003
     recipe_id=napa-kimchi  section=method  dietary_tags=[contains-fish|contains-shellfish|gluten-free|dairy-free]

FILTERED    (top-5)  where={'tag_contains_shellfish': True}
  1. score=0.5053  napa-kimchi::structure::c003
     recipe_id=napa-kimchi  section=method  dietary_tags=[contains-fish|contains-shellfish|gluten-free|dairy-free]
  2. score=0.4896  napa-kimchi::structure::c001
     recipe_id=napa-kimchi  section=ingredients  dietary_tags=[contains-fish|contains-shellfish|gluten-free|dairy-free]
  3. score=0.4659  napa-kimchi::structure::c002
     recipe_id=napa-kimchi  section=ingredients  dietary_tags=[contains-fish|contains-shellfish|gluten-free|dairy-free]
  4. score=0.3605  napa-kimchi::structure::c000
     recipe_id=napa-kimchi  section=title  dietary_tags=[contains-fish|contains-shellfish|gluten-free|dairy-free]
  5. score=0.3506  napa-kimchi::structure::c004
     recipe_id=napa-kimchi  section=allergens  dietary_tags=[contains-fish|contains-shellfish|gluten-free|dairy-free]

top-1 unfiltered : red-sauerkraut::structure::c002 (recipe_id=red-sauerkraut, score=0.7252)
top-1 filtered   : napa-kimchi::structure::c003 (recipe_id=napa-kimchi, score=0.5053)
TOP-1 CHANGED    : YES
```

**Query:** `Is the napa cabbage kimchi safe for someone with a shellfish allergy?`
**Filter:** `where={'tag_contains_egg': True}`  (dietary_tags contains `contains-egg`)

```text
UNFILTERED  (top-5)
  1. score=0.7967  napa-kimchi::structure::c004
     recipe_id=napa-kimchi  section=allergens  dietary_tags=[contains-fish|contains-shellfish|gluten-free|dairy-free]
  2. score=0.6459  napa-kimchi::structure::c003
     recipe_id=napa-kimchi  section=method  dietary_tags=[contains-fish|contains-shellfish|gluten-free|dairy-free]
  3. score=0.5535  napa-kimchi::structure::c001
     recipe_id=napa-kimchi  section=ingredients  dietary_tags=[contains-fish|contains-shellfish|gluten-free|dairy-free]
  4. score=0.5258  napa-kimchi::structure::c002
     recipe_id=napa-kimchi  section=ingredients  dietary_tags=[contains-fish|contains-shellfish|gluten-free|dairy-free]
  5. score=0.4974  pad-thai::structure::c005
     recipe_id=pad-thai  section=allergens  dietary_tags=[gluten-free|contains-egg|contains-shellfish|contains-peanut]

FILTERED    (top-5)  where={'tag_contains_egg': True}
  1. score=0.4974  pad-thai::structure::c005
     recipe_id=pad-thai  section=allergens  dietary_tags=[gluten-free|contains-egg|contains-shellfish|contains-peanut]
  2. score=0.4081  shakshuka::structure::c004
     recipe_id=shakshuka  section=allergens  dietary_tags=[vegetarian|gluten-free|contains-egg]
  3. score=0.3603  pad-thai::structure::c003
     recipe_id=pad-thai  section=method  dietary_tags=[gluten-free|contains-egg|contains-shellfish|contains-peanut]
  4. score=0.3491  pad-thai::structure::c004
     recipe_id=pad-thai  section=method  dietary_tags=[gluten-free|contains-egg|contains-shellfish|contains-peanut]
  5. score=0.3060  pad-thai::structure::c001
     recipe_id=pad-thai  section=ingredients  dietary_tags=[gluten-free|contains-egg|contains-shellfish|contains-peanut]

top-1 unfiltered : napa-kimchi::structure::c004 (recipe_id=napa-kimchi, score=0.7967)
top-1 filtered   : pad-thai::structure::c005 (recipe_id=pad-thai, score=0.4974)
TOP-1 CHANGED    : YES
```

**Query:** `Is the napa cabbage kimchi safe for someone with a shellfish allergy?`
**Filter:** `where={'tag_contains_peanut': True}`  (dietary_tags contains `contains-peanut`)

```text
UNFILTERED  (top-5)
  1. score=0.7967  napa-kimchi::structure::c004
     recipe_id=napa-kimchi  section=allergens  dietary_tags=[contains-fish|contains-shellfish|gluten-free|dairy-free]
  2. score=0.6459  napa-kimchi::structure::c003
     recipe_id=napa-kimchi  section=method  dietary_tags=[contains-fish|contains-shellfish|gluten-free|dairy-free]
  3. score=0.5535  napa-kimchi::structure::c001
     recipe_id=napa-kimchi  section=ingredients  dietary_tags=[contains-fish|contains-shellfish|gluten-free|dairy-free]
  4. score=0.5258  napa-kimchi::structure::c002
     recipe_id=napa-kimchi  section=ingredients  dietary_tags=[contains-fish|contains-shellfish|gluten-free|dairy-free]
  5. score=0.4974  pad-thai::structure::c005
     recipe_id=pad-thai  section=allergens  dietary_tags=[gluten-free|contains-egg|contains-shellfish|contains-peanut]

FILTERED    (top-5)  where={'tag_contains_peanut': True}
  1. score=0.4974  pad-thai::structure::c005
     recipe_id=pad-thai  section=allergens  dietary_tags=[gluten-free|contains-egg|contains-shellfish|contains-peanut]
  2. score=0.3603  pad-thai::structure::c003
     recipe_id=pad-thai  section=method  dietary_tags=[gluten-free|contains-egg|contains-shellfish|contains-peanut]
  3. score=0.3491  pad-thai::structure::c004
     recipe_id=pad-thai  section=method  dietary_tags=[gluten-free|contains-egg|contains-shellfish|contains-peanut]
  4. score=0.3060  pad-thai::structure::c001
     recipe_id=pad-thai  section=ingredients  dietary_tags=[gluten-free|contains-egg|contains-shellfish|contains-peanut]
  5. score=0.2962  pad-thai::structure::c002
     recipe_id=pad-thai  section=ingredients  dietary_tags=[gluten-free|contains-egg|contains-shellfish|contains-peanut]

top-1 unfiltered : napa-kimchi::structure::c004 (recipe_id=napa-kimchi, score=0.7967)
top-1 filtered   : pad-thai::structure::c005 (recipe_id=pad-thai, score=0.4974)
TOP-1 CHANGED    : YES
```

**Query:** `How much fine sea salt goes into the 2kg country sourdough?`
**Filter:** `where={'tag_contains_fish': True}`  (dietary_tags contains `contains-fish`)

```text
UNFILTERED  (top-5)
  1. score=0.6028  sourdough-2kg::structure::c001
     recipe_id=sourdough-2kg  section=ingredients  dietary_tags=[vegan|dairy-free|nut-free]
  2. score=0.5790  sourdough-2kg::structure::c002
     recipe_id=sourdough-2kg  section=method  dietary_tags=[vegan|dairy-free|nut-free]
  3. score=0.5294  sourdough-2kg::structure::c004
     recipe_id=sourdough-2kg  section=allergens  dietary_tags=[vegan|dairy-free|nut-free]
  4. score=0.5048  sourdough-2kg::structure::c003
     recipe_id=sourdough-2kg  section=method  dietary_tags=[vegan|dairy-free|nut-free]
  5. score=0.4941  sourdough-2kg::structure::c000
     recipe_id=sourdough-2kg  section=title  dietary_tags=[vegan|dairy-free|nut-free]

FILTERED    (top-5)  where={'tag_contains_fish': True}
  1. score=0.4887  napa-kimchi::structure::c001
     recipe_id=napa-kimchi  section=ingredients  dietary_tags=[contains-fish|contains-shellfish|gluten-free|dairy-free]
  2. score=0.4272  napa-kimchi::structure::c003
     recipe_id=napa-kimchi  section=method  dietary_tags=[contains-fish|contains-shellfish|gluten-free|dairy-free]
  3. score=0.3316  napa-kimchi::structure::c002
     recipe_id=napa-kimchi  section=ingredients  dietary_tags=[contains-fish|contains-shellfish|gluten-free|dairy-free]
  4. score=0.3092  napa-kimchi::structure::c004
     recipe_id=napa-kimchi  section=allergens  dietary_tags=[contains-fish|contains-shellfish|gluten-free|dairy-free]
  5. score=0.2747  napa-kimchi::structure::c000
     recipe_id=napa-kimchi  section=title  dietary_tags=[contains-fish|contains-shellfish|gluten-free|dairy-free]

top-1 unfiltered : sourdough-2kg::structure::c001 (recipe_id=sourdough-2kg, score=0.6028)
top-1 filtered   : napa-kimchi::structure::c001 (recipe_id=napa-kimchi, score=0.4887)
TOP-1 CHANGED    : YES
```

**Query:** `How much fine sea salt goes into the 2kg country sourdough?`
**Filter:** `where={'tag_contains_shellfish': True}`  (dietary_tags contains `contains-shellfish`)

```text
UNFILTERED  (top-5)
  1. score=0.6028  sourdough-2kg::structure::c001
     recipe_id=sourdough-2kg  section=ingredients  dietary_tags=[vegan|dairy-free|nut-free]
  2. score=0.5790  sourdough-2kg::structure::c002
     recipe_id=sourdough-2kg  section=method  dietary_tags=[vegan|dairy-free|nut-free]
  3. score=0.5294  sourdough-2kg::structure::c004
     recipe_id=sourdough-2kg  section=allergens  dietary_tags=[vegan|dairy-free|nut-free]
  4. score=0.5048  sourdough-2kg::structure::c003
     recipe_id=sourdough-2kg  section=method  dietary_tags=[vegan|dairy-free|nut-free]
  5. score=0.4941  sourdough-2kg::structure::c000
     recipe_id=sourdough-2kg  section=title  dietary_tags=[vegan|dairy-free|nut-free]

FILTERED    (top-5)  where={'tag_contains_shellfish': True}
  1. score=0.4887  napa-kimchi::structure::c001
     recipe_id=napa-kimchi  section=ingredients  dietary_tags=[contains-fish|contains-shellfish|gluten-free|dairy-free]
  2. score=0.4272  napa-kimchi::structure::c003
     recipe_id=napa-kimchi  section=method  dietary_tags=[contains-fish|contains-shellfish|gluten-free|dairy-free]
  3. score=0.3316  napa-kimchi::structure::c002
     recipe_id=napa-kimchi  section=ingredients  dietary_tags=[contains-fish|contains-shellfish|gluten-free|dairy-free]
  4. score=0.3092  napa-kimchi::structure::c004
     recipe_id=napa-kimchi  section=allergens  dietary_tags=[contains-fish|contains-shellfish|gluten-free|dairy-free]
  5. score=0.2898  pad-thai::structure::c002
     recipe_id=pad-thai  section=ingredients  dietary_tags=[gluten-free|contains-egg|contains-shellfish|contains-peanut]

top-1 unfiltered : sourdough-2kg::structure::c001 (recipe_id=sourdough-2kg, score=0.6028)
top-1 filtered   : napa-kimchi::structure::c001 (recipe_id=napa-kimchi, score=0.4887)
TOP-1 CHANGED    : YES
```
