"""Critique output parsing: tolerant JSON extraction, validation, clamping."""

from __future__ import annotations

from app.critique.parser import CritiqueParseError, parse_critique


def test_parses_clean_json() -> None:
    j = parse_critique('{"relevance": 0.9, "groundedness": 0.3, "unverifiable": ["x"]}')
    assert j.relevance == 0.9 and j.groundedness == 0.3 and j.unverifiable == ["x"]


def test_tolerates_code_fence_and_prose() -> None:
    fenced = '```json\n{"relevance":0.5,"groundedness":0.6,"unverifiable":[]}\n```'
    assert parse_critique(fenced).groundedness == 0.6
    prose = 'Here is my review: {"relevance":0.4,"groundedness":0.2,"unverifiable":[]} done'
    assert parse_critique(prose).relevance == 0.4


def test_clamps_scores_to_unit_interval() -> None:
    j = parse_critique('{"relevance": 1.5, "groundedness": -0.2, "unverifiable": []}')
    assert j.relevance == 1.0 and j.groundedness == 0.0


def test_missing_keys_raise() -> None:
    for bad in ['{"relevance": 0.5}', "{}", "not json", '{"unverifiable": []}']:
        try:
            parse_critique(bad)
            raise AssertionError(f"expected CritiqueParseError for {bad!r}")
        except CritiqueParseError:
            pass
