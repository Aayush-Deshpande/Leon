"""Request/response models for POST /query. Shapes owned by `[220]`."""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.orchestration.types import QueryResponse


class QueryRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2000)


class CitationModel(BaseModel):
    id: str
    chunk_id: str
    source_document: str
    locator: str
    passage: str


class RoutingModel(BaseModel):
    outcome: str
    reformulations: int


class QueryAnswerResponse(BaseModel):
    answer: str
    citations: list[CitationModel]
    confidence: str
    routing: RoutingModel
    reason: str | None = None

    @classmethod
    def from_domain(cls, response: QueryResponse) -> QueryAnswerResponse:
        return cls(
            answer=response.answer,
            citations=[
                CitationModel(
                    id=c.id,
                    chunk_id=c.chunk_id,
                    source_document=c.source_document,
                    locator=c.locator,
                    passage=c.passage,
                )
                for c in response.citations
            ],
            confidence=response.confidence,
            routing=RoutingModel(
                outcome=response.routing_outcome, reformulations=response.reformulations
            ),
            reason=response.reason,
        )
