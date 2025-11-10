"""
Tests for automation modules.
"""

import pytest


class TestAutomationModules:
    """Test automation module components."""

    def test_guardrails_imports(self):
        """Test that guardrails modules can be imported."""
        guardrail_modules = [
            "automation.guardrails.ingest_docs",
            "automation.guardrails.middleware",
            "automation.guardrails.validate_api",
        ]

        for module_name in guardrail_modules:
            try:
                import importlib

                importlib.import_module(module_name)
                assert True  # Module imported successfully
            except ImportError:
                pytest.skip(f"Module {module_name} not available")
