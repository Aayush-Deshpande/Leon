"""Config defaults match the frozen `[470]`/`[500]` contract and `[310]` security rules."""

from __future__ import annotations

from app.config import Settings


def _settings(**overrides: object) -> Settings:
    # `_env_file` is a valid pydantic-settings init kwarg; not in the typed signature.
    return Settings(_env_file=None, **overrides)  # type: ignore[call-arg]


def test_defaults_match_configuration_matrix() -> None:
    s = _settings()
    # [240]/ADR-0018 — embedding HARD contract
    assert s.embedding_model == "BAAI/bge-base-en-v1.5"
    assert s.embedding_dim == 768
    # [240]/ADR-0014 — sizing & fusion
    assert (s.k_dense, s.k_sparse, s.top_n, s.k_rrf) == (20, 20, 5, 60)
    # [210] — thresholds & retry
    assert (s.t_relevance, s.t_groundedness, s.max_reformulations) == (0.70, 0.80, 2)
    # [220]/ADR-0019 — citation fuzzy threshold
    assert s.citation_fuzzy_threshold == 0.95
    # [230]/ADR-0006 — HNSW params
    assert (s.hnsw_m, s.hnsw_ef_construction) == (16, 64)


def test_sec1_binds_localhost_by_default() -> None:
    # [310] SEC-1: no public bind by default
    assert _settings().bind_host == "127.0.0.1"


def test_secrets_are_none_by_default() -> None:
    # [310] SEC-2: no secrets embedded in code
    s = _settings()
    assert s.database_url is None
    assert s.openrouter_api_key is None


def test_critique_defaults_to_generation_model() -> None:
    # A-2: critique uses the generation model family unless overridden
    s = _settings(generation_model="some/model")
    assert s.effective_critique_model == "some/model"
    s2 = _settings(generation_model="a/b", critique_model="c/d")
    assert s2.effective_critique_model == "c/d"
