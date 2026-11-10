"""Health / readiness route. Realizes FR-22; contract owned by `[220]`."""

from __future__ import annotations

from fastapi import APIRouter

from app.config import get_settings
from app.models.health import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Liveness/readiness check. Returns `{status, version}` per `[220]`."""
    return HealthResponse(status="ok", version=get_settings().app_version)
