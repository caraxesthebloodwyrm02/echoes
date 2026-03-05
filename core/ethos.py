"""Echoes ethos enforcement.

Validates that the runtime environment meets Echoes' operational
requirements (e.g. required env vars, Python version guards).
Called automatically on package import via app/__init__.py.
"""

import logging
import os

logger = logging.getLogger(__name__)

_CANONICAL_PROVIDERS = ("openai",)


def enforce() -> None:
    """Run lightweight startup-time checks.

    Sets default env vars if unset: ECHOES_RESEARCH_ONLY, ECHOES_EMBEDDINGS_PROVIDER,
    ECHOES_PARTNERSHIP. Respects existing ECHOES_EMBEDDINGS_PROVIDER and logs a
    warning if non-canonical. The minimum Python version (>=3.12) is enforced by
    ``requires-python`` in pyproject.toml.
    """
    if os.environ.get("ECHOES_RESEARCH_ONLY") is None:
        os.environ["ECHOES_RESEARCH_ONLY"] = "1"
    if os.environ.get("ECHOES_EMBEDDINGS_PROVIDER") is None:
        os.environ["ECHOES_EMBEDDINGS_PROVIDER"] = "openai"
    if os.environ.get("ECHOES_PARTNERSHIP") is None:
        os.environ["ECHOES_PARTNERSHIP"] = "OpenAI"
    provider = os.environ.get("ECHOES_EMBEDDINGS_PROVIDER", "").lower()
    if provider and provider not in _CANONICAL_PROVIDERS:
        logger.warning("Non-canonical embeddings provider: %s", provider)
