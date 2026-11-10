"""Ingestion pipeline orchestration and index writers (C3).

extract → chunk → embed → dual-index (pgvector `chunks` + persisted BM25 tokens),
recording provenance and `corpus_version`. The dense store uses the generic `db`
infrastructure; the sparse artifact is the tokenized corpus persisted to disk
(`[230]` D2 — BM25 scoring is built at query time in P2).
"""

from __future__ import annotations

import json
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from app.ingestion.chunk import (
    ChunkRecord,
    TokenCounter,
    chunk_case_law,
    chunk_statute,
    default_count_tokens,
)
from app.ingestion.embed import Embedder
from app.ingestion.extract import ParsedDocument
from app.ingestion.tokenizer import tokenize


@dataclass(frozen=True)
class SourceMeta:
    """Provenance record written to `source_documents` ([230])."""

    doc_id: str
    title: str
    type: str
    citation_label: str
    origin: str
    retrieved_at: str | None
    corpus_version: str
    raw_path: str


@dataclass(frozen=True)
class IngestionResult:
    documents: int
    chunks: int
    corpus_version: str


class CorpusStore(Protocol):
    """Dense-store write surface used by ingestion."""

    def write_source(self, source: SourceMeta) -> None: ...
    def write_chunks(
        self, chunks: Sequence[ChunkRecord], embeddings: Sequence[list[float]]
    ) -> None: ...


def run_ingestion(
    documents: Sequence[ParsedDocument],
    embedder: Embedder,
    store: CorpusStore,
    sparse_dir: Path,
    *,
    count_tokens: TokenCounter = default_count_tokens,
) -> IngestionResult:
    """Run the full ingestion pipeline for a parsed corpus."""
    if not documents:
        raise ValueError("no documents to ingest")
    corpus_version = documents[0].corpus_version
    sparse_records: list[dict[str, object]] = []
    total_chunks = 0

    for doc in documents:
        store.write_source(_to_source_meta(doc))
        chunks = _chunk_document(doc, count_tokens)
        texts = [c.text for c in chunks]
        embeddings = embedder.embed_passages(texts) if texts else []
        store.write_chunks(chunks, embeddings)
        for chunk in chunks:
            sparse_records.append({"chunk_id": chunk.chunk_id, "tokens": tokenize(chunk.text)})
        total_chunks += len(chunks)

    _persist_sparse_index(sparse_records, sparse_dir, corpus_version)
    return IngestionResult(len(documents), total_chunks, corpus_version)


def _chunk_document(doc: ParsedDocument, count_tokens: TokenCounter) -> list[ChunkRecord]:
    if doc.type == "statute":
        return chunk_statute(
            doc.doc_id,
            doc.jurisdiction,
            doc.corpus_version,
            doc.statute_sections,
            count_tokens=count_tokens,
        )
    return chunk_case_law(
        doc.doc_id,
        doc.jurisdiction,
        doc.corpus_version,
        doc.paragraphs,
        count_tokens=count_tokens,
    )


def _to_source_meta(doc: ParsedDocument) -> SourceMeta:
    return SourceMeta(
        doc_id=doc.doc_id,
        title=doc.title,
        type=doc.type,
        citation_label=doc.citation_label,
        origin=doc.origin,
        retrieved_at=doc.retrieved_at,
        corpus_version=doc.corpus_version,
        raw_path=doc.raw_path,
    )


def _persist_sparse_index(
    records: list[dict[str, object]], sparse_dir: Path, corpus_version: str
) -> Path:
    out_dir = sparse_dir / corpus_version
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "bm25.json"
    payload = {"corpus_version": corpus_version, "documents": records}
    out_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    return out_path


def create_pgvector_store(session_factory: object) -> CorpusStore:
    """Build a pgvector-backed store. Imports `db` lazily (needs pgvector/psycopg)."""
    from app import db  # deferred: requires pgvector + a real database

    class _PgVectorStore:
        def __init__(self, factory: object) -> None:
            self._factory = factory

        def write_source(self, source: SourceMeta) -> None:
            with db.session_scope(self._factory) as session:  # type: ignore[arg-type]
                session.merge(
                    db.SourceDocument(
                        doc_id=source.doc_id,
                        title=source.title,
                        type=source.type,
                        citation_label=source.citation_label,
                        origin=source.origin,
                        retrieved_at=source.retrieved_at,
                        corpus_version=source.corpus_version,
                        raw_path=source.raw_path,
                    )
                )

        def write_chunks(
            self, chunks: Sequence[ChunkRecord], embeddings: Sequence[list[float]]
        ) -> None:
            with db.session_scope(self._factory) as session:  # type: ignore[arg-type]
                for chunk, embedding in zip(chunks, embeddings, strict=True):
                    session.merge(
                        db.Chunk(
                            chunk_id=chunk.chunk_id,
                            source_document_id=chunk.source_document_id,
                            section_locator=chunk.section_locator,
                            doc_type=chunk.doc_type,
                            jurisdiction=chunk.jurisdiction,
                            text=chunk.text,
                            embedding=embedding,
                            corpus_version=chunk.corpus_version,
                        )
                    )

    return _PgVectorStore(session_factory)
