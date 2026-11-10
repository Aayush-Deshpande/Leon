"""Extraction parses the fixture corpus with provenance ([130])."""

from __future__ import annotations

from pathlib import Path

from app.ingestion.extract import load_corpus

CORPUS = Path(__file__).resolve().parents[3] / "data" / "corpus" / "corpus-v1.0"


def test_loads_fixture_with_provenance() -> None:
    docs = load_corpus(CORPUS)
    assert len(docs) == 2
    by_id = {d.doc_id: d for d in docs}

    statute = by_id["ica-1872-core"]
    assert statute.type == "statute"
    locators = [loc for loc, _ in statute.statute_sections]
    assert "Section 10" in locators and "Section 11" in locators
    assert statute.origin and statute.retrieved_at and statute.corpus_version == "corpus-v1.0"

    judgment = by_id["fixture-judgment-illustrative"]
    assert judgment.type == "case_law"
    assert len(judgment.paragraphs) >= 3
