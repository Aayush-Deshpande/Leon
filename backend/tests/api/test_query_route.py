"""POST /query route: JSON + SSE + validation ([220])."""

from __future__ import annotations

from app.api.deps import get_orchestrator, get_trace_logger
from app.generation.types import Citation
from app.main import create_app
from app.orchestration.types import QueryResponse, TraceRecord
from fastapi.testclient import TestClient


class _FakeOrchestrator:
    def handle(self, query: str):
        response = QueryResponse(
            answer="Agreements are contracts [id#0].",
            citations=[Citation("c1", "id#0", "ica", "Section 10", "passage")],
            confidence="high",
            routing_outcome="returned",
            reformulations=0,
            reason=None,
        )
        trace = TraceRecord(
            "q", "v", ["id#0"], "draft", 0.9, 0.9, [], "returned", 0, [1.0], "high", 5
        )
        return response, trace


class _FakeLogger:
    def __init__(self) -> None:
        self.persisted = 0

    def persist(self, trace) -> None:
        self.persisted += 1


def _client() -> TestClient:
    app = create_app()
    app.dependency_overrides[get_orchestrator] = lambda: _FakeOrchestrator()
    app.dependency_overrides[get_trace_logger] = _FakeLogger
    return TestClient(app)


def test_query_json_contract() -> None:
    r = _client().post("/query", json={"query": "what is a contract?"})
    assert r.status_code == 200
    body = r.json()
    assert set(body.keys()) == {"answer", "citations", "confidence", "routing", "reason"}
    assert body["confidence"] == "high"
    assert body["routing"] == {"outcome": "returned", "reformulations": 0}
    assert body["citations"][0]["chunk_id"] == "id#0"


def test_query_validation_rejects_empty() -> None:
    r = _client().post("/query", json={"query": ""})
    assert r.status_code == 422


def test_query_sse_stream() -> None:
    r = _client().post("/query", json={"query": "hi"}, headers={"accept": "text/event-stream"})
    assert r.status_code == 200
    assert "text/event-stream" in r.headers["content-type"]
    assert "event: final" in r.text
