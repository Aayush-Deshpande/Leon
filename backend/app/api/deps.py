"""FastAPI dependency wiring.

Builds the Orchestrator from real components. Heavy construction (DB engine, models)
is lazy and happens on first request; tests override `get_orchestrator`.
"""

from __future__ import annotations

from functools import lru_cache
from typing import TYPE_CHECKING

from app.orchestration.controller import Orchestrator

if TYPE_CHECKING:
    from app.evaluation.logger import TraceSink


def get_trace_logger() -> TraceSink:
    """Construct the trace logger (lazy DB access)."""
    from app import db
    from app.config import get_settings
    from app.evaluation.logger import TraceLogger

    engine = db.create_db_engine(get_settings().database_url)
    return TraceLogger(db.make_session_factory(engine))


@lru_cache
def get_orchestrator() -> Orchestrator:
    """Construct the production orchestrator (real retrieval/generation/critique/tools)."""
    from app import db
    from app.config import get_settings
    from app.critique.critic import create_critique_service
    from app.generation.generator import create_generation_service
    from app.generation.llm import create_llm_client
    from app.orchestration.reformulate import LLMReformulator
    from app.retrieval.service import RankedContext, create_retriever, retrieve
    from app.tools.citation_verify import CitationVerifierAdapter

    cfg = get_settings()
    engine = db.create_db_engine(cfg.database_url)
    session_factory = db.make_session_factory(engine)
    dense, sparse, repository, reranker = create_retriever(session_factory, cfg)

    class _Retriever:
        def retrieve(self, query: str) -> RankedContext:
            return retrieve(
                query,
                dense=dense,
                sparse=sparse,
                repository=repository,
                reranker=reranker,
                settings=cfg,
            )

    return Orchestrator(
        retriever=_Retriever(),
        generator=create_generation_service(),
        critic=create_critique_service(),
        reformulator=LLMReformulator(create_llm_client()),
        verifier=CitationVerifierAdapter(),
        settings=cfg,
    )
