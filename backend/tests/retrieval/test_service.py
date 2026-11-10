"""Retrieval orchestration: hybrid sources → RRF → rerank → top_n (FR-2/3/4, P8)."""

from __future__ import annotations

from app.config import Settings
from app.retrieval.service import ChunkData, RankedContext, ScoredId, retrieve


class _FakeDense:
    def search(self, query: str, k: int) -> list[ScoredId]:
        return [ScoredId("a", 0.9), ScoredId("b", 0.8)]  # 'a' is dense-only


class _FakeSparse:
    def search(self, query: str, k: int) -> list[ScoredId]:
        return [ScoredId("c", 0.5), ScoredId("b", 0.4)]  # 'c' is sparse-only


class _FakeRepo:
    def fetch(self, chunk_ids: list[str]) -> dict[str, ChunkData]:
        return {
            cid: ChunkData(cid, f"text {cid}", f"Section {cid}", f"doc-{cid}", "statute", "IN")
            for cid in chunk_ids
        }


class _FakeReranker:
    def __init__(self) -> None:
        self.seen: list[str] = []

    def rerank(self, query: str, candidates: list[ChunkData]) -> list[ScoredId]:
        self.seen = [c.chunk_id for c in candidates]
        n = len(candidates)
        return [ScoredId(c.chunk_id, float(n - i)) for i, c in enumerate(candidates)]


def test_p8_both_sources_contribute_and_top_n_respected() -> None:
    reranker = _FakeReranker()
    settings = Settings(_env_file=None, top_n=2)  # type: ignore[call-arg]
    ctx = retrieve(
        "what makes an agreement a contract",
        dense=_FakeDense(),
        sparse=_FakeSparse(),
        repository=_FakeRepo(),
        reranker=reranker,
        settings=settings,
    )
    assert isinstance(ctx, RankedContext)
    # P8: both a dense-only ('a') and a sparse-only ('c') candidate reached rerank.
    assert {"a", "c"} <= set(reranker.seen)
    # top_n respected and scores aligned to candidates.
    assert len(ctx.candidates) == 2
    assert len(ctx.reranker_topk_scores) == 2
    assert [c.score for c in ctx.candidates] == ctx.reranker_topk_scores
    # metadata preserved end-to-end.
    assert all(
        c.text.startswith("text ") and c.section_locator.startswith("Section")
        for c in ctx.candidates
    )
