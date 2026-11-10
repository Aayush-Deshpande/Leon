"""PT-GEN prompt construction (`[330]`).

Renders the generation system+user prompt from the query and RankedContext. This is
the ONLY place the generation prompt is built; wording follows PT-GEN in `[330]`
(context-only, cite every claim with [chunk_id], state insufficiency — no outside
knowledge).
"""

from __future__ import annotations

from app.retrieval.service import RankedContext

# PT-GEN system instruction (verbatim intent per [330]).
PT_GEN_SYSTEM = (
    "You answer legal questions using ONLY the provided context passages. "
    "Cite every claim with the passage's [chunk_id]. If the context does not "
    "contain the answer, respond that the provided sources are insufficient — "
    "do not use outside knowledge."
)


def build_generation_prompt(query: str, context: RankedContext) -> tuple[str, str]:
    """Return (system, user) messages for generation."""
    lines = [f"Question: {query}", "Context:"]
    for candidate in context.candidates:
        lines.append(f"[{candidate.chunk_id}] ({candidate.section_locator}) {candidate.text}")
    lines.append("Output: A grounded answer with inline [chunk_id] citations.")
    return PT_GEN_SYSTEM, "\n".join(lines)
