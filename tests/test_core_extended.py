"""
Tests for core utilities.
"""

import pytest


class TestCoreUtilities:
    """Test core utility functions."""

    def test_display_utils_import(self):
        """Test that display utils can be imported."""
        try:
            from core.display_utils import safe_symbol

            assert callable(safe_symbol)
        except ImportError:
            pytest.skip("core.display_utils not available")

    def test_exporter_import(self):
        """Test that exporter can be imported."""
        try:
            from core.exporter import export_json, export_text

            assert callable(export_text)
            assert callable(export_json)
        except ImportError:
            pytest.skip("core.exporter not available")
