"""Evaluation metric definitions (`[340]`).

Pure functions over trace-like records (objects exposing relevance_score,
groundedness_score, routing_outcome, latency_ms, reranker_topk_scores). Reranker
scores are normalized to [0,1] before aggregation (O4).
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from typing import Protocol, TypedDict

from app.orchestration.types import RETURNED


class LatencySummary(TypedDict):
    p50: int
    p95: int


class Summary(TypedDict):
    avg_relevance: float
    avg_groundedness: float
    fallback_rate: float
    latency_ms: LatencySummary
    count: int


class TraceLike(Protocol):
    relevance_score: float | None
    groundedness_score: float | None
    routing_outcome: str
    latency_ms: int
    reranker_topk_scores: list[float]


def normalize_score(value: float) -> float:
    """Map an unbounded reranker score to [0,1] (logistic; O4)."""
    return 1.0 / (1.0 + math.exp(-value))


def _mean(values: Sequence[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def percentile(values: Sequence[int], pct: float) -> int:
    """Nearest-rank percentile."""
    if not values:
        return 0
    ordered = sorted(values)
    rank = max(1, math.ceil(pct / 100.0 * len(ordered)))
    return ordered[rank - 1]


def fallback_rate(traces: Sequence[TraceLike]) -> float:
    if not traces:
        return 0.0
    fallbacks = sum(1 for t in traces if t.routing_outcome != RETURNED)
    return fallbacks / len(traces)


def retrieval_precision_proxy(traces: Sequence[TraceLike]) -> float:
    """Mean normalized reranker top-k score across traces (`[340]`)."""
    normalized = [normalize_score(s) for t in traces for s in t.reranker_topk_scores]
    return _mean(normalized)


def compute_summary(traces: Sequence[TraceLike]) -> Summary:
    """Aggregate metrics backing the `GET /evaluation/summary` shape (`[220]`)."""
    latencies = [t.latency_ms for t in traces]
    return Summary(
        avg_relevance=_mean([t.relevance_score for t in traces if t.relevance_score is not None]),
        avg_groundedness=_mean(
            [t.groundedness_score for t in traces if t.groundedness_score is not None]
        ),
        fallback_rate=fallback_rate(traces),
        latency_ms=LatencySummary(p50=percentile(latencies, 50), p95=percentile(latencies, 95)),
        count=len(traces),
    )
