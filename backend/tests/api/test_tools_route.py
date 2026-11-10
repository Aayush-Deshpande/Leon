"""POST /tools/verify_citation route ([220]/FR-16), against the fixture corpus."""

from __future__ import annotations

from pathlib import Path

from app.api.routes.tools import get_citation_verifier
from app.main import create_app
from app.tools.citation_verify import CitationVerifierAdapter
from fastapi.testclient import TestClient

FIXTURE = Path(__file__).resolve().parents[3] / "data" / "corpus" / "corpus-v1.0"


def _client() -> TestClient:
    app = create_app()
    app.dependency_overrides[get_citation_verifier] = lambda: CitationVerifierAdapter(
        corpus_dir=FIXTURE, fuzzy_threshold=0.95
    )
    return TestClient(app)


def test_verify_citation_route_found() -> None:
    r = _client().post(
        "/tools/verify_citation",
        json={
            "locator": "Section 10",
            "quoted_text": "free consent of parties competent to contract",
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["exists"] is True and body["source_document"] == "ica-1872-core"


def test_verify_citation_route_not_found() -> None:
    r = _client().post(
        "/tools/verify_citation", json={"locator": "x", "quoted_text": "quantum chromodynamics"}
    )
    assert r.status_code == 200 and r.json()["exists"] is False
