"""Reciprocal Rank Fusion (ADR-0014)."""

from __future__ import annotations

from app.retrieval.fusion import reciprocal_rank_fusion


def test_rrf_prefers_items_in_both_lists() -> None:
    fused = reciprocal_rank_fusion([["a", "b", "c"], ["c", "d"]], k=60)
    assert fused[0] == "c"  # appears in both lists -> highest fused score
    assert set(fused) == {"a", "b", "c", "d"}  # de-duplicated union
    assert len(fused) == len(set(fused))


def test_rrf_is_deterministic_on_ties() -> None:
    fused = reciprocal_rank_fusion([["x", "y"], ["p", "q"]], k=60)
    # x and p share rank 0; tie broken by first appearance (x before p).
    assert fused[0] == "x"
