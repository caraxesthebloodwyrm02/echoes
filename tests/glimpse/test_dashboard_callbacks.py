"""Scaffolding for Q4 dashboard callback tests (TODO-001). Skips when dashboard absent."""

import pytest

try:
    import dashboard  # or Q4.dashboard when restored  # noqa: F401
    DASHBOARD_AVAILABLE = True
except ImportError:
    DASHBOARD_AVAILABLE = False


@pytest.mark.skipif(not DASHBOARD_AVAILABLE, reason="Q4 dashboard module not found")
class TestDashboardCallbacks:
    """Placeholder for filter, table edit, chart, export, privacy callbacks."""

    def test_dashboard_callbacks_placeholder(self) -> None:
        """Scaffold: implement when Q4/dashboard is restored."""
        pass
