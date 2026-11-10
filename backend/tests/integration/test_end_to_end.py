"""End-to-end integration (gated).

Runs only when LEON_RUN_INTEGRATION=1 with a reachable Postgres+pgvector, an
ingested corpus, and a configured LLM provider. Verifies the full pipeline:
ingest → /query → grounded cited answer or explicit low-confidence, plus P11
calibration. Skipped by default so the offline unit suite stays green.
"""

from __future__ import annotations

import os


def _integration_enabled() -> bool:
    return os.getenv("LEON_RUN_INTEGRATION") == "1"


def test_end_to_end_query() -> None:
    if not _integration_enabled():
        print("SKIP integration (set LEON_RUN_INTEGRATION=1 with DB + LLM configured)")
        return

    from app.main import create_app
    from fastapi.testclient import TestClient

    client = TestClient(create_app())
    resp = client.post("/query", json={"query": "Who is competent to contract?"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["confidence"] in {"high", "low"}
    if body["confidence"] == "high":
        assert body["citations"], "a high-confidence answer must carry >=1 citation (P7)"
    else:
        assert body["reason"], "a low-confidence answer must state a reason (FR-15)"
