"""Calibration harness (ADR-0021 / P11): agreement, threshold selection, dataset."""

from __future__ import annotations

from app.critique.calibration import (
    GROUNDED,
    UNGROUNDED,
    critique_agreement,
    generate_calibration_set,
    meets_p11,
    predicted_is_grounded,
    select_thresholds,
)

from tests.critique._fixtures import grounded_judgment, make_candidate, ungrounded_judgment


def test_predicted_is_grounded_gate() -> None:
    assert predicted_is_grounded(grounded_judgment(), 0.7, 0.8) is True
    assert predicted_is_grounded(ungrounded_judgment(), 0.7, 0.8) is False
    # unverifiable present blocks grounded even with high scores
    from app.critique.types import CritiqueJudgment

    assert predicted_is_grounded(CritiqueJudgment(0.9, 0.9, ["x"]), 0.7, 0.8) is False


def test_agreement_and_threshold_selection() -> None:
    labels = [GROUNDED, GROUNDED, UNGROUNDED, UNGROUNDED]
    judgments = [
        grounded_judgment(),
        grounded_judgment(),
        ungrounded_judgment(),
        ungrounded_judgment(),
    ]
    t_rel, t_ground, agreement = select_thresholds(labels, judgments)
    assert agreement == 1.0 and meets_p11(agreement)
    assert critique_agreement(labels, judgments, t_rel, t_ground) == 1.0


def test_p11_boundary() -> None:
    assert meets_p11(0.80) is True
    assert meets_p11(0.79) is False


def test_generate_balanced_dataset() -> None:
    examples = generate_calibration_set([make_candidate()], size=6)
    assert len(examples) == 6
    labels = [e.label for e in examples]
    assert labels.count(GROUNDED) == 3 and labels.count(UNGROUNDED) == 3
    grounded = [e for e in examples if e.label == GROUNDED][0]
    ungrounded = [e for e in examples if e.label == UNGROUNDED][0]
    assert "[ica-1872-core#0000]" in grounded.draft.text  # cites a supplied chunk
    assert "fabricated-" in ungrounded.draft.text  # cites an id absent from context
