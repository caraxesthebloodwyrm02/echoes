"""
Tests for IMPACT_ANALYTICS integration
"""

import sys
from pathlib import Path
from unittest.mock import patch

# Add the integrations directory to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "integrations"))

from integrations.impact_analytics_connector import (ImpactAnalyticsConnector,
                                                     ImpactMetrics,
                                                     generate_impact_report,
                                                     get_impact_status,
                                                     record_ai_evaluation,
                                                     record_research_progress)
from integrations.turbo_bridge import (TurboBridge, create_bridge,
                                       get_bridge_health, unified_analysis)


class TestImpactAnalyticsConnector:
    """Test the IMPACT_ANALYTICS connector functionality."""

    def test_connector_initialization_graceful_fallback(self):
        """Test connector initialization with graceful fallback when IMPACT_ANALYTICS unavailable."""
        # Since IMPACT_ANALYTICS may not be available in test environment,
        # the connector should handle this gracefully
        connector = ImpactAnalyticsConnector()

        # The connector should always initialize, but connection status may vary
        assert hasattr(connector, "is_connected")
        assert hasattr(connector, "workflow_tracker")
        assert hasattr(connector, "connected")

        # Test that methods exist and return appropriate types
        result = connector.record_evaluation("test", "response", 85.0, {})
        assert isinstance(result, bool)

        metrics = connector.get_metrics()
        assert isinstance(metrics, ImpactMetrics)

    def test_record_evaluation_returns_bool(self):
        """Test that record_evaluation returns a boolean."""
        connector = ImpactAnalyticsConnector()
        result = connector.record_evaluation(
            prompt="Test prompt",
            response="Test response",
            safety_score=85.0,
            bias_analysis={"bias_reduction_index": 45.0},
        )
        assert isinstance(result, bool)

    def test_record_milestone_returns_bool(self):
        """Test that record_milestone returns a boolean."""
        connector = ImpactAnalyticsConnector()
        result = connector.record_milestone("test_milestone", 75.0)
        assert isinstance(result, bool)

    def test_get_metrics_returns_impact_metrics(self):
        """Test that get_metrics returns ImpactMetrics object."""
        connector = ImpactAnalyticsConnector()
        metrics = connector.get_metrics()

        assert isinstance(metrics, ImpactMetrics)
        # Check that all expected attributes exist
        assert hasattr(metrics, "safety_score")
        assert hasattr(metrics, "bias_reduction_index")
        assert hasattr(metrics, "total_evaluations")
        assert hasattr(metrics, "recent_milestones")
        assert hasattr(metrics, "error")

    def test_generate_report_returns_string_or_none(self):
        """Test that generate_report returns string path or None."""
        connector = ImpactAnalyticsConnector()
        result = connector.generate_report()

        assert result is None or isinstance(result, str)

    def test_is_connected_returns_bool(self):
        """Test that is_connected returns a boolean."""
        connector = ImpactAnalyticsConnector()
        result = connector.is_connected()
        assert isinstance(result, bool)


