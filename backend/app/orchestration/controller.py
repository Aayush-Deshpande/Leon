"""Agent Controller (C7) — the in-loop evaluation state machine (`[210]`).

Implements RETRIEVE → GENERATE → CRITIQUE → DECIDE → {RETURN, REFORMULATE, TOOL,
LOW_CONFIDENCE}. Enforces the control-flow invariants (`[320]` P1–P4):
  P1  no answer returned without a completed critique;
  P2  reformulations never exceed MAX_REFORMULATIONS; the loop always terminates;
  P3  a citation not confirmed present is never returned as verified;
  P4  the citation-verification tool is invoked at most once per turn.
Failures/timeouts fail closed to LOW_CONFIDENCE (`[210]` m7).
"""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import Protocol

from app.config import Settings, get_settings
from app.critique.types import CritiqueJudgment
from app.generation.types import DraftAnswer
from app.orchestration.reformulate import Reformulator
from app.orchestration.types import (
    CONFIDENCE_HIGH,
    CONFIDENCE_LOW,
    LOW_CONFIDENCE,
    LOW_CONFIDENCE_ADVISORY,
    REFORMULATED,
    RETURNED,
    TOOL_VERIFIED,
    QueryResponse,
    TraceRecord,
)
from app.retrieval.service import RankedContext


class Retriever(Protocol):
    def retrieve(self, query: str) -> RankedContext: ...


class Generator(Protocol):
    def generate(self, query: str, context: RankedContext) -> DraftAnswer: ...


class Critic(Protocol):
    def evaluate(
        self, query: str, context: RankedContext, draft: DraftAnswer
    ) -> CritiqueJudgment: ...


class CitationVerifier(Protocol):
    def exists(self, locator: str) -> bool: ...


class Orchestrator:
    """Routes a query through the in-loop evaluation control flow."""

    def __init__(
        self,
        retriever: Retriever,
        generator: Generator,
        critic: Critic,
        reformulator: Reformulator,
        verifier: CitationVerifier | None = None,
        settings: Settings | None = None,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self._retriever = retriever
        self._generator = generator
        self._critic = critic
        self._reformulator = reformulator
        self._verifier = verifier
        self._cfg = settings or get_settings()
        self._clock = clock

    def handle(self, query: str) -> tuple[QueryResponse, TraceRecord]:
        started = self._clock()
        cfg = self._cfg
        current_query = query
        reformulations = 0

        while True:
            try:
                context = self._retrieve_with_retry(current_query)
                draft = self._generator.generate(current_query, context)
                judgment = self._critic.evaluate(
                    current_query, context, draft
                )  # P1: always critique
            except Exception as exc:  # noqa: BLE001 — fail closed ([210] m7)
                return self._low_confidence(
                    query, reformulations, reason=f"pipeline error: {exc}", started=started
                )

            tool_used = False
            unverifiable = list(judgment.unverifiable)

            # DECIDE (with at most one tool verification per turn — P4).
            if self._passes(judgment.relevance, judgment.groundedness, unverifiable):
                return self._returned(
                    query, context, draft, judgment, reformulations, tool_used, started
                )

            if unverifiable and self._verifier is not None:
                unverifiable = self._verify_citations(
                    unverifiable
                )  # P3: confirmed-absent stay unverifiable
                tool_used = True
                if self._passes(judgment.relevance, judgment.groundedness, unverifiable):
                    return self._returned(
                        query, context, draft, judgment, reformulations, tool_used, started
                    )

            if judgment.relevance < cfg.t_relevance and reformulations < cfg.max_reformulations:
                reformulations += 1  # P2: bounded
                current_query = self._reformulator.reformulate(query)
                continue

            return self._low_confidence(
                query,
                reformulations,
                reason="insufficient groundedness or relevance after evaluation",
                started=started,
                context=context,
                draft=draft,
                judgment=judgment,
                unverifiable=unverifiable,
            )

    def _passes(self, relevance: float, groundedness: float, unverifiable: list[str]) -> bool:
        return (
            relevance >= self._cfg.t_relevance
            and groundedness >= self._cfg.t_groundedness
            and not unverifiable
        )

    def _verify_citations(self, unverifiable: list[str]) -> list[str]:
        assert self._verifier is not None
        # Keep only citations the tool CANNOT confirm present (never mark absent as verified — P3).
        return [c for c in unverifiable if not self._verifier.exists(c)]

    def _retrieve_with_retry(self, query: str) -> RankedContext:
        try:
            return self._retriever.retrieve(query)
        except Exception:  # noqa: BLE001 — one bounded retry, then propagate (fail closed)
            return self._retriever.retrieve(query)

    def _returned(
        self, query, context, draft, judgment, reformulations, tool_used, started
    ) -> tuple[QueryResponse, TraceRecord]:
        outcome = RETURNED
        if reformulations > 0:
            outcome = REFORMULATED
        elif tool_used:
            outcome = TOOL_VERIFIED
        response = QueryResponse(
            answer=draft.text,
            citations=draft.citations,
            confidence=CONFIDENCE_HIGH,
            routing_outcome=outcome,
            reformulations=reformulations,
            reason=None,
        )
        trace = self._trace(
            query,
            context,
            draft,
            judgment,
            outcome,
            reformulations,
            CONFIDENCE_HIGH,
            started,
            unverifiable=judgment.unverifiable,
        )
        return response, trace

    def _low_confidence(
        self,
        query,
        reformulations,
        *,
        reason,
        started,
        context=None,
        draft=None,
        judgment=None,
        unverifiable=None,
    ) -> tuple[QueryResponse, TraceRecord]:
        response = QueryResponse(
            answer=LOW_CONFIDENCE_ADVISORY,
            citations=[],
            confidence=CONFIDENCE_LOW,
            routing_outcome=LOW_CONFIDENCE,
            reformulations=reformulations,
            reason=reason,
        )
        trace = self._trace(
            query,
            context,
            draft,
            judgment,
            LOW_CONFIDENCE,
            reformulations,
            CONFIDENCE_LOW,
            started,
            unverifiable=unverifiable
            if unverifiable is not None
            else (judgment.unverifiable if judgment else []),
        )
        return response, trace

    def _trace(
        self,
        query,
        context,
        draft,
        judgment,
        outcome,
        reformulations,
        confidence,
        started,
        *,
        unverifiable,
    ) -> TraceRecord:
        elapsed_ms = int((self._clock() - started) * 1000)
        return TraceRecord(
            query_text=query,
            corpus_version=self._cfg.corpus_version,
            retrieved_chunk_ids=[c.chunk_id for c in context.candidates] if context else [],
            draft_answer=draft.text if draft else "",
            relevance_score=judgment.relevance if judgment else None,
            groundedness_score=judgment.groundedness if judgment else None,
            unverifiable_citations=list(unverifiable),
            routing_outcome=outcome,
            reformulations=reformulations,
            reranker_topk_scores=list(context.reranker_topk_scores) if context else [],
            confidence=confidence,
            latency_ms=elapsed_ms,
        )
