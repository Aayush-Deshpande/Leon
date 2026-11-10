"""PT-CRIT prompt construction (`[330]`).

The critique prompt is deliberately distinct from PT-GEN (S4/S5 separation
invariant, `[240]`, property P5). It asks an independent reviewer to score relevance
and citation-groundedness and to list unsupported citations, emitting JSON only per
the critique output contract (`[220]`/`[330]`).
"""

from __future__ import annotations

from app.generation.types import DraftAnswer
from app.retrieval.service import RankedContext

PT_CRIT_SYSTEM = (
    "You are an independent reviewer. Given a question, the context, and a draft "
    "answer, assess (1) whether the context is relevant to the question and (2) "
    "whether every citation in the draft is supported by the context. List any "
    "citation not supported by the context. Output JSON only, with exactly the keys "
    '{"relevance": <0..1>, "groundedness": <0..1>, "unverifiable": [<citation>, ...]}.'
)


def build_critique_prompt(
    query: str, context: RankedContext, draft: DraftAnswer
) -> tuple[str, str]:
    """Return (system, user) messages for the critique step."""
    lines = [f"Question: {query}", "Context:"]
    for candidate in context.candidates:
        lines.append(f"[{candidate.chunk_id}] {candidate.text}")
    lines.append("Draft answer:")
    lines.append(draft.text)
    lines.append("Output: JSON only, per the required schema.")
    return PT_CRIT_SYSTEM, "\n".join(lines)
