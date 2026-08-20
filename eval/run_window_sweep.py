"""Supporting evidence for the shipping decision: is the gain available cheaper?

Section 7 of results_week4.md argues the reranker is not worth its latency. The
obvious rebuttal is "shrink the candidate window", so this measures that instead
of assuming it.

Two findings, both in the output:

  * the window cannot drop below 14, because g03's correct chunk sits at rank 14
    and a smaller window cannot see it - the whole gain disappears at 10 and 5;
  * shrinking barely helps anyway, because the cost is the fixed price of
    invoking the cross-encoder, not the number of pairs scored. Five pairs
    already costs 3.1x dense.

Timing here uses 5 samples per question and its own warmup, so these numbers are
comparable to each other but NOT to the p50 table in section 5, which used 7.

    python eval/run_window_sweep.py        # -> out/window_sweep.txt
"""

import json, statistics, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from rag.store import get_collection, search
from rag.rerank import rerank_search

golden = [json.loads(l) for l in Path(__file__).resolve().parent / "golden_set.jsonl".read_text(encoding="utf-8").splitlines() if l.strip()]
c = get_collection("structure")

# warm both models
for _ in range(3):
    rerank_search(c, "warm up", k=3, candidates=5)

print(f"{'config':<22}{'hit@3':<8}{'p50 ms':<10}{'fixes g03?':<12}")
# dense control
lat = []
hits = 0
for g in golden:
    for _ in range(5):
        t = time.perf_counter(); ids = [h.chunk_id for h in search(c, g["question"], k=3)]; lat.append((time.perf_counter()-t)*1000)
    hits += 1 if g["expected_chunk_id"] in ids else 0
print(f"{'dense (no rerank)':<22}{str(hits)+'/12':<8}{statistics.median(lat):<10.1f}{'n/a':<12}")

for cand in (5, 10, 14, 25):
    lat = []; hits = 0; g03 = None
    for g in golden:
        for _ in range(5):
            t = time.perf_counter(); ids = [h.chunk_id for h in rerank_search(c, g["question"], k=3, candidates=cand)]; lat.append((time.perf_counter()-t)*1000)
        got = g["expected_chunk_id"] in ids
        hits += 1 if got else 0
        if g["id"] == "g03": g03 = got
    print(f"{'rerank, window='+str(cand):<22}{str(hits)+'/12':<8}{statistics.median(lat):<10.1f}{('YES' if g03 else 'no'):<12}")
