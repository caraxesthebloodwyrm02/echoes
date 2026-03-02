"""
Pytest configuration for Echoes tests.

Skips API-key-dependent tests when OPENAI_API_KEY is not set (e.g. in CI).
"""

import os

import pytest

# Modules that require OPENAI_API_KEY; skipped when key is missing
API_KEY_DEPENDENT_MODULES = [
    "test_all_demos",
    "test_agentic_assistant",
    "test_echoes_assistant_v2_comprehensive",
    "test_model_router",
    "test_multi_agent_workflows",
]


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers",
        "requires_openai: mark test as requiring OPENAI_API_KEY (skipped when missing)",
    )


def pytest_collection_modifyitems(config, items):
    """Skip API-key-dependent tests when OPENAI_API_KEY is not set."""
    if os.getenv("OPENAI_API_KEY"):
        return

    skip_openai = pytest.mark.skip(
        reason="OPENAI_API_KEY not set (API-key-dependent test)"
    )

    for item in items:
        module_name = item.module.__name__
        # Match tests.test_agentic_assistant, tests.test_all_demos, etc.
        if any(
            module_name == m or module_name.endswith("." + m)
            for m in API_KEY_DEPENDENT_MODULES
        ):
            item.add_marker(skip_openai)
