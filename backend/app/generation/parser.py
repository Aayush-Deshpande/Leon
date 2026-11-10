"""Response parsing + citation extraction (C5).

Extracts inline [chunk_id] markers and builds Citation objects ONLY for ids that
were actually supplied in the context ([220] contract). The answer text is preserved
exactly as returned by the model — unknown/unresolved markers are never stripped,
so P4 (critique) and P6 (citation verification) can evaluate them.
"""

from __future__ import annotations

import re

from app.generation.types import Citation, DraftAnswer
from app.retrieval.service import RankedContext

_MARKER = re.compile(r"\[([^\[\]]+)\]")


def parse_answer(raw_text: str, context: RankedContext) -> DraftAnswer:
    """Build a DraftAnswer: verbatim text + citations resolved from supplied context."""
    return DraftAnswer(text=raw_text, citations=extract_citations(raw_text, context))


def extract_citations(raw_text: str, context: RankedContext) -> list[Citation]:
    """One Citation per distinct supplied chunk id referenced in the text (in order)."""
    by_chunk = {c.chunk_id: c for c in context.candidates}
    citations: list[Citation] = []
    seen: set[str] = set()
    for match in _MARKER.finditer(raw_text):
        chunk_id = match.group(1).strip()
        if chunk_id not in by_chunk or chunk_id in seen:
            continue  # unknown markers are left in the text, not turned into citations
        seen.add(chunk_id)
        candidate = by_chunk[chunk_id]
        citations.append(
            Citation(
                id=f"c{len(citations) + 1}",
                chunk_id=candidate.chunk_id,
                source_document=candidate.source_document_id,
                locator=candidate.section_locator,
                passage=candidate.text,
            )
        )
    return citations
