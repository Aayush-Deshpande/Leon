"""GET /evaluation/summary (FR-20). Aggregate metrics; shape owned by `[220]`."""

from __future__ import annotations

from collections.abc import Sequence
from typing import cast

from fastapi import APIRouter, Depends

from app.evaluation.metrics import TraceLike, compute_summary
from app.models.evaluation import LatencyModel, SummaryResponse

router = APIRouter(tags=["evaluation"])


def get_traces() -> Sequence[TraceLike]:
    """Load trace rows from the relational store (lazy DB access)."""
    from sqlalchemy import select

    from app import db
    from app.config import get_settings

    engine = db.create_db_engine(get_settings().database_url)
    factory = db.make_session_factory(engine)
    with db.session_scope(factory) as session:
        return cast(Sequence[TraceLike], list(session.execute(select(db.Trace)).scalars().all()))


@router.get("/evaluation/summary", response_model=SummaryResponse)
def evaluation_summary(
    traces: Sequence[TraceLike] = Depends(get_traces),
) -> SummaryResponse:
    summary = compute_summary(traces)
    return SummaryResponse(
        avg_groundedness=summary["avg_groundedness"],
        avg_relevance=summary["avg_relevance"],
        fallback_rate=summary["fallback_rate"],
        latency_ms=LatencyModel(p50=summary["latency_ms"]["p50"], p95=summary["latency_ms"]["p95"]),
        count=summary["count"],
    )
