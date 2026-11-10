"""Extraction & cleaning (C3).

Loads raw source documents and their provenance from ``data/corpus/<version>/``
(a ``manifest.json`` plus per-document text files) and parses them into structural
units for chunking. Works for any corpus placed under the version directory without
code changes (`[130]`).
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

_SECTION_HEADER = re.compile(r"(?m)^\s*(\d+[A-Z]?)\.\s+")
_BLANK_LINE = re.compile(r"\n\s*\n")
_WS = re.compile(r"[ \t]+")


@dataclass(frozen=True)
class ParsedDocument:
    """A source document with provenance and parsed structural units."""

    doc_id: str
    type: str  # 'statute' | 'case_law'
    title: str
    citation_label: str
    origin: str
    retrieved_at: str | None
    jurisdiction: str
    corpus_version: str
    raw_path: str
    statute_sections: list[tuple[str, str]] = field(default_factory=list)
    paragraphs: list[str] = field(default_factory=list)


def _clean(text: str) -> str:
    return _WS.sub(" ", text.replace("\r\n", "\n")).strip()


def parse_statute(text: str, fallback_locator: str) -> list[tuple[str, str]]:
    """Split statute text into (section_locator, body) by section headers."""
    matches = list(_SECTION_HEADER.finditer(text))
    if not matches:
        return [(fallback_locator, _clean(text))]
    sections: list[tuple[str, str]] = []
    for i, m in enumerate(matches):
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = _clean(text[start:end])
        if body:
            sections.append((f"Section {m.group(1)}", body))
    return sections


def parse_case_law(text: str) -> list[str]:
    """Split a judgment into paragraphs on blank lines."""
    return [_clean(p) for p in _BLANK_LINE.split(text) if p.strip()]


def load_corpus(corpus_dir: Path) -> list[ParsedDocument]:
    """Load and parse every document listed in ``<corpus_dir>/manifest.json``."""
    manifest_path = corpus_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    corpus_version = manifest["corpus_version"]
    parsed: list[ParsedDocument] = []
    for entry in manifest["documents"]:
        raw_path = corpus_dir / entry["file"]
        raw_text = raw_path.read_text(encoding="utf-8")
        doc_type = entry["type"]
        jurisdiction = entry.get("jurisdiction", "IN")
        statute_sections: list[tuple[str, str]] = []
        paragraphs: list[str] = []
        if doc_type == "statute":
            statute_sections = parse_statute(raw_text, entry["citation_label"])
        else:
            paragraphs = parse_case_law(raw_text)
        parsed.append(
            ParsedDocument(
                doc_id=entry["doc_id"],
                type=doc_type,
                title=entry["title"],
                citation_label=entry["citation_label"],
                origin=entry["origin"],
                retrieved_at=entry.get("retrieved_at"),
                jurisdiction=jurisdiction,
                corpus_version=corpus_version,
                raw_path=str(raw_path),
                statute_sections=statute_sections,
                paragraphs=paragraphs,
            )
        )
    return parsed
