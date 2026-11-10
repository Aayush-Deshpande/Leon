"""Query reformulation (PT-REFORM, `[330]`), used by the `[210]` REFORMULATE branch."""

from __future__ import annotations

from typing import Protocol

from app.generation.llm import LLMClient

PT_REFORM_SYSTEM = (
    "Rewrite the question to improve retrieval of relevant legal passages, "
    "preserving the user's intent. Return only the rewritten query."
)


class Reformulator(Protocol):
    def reformulate(self, query: str) -> str: ...


class LLMReformulator:
    """Reformulates a query via the provider-agnostic LLM client."""

    def __init__(self, llm: LLMClient) -> None:
        self._llm = llm

    def reformulate(self, query: str) -> str:
        user = f"Original question: {query}\nPrior retrieval was insufficient."
        return self._llm.generate(PT_REFORM_SYSTEM, user).strip() or query
