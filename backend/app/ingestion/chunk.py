"""Structure-aligned chunking (`[130]`).

Statute: one chunk per Section; long sections split at sub-section/clause
boundaries; sentence-split as a last resort (never mid-sentence).
Case law: sliding window of ~512 tokens with ~12% overlap over paragraphs.
Every chunk is bounded at 512 tokens and carries citation metadata (`[110]`/`[230]`).
"""

from __future__ import annotations

import re
from collections.abc import Callable, Sequence
from dataclasses import dataclass

CHUNK_MAX_TOKENS = 512  # [130] chunk-size bound
CASE_LAW_OVERLAP = 0.12  # [130] sliding-window overlap

TokenCounter = Callable[[str], int]

_WORDS = re.compile(r"\S+")
_SENTENCE = re.compile(r"(?<=[.;:])\s+")
_SUBSECTION_SPLIT = re.compile(r"(?=(?:^|\s)\((?:\d+|[a-z]+)\)\s)")
_SUBSECTION_MARK = re.compile(r"\((\d+|[a-z]+)\)")


def default_count_tokens(value: str) -> int:
    """Whitespace-based token approximation (deterministic, offline).

    The production embedder's tokenizer can be injected for exact 512-token bounds;
    this default keeps chunking testable without downloading model weights (R-P1-6).
    """
    return len(_WORDS.findall(value))


@dataclass(frozen=True)
class ChunkRecord:
    """A produced chunk. Fields align with `chunks` in `[230]`."""

    chunk_id: str
    source_document_id: str
    section_locator: str
    doc_type: str
    jurisdiction: str
    text: str
    corpus_version: str


def chunk_statute(
    doc_id: str,
    jurisdiction: str,
    corpus_version: str,
    sections: Sequence[tuple[str, str]],
    *,
    count_tokens: TokenCounter = default_count_tokens,
) -> list[ChunkRecord]:
    """Chunk statute sections. `sections` = ordered (section_locator, text)."""
    pieces: list[tuple[str, str]] = []
    for locator, body in sections:
        body = body.strip()
        if not body:
            continue
        if count_tokens(body) <= CHUNK_MAX_TOKENS:
            pieces.append((locator, body))
        else:
            pieces.extend(_split_section(locator, body, count_tokens))
    return _finalize(doc_id, "statute", jurisdiction, corpus_version, pieces)


def chunk_case_law(
    doc_id: str,
    jurisdiction: str,
    corpus_version: str,
    paragraphs: Sequence[str],
    *,
    count_tokens: TokenCounter = default_count_tokens,
) -> list[ChunkRecord]:
    """Chunk a judgment into overlapping ~512-token windows over paragraphs."""
    paras = _bound_paragraphs([p.strip() for p in paragraphs if p.strip()], count_tokens)
    pieces: list[tuple[str, str]] = []
    i, n = 0, len(paras)
    while i < n:
        window: list[str] = []
        tokens = 0
        j = i
        while j < n and (not window or tokens + count_tokens(paras[j]) <= CHUNK_MAX_TOKENS):
            window.append(paras[j])
            tokens += count_tokens(paras[j])
            j += 1
        locator = f"\u00b6{i + 1}" if len(window) == 1 else f"\u00b6{i + 1}-{j}"
        pieces.append((locator, " ".join(window)))
        if j >= n:
            break
        step_back = max(1, round((j - i) * CASE_LAW_OVERLAP))
        i = max(i + 1, j - step_back)
    return _finalize(doc_id, "case_law", jurisdiction, corpus_version, pieces)


def _split_section(locator: str, body: str, count_tokens: TokenCounter) -> list[tuple[str, str]]:
    units = [u.strip() for u in _SUBSECTION_SPLIT.split(body) if u.strip()]
    if len(units) <= 1:
        return [(f"{locator} (cont.)", frag) for frag in _split_sentences(body, count_tokens)]
    out: list[tuple[str, str]] = []
    buffer: list[str] = []
    buffer_tokens = 0
    for unit in units:
        unit_tokens = count_tokens(unit)
        if unit_tokens > CHUNK_MAX_TOKENS:
            out.extend(_flush(locator, buffer))
            buffer, buffer_tokens = [], 0
            out.extend((f"{locator} (cont.)", f) for f in _split_sentences(unit, count_tokens))
            continue
        if buffer and buffer_tokens + unit_tokens > CHUNK_MAX_TOKENS:
            out.extend(_flush(locator, buffer))
            buffer, buffer_tokens = [], 0
        buffer.append(unit)
        buffer_tokens += unit_tokens
    out.extend(_flush(locator, buffer))
    return out


def _flush(locator: str, buffer: list[str]) -> list[tuple[str, str]]:
    if not buffer:
        return []
    joined = " ".join(buffer)
    mark = _SUBSECTION_MARK.search(buffer[0])
    loc = f"{locator}({mark.group(1)})" if mark else locator
    return [(loc, joined)]


def _split_sentences(body: str, count_tokens: TokenCounter) -> list[str]:
    sentences = [s.strip() for s in _SENTENCE.split(body) if s.strip()]
    frags: list[str] = []
    current: list[str] = []
    current_tokens = 0
    for sentence in sentences:
        st = count_tokens(sentence)
        if current and current_tokens + st > CHUNK_MAX_TOKENS:
            frags.append(" ".join(current))
            current, current_tokens = [], 0
        current.append(sentence)
        current_tokens += st
    if current:
        frags.append(" ".join(current))
    return frags


def _bound_paragraphs(paragraphs: list[str], count_tokens: TokenCounter) -> list[str]:
    bounded: list[str] = []
    for para in paragraphs:
        if count_tokens(para) <= CHUNK_MAX_TOKENS:
            bounded.append(para)
        else:
            bounded.extend(_split_sentences(para, count_tokens))
    return bounded


def _finalize(
    doc_id: str,
    doc_type: str,
    jurisdiction: str,
    corpus_version: str,
    pieces: Sequence[tuple[str, str]],
) -> list[ChunkRecord]:
    return [
        ChunkRecord(
            chunk_id=f"{doc_id}#{index:04d}",
            source_document_id=doc_id,
            section_locator=locator,
            doc_type=doc_type,
            jurisdiction=jurisdiction,
            text=body,
            corpus_version=corpus_version,
        )
        for index, (locator, body) in enumerate(pieces)
    ]
