"""MCP-exposed citation-verification HTTP adapter (FR-16). Contract owned by `[220]`."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.tools.citation_verify import CitationVerifierAdapter

router = APIRouter(tags=["tools"])


class VerifyCitationRequest(BaseModel):
    locator: str
    quoted_text: str | None = None


class VerifyCitationResponse(BaseModel):
    exists: bool
    source_document: str | None = None
    matched_passage: str | None = None


def get_citation_verifier() -> CitationVerifierAdapter:
    return CitationVerifierAdapter()


@router.post("/tools/verify_citation", response_model=VerifyCitationResponse)
def verify_citation_route(
    payload: VerifyCitationRequest,
    verifier: CitationVerifierAdapter = Depends(get_citation_verifier),
) -> VerifyCitationResponse:
    result = verifier.verify(payload.locator, payload.quoted_text)
    return VerifyCitationResponse(
        exists=result.exists,
        source_document=result.source_document,
        matched_passage=result.matched_passage,
    )
