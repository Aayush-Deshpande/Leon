"""Optional web-search fallback tool (A-5, FR-17) — DEFERRED.

Per assumption A-5 (`[120]`) and IMPL, this tool is optional and not part of the
`[210]` control flow. It is intentionally not implemented; enabling it requires a
future ADR that adds a corpus-miss branch to the control flow.
"""

from __future__ import annotations


def web_search(_query: str) -> None:  # pragma: no cover - deferred
    raise NotImplementedError(
        "web_fallback is deferred (A-5); enabling it requires an ADR adding a "
        "corpus-miss branch to the [210] control flow."
    )
