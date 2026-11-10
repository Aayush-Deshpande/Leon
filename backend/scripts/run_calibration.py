"""Calibration runner (ADR-0021 / P11) — integration (needs DB + LLM).

Builds a balanced calibration set from ingested chunks, scores it with the real
critique service, selects the `[210]` thresholds that maximize critique-agreement,
and reports whether property P11 (agreement >= 0.80) is met.

Usage: python -m scripts.run_calibration
"""

from __future__ import annotations

from app.config import get_settings
from app.critique.calibration import (
    generate_calibration_set,
    meets_p11,
    run_calibration,
    select_thresholds,
)
from app.critique.critic import create_critique_service
from app.retrieval.service import RetrievedCandidate


def main() -> None:  # pragma: no cover - integration entrypoint
    from app import db
    from sqlalchemy import select

    cfg = get_settings()
    engine = db.create_db_engine(cfg.database_url)
    factory = db.make_session_factory(engine)
    with db.session_scope(factory) as session:
        rows = list(session.execute(select(db.Chunk).limit(50)).scalars().all())

    candidates = [
        RetrievedCandidate(
            r.chunk_id,
            r.text,
            r.section_locator,
            r.source_document_id,
            r.doc_type,
            r.jurisdiction,
            1.0,
        )
        for r in rows
    ]
    examples = generate_calibration_set(candidates, size=100)
    judgments = run_calibration(examples, create_critique_service())
    labels = [e.label for e in examples]
    t_rel, t_ground, agreement = select_thresholds(labels, judgments)
    print(f"Calibrated thresholds: T_relevance={t_rel}, T_groundedness={t_ground}")
    print(f"Critique-agreement={agreement:.3f}  P11(>=0.80)={meets_p11(agreement)}")


if __name__ == "__main__":  # pragma: no cover
    main()
