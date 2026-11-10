"""Critique Service orchestration with a fake LLM (distinct call; no routing)."""

from __future__ import annotations

from app.critique.critic import CritiqueService
from app.critique.types import CritiqueJudgment

from tests.critique._fixtures import make_context, make_draft


class _FakeLLM:
    def __init__(self, reply: str) -> None:
        self._reply = reply
        self.systems: list[str] = []

    def generate(self, system: str, user: str) -> str:
        self.systems.append(system)
        return self._reply


def test_evaluate_returns_judgment() -> None:
    llm = _FakeLLM('{"relevance": 0.8, "groundedness": 0.7, "unverifiable": []}')
    judgment = CritiqueService(llm).evaluate("q", make_context(), make_draft())
    assert isinstance(judgment, CritiqueJudgment)
    assert judgment.relevance == 0.8 and judgment.groundedness == 0.7
    assert len(llm.systems) == 1  # exactly one critique call
    assert "independent reviewer" in llm.systems[0]  # used PT-CRIT, not PT-GEN


def test_flags_unverifiable_citation() -> None:
    llm = _FakeLLM('{"relevance": 0.6, "groundedness": 0.2, "unverifiable": ["ghost-1"]}')
    judgment = CritiqueService(llm).evaluate("q", make_context(), make_draft())
    assert judgment.unverifiable == ["ghost-1"]
