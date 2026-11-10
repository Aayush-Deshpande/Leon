"""Citation extraction: only supplied context ids; verbatim text; unknown markers kept."""

from __future__ import annotations

from app.generation.parser import parse_answer

from tests.generation._fixtures import make_context


def test_resolves_citation_from_supplied_context() -> None:
    ctx = make_context()
    draft = parse_answer("Agreements are contracts made by free consent [ica-1872-core#0000].", ctx)
    assert draft.text.endswith("[ica-1872-core#0000].")  # text preserved verbatim
    assert len(draft.citations) == 1
    c = draft.citations[0]
    assert c.chunk_id == "ica-1872-core#0000"
    assert c.source_document == "ica-1872-core"
    assert c.locator == "Section 10"
    assert c.passage.startswith("All agreements are contracts")
    assert c.id == "c1"


def test_unknown_marker_is_preserved_and_not_cited() -> None:
    ctx = make_context()
    draft = parse_answer("This claim cites nothing real [ghost-id-999].", ctx)
    assert "[ghost-id-999]" in draft.text  # never silently discarded
    assert draft.citations == []


def test_duplicate_markers_dedup_to_one_citation() -> None:
    ctx = make_context()
    draft = parse_answer("See [ica-1872-core#0000] and again [ica-1872-core#0000].", ctx)
    assert len(draft.citations) == 1
