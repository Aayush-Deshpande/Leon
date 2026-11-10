"""Critique value type. Fields mirror the `[220]` `CritiqueJudgment`; semantics `[340]`."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class CritiqueJudgment:
    """Structured critique output ([220]): relevance, groundedness, unverifiable citations."""

    relevance: float
    groundedness: float
    unverifiable: list[str] = field(default_factory=list)
