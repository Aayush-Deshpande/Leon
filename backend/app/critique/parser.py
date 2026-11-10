"""Parse the PT-CRIT structured output into a CritiqueJudgment.

Tolerates code fences / surrounding prose by extracting the JSON object; validates
required keys and clamps scores to [0,1]. Unusable output raises CritiqueParseError,
which the orchestrator (`[210]`) treats as a failed critique (fail-closed to
low-confidence, `[210]` m7).
"""

from __future__ import annotations

import json

from app.critique.types import CritiqueJudgment


class CritiqueParseError(ValueError):
    """Raised when the critique output cannot be parsed into a CritiqueJudgment."""


def _extract_json_object(raw: str) -> dict[str, object]:
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass
    start, end = raw.find("{"), raw.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise CritiqueParseError("no JSON object found in critique output")
    try:
        parsed = json.loads(raw[start : end + 1])
    except json.JSONDecodeError as exc:
        raise CritiqueParseError(f"invalid JSON in critique output: {exc}") from exc
    if not isinstance(parsed, dict):
        raise CritiqueParseError("critique output is not a JSON object")
    return parsed


def _clamp_unit(value: object, field: str) -> float:
    try:
        number = float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError) as exc:
        raise CritiqueParseError(f"'{field}' is not a number") from exc
    return max(0.0, min(1.0, number))


def parse_critique(raw: str) -> CritiqueJudgment:
    """Parse raw model output into a validated CritiqueJudgment."""
    obj = _extract_json_object(raw)
    if "relevance" not in obj or "groundedness" not in obj:
        raise CritiqueParseError("missing required keys 'relevance'/'groundedness'")
    unverifiable_raw = obj.get("unverifiable", [])
    if not isinstance(unverifiable_raw, list):
        raise CritiqueParseError("'unverifiable' must be a list")
    return CritiqueJudgment(
        relevance=_clamp_unit(obj["relevance"], "relevance"),
        groundedness=_clamp_unit(obj["groundedness"], "groundedness"),
        unverifiable=[str(item) for item in unverifiable_raw],
    )
