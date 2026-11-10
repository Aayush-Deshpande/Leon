"""Citation-verification tool (C8, FR-16, ADR-0019).

Checks a cited locator/quote against the RAW source documents (D4, ground truth per
`[130]`) — never against embeddings. Matching: normalized substring, with a
configurable fuzzy fallback (default 0.95) to tolerate OCR variance. This is the
capability behind both the HTTP route and the MCP tool (one implementation).
"""

from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path

from app.config import get_settings

_PUNCT = re.compile(r"[^\w\s]")
_WS = re.compile(r"\s+")


def normalize(value: str) -> str:
    folded = _PUNCT.sub(" ", unicodedata.normalize("NFKC", value).lower())
    return _WS.sub(" ", folded).strip()


@dataclass(frozen=True)
class VerificationResult:
    exists: bool
    source_document: str | None
    matched_passage: str | None


def verify_citation(
    locator: str,
    quoted_text: str | None,
    sources: list[tuple[str, str]],
    fuzzy_threshold: float,
) -> VerificationResult:
    """Verify a citation against raw sources = list of (doc_id, raw_text)."""
    if quoted_text:
        nq = normalize(quoted_text)
        if not nq:
            return VerificationResult(False, None, None)
        for doc_id, text in sources:
            if nq in normalize(text):
                return VerificationResult(True, doc_id, quoted_text)
        best_ratio, best_doc = 0.0, None
        for doc_id, text in sources:
            nt = normalize(text)
            match = SequenceMatcher(None, nq, nt).find_longest_match(0, len(nq), 0, len(nt))
            ratio = match.size / len(nq)
            if ratio > best_ratio:
                best_ratio, best_doc = ratio, doc_id
        if best_ratio >= fuzzy_threshold:
            return VerificationResult(True, best_doc, quoted_text)
        return VerificationResult(False, None, None)

    nl = normalize(locator)
    for doc_id, text in sources:
        if nl and nl in normalize(text):
            return VerificationResult(True, doc_id, None)
    return VerificationResult(False, None, None)


def _load_sources(corpus_dir: Path) -> list[tuple[str, str]]:
    manifest = json.loads((corpus_dir / "manifest.json").read_text(encoding="utf-8"))
    return [
        (entry["doc_id"], (corpus_dir / entry["file"]).read_text(encoding="utf-8"))
        for entry in manifest["documents"]
    ]


class CitationVerifierAdapter:
    """Loads raw sources from the corpus dir and verifies citations (ADR-0019)."""

    def __init__(
        self, corpus_dir: Path | None = None, fuzzy_threshold: float | None = None
    ) -> None:
        cfg = get_settings()
        self._corpus_dir = corpus_dir or (Path("data/corpus") / cfg.corpus_version)
        self._threshold = (
            cfg.citation_fuzzy_threshold if fuzzy_threshold is None else fuzzy_threshold
        )
        self._sources: list[tuple[str, str]] | None = None

    def _ensure_loaded(self) -> list[tuple[str, str]]:
        if self._sources is None:
            self._sources = _load_sources(self._corpus_dir)
        return self._sources

    def verify(self, locator: str, quoted_text: str | None = None) -> VerificationResult:
        return verify_citation(locator, quoted_text, self._ensure_loaded(), self._threshold)

    def exists(self, locator: str) -> bool:
        """Controller hook ([210] TOOL): is this citation present in ground truth?"""
        return self.verify(locator, None).exists
