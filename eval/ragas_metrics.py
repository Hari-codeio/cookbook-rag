"""RAGAS faithfulness and context precision, implemented against the published
definitions, plus the one free diagnostic that catches what neither of them can.

WHAT THIS IS, AND WHAT IT IS NOT

This is NOT the `ragas` pip package. Two reasons, both stated so the numbers can
be read for what they are:

  1. The library's LLM plumbing defaults to a different provider, and this
     project pins one model (gemini-3.1-flash-lite) so that every number in
     results_week6.md comes off the same instrument. Swapping the instrument for
     the bonus section would make its figures incomparable with the rest.
  2. The library's faithfulness issues one verification call PER CLAIM. On a
     free-tier key that is the difference between an eval that runs and one that
     dies at 429. This module batches the verification into one call per case,
     which is a real deviation and is listed below with the others.

What it IS: the two metrics' published formulas, transcribed as equations and
implemented literally, including the parts implementations get wrong. The
formulas were independently stated by two agents from the published definitions
and cross-checked against each other before a line of this was written; both
statements are kept at out/ragas_raw/formula_statements.json.

  FAITHFULNESS
      F = |{claims entailed by the retrieved context}| / |{claims in the answer}|

      Two LLM steps, deliberately kept separate because RAGAS keeps them
      separate and the separation is load-bearing:
        step 1  decompose the answer into standalone, pronoun-free statements,
                given ONLY (question, answer). The context is NOT shown. If it
                were, the model could tailor which claims it extracts to what
                happens to be supported, which inflates the score.
        step 2  join every retrieved chunk with "\\n" into ONE premise and give
                a 1/0 entailment verdict per statement.
      Empty statement list -> None (RAGAS returns NaN here, not 0.0).

  CONTEXT PRECISION @ K   (the non-LLM-with-reference shape)
      Precision@k        = (SUM_{j<=k} v_j) / k
      ContextPrecision@K = SUM_{k=1..K} (Precision@k * v_k) / SUM_{k=1..K} v_k

      Implemented exactly as shipped, including the three details that are easy
      to get wrong:
        * the `if v_k:` gate - Precision@k is accumulated ONLY at ranks where
          v_k = 1. An irrelevant chunk still advances k, so it dilutes every
          later Precision@k, but contributes no term of its own.
        * the denominator is the number of relevant chunks FOUND IN THE TOP K
          (SUM v_k), NOT K, and NOT the number of relevant docs in the corpus.
          Dividing by K would penalise retrieving extra irrelevant chunks even
          when the ranking is perfect; dividing by corpus relevants would fold
          in recall, which this metric deliberately does not measure.
        * the +1e-10 on the denominator, so an all-irrelevant list scores 0.0
          rather than raising. It is why a single relevant chunk at rank 1
          prints 0.9999999999 and not 1.0.

      DEVIATION, NAMED: RAGAS's NonLLMContextPrecisionWithReference sets v_k by
      Levenshtein string similarity between chunk k and the reference contexts,
      thresholded at 0.5. Here v_k is set by exact recipe_id membership:

          v_k = 1  iff  recipe_id(chunk k) is in relevant_recipe_ids

      because every chunk in this corpus carries its recipe_id in the block
      header, so the thing string similarity is approximating is available
      exactly. This is stricter and fully deterministic - no threshold to tune,
      no fuzzy-match false positives. It is NOT RAGAS's IDBasedContextPrecision,
      which is hits/total and not rank-aware; the rank-aware average-precision
      aggregation above is unchanged.

  GROUNDING DIAGNOSTICS   (not a RAGAS metric - the point of the bonus)
      Free, deterministic, no model call. Both formula statements independently
      concluded that faithfulness and context precision share a blind spot:
      neither ever forms the pair (claim, chunk that supported it). Faithfulness
      flattens the chunks into one premise, so support by ANY chunk is
      indistinguishable from support by the RIGHT chunk. Context precision never
      reads where the answer grounded itself - the with-reference variant does
      not even accept the response. So "grounded in a defensible-but-unservable
      card while a better card sat higher in the same retrieved list" scores
      identically to ideal behaviour.

      These three fields close that gap, and they cost nothing:
        grounding_rank        rank of the best chunk from the card the answer
                              actually stood on (output.base_recipe_id)
        best_relevant_rank    rank of the best relevant chunk available
        relevant_above        relevant recipe_ids ranked strictly higher than
                              the one the answer used
      grounding_optimal is False exactly when the answer walked past better
      evidence that was already on screen.
"""

from __future__ import annotations

