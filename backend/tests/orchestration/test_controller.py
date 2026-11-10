"""Control-flow invariants P1-P4 + confidence + fail-closed ([210]/[320])."""

from __future__ import annotations

from app.config import Settings
from app.critique.types import CritiqueJudgment
from app.generation.types import Citation, DraftAnswer
from app.orchestration.controller import Orchestrator
from app.retrieval.service import RankedContext, RetrievedCandidate

SETTINGS = Settings(_env_file=None)  # type: ignore[call-arg]


def _ctx() -> RankedContext:
    cand = RetrievedCandidate("id#0", "text", "Section 10", "doc", "statute", "IN", 1.0)
    return RankedContext(candidates=[cand], reranker_topk_scores=[1.0])


class _Retriever:
    def retrieve(self, query: str) -> RankedContext:
        return _ctx()


class _Generator:
    def __init__(self, raises: bool = False) -> None:
        self._raises = raises

    def generate(self, query: str, context: RankedContext) -> DraftAnswer:
        if self._raises:
            raise RuntimeError("boom")
        return DraftAnswer("draft [id#0]", [Citation("c1", "id#0", "doc", "Section 10", "text")])


class _Critic:
    def __init__(self, judgments: list[CritiqueJudgment]) -> None:
        self._j = judgments
        self.calls = 0

    def evaluate(self, query, context, draft) -> CritiqueJudgment:
        self.calls += 1
        return self._j[min(self.calls - 1, len(self._j) - 1)]


class _Reformulator:
    def __init__(self) -> None:
        self.calls = 0

    def reformulate(self, query: str) -> str:
        self.calls += 1
        return f"reformulated {self.calls}"


class _Verifier:
    def __init__(self, exists: bool) -> None:
        self._exists = exists
        self.calls = 0

    def exists(self, locator: str) -> bool:
        self.calls += 1
        return self._exists


def _orch(critic, reformulator=None, verifier=None, generator=None) -> Orchestrator:
    return Orchestrator(
        retriever=_Retriever(),
        generator=generator or _Generator(),
        critic=critic,
        reformulator=reformulator or _Reformulator(),
        verifier=verifier,
        settings=SETTINGS,
    )


def test_pass_returns_high_confidence_and_always_critiques() -> None:  # P1
    critic = _Critic([CritiqueJudgment(0.9, 0.9, [])])
    resp, trace = _orch(critic).handle("q")
    assert resp.confidence == "high" and resp.routing_outcome == "returned"
    assert resp.citations and critic.calls == 1
    assert trace.retrieved_chunk_ids == ["id#0"] and trace.reranker_topk_scores == [1.0]


def test_reformulation_is_bounded_and_terminates() -> None:  # P2
    critic = _Critic([CritiqueJudgment(0.1, 0.9, [])])
    reformer = _Reformulator()
    resp, _ = _orch(critic, reformulator=reformer).handle("q")
    assert resp.confidence == "low" and resp.routing_outcome == "low_confidence"
    assert resp.reformulations == 2 and reformer.calls == 2  # MAX_REFORMULATIONS
    assert critic.calls == 3  # initial + 2 reformulated turns


def test_tool_verification_once_then_return() -> None:  # P4 + tool_verified
    critic = _Critic([CritiqueJudgment(0.9, 0.9, ["Section 10"])])
    verifier = _Verifier(exists=True)
    resp, _ = _orch(critic, verifier=verifier).handle("q")
    assert resp.routing_outcome == "tool_verified" and resp.confidence == "high"
    assert verifier.calls == 1  # at most once per turn


def test_unconfirmed_citation_never_returned_verified() -> None:  # P3
    critic = _Critic([CritiqueJudgment(0.9, 0.9, ["ghost"])])
    verifier = _Verifier(exists=False)
    resp, _ = _orch(critic, verifier=verifier).handle("q")
    assert resp.routing_outcome == "low_confidence" and resp.confidence == "low"
    assert verifier.calls == 1


def test_generation_failure_fails_closed() -> None:
    critic = _Critic([CritiqueJudgment(0.9, 0.9, [])])
    resp, _ = _orch(critic, generator=_Generator(raises=True)).handle("q")
    assert resp.confidence == "low" and resp.routing_outcome == "low_confidence"
    assert resp.reason and "pipeline error" in resp.reason
