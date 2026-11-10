"""Generation Service orchestration with a fake LLM (provider-agnostic; no critique)."""

from __future__ import annotations

from app.generation.generator import GenerationService
from app.generation.types import DraftAnswer

from tests.generation._fixtures import make_context


class _FakeLLM:
    def __init__(self, reply: str) -> None:
        self._reply = reply
        self.calls: list[tuple[str, str]] = []

    def generate(self, system: str, user: str) -> str:
        self.calls.append((system, user))
        return self._reply


def test_generate_returns_cited_draft_from_context() -> None:
    llm = _FakeLLM("Agreements are contracts by free consent [ica-1872-core#0000].")
    draft = GenerationService(llm).generate("q", make_context())
    assert isinstance(draft, DraftAnswer)
    assert len(llm.calls) == 1  # LLM invoked exactly once
    assert [c.chunk_id for c in draft.citations] == ["ica-1872-core#0000"]


def test_generator_preserves_unknown_markers_and_adds_nothing_else() -> None:
    llm = _FakeLLM("Draft with a bogus cite [not-in-context].")
    draft = GenerationService(llm).generate("q", make_context())
    assert "[not-in-context]" in draft.text  # verbatim
    assert draft.citations == []
    # DraftAnswer carries only text + citations — no scores/routing fields leaked in.
    assert set(vars(draft).keys()) == {"text", "citations"}
