"""Reciprocal Rank Fusion (ADR-0014, `[240]`).

Merges ranked candidate lists (dense + sparse) by rank, deduplicated by chunk id.
Rank-based fusion is used because dense cosine scores and BM25 scores are not on a
comparable scale. Default rank constant `k = 60`.
"""

from __future__ import annotations

from collections.abc import Sequence


def reciprocal_rank_fusion(rankings: Sequence[Sequence[str]], *, k: int = 60) -> list[str]:
    """Fuse ranked id lists into one ordered, de-duplicated list.

    Score(id) = sum over lists of 1 / (k + rank), rank being 0-based position.
    Ties are broken by first appearance to keep the result deterministic.
    """
    scores: dict[str, float] = {}
    first_seen: dict[str, int] = {}
    order = 0
    for ranking in rankings:
        for rank, chunk_id in enumerate(ranking):
            scores[chunk_id] = scores.get(chunk_id, 0.0) + 1.0 / (k + rank)
            if chunk_id not in first_seen:
                first_seen[chunk_id] = order
                order += 1
    return sorted(scores, key=lambda cid: (-scores[cid], first_seen[cid]))
