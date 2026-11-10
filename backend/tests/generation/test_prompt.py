"""PT-GEN prompt construction (`[330]`)."""

from __future__ import annotations

from app.generation.prompt import build_generation_prompt

from tests.generation._fixtures import make_context


def test_prompt_follows_pt_gen() -> None:
    system, user = build_generation_prompt("What makes an agreement a contract?", make_context())
    # Anti-hallucination + citation instructions present ([330]).
    assert "ONLY" in system and "insufficient" in system and "[chunk_id]" in system
    # Query + context rendered with [chunk_id] and section locator.
    assert "Question: What makes an agreement a contract?" in user
    assert "[ica-1872-core#0000] (Section 10)" in user
    assert "[ica-1872-core#0001] (Section 11)" in user