class TestTurboBridge:
    """Test the TurboBridge unified integration."""

    def test_bridge_initialization(self):
        """Test bridge initialization."""
        bridge = TurboBridge()

        # Check that platforms dict exists
        assert hasattr(bridge, "platforms")
        assert isinstance(bridge.platforms, dict)

        # Check that expected platform keys exist
        assert "impact_analytics" in bridge.platforms

    def test_unified_analysis_basic(self):
        """Test basic unified analysis functionality."""
        bridge = TurboBridge()
        result = bridge.unified_analysis(
            {"text": ["analysis text"], "query": "search query"}
        )

        # Check that result has expected structure
        assert isinstance(result, dict)
        assert "platforms_connected" in result
        assert "analysis_results" in result
        assert "errors" in result
        assert isinstance(result["platforms_connected"], list)
        assert isinstance(result["analysis_results"], dict)
        assert isinstance(result["errors"], list)

    def test_bridge_health_check(self):
        """Test bridge health check functionality."""
        bridge = TurboBridge()
        health = bridge.health_check()

        assert isinstance(health, dict)
        assert "overall_status" in health
        assert "platform_health" in health
        assert "timestamp" in health
        assert isinstance(health["platform_health"], dict)

    def test_get_connected_platforms(self):
        """Test getting connected platforms."""
        bridge = TurboBridge()
        platforms = bridge.get_connected_platforms()

        assert isinstance(platforms, list)
        # Should at least have impact_analytics (even if not connected)
        # but the actual connection depends on environment

    def test_is_platform_connected_returns_bool(self):
        """Test platform connection checking."""
        bridge = TurboBridge()
        result = bridge.is_platform_connected("impact_analytics")
        assert isinstance(result, bool)

    def test_record_evaluation_bridge_method(self):
        """Test bridge record_evaluation method."""
        bridge = TurboBridge()
        result = bridge.record_evaluation("prompt", "response", 85.0, {"bias": 10.0})
        assert isinstance(result, bool)

    def test_record_milestone_bridge_method(self):
        """Test bridge record_milestone method."""
        bridge = TurboBridge()
        result = bridge.record_milestone("milestone", 75.0)
        assert isinstance(result, bool)

    def test_get_impact_metrics_bridge_method(self):
        """Test bridge get_impact_metrics method."""
        bridge = TurboBridge()
        metrics = bridge.get_impact_metrics()
        assert isinstance(metrics, ImpactMetrics)

    def test_generate_impact_report_bridge_method(self):
        """Test bridge generate_impact_report method."""
        bridge = TurboBridge()
        result = bridge.generate_impact_report()
        assert result is None or isinstance(result, str)

    def test_create_bridge_function(self):
        """Test the create_bridge convenience function."""
        bridge = create_bridge()
        assert isinstance(bridge, TurboBridge)

    @patch("integrations.turbo_bridge.turbo_bridge")
    def test_unified_analysis_function(self, mock_bridge):
        """Test the unified_analysis convenience function."""
        mock_bridge.unified_analysis.return_value = {"test": "result"}

        result = unified_analysis({"query": "test"})

        mock_bridge.unified_analysis.assert_called_once_with({"query": "test"})
        assert result == {"test": "result"}

    @patch("integrations.turbo_bridge.turbo_bridge")
    def test_get_bridge_health_function(self, mock_bridge):
        """Test the get_bridge_health convenience function."""
        mock_bridge.health_check.return_value = {"status": "healthy"}

        result = get_bridge_health()

        assert result == {"status": "healthy"}


class TestConvenienceFunctions:
    """Test convenience functions for IMPACT_ANALYTICS integration."""

    @patch("integrations.impact_analytics_connector.impact_connector")
    def test_record_ai_evaluation_function(self, mock_connector):
        """Test record_ai_evaluation convenience function."""
        mock_connector.record_evaluation.return_value = True

        result = record_ai_evaluation("prompt", "response", 85.0, {"bias": 10.0})

        assert result is True
        mock_connector.record_evaluation.assert_called_once()

    @patch("integrations.impact_analytics_connector.impact_connector")
    def test_record_research_progress_function(self, mock_connector):
        """Test record_research_progress convenience function."""
        mock_connector.record_milestone.return_value = True

        result = record_research_progress("milestone", 75.0)

        assert result is True
        mock_connector.record_milestone.assert_called_once_with(
            "milestone", 75.0, "research", None
        )

    @patch("integrations.impact_analytics_connector.impact_connector")
    def test_get_impact_status_function(self, mock_connector):
        """Test get_impact_status convenience function."""
        mock_metrics = ImpactMetrics(safety_score=85.0)
        mock_connector.get_metrics.return_value = mock_metrics

        result = get_impact_status()

        assert isinstance(result, ImpactMetrics)
        assert result.safety_score == 85.0

    @patch("integrations.impact_analytics_connector.impact_connector")
    def test_generate_impact_report_function(self, mock_connector):
        """Test generate_impact_report convenience function."""
        mock_connector.generate_report.return_value = "/path/to/report.md"

        result = generate_impact_report()

        assert result == "/path/to/report.md"
