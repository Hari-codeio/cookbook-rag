### `tr_93031da07c32`: 'Tikka masala with no dairy, my son has a milk allergy'

release `squad-v1`, user `u_0107`, 2026-10-13T00:57:31+00:00

| stage | spans | model calls | latency ms | input tok | output tok | cost $ | share |
|---|---|---|---|---|---|---|---|
| retrieval | 1 | 0 | 300 | 0 | 0 | 0.000000 | 0% |
| generation | 6 | 6 | 25497 | 3731 | 1302 | 0.002886 | 100% |
| tool | 3 | 0 | 86 | 0 | 0 | 0.000000 | 0% |
| **request** | 10 | 6 | 25920 (wall) | 3731 | 1302 | **0.002886** | 100% |

By step (leaf spans grouped):

| step | stage | calls | latency ms | input tok | output tok | cost $ | share |
|---|---|---|---|---|---|---|---|
| plan | generation | 1 | 4456 | 165 | 36 | 0.000095 | 3% |
| recipe_search | retrieval | 1 | 300 | 0 | 0 | 0.000000 | 0% |
| scale_recipe | tool | 1 | 32 | 0 | 0 | 0.000000 | 0% |
| allergen_worker | generation | 2 | 6807 | 1463 | 236 | 0.000720 | 25% |
| get_allergen_profile | tool | 2 | 54 | 0 | 0 | 0.000000 | 0% |
| substitution_worker | generation | 2 | 8551 | 1106 | 306 | 0.000735 | 25% |
| synthesise | generation | 1 | 5683 | 997 | 724 | 0.001335 | 46% |

### `tr_919c9b03134d`: 'Tikka masala with no dairy, my son has a milk allergy'

release `squad-v1`, user `u_0121`, 2026-10-13T00:52:51+00:00

| stage | spans | model calls | latency ms | input tok | output tok | cost $ | share |
|---|---|---|---|---|---|---|---|
| retrieval | 1 | 0 | 281 | 0 | 0 | 0.000000 | 0% |
| generation | 6 | 6 | 23490 | 3731 | 1302 | 0.002886 | 100% |
| tool | 3 | 0 | 80 | 0 | 0 | 0.000000 | 0% |
| **request** | 10 | 6 | 23853 (wall) | 3731 | 1302 | **0.002886** | 100% |

By step (leaf spans grouped):

| step | stage | calls | latency ms | input tok | output tok | cost $ | share |
|---|---|---|---|---|---|---|---|
| plan | generation | 1 | 4111 | 165 | 36 | 0.000095 | 3% |
| recipe_search | retrieval | 1 | 281 | 0 | 0 | 0.000000 | 0% |
| scale_recipe | tool | 1 | 30 | 0 | 0 | 0.000000 | 0% |
| allergen_worker | generation | 2 | 6252 | 1463 | 236 | 0.000720 | 25% |
| get_allergen_profile | tool | 2 | 50 | 0 | 0 | 0.000000 | 0% |
| substitution_worker | generation | 2 | 7777 | 1106 | 306 | 0.000735 | 25% |
| synthesise | generation | 1 | 5350 | 997 | 724 | 0.001335 | 46% |
