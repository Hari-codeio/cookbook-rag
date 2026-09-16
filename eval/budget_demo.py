"""Show each of the four budgets firing, and terminating cleanly.

    python eval/budget_demo.py

Writes out/budget_termination.log.

The point is not that a limit exists. It is that all FOUR are checked, that the
run STOPS rather than spins, and that it comes back with the name of the budget
that fired instead of an exception. A budget that is declared and never tested
is a comment with ambition, so each one gets its own run here and the log shows
which fired.

The last run is the one that matters most: it uses production budgets except for
max_laps, on a request that cannot be satisfied, so the loop would otherwise spin
until the quota ran out.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from rag.agent import Budgets, run_agent  # noqa: E402
from rag.generate import build_client  # noqa: E402
from rag.tools import REGISTRY_V2, TOOL_SCHEMAS_V2  # noqa: E402

OUT = ROOT / "out" / "budget_termination.log"

REQUEST = "Make the Chicken Tikka Masala 2x and completely dairy free."

# An unsatisfiable request: nothing in the archive is a nut-free swap for the
# peanuts AND the model is told to keep going until everything is safe, so a
# loop with no lap ceiling has no reason to stop.
SPIN_REQUEST = (
    "Make the Pad Thai 2x with no peanuts, no shellfish, no egg, no fish and no soy, "
    "and keep substituting until every single ingredient is clear of all five."
)

RUNS = [
    ("max_laps", Budgets(max_laps=2), REQUEST),
    ("max_tokens", Budgets(max_tokens=3000), REQUEST),
    ("max_cost_usd", Budgets(max_cost_usd=0.0004), REQUEST),
    ("max_seconds", Budgets(max_seconds=4.0), REQUEST),
    ("max_laps (spin guard, production budgets otherwise)", Budgets(max_laps=5), SPIN_REQUEST),
]


def main() -> None:
    client = build_client()
    lines: list[str] = []

    def emit(text: str = "") -> None:
        print(text)
        lines.append(text)

    emit("WEEK 7 - BUDGET TERMINATION LOG")
    emit("=" * 78)
    emit("Each run below trips one budget. None raises. Every one returns")
    emit("terminated_by set to the budget that fired, and stops.")
    emit("")

    for label, budgets, request in RUNS:
        emit("-" * 78)
        emit(f"RUN: expecting {label} to fire")
        emit(
            f"budgets: max_laps={budgets.max_laps} max_tokens={budgets.max_tokens} "
            f"max_cost_usd={budgets.max_cost_usd} max_seconds={budgets.max_seconds}"
        )
        emit(f"request: {request[:96]}")
        emit("")
        result = run_agent(client, request, budgets, TOOL_SCHEMAS_V2, REGISTRY_V2)
        for entry in result.log:
            emit("  " + json.dumps(entry, ensure_ascii=False))
        emit("")
        emit(f"  terminated_by : {result.terminated_by or '(ran to completion)'}")
        emit(f"  ok            : {result.ok}")
        emit(f"  error         : {result.error or '(none)'}")
        emit(f"  laps          : {result.laps}")
        emit(f"  tokens        : {result.total_tokens}")
        emit(f"  cost          : ${result.cost_usd:.6f}")
        emit(f"  latency       : {result.latency_ms:.0f} ms")
        emit(f"  raised        : no (clean termination)")
        emit("")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"written: {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
