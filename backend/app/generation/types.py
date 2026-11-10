"""Generation value types. Citation fields mirror the `[220]` citation contract."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Citation:
    """A resolved citation ([220] citations[] shape)."""

    id: str
    chunk_id: str
    source_document: str
    locator: str
    passage: str


@dataclass(frozen=True)
class DraftAnswer:
    """The generation output: verbatim answer text + resolved citations."""

    text: str
    citations: list[Citation] = field(default_factory=list)
