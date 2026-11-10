"""Health endpoint schema. Conforms to `[220]` GET /health contract."""

from __future__ import annotations

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Response body for GET /health per `[220]`."""

    status: str
    version: str
