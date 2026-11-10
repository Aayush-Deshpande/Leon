"""Chunking conforms to `[130]` (structure-aligned, bounded, overlapping case law)."""

from __future__ import annotations

from app.ingestion.chunk import CHUNK_MAX_TOKENS, chunk_case_law, chunk_statute


# Inflating counter so small deterministic fixtures exceed the 512 bound.
def _inflate(text: str) -> int:
    return len(text.split()) * 100


def test_short_statute_section_is_single_chunk() -> None:
    chunks = chunk_statute("d", "IN", "v1", [("Section 10", "all agreements are contracts")])
    assert len(chunks) == 1
    c = chunks[0]
    assert c.section_locator == "Section 10"
    assert c.doc_type == "statute" and c.jurisdiction == "IN" and c.corpus_version == "v1"
    assert c.chunk_id == "d#0000"


def test_long_section_splits_at_subsections_and_stays_bounded() -> None:
    body = "(1) alpha beta gamma. (2) delta epsilon zeta. (3) eta theta iota."
    chunks = chunk_statute("d", "IN", "v1", [("Section 2", body)], count_tokens=_inflate)
    assert len(chunks) > 1
    assert all(_inflate(c.text) <= CHUNK_MAX_TOKENS for c in chunks)
    assert len({c.chunk_id for c in chunks}) == len(chunks)  # unique ids
    assert any("(" in c.section_locator for c in chunks)  # sub-section marker in locator


def test_case_law_windows_overlap_and_are_bounded() -> None:
    paras = ["para one alpha", "para two beta", "para three gamma", "para four delta"]
    chunks = chunk_case_law("j", "IN", "v1", paras, count_tokens=_inflate)
    assert len(chunks) >= 2
    assert all(_inflate(c.text) <= CHUNK_MAX_TOKENS for c in chunks)
    # Overlap: some paragraph text appears in two adjacent windows.
    joined = [c.text for c in chunks]
    assert any(set(joined[i].split()) & set(joined[i + 1].split()) for i in range(len(joined) - 1))
    assert all(c.section_locator.startswith("\u00b6") for c in chunks)
