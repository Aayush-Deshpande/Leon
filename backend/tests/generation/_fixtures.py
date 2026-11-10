"""Shared test helpers for generation tests."""

from __future__ import annotations

from app.retrieval.service import RankedContext, RetrievedCandidate


def make_context() -> RankedContext:
    candidates = [
        RetrievedCandidate(
            chunk_id="ica-1872-core#0000",
            text=(
                "All agreements are contracts if made by the free consent "
                "of parties competent to contract."
            ),
            section_locator="Section 10",
            source_document_id="ica-1872-core",
            doc_type="statute",
            jurisdiction="IN",
            score=2.0,
        ),
        RetrievedCandidate(
            chunk_id="ica-1872-core#0001",
            text="Every person is competent to contract who is of the age of majority.",
            section_locator="Section 11",
            source_document_id="ica-1872-core",
            doc_type="statute",
            jurisdiction="IN",
            score=1.0,
        ),
    ]
    return RankedContext(candidates=candidates, reranker_topk_scores=[2.0, 1.0])
