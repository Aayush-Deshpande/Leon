"""POST /query route (FR-1, FR-21). Contract + streaming owned by `[220]`.

Content negotiation: `Accept: text/event-stream` → SSE (status/token/final events,
post-critique replay per `[220]`); otherwise a single JSON payload.
"""

from __future__ import annotations

import json
from collections.abc import Iterator

from fastapi import APIRouter, BackgroundTasks, Depends, Request
from fastapi.responses import StreamingResponse

from app.api.deps import get_orchestrator, get_trace_logger
from app.evaluation.logger import TraceSink
from app.models.query import QueryAnswerResponse, QueryRequest
from app.orchestration.controller import Orchestrator
from app.orchestration.types import CONFIDENCE_HIGH

router = APIRouter(tags=["query"])


@router.post("/query", response_model=QueryAnswerResponse)
def query(
    payload: QueryRequest,
    request: Request,
    background: BackgroundTasks,
    orchestrator: Orchestrator = Depends(get_orchestrator),
    trace_logger: TraceSink = Depends(get_trace_logger),
) -> QueryAnswerResponse | StreamingResponse:
    response, trace = orchestrator.handle(payload.query)
    background.add_task(trace_logger.persist, trace)  # FR-19: non-blocking
    body = QueryAnswerResponse.from_domain(response)

    if "text/event-stream" in request.headers.get("accept", ""):
        return StreamingResponse(_sse_events(body), media_type="text/event-stream")
    return body


def _sse_events(body: QueryAnswerResponse) -> Iterator[str]:
    yield _event("status", {"state": "checking"})
    # Tokens are a replay of the already-critique-passed answer ([220]); none on low-confidence.
    if body.confidence == CONFIDENCE_HIGH:
        for token in body.answer.split():
            yield _event("token", {"text": token + " "})
    yield _event("final", body.model_dump())


def _event(name: str, data: dict[str, object]) -> str:
    return f"event: {name}\ndata: {json.dumps(data)}\n\n"
