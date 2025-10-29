"""Echoes ethos: import-time grounding of platform principles.

This module centralizes non-changing values (licensing, ethics, provider
choices, partnerships, inspirations) and provides a lightweight
`enforce()` hook that safely sets environment defaults at import time.

Security: never logs secrets or configuration values; only presence/absence.
"""

import os
import logging

# Canonical ethical principles guiding feature design and behavior
ETHICAL_PRINCIPLES = (
    "compassion",
    "truth",
    "discipline",
    "sacrifice",
    "enlightenment",
    "unity",
    "justice",
)

# Research-only mode signal for guardrails/docs flows
RESEARCH_ONLY = True

# Canonical embedding backend (post-migration)
EMBEDDINGS_PROVIDER = "openai"

# Strategic partner identifier
PARTNERSHIP = "OpenAI"

# Human inspirations referenced in acknowledgements
ACK_REFERENCES = {
    "music": ["Pink Floyd", "David Gilmour", "Syd Barrett"],
    "design": ["Jony Ive"],
}


def enforce() -> None:
    """Apply non-invasive environment defaults that reflect Echoes ethos.

    - Sets research-only flag, canonical embeddings provider, and partnership id.
    - Emits minimal, non-sensitive logs for observability. Never logs secrets.
    - Designed to be safe at import time (idempotent, side-effect limited).
    """
    logger = logging.getLogger(__name__)
    try:
        os.environ.setdefault("ECHOES_RESEARCH_ONLY", "1" if RESEARCH_ONLY else "0")
        os.environ.setdefault("ECHOES_EMBEDDINGS_PROVIDER", EMBEDDINGS_PROVIDER)
        os.environ.setdefault("ECHOES_PARTNERSHIP", PARTNERSHIP)

        if os.environ.get("ECHOES_EMBEDDINGS_PROVIDER") != "openai":
            logger.warning("Non-canonical embeddings provider active")

        # Only indicate presence/absence—never log key material.
        if not os.environ.get("OPENAI_API_KEY"):
            logger.info("OPENAI_API_KEY not set")
    except Exception as e:
        # Do not raise at import time; remain silent unless debugging.
        logger.debug(f"ethos enforce skipped: {e}")
