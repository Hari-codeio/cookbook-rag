"""Prove the assertions can fail. Run with no arguments; no API calls.

All six assertions passed on all 25 real substitutions. That is a good result
and it is also indistinguishable, from the outside, from six checks that cannot
fail. So each one is fed a deliberately broken payload built by mutating a real
one, and has to catch it.

    python eval/test_assertions.py
"""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from eval import assertions as A  # noqa: E402
from rag.config import GEN_PINNED_MODEL, OUT_DIR  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def real_payload() -> dict:
    """A genuine substituted output from the frozen run: c18, chocolate brioche."""
    for line in (OUT_DIR / "substitutions_v1.jsonl").read_text(encoding="utf-8").splitlines():
        rec = json.loads(line)
        if rec["case_id"] == "c18":
            return rec["output"]
    raise SystemExit("c18 not found in out/substitutions_v1.jsonl")


def main() -> None:
    base = real_payload()
    ok, _ = A.a2_allergen_warning_present(base)
    assert ok, "the unmutated payload should pass"

    cases: list[tuple[str, dict, str]] = []

    # A1: method calls for an ingredient that is not in the list.
    m = copy.deepcopy(base)
    m["method"] = m["method"] + " Fold through 60 g of roasted peanuts at the end."
    cases.append(("A1", m, "method names peanuts, the list does not"))

    # A2a: an allergen-bearing ingredient with an empty warning.
    m = copy.deepcopy(base)
    m["allergen_warning"] = ""
    cases.append(("A2", m, "wheat/egg/dairy present, warning blank"))

    # A2b: a warning that names some allergens but not all of them.
    m = copy.deepcopy(base)
    m["allergen_warning"] = "Contains wheat (gluten)."
    cases.append(("A2", m, "warning omits egg and dairy, which are in the list"))

    # A3: an oven temperature with the unit stripped.
    m = copy.deepcopy(base)
    m["oven"] = "180"
    cases.append(("A3", m, "oven number with no C or F"))

    # A4: a placeholder instead of a yield or an honest blank.
    m = copy.deepcopy(base)
    m["servings"] = "N/A"
    cases.append(("A4", m, "placeholder servings"))

    # A5: a quantity a cook cannot weigh.
    m = copy.deepcopy(base)
    m["ingredients"] = copy.deepcopy(base["ingredients"])
    m["ingredients"][0]["amount"] = "a generous handful"
    cases.append(("A5", m, "amount does not parse as number+unit"))

    print(f"{'check':<6}{'fired':<8}{'mutation'}")
    print("-" * 78)
    failures = 0
    for code, payload, what in cases:
        res = A.run_all(payload, model=GEN_PINNED_MODEL)
        fired = [c["code"] for c in res["checks"] if not c["passed"]]
        caught = code in fired
        failures += not caught
        print(f"{code:<6}{('YES' if caught else 'NO -- BUG'):<8}{what}")
        if not caught:
            print(f"        expected {code} to fail; failures were {fired or 'none'}")

    # A6 needs the model argument, not a payload mutation.
    res = A.run_all(base, model="some-other-model")
    caught = any(c["code"] == "A6" and not c["passed"] for c in res["checks"])
    failures += not caught
    print(f"{'A6':<6}{('YES' if caught else 'NO -- BUG'):<8}answered by a model other than the pinned {GEN_PINNED_MODEL}")

    print("-" * 78)
    if failures:
        raise SystemExit(f"{failures} assertion(s) did not catch their mutation")
    print(f"all {len(cases) + 1} mutations caught; the six checks are not decorative")


if __name__ == "__main__":
    main()
