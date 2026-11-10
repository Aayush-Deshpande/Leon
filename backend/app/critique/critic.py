"""Critique Service (C6).

Exactly: build PT-CRIT, invoke the LLM (a distinct call from generation), parse the
structured output into a CritiqueJudgment. It does NOT route, retry, verify against
raw ground truth (P6/MCP), or apply thresholds (`[210]`). Reuses the provider-agnostic
client from `app/generation/llm.py` (A-2: same model family by default).
"""

from __future__ import annotations

from app.config import Settings, get_settings
from app.critique.parser import parse_critique
from app.critique.prompt import build_critique_prompt
from app.critique.types import CritiqueJudgment
from app.generation.llm import LLMClient, create_llm_client
from app.generation.types import DraftAnswer
from app.retrieval.service import RankedContext


class CritiqueService:
    """Independently evaluates a draft answer's relevance and citation-groundedness."""

    def __init__(self, llm: LLMClient) -> None:
        self._llm = llm

    def evaluate(self, query: str, context: RankedContext, draft: DraftAnswer) -> CritiqueJudgment:
        system, user = build_critique_prompt(query, context, draft)
        raw = self._llm.generate(system, user)
        return parse_critique(raw)


def create_critique_service(settings: Settings | None = None) -> CritiqueService:
    """Build the critique service with the critique model (A-2 default, config `[500]`)."""
    cfg = settings or get_settings()
    client = create_llm_client(cfg, model=cfg.effective_critique_model)
    return CritiqueService(client)
