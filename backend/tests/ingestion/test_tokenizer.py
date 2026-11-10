"""BM25 analyzer conforms to ADR-0020."""

from __future__ import annotations

from app.ingestion.tokenizer import tokenize


def test_preserves_statutory_references() -> None:
    assert "section10(2)" in tokenize("Section 10(2) of the Act")
    assert "s.10" in tokenize("See s.10 here")
    assert "10(1)(a)" in tokenize("clause 10(1)(a) applies")


def test_removes_stopwords_and_lowercases() -> None:
    tokens = tokenize("The Free Consent of the Parties")
    assert "the" not in tokens and "of" not in tokens
    assert "free" in tokens and "consent" in tokens and "parties" in tokens


def test_no_stemming() -> None:
    tokens = tokenize("contracts contract contracting")
    assert "contracts" in tokens and "contract" in tokens and "contracting" in tokens
