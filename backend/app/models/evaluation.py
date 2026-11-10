"""Response model for GET /evaluation/summary. Shape owned by `[220]`."""

from __future__ import annotations

from pydantic import BaseModel


class LatencyModel(BaseModel):
    p50: int
    p95: int


class SummaryResponse(BaseModel):
    avg_groundedness: float
    avg_relevance: float
    fallback_rate: float
    latency_ms: LatencyModel
    count: int