import json
import re
from typing import Any

# RAGAS's denominator epsilon. Kept rather than tidied away: it is visible in
# the published outputs and removing it changes the printed numbers.
EPSILON = 1e-10

CONTEXT_BLOCK_RE = re.compile(
    r'<context\s+chunk_id="(?P<chunk_id>[^"]+)"\s+recipe_id="(?P<recipe_id>[^"]+)"[^>]*>'
    r"(?P<body>.*?)</context>",
    re.DOTALL,
)


# ---------------------------------------------------------------------------
# Inputs
# ---------------------------------------------------------------------------


def parse_context_blocks(context: str) -> list[dict[str, str]]:
    """The retrieved chunks, in the rank order they were given to the model."""
    return [
        {
            "chunk_id": m.group("chunk_id"),
            "recipe_id": m.group("recipe_id"),
            "text": m.group("body").strip(),
        }
        for m in CONTEXT_BLOCK_RE.finditer(context or "")
    ]


def render_response(output: dict[str, Any]) -> str:
    """The structured output as prose, deterministically.

    Faithfulness is defined over a natural-language response, and this app emits
    JSON. The serialisation has to be a pure function of the output - no
    sampling, no reordering - or the claim decomposition would move between runs
    and the score with it. Empty fields are dropped rather than rendered as
    "none", so the decomposer is never handed a claim the app did not make.
    """
    parts: list[str] = []

    # `can_substitute` is DELIBERATELY NOT RENDERED, and this is a correction to
    # the first version of this file rather than an oversight.
    #
    # v1 rendered it as "The requested substitution cannot be made." The metric
    # then scored 25/25 cases with that sentence as a claim and 25/25 verdicts of
    # 0, with the NLI judge giving the same reason every time: "the context does
    # not mention a requested substitution." It is right. The context is recipe
    # cards; it contains no representation of the user's request, so a claim
    # ABOUT the request is not something the context can entail or contradict.
    #
    # That made it a constant -1 claim on every case's numerator. It moved every
    # score down and discriminated between none of them, which is the definition
    # of a miscalibrated instrument rather than a finding. It also pushed the
    # cases the bonus is about below the 0.9 threshold for a reason that has
    # nothing to do with their grounding.
    #
    # can_substitute is a control-flow decision about the app's own behaviour,
    # not an assertion about recipes. The substantive content of a decline is
    # `unsupported`, which IS rendered below and IS scorable against the cards.
    # Both runs are kept: out/ragas_v1_decisionclaim.md has the v1 numbers.

    if output.get("title"):
        parts.append(f"The result is titled {output['title']}.")
    if output.get("base_recipe_id"):
        parts.append(f"It is based on the recipe {output['base_recipe_id']}.")
    if output.get("servings"):
        parts.append(f"It serves {output['servings']}.")

    for swap in output.get("swaps") or []:
        if isinstance(swap, dict):
            frm, to = swap.get("from"), swap.get("to")
            why = swap.get("why") or swap.get("evidence") or swap.get("chunk_id")
            line = f"Substitute {frm} with {to}." if frm and to else json.dumps(swap, ensure_ascii=False)
            if why:
                line += f" Evidence: {why}."
            parts.append(line)
        elif swap:
            parts.append(str(swap))

    ing = output.get("ingredients") or []
    if ing:
        rendered = []
        for item in ing:
            if isinstance(item, dict):
                name = item.get("name") or item.get("ingredient") or ""
                amt = item.get("amount") or item.get("quantity") or ""
                rendered.append(f"{name} {amt}".strip())
            elif item:
                rendered.append(str(item))
        if rendered:
            parts.append("The ingredients are: " + "; ".join(rendered) + ".")

    method = output.get("method")
    if isinstance(method, list) and method:
        parts.append("The method is: " + " ".join(str(s) for s in method))
    elif isinstance(method, str) and method.strip():
        parts.append("The method is: " + method.strip())

    if output.get("oven"):
        parts.append(f"The oven setting is {output['oven']}.")
    if output.get("allergen_warning"):
        parts.append(f"Allergen warning: {output['allergen_warning']}")
    if output.get("unsupported"):
        parts.append(f"The following could not be grounded in the archive: {output['unsupported']}")

    return "\n".join(p for p in parts if p and p.strip())


# ---------------------------------------------------------------------------
# Context precision @ K
# ---------------------------------------------------------------------------


