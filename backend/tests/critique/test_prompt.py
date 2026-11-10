"""PT-CRIT construction (`[330]`) and separation from PT-GEN (property P5)."""

from __future__ import annotations

from app.critique.prompt import PT_CRIT_SYSTEM, build_critique_prompt
from app.generation.prompt import PT_GEN_SYSTEM

from tests.critique._fixtures import make_context, make_draft


def test_pt_crit_content() -> None:
    system, user = build_critique_prompt("What makes a contract?", make_context(), make_draft())
    assert "independent reviewer" in system
    assert "relevant" in system and "supported by the context" in system
    assert "JSON only" in system
    assert "Question: What makes a contract?" in user
    assert "[ica-1872-core#0000]" in user
    assert "Draft answer:" in user


def test_critique_prompt_is_distinct_from_generation() -> None:
    # P5: generation and critique must not share a prompt.
    assert PT_CRIT_SYSTEM != PT_GEN_SYSTEM
