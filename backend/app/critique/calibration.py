"""Critique calibration harness (ADR-0021, `[340]`, property P11).

Builds a balanced grounded/ungrounded labeled set, measures critique-agreement, and
selects `[210]` thresholds that maximize agreement. Pure functions operate on
supplied judgments so the harness is unit-testable without an LLM; `run_calibration`
scores a set with a real critique service (integration-gated).
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from app.critique.types import CritiqueJudgment
from app.generation.types import DraftAnswer
from app.retrieval.service import RankedContext, RetrievedCandidate

GROUNDED = "grounded"
UNGROUNDED = "ungrounded"
P11_MIN_AGREEMENT = 0.80  # ADR-0021 / [320] P11
P11_MIN_SAMPLES = 100  # ADR-0021 minimum balanced dataset size


@dataclass(frozen=True)
class CalibrationExample:
    """A labeled calibration case ([340])."""

    query: str
    context: RankedContext
    draft: DraftAnswer
    label: str  # GROUNDED | UNGROUNDED


def generate_calibration_set(
    candidates: Sequence[RetrievedCandidate], size: int = P11_MIN_SAMPLES
) -> list[CalibrationExample]:
    """Build a balanced set: grounded (cites a supplied chunk) vs ungrounded (fabricated cite)."""
    if not candidates:
        raise ValueError("need at least one candidate to generate a calibration set")
    per_class = (size + 1) // 2
    examples: list[CalibrationExample] = []
    for i in range(per_class):
        cand = candidates[i % len(candidates)]
        ctx = RankedContext(candidates=[cand], reranker_topk_scores=[cand.score])
        # Grounded: cite the supplied chunk.
        examples.append(
            CalibrationExample(
                query=f"What does {cand.section_locator} provide? (case {i})",
                context=ctx,
                draft=DraftAnswer(text=f"{cand.text} [{cand.chunk_id}]"),
                label=GROUNDED,
            )
        )
        # Ungrounded: cite a fabricated id absent from context.
        examples.append(
            CalibrationExample(
                query=f"Unrelated question {i}",
                context=ctx,
                draft=DraftAnswer(text=f"An unsupported claim. [fabricated-{i}]"),
                label=UNGROUNDED,
            )
        )
    return examples[:size]


def predicted_is_grounded(j: CritiqueJudgment, t_relevance: float, t_groundedness: float) -> bool:
    """The `[210]` pass condition applied to a single judgment."""
    return j.relevance >= t_relevance and j.groundedness >= t_groundedness and not j.unverifiable


def critique_agreement(
    labels: Sequence[str],
    judgments: Sequence[CritiqueJudgment],
    t_relevance: float,
    t_groundedness: float,
) -> float:
    """Accuracy of the gate's grounded/ungrounded verdict vs. labels."""
    if len(labels) != len(judgments):
        raise ValueError("labels and judgments must be the same length")
    if not labels:
        return 0.0
    correct = 0
    for label, judgment in zip(labels, judgments, strict=True):
        predicted = (
            GROUNDED if predicted_is_grounded(judgment, t_relevance, t_groundedness) else UNGROUNDED
        )
        correct += int(predicted == label)
    return correct / len(labels)


def select_thresholds(
    labels: Sequence[str], judgments: Sequence[CritiqueJudgment], *, step: float = 0.05
) -> tuple[float, float, float]:
    """Grid-search (T_relevance, T_groundedness) maximizing agreement.

    Returns (t_rel, t_ground, agreement).
    """
    grid = [round(i * step, 4) for i in range(int(1 / step) + 1)]
    best = (0.0, 0.0, -1.0)
    for t_rel in grid:
        for t_ground in grid:
            score = critique_agreement(labels, judgments, t_rel, t_ground)
            if score > best[2]:
                best = (t_rel, t_ground, score)
    return best


def meets_p11(agreement: float) -> bool:
    """Property P11 gate: critique-agreement must reach the minimum ([320]/ADR-0021)."""
    return agreement >= P11_MIN_AGREEMENT


def run_calibration(
    examples: Sequence[CalibrationExample], critic: object
) -> list[CritiqueJudgment]:
    """Score each example with a critique service (integration-gated: needs a real LLM)."""
    return [critic.evaluate(e.query, e.context, e.draft) for e in examples]  # type: ignore[attr-defined]