def context_precision_at_k(
    chunks: list[dict[str, str]],
    relevant_recipe_ids: list[str] | set[str],
) -> dict[str, Any]:
    """Rank-aware average precision over the retrieved list.

        Precision@k        = (SUM_{j<=k} v_j) / k
        ContextPrecision@K = SUM_k (Precision@k * v_k) / SUM_k v_k

    Returns the score plus the per-rank working, so the arithmetic in the
    write-up can be checked by hand against the table.
    """
    relevant = set(relevant_recipe_ids or ())

    cumsum = 0
    numerator = 0.0
    ranks: list[dict[str, Any]] = []

    for i, chunk in enumerate(chunks):
        v = 1 if chunk["recipe_id"] in relevant else 0
        cumsum += v
        precision_at_k = cumsum / (i + 1)
        # The `if v:` gate. An irrelevant chunk advances k and dilutes every
        # later Precision@k, but contributes no term of its own.
        contribution = precision_at_k if v else 0.0
        if v:
            numerator += precision_at_k
        ranks.append(
            {
                "rank": i + 1,
                "chunk_id": chunk["chunk_id"],
                "recipe_id": chunk["recipe_id"],
                "v_k": v,
                "precision_at_k": round(precision_at_k, 6),
                "contribution": round(contribution, 6),
            }
        )

    denominator = cumsum + EPSILON
    score = numerator / denominator if chunks else 0.0

    return {
        "score": score,
        "k": len(chunks),
        "n_relevant_retrieved": cumsum,
        "numerator": numerator,
        "denominator": denominator,
        "ranks": ranks,
    }


# ---------------------------------------------------------------------------
# Faithfulness
# ---------------------------------------------------------------------------


def faithfulness_score(verdicts: list[dict[str, Any]]) -> float | None:
    """F = supported / total. None on an empty statement list (RAGAS: NaN)."""
    if not verdicts:
        return None
    supported = sum(1 for v in verdicts if v.get("verdict"))
    return supported / len(verdicts)


def joined_premise(chunks: list[dict[str, str]]) -> str:
    """RAGAS joins every retrieved chunk into ONE premise with "\\n".

    This single line is the whole reason faithfulness cannot see attribution:
    after the join there is no chunk identity left for a verdict to point at.
    The chunk_id header is kept in the text so the premise is not degraded
    relative to what the app itself was shown.
    """
    return "\n".join(
        f'<context chunk_id="{c["chunk_id"]}" recipe_id="{c["recipe_id"]}">\n{c["text"]}\n</context>'
        for c in chunks
    )


STATEMENT_SYSTEM = """\
You decompose an answer into atomic statements. This is step 1 of a two-step \
faithfulness measurement and you are deliberately NOT shown the source context, \
so do not speculate about what is or is not supported - that is step 2's job.

Given a question and an answer, break the answer into individual statements.

Rules:
- Each statement must be fully understandable on its own.
- Use NO pronouns. Substitute the entity name back in every time.
- One sentence may yield several statements. Split on each distinct assertion.
- Every statement must be something the ANSWER asserts. Do not add, infer or
  complete anything the answer did not say.
- If the answer declines or says something could not be grounded, the decline
  and each thing it names are statements like any other.
- Do not judge, rank or comment on the statements. Only list them.
"""

NLI_SYSTEM = """\
You judge whether statements can be inferred from a context. This is step 2 of a \
faithfulness measurement.

For each statement, return verdict 1 if the statement can be DIRECTLY inferred
from the given context, or 0 if it cannot.

Rules:
- Judge against the context ONLY. Not against your own knowledge of cooking, and
  not against whether the statement is good advice.
- "Directly inferred" means the context states it or straightforwardly entails
  it. A number you would have to CALCULATE from the context is not directly
  inferred; a number printed in the context is.
- A statement asserting that the context LACKS something is verdict 1 when the
  context indeed lacks it, and 0 when the context in fact contains it.
- Return one entry per statement, in the order given, with a one-clause reason.
"""

STATEMENT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "statements": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Atomic, pronoun-free statements the answer asserts.",
        }
    },
    "required": ["statements"],
}

NLI_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "verdicts": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "statement": {"type": "string"},
                    # Plain integer, not an enum: the Gemini schema layer only
                    # accepts string enum members, so `enum: [0, 1]` is rejected
                    # outright. The 1/0 contract is carried by the description
                    # and enforced by the coercion in run_ragas.score_case,
                    # which treats anything that is not exactly 1 as 0.
                    "verdict": {
                        "type": "integer",
                        "description": "1 if the statement is directly inferable from the context, else 0.",
                    },
                    "reason": {"type": "string"},
                },
                "required": ["statement", "verdict", "reason"],
            },
        }
    },
    "required": ["verdicts"],
}


