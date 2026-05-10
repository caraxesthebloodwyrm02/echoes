"""Backend-aware default chat model names for EchoesAgentsV1 runtime specs.

When ``MISTRAL_API_KEY`` or ``GRIDSTRAL_API_KEY`` is set, defaults prefer Mistral
model IDs so specs match an OpenAI-compatible Mistral HTTP stack.

Call sites that invoke **OpenAI's** ``api.openai.com`` chat completions must use
:func:`openai_chat_completion_models` instead, which keeps OpenAI model IDs even
if Mistral keys are present for other surfaces.
"""

from __future__ import annotations

import os


def mistral_api_key() -> str | None:
    return os.getenv("MISTRAL_API_KEY") or os.getenv("GRIDSTRAL_API_KEY")


def using_mistral_backend() -> bool:
    return bool(mistral_api_key())


def default_legacy_model() -> str:
    """Default model for the minimal / legacy assistant profile."""
    if using_mistral_backend():
        return os.getenv("EVOLUTION_MODEL_LEGACY", "mistral-small-latest")
    return os.getenv("EVOLUTION_MODEL_LEGACY", "gpt-4o")


def default_agent_model() -> str:
    """Default model for the agent / Codex-oriented profile."""
    if using_mistral_backend():
        return os.getenv("EVOLUTION_MODEL_AGENT", "mistral-medium-latest")
    return os.getenv("EVOLUTION_MODEL_AGENT", "gpt-5.5")


def openai_chat_completion_models() -> tuple[str, str]:
    """``(primary, fallback)`` model IDs for OpenAI ``chat.completions`` clients only.

    Honors ``EVOLUTION_MODEL_AGENT`` / ``EVOLUTION_MODEL_LEGACY`` when set, but
    default fallbacks remain OpenAI model names so calls to OpenAI's API are
    never given Mistral model identifiers from :func:`default_agent_model`.
    """
    return (
        os.getenv("EVOLUTION_MODEL_AGENT", "gpt-5.5"),
        os.getenv("EVOLUTION_MODEL_LEGACY", "gpt-4o"),
    )
