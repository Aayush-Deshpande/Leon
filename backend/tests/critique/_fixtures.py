"""Shared helpers for critique tests."""

from __future__ import annotations

from app.critique.types import CritiqueJudgment
from app.generation.types import DraftAnswer
from app.retrieval.service import RankedContext, RetrievedCandidate


def make_candidate(chunk_id: str = "ica-1872-core#0000") -> RetrievedCandidate:
    return RetrievedCandidate(
        chunk_id=chunk_id,
        text="All agreements are contracts if made by the free consent of competent parties.",
        section_locator="Section 10",
        source_document_id="ica-1872-core",
        doc_type="statute",
        jurisdiction="IN",
        score=2.0,
    )


def make_context() -> RankedContext:
    c = make_candidate()
    return RankedContext(candidates=[c], reranker_topk_scores=[c.score])


def make_draft(text: str = "Agreements need free consent [ica-1872-core#0000].") -> DraftAnswer:
    return DraftAnswer(text=text)


def grounded_judgment() -> CritiqueJudgment:
    return CritiqueJudgment(relevance=0.9, groundedness=0.9, unverifiable=[])


def ungrounded_judgment() -> CritiqueJudgment:
    return CritiqueJudgment(relevance=0.2, groundedness=0.1, unverifiable=["fabricated-0"])
