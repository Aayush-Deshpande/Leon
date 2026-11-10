"""Provider-agnostic LLM client (ADR-0022, `[240]` S4).

Leon demonstrates the architecture, not a specific model. The client targets any
OpenAI-compatible provider (OpenRouter or Google Gemini's OpenAI-compatible
endpoint) selected via `[500]`. Deterministic inference (`temperature=0`) is the
default for reproducible tests/evaluation.

Reused by P4 critique (per the R-P3-1 decision); no shared module is introduced.
"""

from __future__ import annotations

from typing import Protocol

from app.config import Settings, get_settings

# OpenAI-compatible base URLs per provider ([500]).
PROVIDER_BASE_URLS = {
    "openrouter": "https://openrouter.ai/api/v1",
    "gemini": "https://generativelanguage.googleapis.com/v1beta/openai",
    "google": "https://generativelanguage.googleapis.com/v1beta/openai",
}


class LLMClient(Protocol):
    """Minimal chat-completion interface used by generation (and critique in P4)."""

    def generate(self, system: str, user: str) -> str:
        """Return the assistant message content for a system+user prompt."""
        ...


class OpenAICompatibleClient:
    """OpenAI-compatible chat client (OpenRouter / Gemini). Model is operator-selected."""

    def __init__(
        self,
        model: str,
        api_key: str | None,
        *,
        base_url: str = "https://openrouter.ai/api/v1",
        temperature: float = 0.0,
        timeout_ms: int = 30_000,
    ) -> None:
        if not model:
            raise RuntimeError("GENERATION_MODEL is not configured (see docs/50-operations/500).")
        self._model = model
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._temperature = temperature
        self._timeout_s = timeout_ms / 1000.0

    def generate(self, system: str, user: str) -> str:
        import httpx

        headers = {"Content-Type": "application/json"}
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"
        payload = {
            "model": self._model,
            "temperature": self._temperature,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }
        response = httpx.post(
            f"{self._base_url}/chat/completions",
            headers=headers,
            json=payload,
            timeout=self._timeout_s,
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        return str(content)


# Backwards-compatible alias (older imports referenced OpenRouterClient).
OpenRouterClient = OpenAICompatibleClient


def _resolve_provider(cfg: Settings) -> tuple[str, str | None]:
    """Return (base_url, api_key) for the configured provider from `[500]` settings."""
    provider = (cfg.generation_provider or "openrouter").lower()
    base_url = PROVIDER_BASE_URLS.get(provider, PROVIDER_BASE_URLS["openrouter"])
    if provider in ("gemini", "google"):
        api_key = cfg.gemini_api_key
    else:
        api_key = cfg.openrouter_api_key
    return base_url, api_key


def create_llm_client(settings: Settings | None = None, *, model: str | None = None) -> LLMClient:
    """Build the configured LLM client from `[500]` settings.

    `model` overrides the generation model (used by critique for the A-2 model family).
    """
    cfg = settings or get_settings()
    base_url, api_key = _resolve_provider(cfg)
    return OpenAICompatibleClient(
        model=model or cfg.generation_model,
        api_key=api_key,
        base_url=base_url,
        temperature=0.0,
        timeout_ms=cfg.model_call_timeout_ms,
    )
