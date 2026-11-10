"""Embedding stage constants match the frozen `[240]`/ADR-0018 contract.

The real BgeEmbedder is exercised in the networked integration environment
(model weights download); here we assert the pinned contract constants.
"""

from __future__ import annotations

from app.ingestion import embed


def test_embedding_contract_constants() -> None:
    assert embed.EMBEDDING_MODEL == "BAAI/bge-base-en-v1.5"
    assert embed.EMBEDDING_DIM == 768
