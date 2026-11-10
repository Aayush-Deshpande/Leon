"""Dense retrieval + chunk fetch (C4a) against pgvector (`[230]`/`[240]` S1).

Cosine similarity per `leon.md` §5.1 (HNSW `vector_cosine_ops`). The `db` import is
deferred so the retrieval orchestration stays importable without pgvector/psycopg.
"""

from __future__ import annotations

from app.ingestion.embed import Embedder
from app.retrieval.service import ChunkData, ScoredId


class PgVectorDenseSearcher:
    """Embeds the query and returns top-k chunks by cosine similarity."""

    def __init__(self, embedder: Embedder, session_factory: object) -> None:
        self._embedder = embedder
        self._session_factory = session_factory

    def search(self, query: str, k: int) -> list[ScoredId]:
        from sqlalchemy import select

        from app import db

        vector = self._embedder.embed_query(query)
        with db.session_scope(self._session_factory) as session:  # type: ignore[arg-type]
            distance = db.Chunk.embedding.cosine_distance(vector)
            rows = session.execute(
                select(db.Chunk.chunk_id, distance.label("distance")).order_by(distance).limit(k)
            ).all()
        return [ScoredId(chunk_id=cid, score=1.0 - float(dist)) for cid, dist in rows]


class PgVectorChunkRepository:
    """Fetches chunk content + metadata for a set of chunk ids."""

    def __init__(self, session_factory: object) -> None:
        self._session_factory = session_factory

    def fetch(self, chunk_ids: list[str]) -> dict[str, ChunkData]:
        if not chunk_ids:
            return {}
        from sqlalchemy import select

        from app import db

        with db.session_scope(self._session_factory) as session:  # type: ignore[arg-type]
            rows = (
                session.execute(select(db.Chunk).where(db.Chunk.chunk_id.in_(chunk_ids)))
                .scalars()
                .all()
            )
        return {
            row.chunk_id: ChunkData(
                chunk_id=row.chunk_id,
                text=row.text,
                section_locator=row.section_locator,
                source_document_id=row.source_document_id,
                doc_type=row.doc_type,
                jurisdiction=row.jurisdiction,
            )
            for row in rows
        }
