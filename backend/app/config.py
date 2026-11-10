"""Application configuration.

Single source of runtime configuration, wired to the environment contract in
`docs/50-operations/500_DEPLOYMENT_AND_ENVIRONMENT.md` and the parameter matrix
`docs/40-planning/470_CONFIGURATION_MATRIX.md`.

Security: secrets are read from the environment only and are never hard-coded or
logged (`[310]` SEC-2). The service binds to `127.0.0.1` by default (`[310]` SEC-1).
"""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typed runtime settings. Field defaults match `[470]`/`[500]`."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "leon"
    app_version: str = "0.1.0"
    bind_host: str = "127.0.0.1"  # SEC-1: never bind to a public interface without a proxy/CR
    bind_port: int = 8000

    # Embedding — HARD contract (ADR-0018); model/dim change requires a CR + re-embed.
    embedding_provider: str = "sentence-transformers"
    embedding_model: str = "BAAI/bge-base-en-v1.5"
    embedding_dim: int = 768

    # Reranker (config, [240])
    reranker_model: str = "BAAI/bge-reranker-base"

    # Generation / Critique — provider-agnostic interface (ADR-0022); model is operator-selected.
    generation_provider: str = "gemini"
    generation_model: str = "gemini-2.0-flash"  # operator-selected via env (GENERATION_MODEL)
    critique_model: str = ""  # defaults to generation_model when empty (A-2)

    # Retrieval sizing & fusion ([240] / ADR-0014)
    k_dense: int = 20
    k_sparse: int = 20
    top_n: int = 5
    k_rrf: int = 60

    # Vector index (pgvector HNSW, [230] / ADR-0006)
    hnsw_m: int = 16
    hnsw_ef_construction: int = 64

    # Control-flow thresholds & retry ([210]); provisional until calibrated ([340]).
    t_relevance: float = 0.70
    t_groundedness: float = 0.80
    max_reformulations: int = 2

    # Citation verification ([220] / ADR-0019)
    citation_fuzzy_threshold: float = 0.95

    # Timeouts & limits
    model_call_timeout_ms: int = 30_000
    rate_limit_rpm: int = 60

    # Corpus ([130])
    corpus_version: str = "corpus-v1.0"

    # Secrets — env only; default None so nothing sensitive is embedded in code.
    database_url: str | None = Field(default=None)
    openrouter_api_key: str | None = Field(default=None, repr=False)
    gemini_api_key: str | None = Field(default=None, repr=False)

    @property
    def effective_critique_model(self) -> str:
        """Critique defaults to the generation model family (A-2) unless overridden."""
        return self.critique_model or self.generation_model


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance (single load per process)."""
    return Settings()
