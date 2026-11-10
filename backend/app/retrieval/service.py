"""Retrieval Service orchestration (C4).

Wires dense + sparse search → RRF fusion (`k_rrf`) → cross-encoder rerank → `top_n`,
returning a `RankedContext` with `reranker_topk_scores`. Realizes FR-2/FR-3/FR-4 and
the `Retrieval.retrieve` contract (`[220]`). Model roles/sizing are frozen in `[240]`.

Concrete searchers/reranker (dense/sparse/reranker modules) defer their heavy imports,
so this orchestration module is importable and unit-testable without a DB or models.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from app.config import Settings, get_settings
from app.retrieval.fusion import reciprocal_rank_fusion


@dataclass(frozen=True)
class ScoredId:
    """A retrieval hit: chunk id + method-specific score."""

    chunk_id: str
    score: float


@dataclass(frozen=True)
class ChunkData:
    """Chunk content + metadata fetched for reranking/return ([110]/[230])."""

    chunk_id: str
    text: str
    section_locator: str
    source_document_id: str
    doc_type: str
    jurisdiction: str


@dataclass(frozen=True)
class RetrievedCandidate:
    """A ranked candidate returned to the caller ([110])."""

    chunk_id: str
    text: str
    section_locator: str
    source_document_id: str
    doc_type: str
    jurisdiction: str
    score: float


@dataclass(frozen=True)
class RankedContext:
    """Ordered candidates + reranker scores of the top-k ([220] `Retrieval.retrieve`)."""

    candidates: list[RetrievedCandidate]
    reranker_topk_scores: list[float]


class DenseSearcher(Protocol):
    def search(self, query: str, k: int) -> list[ScoredId]: ...


class SparseSearcher(Protocol):
    def search(self, query: str, k: int) -> list[ScoredId]: ...


class ChunkRepository(Protocol):
    def fetch(self, chunk_ids: list[str]) -> dict[str, ChunkData]: ...


class Reranker(Protocol):
    def rerank(self, query: str, candidates: list[ChunkData]) -> list[ScoredId]: ...


def retrieve(
    query: str,
    *,
    dense: DenseSearcher,
    sparse: SparseSearcher,
    repository: ChunkRepository,
    reranker: Reranker,
    settings: Settings | None = None,
) -> RankedContext:
    """Run hybrid retrieval → RRF → rerank → top_n for a query."""
    cfg = settings or get_settings()

    dense_ids = [h.chunk_id for h in dense.search(query, cfg.k_dense)]
    sparse_ids = [h.chunk_id for h in sparse.search(query, cfg.k_sparse)]

    fused_ids = reciprocal_rank_fusion([dense_ids, sparse_ids], k=cfg.k_rrf)
    data = repository.fetch(fused_ids)
    candidates = [data[cid] for cid in fused_ids if cid in data]

    reranked = reranker.rerank(query, candidates)[: cfg.top_n]
    by_id = {c.chunk_id: c for c in candidates}
    ordered = [
        RetrievedCandidate(
            chunk_id=r.chunk_id,
            text=by_id[r.chunk_id].text,
            section_locator=by_id[r.chunk_id].section_locator,
            source_document_id=by_id[r.chunk_id].source_document_id,
            doc_type=by_id[r.chunk_id].doc_type,
            jurisdiction=by_id[r.chunk_id].jurisdiction,
            score=r.score,
        )
        for r in reranked
        if r.chunk_id in by_id
    ]
    return RankedContext(candidates=ordered, reranker_topk_scores=[c.score for c in ordered])


def create_retriever(
    session_factory: object, settings: Settings | None = None
) -> tuple[DenseSearcher, SparseSearcher, ChunkRepository, Reranker]:
    """Build concrete retrieval components (lazy heavy imports)."""
    from pathlib import Path

    from app.ingestion.embed import BgeEmbedder
    from app.retrieval.dense import PgVectorChunkRepository, PgVectorDenseSearcher
    from app.retrieval.reranker import CrossEncoderReranker
    from app.retrieval.sparse import Bm25SparseSearcher

    cfg = settings or get_settings()
    embedder = BgeEmbedder(cfg.embedding_model)
    sparse_index = Path("data/index/sparse") / cfg.corpus_version / "bm25.json"
    return (
        PgVectorDenseSearcher(embedder, session_factory),
        Bm25SparseSearcher(sparse_index),
        PgVectorChunkRepository(session_factory),
        CrossEncoderReranker(cfg.reranker_model),
    )
