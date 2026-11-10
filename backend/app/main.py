"""FastAPI application entrypoint.

Assembles the HTTP surface defined in `[220]`. In P0 only `GET /health` is wired;
`POST /query` and other routes are added in their respective phases.
"""

from __future__ import annotations

from fastapi import FastAPI

from app.api.routes import evaluation, health, query, tools
from app.config import get_settings


def create_app() -> FastAPI:
    """Application factory. Assembles the `[220]` HTTP surface."""
    settings = get_settings()
    app = FastAPI(title=settings.app_name, version=settings.app_version)
    app.include_router(health.router)
    app.include_router(query.router)
    app.include_router(tools.router)
    app.include_router(evaluation.router)
    return app


app = create_app()
