"""Evaluation metrics (`[340]`)."""

from __future__ import annotations

from app.evaluation.metrics import (
    TraceLike,
    compute_summary,
    fallback_rate,
    normalize_score,
    percentile,
    retrieval_precision_proxy,
)
from app.orchestration.types import TraceRecord


def _trace(
    outcome: str, rel: float, ground: float, latency: int, scores: list[float]
) -> TraceRecord:
    return TraceRecord(
        query_text="q",
        corpus_version="v",
        retrieved_chunk_ids=["a"],
        draft_answer="d",
        relevance_score=rel,
        groundedness_score=ground,
        unverifiable_citations=[],
        routing_outcome=outcome,
        reformulations=0,
        reranker_topk_scores=scores,
        confidence="high" if outcome == "returned" else "low",
        latency_ms=latency,
    )


TRACES: list[TraceLike] = [
    _trace("returned", 0.9, 0.9, 100, [2.0, 1.0]),
    _trace("returned", 0.7, 0.8, 200, [1.0]),
    _trace("low_confidence", 0.2, 0.1, 300, [0.0]),
    _trace("reformulated", 0.6, 0.9, 400, [0.5]),
]


def test_normalize_and_percentile() -> None:
    assert normalize_score(0.0) == 0.5
    assert percentile([100, 200, 300, 400], 50) == 200
    assert percentile([100, 200, 300, 400], 95) == 400
    assert percentile([], 50) == 0


def test_fallback_rate_counts_non_returned() -> None:
    assert fallback_rate(TRACES) == 0.5  # 2 of 4 not 'returned'


def test_retrieval_precision_proxy_is_normalized_mean() -> None:
    proxy = retrieval_precision_proxy(TRACES)
    assert 0.0 <= proxy <= 1.0


def test_compute_summary_shape_and_values() -> None:
    s = compute_summary(TRACES)
    assert set(s.keys()) == {
        "avg_relevance",
        "avg_groundedness",
        "fallback_rate",
        "latency_ms",
        "count",
    }
    assert s["count"] == 4
    assert abs(float(s["avg_relevance"]) - 0.6) < 1e-9
    assert s["latency_ms"] == {"p50": 200, "p95": 400}
