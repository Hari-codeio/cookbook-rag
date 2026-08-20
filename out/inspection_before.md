# Inspection view — golden set, strategy=structure, k=3, deep=25

```text
=== g01 how much xanthan gum in the gluten free brioche
expected      : gf-brioche::structure::c001   token='Xanthan gum'
hit@3         : HIT    expected chunk rank: 2 of 94    in top-25: yes
top-3:
  1. 0.7217  gf-brioche::structure::c002                  method       [token:yes]
      Recipe: Gluten-Free Brioche (cuisine: french) / Section: Method / Whisk the flour blend, xanthan
  2. 0.6736  gf-brioche::structure::c001                  ingredients  [token:yes]  <== EXPECTED
      Recipe: Gluten-Free Brioche (cuisine: french) / Section: Ingredients (rows 1-8 of 8) / | Ingredi
  3. 0.5799  gf-brioche::structure::c000                  title        [token:no ]
      Recipe: Gluten-Free Brioche (cuisine: french) / Section: Title / # Gluten-Free Brioche / An enri

=== g02 xanthan for the gf sandwich loaf
expected      : gf-sandwich-loaf::structure::c001   token='Xanthan gum'
hit@3         : HIT    expected chunk rank: 2 of 94    in top-25: yes
top-3:
  1. 0.6868  gf-sandwich-loaf::structure::c002            method       [token:yes]
      Recipe: Gluten-Free Sandwich Loaf (cuisine: european) / Section: Method / Whisk the flour blend,
  2. 0.6256  gf-sandwich-loaf::structure::c001            ingredients  [token:yes]  <== EXPECTED
      Recipe: Gluten-Free Sandwich Loaf (cuisine: european) / Section: Ingredients (rows 1-7 of 7) / |
  3. 0.5585  gf-sandwich-loaf::structure::c003            allergens    [token:no ]
      Recipe: Gluten-Free Sandwich Loaf (cuisine: european) / Section: Allergens / Gluten free, provid

=== g03 psyllium husk amount
expected      : gf-sandwich-loaf::structure::c001   token='Psyllium husk'
hit@3         : MISS    expected chunk rank: 14 of 94    in top-25: yes
top-3:
  1. 0.2743  red-sauerkraut::structure::c001              ingredients  [token:no ]
      Recipe: Red Cabbage Sauerkraut (cuisine: german) / Section: Ingredients (rows 1-5 of 5) / | Ingr
  2. 0.2550  gf-sandwich-loaf::structure::c002            method       [token:yes]
      Recipe: Gluten-Free Sandwich Loaf (cuisine: european) / Section: Method / Whisk the flour blend,
  3. 0.2488  red-sauerkraut::structure::c002              method       [token:no ]
      Recipe: Red Cabbage Sauerkraut (cuisine: german) / Section: Method / Scatter the fine sea salt o
evidence:
  - correct chunk WAS retrieved, at rank 14, but ranked below 3. Mis-ordering, not absence -> a reranker could reach it.
  - token 'Psyllium husk' present in 1 of the top-3 chunks: ['gf-sandwich-loaf::structure::c002']

=== g04 how much saeujeot in the kimchi
expected      : napa-kimchi::structure::c001   token='saeujeot'
hit@3         : HIT    expected chunk rank: 3 of 94    in top-25: yes
top-3:
  1. 0.4722  napa-kimchi::structure::c002                 ingredients  [token:no ]
      Recipe: Napa Cabbage Kimchi (cuisine: korean) / Section: Ingredients (rows 9-9 of 9) / | Ingredi
  2. 0.4303  napa-kimchi::structure::c000                 title        [token:no ]
      Recipe: Napa Cabbage Kimchi (cuisine: korean) / Section: Title / # Napa Cabbage Kimchi / A cold-
  3. 0.4049  napa-kimchi::structure::c001                 ingredients  [token:yes]  <== EXPECTED
      Recipe: Napa Cabbage Kimchi (cuisine: korean) / Section: Ingredients (rows 1-8 of 9) / | Ingredi

=== g05 amchur amount chana masala
expected      : chana-masala::structure::c002   token='Amchur'
hit@3         : HIT    expected chunk rank: 1 of 94    in top-25: yes
top-3:
  1. 0.6350  chana-masala::structure::c002                ingredients  [token:yes]  <== EXPECTED
      Recipe: Chana Masala (cuisine: indian) / Section: Ingredients (rows 9-11 of 11) / | Ingredient |
  2. 0.5854  chana-masala::structure::c000                title        [token:no ]
      Recipe: Chana Masala (cuisine: indian) / Section: Title / # Chana Masala
  3. 0.5752  chana-masala::structure::c001                ingredients  [token:no ]
      Recipe: Chana Masala (cuisine: indian) / Section: Ingredients (rows 1-8 of 11) / | Ingredient | 

=== g06 what temp do i bake the 2kg sourdough at
expected      : sourdough-2kg::structure::c003   token='250 C'
hit@3         : HIT    expected chunk rank: 1 of 94    in top-25: yes
top-3:
  1. 0.7197  sourdough-2kg::structure::c003               method       [token:yes]  <== EXPECTED
      Recipe: 2kg Country Sourdough (cuisine: european) / Section: Method / Bake straight from the fri
  2. 0.5504  sourdough-2kg::structure::c000               title        [token:no ]
      Recipe: 2kg Country Sourdough (cuisine: european) / Section: Title / # 2kg Country Sourdough / A
  3. 0.5144  sourdough-2kg::structure::c002               method       [token:no ]
      Recipe: 2kg Country Sourdough (cuisine: european) / Section: Method / Whisk the starter into the

=== g07 how much butter in the chocolate brioche
expected      : chocolate-brioche::structure::c001   token='Dark chocolate chips'
hit@3         : HIT    expected chunk rank: 3 of 94    in top-25: yes
top-3:
  1. 0.7454  chocolate-brioche::structure::c002           method       [token:no ]
      Recipe: Chocolate Chip Brioche (cuisine: french) / Section: Method / Whisk the flour, sugar, yea
  2. 0.7311  chocolate-brioche::structure::c000           title        [token:no ]
      Recipe: Chocolate Chip Brioche (cuisine: french) / Section: Title / # Chocolate Chip Brioche / A
  3. 0.7212  chocolate-brioche::structure::c001           ingredients  [token:yes]  <== EXPECTED
      Recipe: Chocolate Chip Brioche (cuisine: french) / Section: Ingredients (rows 1-8 of 8) / | Ingr

=== g08 salt in the rye sourdough
expected      : rye-sourdough::structure::c001   token='Dark rye flour'
hit@3         : HIT    expected chunk rank: 1 of 94    in top-25: yes
top-3:
  1. 0.6895  rye-sourdough::structure::c001               ingredients  [token:yes]  <== EXPECTED
      Recipe: Light Rye Sourdough (cuisine: european) / Section: Ingredients (rows 1-5 of 5) / | Ingre
  2. 0.6689  rye-sourdough::structure::c002               method       [token:no ]
      Recipe: Light Rye Sourdough (cuisine: european) / Section: Method / Whisk the starter into the w
  3. 0.6588  rye-sourdough::structure::c003               allergens    [token:no ]
      Recipe: Light Rye Sourdough (cuisine: european) / Section: Allergens / Contains wheat and rye (g

=== g09 hydration of the wholemeal loaf
expected      : wholemeal-sourdough::structure::c001   token='Wholemeal flour'
hit@3         : MISS    expected chunk rank: 13 of 94    in top-25: yes
top-3:
  1. 0.5602  gf-sandwich-loaf::structure::c002            method       [token:no ]
      Recipe: Gluten-Free Sandwich Loaf (cuisine: european) / Section: Method / Whisk the flour blend,
  2. 0.5125  wholemeal-sourdough::structure::c000         title        [token:no ]
      Recipe: Wholemeal Sourdough (cuisine: european) / Section: Title / # Wholemeal Sourdough / A hig
  3. 0.4922  wholemeal-sourdough::structure::c002         method       [token:no ]
      Recipe: Wholemeal Sourdough (cuisine: european) / Section: Method / Whisk the starter into the w
evidence:
  - correct chunk WAS retrieved, at rank 13, but ranked below 3. Mis-ordering, not absence -> a reranker could reach it.
  - token 'Wholemeal flour' present in 0 of the top-3 chunks

=== g10 can i strain kefir with a metal sieve
expected      : milk-kefir::structure::c002   token='nylon'
hit@3         : HIT    expected chunk rank: 1 of 94    in top-25: yes
top-3:
  1. 0.5111  milk-kefir::structure::c002                  method       [token:yes]  <== EXPECTED
      Recipe: Milk Kefir (cuisine: caucasian) / Section: Method / Tip the live kefir grains into a cle
  2. 0.3577  milk-kefir::structure::c000                  title        [token:no ]
      Recipe: Milk Kefir (cuisine: caucasian) / Section: Title / # Milk Kefir / A continuous grain-cul
  3. 0.3549  milk-kefir::structure::c003                  allergens    [token:no ]
      Recipe: Milk Kefir (cuisine: caucasian) / Section: Allergens / Contains dairy (cow's milk). Not 

=== g11 why do pickles turn soft
expected      : dill-pickles::structure::c002   token='blossom end'
hit@3         : HIT    expected chunk rank: 1 of 94    in top-25: yes
top-3:
  1. 0.5679  dill-pickles::structure::c002                method       [token:yes]  <== EXPECTED
      Recipe: Half-Sour Dill Pickles (cuisine: eastern-european) / Section: Method / Dissolve the coar
  2. 0.4683  dill-pickles::structure::c000                title        [token:no ]
      Recipe: Half-Sour Dill Pickles (cuisine: eastern-european) / Section: Title / # Half-Sour Dill P
  3. 0.4260  dill-pickles::structure::c003                allergens    [token:no ]
      Recipe: Half-Sour Dill Pickles (cuisine: eastern-european) / Section: Allergens / Contains musta

=== g12 is the kimchi ok if im allergic to prawns
expected      : napa-kimchi::structure::c004   token='shellfish'
hit@3         : HIT    expected chunk rank: 1 of 94    in top-25: yes
top-3:
  1. 0.6008  napa-kimchi::structure::c004                 allergens    [token:yes]  <== EXPECTED
      Recipe: Napa Cabbage Kimchi (cuisine: korean) / Section: Allergens / Contains fish (fish sauce) 
  2. 0.5724  pad-thai::structure::c005                    allergens    [token:yes]
      Recipe: Prawn Pad Thai (cuisine: thai) / Section: Allergens / Contains shellfish, egg, peanuts a
  3. 0.4569  pad-thai::structure::c003                    method       [token:no ]
      Recipe: Prawn Pad Thai (cuisine: thai) / Section: Method / Soak the noodles in warm water for th

```