"""Reranker (C4c / `[240]` S3).

Cross-encoder relevance reranking of the fused candidate set. Default model
``BAAI/bge-reranker-base`` (config via `[500]`). Returns candidates ordered by
descending relevance with their raw scores (normalization is a logging-time
concern in P7, `[340]` O4). Heavy import is deferred.
"""

from __future__ import annotations

from app.retrieval.service import ChunkData, ScoredId


class CrossEncoderReranker:
    """sentence-transformers CrossEncoder reranker."""

    def __init__(self, model_name: str) -> None:
        from sentence_transformers import CrossEncoder  # deferred heavy import

        self._model = CrossEncoder(model_name)

    def rerank(self, query: str, candidates: list[ChunkData]) -> list[ScoredId]:
        if not candidates:
            return []
        pairs = [(query, c.text) for c in candidates]
        scores = self._model.predict(pairs)
        ranked = sorted(zip(candidates, scores, strict=True), key=lambda p: p[1], reverse=True)
        return [ScoredId(chunk_id=c.chunk_id, score=float(s)) for c, s in ranked]
