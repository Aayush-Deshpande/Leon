"""Ingestion CLI entrypoint.

Usage:
    python -m app.ingestion.pipeline --corpus-version corpus-v1.0

Provisions the schema, loads the corpus from ``data/corpus/<version>/``, and runs
the ingestion pipeline. Requires DATABASE_URL ([500]) and the embedding model.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from app.config import get_settings
from app.ingestion.embed import BgeEmbedder
from app.ingestion.extract import load_corpus
from app.ingestion.index import create_pgvector_store, run_ingestion

DEFAULT_CORPUS_ROOT = Path("data/corpus")
DEFAULT_SPARSE_ROOT = Path("data/index/sparse")


def main() -> None:
    settings = get_settings()
    parser = argparse.ArgumentParser(description="Leon corpus ingestion")
    parser.add_argument("--corpus-version", default=settings.corpus_version)
    parser.add_argument("--corpus-root", type=Path, default=DEFAULT_CORPUS_ROOT)
    parser.add_argument("--sparse-root", type=Path, default=DEFAULT_SPARSE_ROOT)
    args = parser.parse_args()

    from app import db  # deferred: requires pgvector + a real database

    engine = db.create_db_engine(settings.database_url)
    db.bootstrap_schema(engine)
    session_factory = db.make_session_factory(engine)

    documents = load_corpus(args.corpus_root / args.corpus_version)
    store = create_pgvector_store(session_factory)
    result = run_ingestion(
        documents, BgeEmbedder(settings.embedding_model), store, args.sparse_root
    )
    print(
        f"Ingested {result.documents} document(s), {result.chunks} chunk(s) "
        f"for {result.corpus_version}."
    )


if __name__ == "__main__":
    main()
