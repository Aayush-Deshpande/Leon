"""Citation verification matching (ADR-0019, FR-16)."""

from __future__ import annotations

from pathlib import Path

from app.tools.citation_verify import CitationVerifierAdapter, verify_citation

SOURCES = [("d1", "10. All agreements are contracts made by the free consent of parties.")]
FIXTURE = Path(__file__).resolve().parents[3] / "data" / "corpus" / "corpus-v1.0"


def test_normalized_substring_match() -> None:
    r = verify_citation("Section 10", "free consent", SOURCES, 0.95)
    assert r.exists and r.source_document == "d1"


def test_fuzzy_tolerates_minor_variation() -> None:
    # 'free consnt' (typo) ~0.81 longest-match ratio -> passes at threshold 0.8, not 0.95.
    assert verify_citation("x", "free consnt", SOURCES, 0.80).exists is True
    assert verify_citation("x", "free consnt", SOURCES, 0.95).exists is False


def test_not_found() -> None:
    assert verify_citation("x", "quantum chromodynamics", SOURCES, 0.95).exists is False


def test_locator_only_resolution() -> None:
    assert verify_citation("free consent", None, SOURCES, 0.95).exists is True


def test_adapter_over_fixture_corpus() -> None:
    adapter = CitationVerifierAdapter(corpus_dir=FIXTURE, fuzzy_threshold=0.95)
    result = adapter.verify("Section 10", "free consent of parties competent to contract")
    assert result.exists and result.source_document == "ica-1872-core"
    assert adapter.exists("free consent") is True
    assert adapter.exists("this phrase is not in the corpus at all") is False
