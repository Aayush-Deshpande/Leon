"""Sparse retrieval (C4b) — BM25 over the P1-persisted tokenized corpus (`[230]` D2).

Loads ``bm25.json`` (chunk_id + tokens produced at ingestion via the ADR-0020
analyzer), builds a BM25Okapi index (library-backed, `rank_bm25`), and scores the
query tokenized with the same analyzer. `rank_bm25` is imported lazily.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.ingestion.tokenizer import tokenize
from app.retrieval.service import ScoredId


class Bm25SparseSearcher:
    """BM25 searcher backed by the persisted tokenized corpus."""

    def __init__(self, index_path: Path) -> None:
        self._index_path = index_path
        self._chunk_ids: list[str] = []
        self._bm25: Any = None  # rank_bm25.BM25Okapi (untyped 3rd-party; see mypy override)

    def _ensure_loaded(self) -> None:
        if self._bm25 is not None:
            return
        from rank_bm25 import BM25Okapi  # deferred: query-time scoring library

        payload = json.loads(self._index_path.read_text(encoding="utf-8"))
        docs = payload["documents"]
        self._chunk_ids = [d["chunk_id"] for d in docs]
        corpus_tokens = [list(d["tokens"]) for d in docs]
        self._bm25 = BM25Okapi(corpus_tokens)

    def search(self, query: str, k: int) -> list[ScoredId]:
        self._ensure_loaded()
        assert self._bm25 is not None
        scores = self._bm25.get_scores(tokenize(query))
        ranked = sorted(zip(self._chunk_ids, scores, strict=True), key=lambda p: p[1], reverse=True)
        return [ScoredId(chunk_id=cid, score=float(s)) for cid, s in ranked[:k] if s > 0.0]
