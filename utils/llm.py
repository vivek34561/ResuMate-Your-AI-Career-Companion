"""Central LLM management: providers and models.

This module centralizes how LLMs are invoked and which models are used.
It wraps the existing provider helpers in `utils.llm_providers` and
exposes a small, unified interface for chat calls.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional, List, Dict, Any

from .llm_providers import groq_chat as _groq_chat

# Catalog of commonly used models per provider
AVAILABLE_MODELS: Dict[str, List[str]] = {
    "groq": [
        "openai/gpt-oss-20b",
        "openai/gpt-oss-120b",
        "llama-3.3-70b-versatile",
    ],
}

DEFAULTS = {
    "groq": os.getenv("GROQ_MODEL") or "openai/gpt-oss-20b",
}


@dataclass
class LLMConfig:
    provider: str = "groq"
    model: Optional[str] = None
    api_key: Optional[str] = None  # required for groq

    def resolved_model(self) -> str:
        if self.model:
            return self.model
        return DEFAULTS.get(self.provider, "openai/gpt-oss-20b")

    @staticmethod
    def from_env(provider: Optional[str] = None) -> "LLMConfig":
        prov = (provider or os.getenv("PROVIDER") or "groq").lower()
        if prov == "groq":
            return LLMConfig(
                provider="groq",
                model=os.getenv("GROQ_MODEL") or DEFAULTS["groq"],
                api_key=os.getenv("GROQ_API_KEY") or None,
            )
        else:
            # Fallback to groq
            return LLMConfig(
                provider="groq",
                model=os.getenv("GROQ_MODEL") or DEFAULTS["groq"],
                api_key=os.getenv("GROQ_API_KEY") or None,
            )


def llm_chat(config: LLMConfig, messages: List[Dict[str, Any]], temperature: float = 0.2, max_tokens: int = 600) -> str:
    """Unified chat interface.

    - For provider == "groq": uses `_groq_chat(api_key, messages, model, temperature, max_tokens)`.
    """
    prov = (config.provider or "groq").lower()
    model = config.resolved_model()

    # default to groq
    api_key = config.api_key or os.getenv("GROQ_API_KEY")
    return _groq_chat(api_key, messages=messages, model=model, temperature=temperature, max_tokens=max_tokens)


def list_models(provider: Optional[str] = None) -> List[str]:
    """Return available model names for a given provider, or for the default provider.
    This does not query remote; it returns our local catalog.
    """
