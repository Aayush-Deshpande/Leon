"""Ingestion pipeline: dual-index write + provenance + sparse persistence.

Uses a fake embedder and an in-memory store so the pipeline is verified offline,
without a database or model weights ([320] test-data policy: mock models in units).
"""

from __future__ import annotations

import json
import tempfile
from collections.abc import Sequence
from pathlib import Path

from app.ingestion.chunk import ChunkRecord
from app.ingestion.embed import EMBEDDING_DIM
from app.ingestion.extract import load_corpus
from app.ingestion.index import IngestionResult, SourceMeta, run_ingestion

CORPUS = Path(__file__).resolve().parents[3] / "data" / "corpus" / "corpus-v1.0"


class _FakeEmbedder:
    def embed_passages(self, texts: list[str]) -> list[list[float]]:
        return [[0.1] * EMBEDDING_DIM for _ in texts]

    def embed_query(self, text: str) -> list[float]:
        return [0.1] * EMBEDDING_DIM


class _FakeStore:
    def __init__(self) -> None:
        self.sources: list[SourceMeta] = []
        self.chunks: list[ChunkRecord] = []

    def write_source(self, source: SourceMeta) -> None:
        self.sources.append(source)

    def write_chunks(
        self, chunks: Sequence[ChunkRecord], embeddings: Sequence[list[float]]
    ) -> None:
        assert len(chunks) == len(embeddings)
        assert all(len(e) == EMBEDDING_DIM for e in embeddings)
        self.chunks.extend(chunks)


def test_pipeline_indexes_fixture_corpus() -> None:
    docs = load_corpus(CORPUS)
    store = _FakeStore()
    with tempfile.TemporaryDirectory() as tmp:
        sparse_dir = Path(tmp)
        result = run_ingestion(docs, _FakeEmbedder(), store, sparse_dir)

        assert isinstance(result, IngestionResult)
        assert result.documents == 2
        assert result.chunks >= 3
        assert result.corpus_version == "corpus-v1.0"

        # Provenance recorded for every source.
        assert {s.doc_id for s in store.sources} == {
            "ica-1872-core",
            "fixture-judgment-illustrative",
        }
        assert all(s.origin and s.corpus_version == "corpus-v1.0" for s in store.sources)

        # Statute locators preserved; corpus_version stamped on chunks.
        statute_locators = {c.section_locator for c in store.chunks if c.doc_type == "statute"}
        assert {"Section 10", "Section 11"} <= statute_locators
        assert all(c.corpus_version == "corpus-v1.0" for c in store.chunks)

        # Sparse index persisted with a token list per chunk ([230] D2).
        bm25 = json.loads((sparse_dir / "corpus-v1.0" / "bm25.json").read_text("utf-8"))
        assert bm25["corpus_version"] == "corpus-v1.0"
        assert len(bm25["documents"]) == len(store.chunks)
        assert all("tokens" in d and "chunk_id" in d for d in bm25["documents"])
