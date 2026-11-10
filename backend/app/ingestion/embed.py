"""Embedding (S1, `[240]` / ADR-0018).

Model: BAAI/bge-base-en-v1.5 (D=768), via sentence-transformers. Uses the model's
prefix convention (``query:`` / ``passage:``). Same model at ingestion and query time.

The heavy import is deferred so pure ingestion units (chunking, tokenizing) remain
importable without torch/sentence-transformers present.
"""

from __future__ import annotations

from typing import Protocol

EMBEDDING_MODEL = "BAAI/bge-base-en-v1.5"
EMBEDDING_DIM = 768
_QUERY_PREFIX = "query: "
_PASSAGE_PREFIX = "passage: "


class Embedder(Protocol):
    """Embedding interface used by ingestion (and, later, retrieval)."""

    def embed_passages(self, texts: list[str]) -> list[list[float]]:
        """Embed corpus chunks (passage prefix)."""
        ...

    def embed_query(self, text: str) -> list[float]:
        """Embed a query (query prefix)."""
        ...


class BgeEmbedder:
    """sentence-transformers implementation of `Embedder` for bge-base-en-v1.5."""

    def __init__(self, model_name: str = EMBEDDING_MODEL) -> None:
        from sentence_transformers import SentenceTransformer  # deferred heavy import

        self._model = SentenceTransformer(model_name)

    def embed_passages(self, texts: list[str]) -> list[list[float]]:
        prefixed = [f"{_PASSAGE_PREFIX}{t}" for t in texts]
        vectors = self._model.encode(prefixed, normalize_embeddings=True)
        return [list(map(float, v)) for v in vectors]

    def embed_query(self, text: str) -> list[float]:
        vector = self._model.encode(f"{_QUERY_PREFIX}{text}", normalize_embeddings=True)
        return [float(x) for x in vector]
