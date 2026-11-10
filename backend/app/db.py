"""Database infrastructure (generic).

Owns engine creation, session management, the ORM base, the `[230]` schema
definitions, and schema bootstrap. This module is infrastructure only — it holds
no ingestion, retrieval, evaluation, or AI logic (those live in their components).

Schema is the frozen contract in `docs/20-architecture/230_DATA_MODEL_AND_STORAGE.md`.
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager

from pgvector.sqlalchemy import Vector
from sqlalchemy import Index, Integer, Text, create_engine, text
from sqlalchemy.dialects.postgresql import ARRAY, REAL, TIMESTAMP, UUID
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

from app.config import get_settings

EMBEDDING_DIM = 768  # [230]/ADR-0018 — matches BAAI/bge-base-en-v1.5


class Base(DeclarativeBase):
    """Declarative ORM base."""


class SourceDocument(Base):
    """`source_documents` table ([230])."""

    __tablename__ = "source_documents"

    doc_id: Mapped[str] = mapped_column(Text, primary_key=True)
    title: Mapped[str] = mapped_column(Text)
    type: Mapped[str] = mapped_column(Text)  # 'statute' | 'case_law'
    citation_label: Mapped[str] = mapped_column(Text)
    origin: Mapped[str] = mapped_column(Text)
    retrieved_at: Mapped[str | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    corpus_version: Mapped[str] = mapped_column(Text)
    raw_path: Mapped[str] = mapped_column(Text)


class Chunk(Base):
    """`chunks` table ([230]). Dense vector column dim = 768 (ADR-0018)."""

    __tablename__ = "chunks"

    chunk_id: Mapped[str] = mapped_column(Text, primary_key=True)
    source_document_id: Mapped[str] = mapped_column(Text)
    section_locator: Mapped[str] = mapped_column(Text)
    doc_type: Mapped[str] = mapped_column(Text)
    jurisdiction: Mapped[str] = mapped_column(Text)
    text: Mapped[str] = mapped_column(Text)
    embedding: Mapped[list[float]] = mapped_column(Vector(EMBEDDING_DIM))
    corpus_version: Mapped[str] = mapped_column(Text)

    __table_args__ = (
        Index(
            "ix_chunks_embedding_hnsw",
            "embedding",
            postgresql_using="hnsw",
            postgresql_with={"m": 16, "ef_construction": 64},
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
    )


class Trace(Base):
    """`traces` table ([230]). Provisioned here; populated in P7 (evaluation)."""

    __tablename__ = "traces"

    trace_id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    query_text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[str | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    corpus_version: Mapped[str] = mapped_column(Text)
    retrieved_chunk_ids: Mapped[list[str]] = mapped_column(ARRAY(Text))
    draft_answer: Mapped[str] = mapped_column(Text)
    relevance_score: Mapped[float | None] = mapped_column(REAL, nullable=True)
    groundedness_score: Mapped[float | None] = mapped_column(REAL, nullable=True)
    unverifiable_citations: Mapped[list[str]] = mapped_column(ARRAY(Text))
    routing_outcome: Mapped[str] = mapped_column(Text)
    reformulations: Mapped[int] = mapped_column(Integer)
    reranker_topk_scores: Mapped[list[float]] = mapped_column(ARRAY(REAL))
    confidence: Mapped[str] = mapped_column(Text)
    latency_ms: Mapped[int] = mapped_column(Integer)


def create_db_engine(database_url: str | None = None) -> Engine:
    """Create a SQLAlchemy engine from the configured DATABASE_URL ([500])."""
    url = database_url or get_settings().database_url
    if not url:
        raise RuntimeError("DATABASE_URL is not configured (see docs/50-operations/500).")
    return create_engine(url, pool_pre_ping=True)


def make_session_factory(engine: Engine) -> sessionmaker[Session]:
    """Return a session factory bound to the given engine."""
    return sessionmaker(bind=engine, expire_on_commit=False)


@contextmanager
def session_scope(session_factory: sessionmaker[Session]) -> Iterator[Session]:
    """Transactional session scope with commit/rollback lifecycle."""
    session = session_factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def bootstrap_schema(engine: Engine) -> None:
    """Enable the pgvector extension and create all `[230]` tables/indexes (idempotent)."""
    with engine.begin() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    Base.metadata.create_all(engine)
