"""BM25 sparse search over persisted tokens. Runs only where rank_bm25 is available."""

from __future__ import annotations

import importlib.util
import json
import tempfile
from pathlib import Path

from app.ingestion.tokenizer import tokenize
from app.retrieval.sparse import Bm25SparseSearcher

_HAS_RANK_BM25 = importlib.util.find_spec("rank_bm25") is not None


def test_bm25_ranks_matching_chunk_first() -> None:
    if not _HAS_RANK_BM25:
        print("SKIP test_bm25 (rank_bm25 not installed)")
        return
    # >=3 docs so BM25 IDF is non-degenerate: a term in 1 of N docs has idf>0 only when N>2
    # (with N=2, idf(term in 1 doc) = log(1.5)-log(1.5) = 0, so every hit scores 0).
    docs = [
        {"chunk_id": "s10", "tokens": tokenize("free consent lawful consideration contract")},
        {"chunk_id": "s11", "tokens": tokenize("competent to contract age of majority sound mind")},
        {
            "chunk_id": "s12",
            "tokens": tokenize("registration of documents in writing before witnesses"),
        },
    ]
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "bm25.json"
        path.write_text(json.dumps({"corpus_version": "v", "documents": docs}), encoding="utf-8")
        searcher = Bm25SparseSearcher(path)
        hits = searcher.search("age of majority to be competent", k=2)
        assert hits and hits[0].chunk_id == "s11"
