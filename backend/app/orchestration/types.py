"""Orchestration value types: the query response ([220]) and the trace record ([230]/[340])."""

from __future__ import annotations

from dataclasses import dataclass, field

from app.generation.types import Citation

# routing_outcome values ([220]/[210]).
RETURNED = "returned"
REFORMULATED = "reformulated"
TOOL_VERIFIED = "tool_verified"
LOW_CONFIDENCE = "low_confidence"

CONFIDENCE_HIGH = "high"
CONFIDENCE_LOW = "low"

LOW_CONFIDENCE_ADVISORY = (
    "The available sources are insufficient to answer this confidently. "
    "Please consult a qualified legal professional."
)


@dataclass(frozen=True)
class QueryResponse:
    """The `POST /query` payload ([220])."""

    answer: str
    citations: list[Citation]
    confidence: str
    routing_outcome: str
    reformulations: int
    reason: str | None = None


@dataclass(frozen=True)
class TraceRecord:
    """Per-query trace ([230] columns; semantics [340]). Persisted by P7."""

    query_text: str
    corpus_version: str
    retrieved_chunk_ids: list[str]
    draft_answer: str
    relevance_score: float | None
    groundedness_score: float | None
    unverifiable_citations: list[str]
    routing_outcome: str
    reformulations: int
    reranker_topk_scores: list[float] = field(default_factory=list)
    confidence: str = CONFIDENCE_LOW
    latency_ms: int = 0
