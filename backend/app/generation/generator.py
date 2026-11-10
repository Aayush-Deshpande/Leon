"""Generation Service (C5).

Exactly four responsibilities: build the prompt, invoke the configured LLM, parse
the response, extract citations. It performs NO confidence scoring, critique,
hallucination detection, routing, or retry — those belong to `[210]`/`[240]` S5/P4.
Implements the `Generation.generate` contract (`[220]`).
"""

from __future__ import annotations

from app.generation.llm import LLMClient, create_llm_client
from app.generation.parser import parse_answer
from app.generation.prompt import build_generation_prompt
from app.generation.types import DraftAnswer
from app.retrieval.service import RankedContext


class GenerationService:
    """Produces a cited draft answer grounded in the supplied context."""

    def __init__(self, llm: LLMClient) -> None:
        self._llm = llm

    def generate(self, query: str, context: RankedContext) -> DraftAnswer:
        system, user = build_generation_prompt(query, context)
        raw_answer = self._llm.generate(system, user)
        return parse_answer(raw_answer, context)


def create_generation_service() -> GenerationService:
    """Build the generation service with the configured provider-agnostic LLM client."""
    return GenerationService(create_llm_client())
