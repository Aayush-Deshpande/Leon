"""Health endpoint conforms to the `[220]` GET /health contract (FR-22)."""

from __future__ import annotations

from app.main import create_app
from fastapi.testclient import TestClient

client = TestClient(create_app())


def test_health_returns_ok_and_version() -> None:
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    # Contract [220]: exactly {status, version}
    assert set(body.keys()) == {"status", "version"}
    assert body["status"] == "ok"
    assert isinstance(body["version"], str) and body["version"]
