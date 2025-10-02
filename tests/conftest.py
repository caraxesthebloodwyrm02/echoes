"""Pytest configuration and fixtures."""

import pytest
from automation.core.context import Context


@pytest.fixture
def context():
    """Create a test context."""
    return Context(dry_run=True, user="testuser", env="testing")
