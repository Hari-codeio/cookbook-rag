"""Offline tests for everything Week 11 added. No API key, no model call.

    python eval/test_w11.py

Four things decide this week's numbers, so each gets a test that proves it can
fail:

  1. the residue check (rag/contract.allergen_residue) - it decides RED and
     GREEN. Every sentence below is a phrasing a real answer produced or a
     correct rewrite must be allowed to produce.
  2. stage totals (rag/obs.stage_totals) - containers must not be counted
     twice, or every cost-by-stage figure doubles.
  3. the index (rag/obs_index) - the answer must be searchable, not only the
     request, and a stale index must rebuild itself.
  4. the plant and its seal (eval/w11_plant.py, eval/drill.py) - the planted
     swap really is dairy, and the seal accepts the planted id and nothing else.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from rag import obs  # noqa: E402
from rag.contract import allergen_residue, check  # noqa: E402

FAILS: list[str] = []


def expect(name: str, got, want) -> None:
    ok = got == want
    print(f"{'ok ' if ok else 'XX '} {name}" + ("" if ok else f"   got={got!r} want={want!r}"))
    if not ok:
        FAILS.append(name)


# (method sentence, allergen, should it count as residue)
METHOD_CASES = [
    ("Soften the onion in the ghee, add the ginger.", "contains-dairy", True),       # out/squad_demo.txt
    ("Then stir in the cream and the crushed kasoori methi.", "contains-dairy", True),
    ("Beat the butter and caster sugar until pale.", "contains-dairy", True),         # smoke run, lemon drizzle
    ("Beat in the eggs and warm milk until the batter climbs.", "contains-dairy", True),
    ("Do not let the butter burn.", "contains-dairy", True),                          # 'not' is still an instruction
    ("Soften the onion in the sunflower oil.", "contains-dairy", False),
    ("Stir in the coconut cream off the heat.", "contains-dairy", False),
    ("Beat the vegan butter stick and caster sugar.", "contains-dairy", False),
    ("Marinate the chicken in the coconut yoghurt.", "contains-dairy", False),
    ("Use sunflower oil instead of ghee.", "contains-dairy", False),                  # a mention, not an instruction
    ("Cook until the sauce turns creamy and buttery.", "contains-dairy", False),      # adjectives are not markers
    ("Make wells and crack in the eggs.", "contains-egg", True),
    ("Pour in the wine and bring to a simmer.", "contains-alcohol", True),
    ("Pour in the beef stock and bring to a simmer.", "contains-alcohol", False),
    ("Finish with the toasted sesame oil.", "contains-sesame", True),
    ("Mix the fish sauce into the paste.", "contains-fish", True),
]


def test_residue() -> None:
    print("\n1. residue check")
    for sentence, allergen, want in METHOD_CASES:
        got = bool(allergen_residue({"method": sentence}, allergen)["method"])
        expect(f"method {allergen:<16} {want!s:<5} {sentence}", got, want)

    answer = {"recipe_id": "lemon-drizzle-cake", "scale_factor": 1.0, "method": "Beat the vegan butter.",
              "ingredients": [{"ingredient": "Ghee", "amount": "225 g"}],
              "substitutions": [{"from": "Unsalted butter", "to": "Ghee", "reason": "no milk solids"}]}
    res = allergen_residue(answer, "contains-dairy")
    expect("planted 'butter -> Ghee' shows up as a swap residue", res["swaps"], ["Ghee"])
    expect("...and as an ingredient-list residue", res["ingredients"], ["Ghee"])
    case = {"expect_recipe_id": "lemon-drizzle-cake", "scale_factor": 1.0, "avoid_allergen": "contains-dairy",
            "expect_substituted": ["butter"], "expect_untouched": []}
    expect("contract.check fails it", check(answer, case)[0], False)
    answer["method"] = "Beat the butter and caster sugar."
    answer["ingredients"] = [{"ingredient": "Vegan butter stick", "amount": "225 g"}]
    answer["substitutions"][0]["to"] = "Vegan butter stick"
    expect("w10 grader (points 1-5) passes a method-only residue", check(answer, case, residue=False)[0], True)
    expect("now grader (points 1-6) fails it", check(answer, case)[0], False)


def test_stage_totals() -> None:
    print("\n2. stage totals")
    rec = obs.Recorder()
    w = rec.add("allergen_worker", obs.CONTAINER, 0, 100)
    g = rec.add("allergen_worker.lap1", "generation", 0, 60, parent=w)
    g.tokens(1_000_000, 0)
    rec.add("allergen_worker.get_allergen_profile", "tool", 60, 5, parent=w)
    tot = obs.stage_totals(rec.spans)
    expect("container excluded, child counted once", tot["generation"]["cost_usd"], obs.USD_PER_1M_INPUT)
    expect("tool latency summed", tot["tool"]["latency_ms"], 5.0)


def _trace(tid: str, request: str, answer: dict, allergen: str = "contains-dairy") -> dict:
    return {"trace_schema": obs.TRACE_SCHEMA, "trace_id": tid, "ts": "2026-10-13T01:00:00+00:00",
            "user": {"user_id": "u_1", "session_id": "s_1"},
            "request": {"text": request, "input_type": "allergen-swap", "allergen": allergen},
            "prompt_version": "squad-v1", "model": {"used": ["m"]}, "retrieval": {"used": "x"},
            "spans": [], "totals": {"latency_ms": 1, "model_calls": 1, "input_tokens": 1,
                                    "output_tokens": 1, "cost_usd": 0.001},
            "output": {"answer": answer, "answer_text": obs.flatten_answer(answer)}, "status": "ok"}


def test_index() -> None:
    print("\n3. index")
    from rag.obs_index import connect

    with tempfile.TemporaryDirectory() as d:
        log = Path(d) / "traces.jsonl"
        a = {"title": "Tikka", "method": "Soften the onion in the ghee.", "substitutions": []}
        b = {"title": "Lemon", "method": "Beat the vegan butter.", "substitutions": []}
        log.write_text(json.dumps(_trace("tr_a", "tikka dairy free", a)) + "\n", encoding="utf-8")
        con = connect(log)
        hits = con.execute("SELECT trace_id FROM requests_fts WHERE requests_fts MATCH ?",
                           ('answer_text : ("ghee")',)).fetchall()
        expect("answer text is searchable", [h[0] for h in hits], ["tr_a"])
        hits = con.execute("SELECT trace_id FROM requests_fts WHERE requests_fts MATCH ?",
                           ('request_text : ("ghee")',)).fetchall()
        expect("...and the request column does not contain it", hits, [])
        con.close()
        with log.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(_trace("tr_b", "lemon dairy free", b)) + "\n")
        con = connect(log)
        expect("index rebuilds when the log grows", con.execute("SELECT COUNT(*) FROM requests").fetchone()[0], 2)
        con.close()


def test_plant_and_seal() -> None:
    print("\n4. plant and seal")
    import eval.w11_plant as plant

    base = _trace("tr_base", "Make the lemon drizzle dairy-free",
                  {"title": "Lemon", "method": "Beat the vegan butter block.",
                   "ingredients": [{"ingredient": "Vegan butter block", "amount": "225 g"}],
                   "substitutions": [{"from": "Unsalted butter", "to": "Vegan butter block", "reason": "r"}]})
    bad = plant.corrupt(json.loads(json.dumps(base)), None, None)
    res = allergen_residue(bad["output"]["answer"], "contains-dairy")
    expect("the planted replacement is itself dairy", bool(res["swaps"]), True)
    expect("the ingredient row was rewritten with it", bool(res["ingredients"]), True)
    expect("answer_text was re-flattened", "Ghee" in bad["output"]["answer_text"], True)

    salt = "s" * 32
    seal = {"salt": salt, "sealed": hashlib.sha256(f"{salt}:tr_planted".encode()).hexdigest()}
    with tempfile.TemporaryDirectory() as d:
        import eval.drill as drill

        drill.SEAL = Path(d) / "seal.json"
        drill.SEAL.write_text(json.dumps(seal), encoding="utf-8")
        expect("seal accepts the planted id", drill.seal_matches("tr_planted"), True)
        expect("seal rejects any other id", drill.seal_matches("tr_other"), False)


def main() -> None:
    os.environ["RAG_TRACE"] = "0"
    test_residue()
    test_stage_totals()
    test_index()
    test_plant_and_seal()
    print()
    if FAILS:
        print(f"{len(FAILS)} FAILED")
        raise SystemExit(1)
    print("all Week 11 checks pass")


if __name__ == "__main__":
    main()