def build_statement_turn(question: str, answer: str) -> str:
    return (
        f"QUESTION\n========\n{question}\n\n"
        f"ANSWER\n======\n{answer}\n\n"
        "List the atomic statements the ANSWER asserts."
    )


def build_nli_turn(premise: str, statements: list[str]) -> str:
    numbered = "\n".join(f"{i}. {s}" for i, s in enumerate(statements, 1))
    return (
        f"CONTEXT\n=======\n{premise}\n\n"
        f"STATEMENTS\n==========\n{numbered}\n\n"
        "Return one verdict per statement, in order."
    )


# ---------------------------------------------------------------------------
# Grounding diagnostics - the free check neither RAGAS metric performs
# ---------------------------------------------------------------------------


def grounding_diagnostics(
    chunks: list[dict[str, str]],
    output: dict[str, Any],
    reference: dict[str, Any],
) -> dict[str, Any]:
    """Did the answer stand on the right card, and did it decline with the
    evidence on screen?

    Deterministic, no model call. This is the axis both RAGAS metrics discard:
    faithfulness throws away chunk identity, context precision throws away the
    answer. Either question below needs both at once, so neither metric can
    compute either one.

    A NOTE ON A DEFINITION I GOT WRONG FIRST TIME, kept here because the wrong
    version is the tempting one. The first cut asked "is the chunk the answer
    grounded on the highest-ranked relevant chunk?" That is wrong. On c01
    (classic brioche -> gluten free) the answer correctly stands on
    classic-brioche, the dish it was asked to modify, while the DONOR card
    gf-brioche happens to rank above it. Standing on the base card is right, and
    a check that marks it wrong because the donor outranked it fails every
    correctly-answered substitution in the set. Relevance is not one flat set:

        base  = the card for the dish the request names. What the answer is OF.
        donor = the card demonstrating the requested change. What licenses it.

    So the two checks are asked separately:

      grounded_in_reference_base
          the answer's base_recipe_id is one the request could defensibly name.
          False means it answered about the wrong dish.

      declined_with_donor_on_screen
          it said can_substitute=false while a card that demonstrates the change
          was sitting in its own retrieved context. This is the judge's criterion
          (b) made deterministic, and it is the exact failure c25 embodies: an
          ambiguous request resolved to the one reading it could not serve, while
          a complete gluten-free loaf sat at rank 1 of the context it was given.
    """
    base_ids = set(reference.get("base_recipe_ids") or ())
    donor_ids = set(reference.get("donor_recipe_ids") or ())
    relevant = set(reference.get("relevant_recipe_ids") or ()) or (base_ids | donor_ids)

    grounded_recipe_id = output.get("base_recipe_id")

    def first_rank(ids: set[str]) -> int | None:
        return next((i + 1 for i, c in enumerate(chunks) if c["recipe_id"] in ids), None)

    grounding_rank = (
        first_rank({grounded_recipe_id}) if grounded_recipe_id else None
    )
    best_base_rank = first_rank(base_ids)
    best_donor_rank = first_rank(donor_ids)

    donors_on_screen = sorted({c["recipe_id"] for c in chunks if c["recipe_id"] in donor_ids})

    # Descriptive only: which other relevant cards outranked the one it used.
    relevant_above: list[str] = []
    if grounding_rank is not None:
        seen: set[str] = set()
        for c in chunks[: grounding_rank - 1]:
            rid = c["recipe_id"]
            if rid in relevant and rid != grounded_recipe_id and rid not in seen:
                seen.add(rid)
                relevant_above.append(rid)

    declined = output.get("can_substitute") is False
    in_base = bool(grounded_recipe_id) and grounded_recipe_id in base_ids
    declined_with_donor = bool(declined and donors_on_screen)

    # Only counted as wrongly grounded when we can actually tell: an answer that
    # names no base recipe at all is not evidence either way.
    if not grounded_recipe_id and not declined:
        wrongly_grounded = None
    else:
        wrongly_grounded = bool(
            (grounded_recipe_id and not in_base) or declined_with_donor
        )

    return {
        "grounded_recipe_id": grounded_recipe_id,
        "grounded_in_reference_base": in_base,
        "grounding_rank": grounding_rank,
        "best_base_rank": best_base_rank,
        "best_donor_rank": best_donor_rank,
        "donors_on_screen": donors_on_screen,
        "relevant_above": relevant_above,
        "declined": declined,
        "declined_with_donor_on_screen": declined_with_donor,
        "wrongly_grounded": wrongly_grounded,
    }
