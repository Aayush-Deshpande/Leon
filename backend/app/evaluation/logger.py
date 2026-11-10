"""Evaluation trace logging (C9, FR-18/FR-19).

Persists a completed TraceRecord to the `traces` table. Invoked from a background
task so it never blocks the user-facing response (FR-19). `db` is imported lazily.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Protocol

from app.orchestration.types import TraceRecord


class TraceSink(Protocol):
    """Anything that can persist a trace (used for typing the /query dependency)."""

    def persist(self, trace: TraceRecord) -> None: ...


class TraceLogger:
    """Writes trace records to the relational store."""

    def __init__(self, session_factory: object) -> None:
        self._session_factory = session_factory

    def persist(self, trace: TraceRecord) -> None:
        from app import db

        with db.session_scope(self._session_factory) as session:  # type: ignore[arg-type]
            session.add(
                db.Trace(
                    trace_id=str(uuid.uuid4()),
                    query_text=trace.query_text,
                    created_at=datetime.now(UTC),
                    corpus_version=trace.corpus_version,
                    retrieved_chunk_ids=trace.retrieved_chunk_ids,
                    draft_answer=trace.draft_answer,
                    relevance_score=trace.relevance_score,
                    groundedness_score=trace.groundedness_score,
                    unverifiable_citations=trace.unverifiable_citations,
                    routing_outcome=trace.routing_outcome,
                    reformulations=trace.reformulations,
                    reranker_topk_scores=trace.reranker_topk_scores,
                    confidence=trace.confidence,
                    latency_ms=trace.latency_ms,
                )
            )
