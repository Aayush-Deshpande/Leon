"""BM25 analyzer for sparse retrieval (ADR-0020, `[240]`).

Policy: lowercase + Unicode NFKC; tokenizer preserves statutory references
(e.g., ``s.10``, ``section 10(2)``, ``10(1)(a)``) as single tokens; English
stopwords removed; NO stemming (protect exact legal terminology).

Applied identically at index build and query time (`[230]` D2).
"""

from __future__ import annotations

import re
import unicodedata

# Minimal English stopword set (no stemming; kept deliberately small and legal-safe).
STOPWORDS: frozenset[str] = frozenset(
    {
        "a",
        "an",
        "and",
        "are",
        "as",
        "at",
        "be",
        "by",
        "for",
        "from",
        "has",
        "he",
        "in",
        "is",
        "it",
        "its",
        "of",
        "on",
        "or",
        "that",
        "the",
        "to",
        "was",
        "were",
        "will",
        "with",
        "which",
        "who",
        "this",
        "these",
        "those",
        "such",
        "any",
    }
)

# Statutory reference: optional 's.'/'section' prefix + number + optional (n)(a) groups.
_STATUTORY_REF = re.compile(r"(?:s\.?\s*|sections?\s+)?\d+[a-z]?(?:\s*\(\d+\))?(?:\s*\([a-z]+\))*")
_WORD = re.compile(r"[a-z0-9]+")
_WS = re.compile(r"\s+")


def _normalize(value: str) -> str:
    return unicodedata.normalize("NFKC", value).lower()


def _is_statutory_ref(token: str) -> bool:
    # Treat as a ref token only when it carries structure (a prefix or parenthesised group),
    # so bare words/plain integers still go through normal word tokenization.
    return ("(" in token) or token.startswith("s") or token.startswith("section")


def tokenize(value: str) -> list[str]:
    """Analyze text into BM25 tokens per ADR-0020."""
    normalized = _normalize(value)
    tokens: list[str] = []
    cursor = 0
    for match in _STATUTORY_REF.finditer(normalized):
        raw = match.group(0).strip()
        if not raw or not _is_statutory_ref(raw):
            continue
        # Emit word tokens from any gap before this reference.
        tokens.extend(_word_tokens(normalized[cursor : match.start()]))
        tokens.append(
            _WS.sub("", raw)
        )  # collapse internal spaces: "section 10(2)" -> "section10(2)"
        cursor = match.end()
    tokens.extend(_word_tokens(normalized[cursor:]))
    return tokens


def _word_tokens(segment: str) -> list[str]:
    return [t for t in _WORD.findall(segment) if t not in STOPWORDS]
