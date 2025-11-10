"""
IMPACT Analytics Connector

Connects Echoes platform with the IMPACT_ANALYTICS system on D: drive for
automated impact tracking and AI safety metrics.
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import logging

# Add IMPACT_ANALYTICS to Python path
IMPACT_ANALYTICS_PATH = Path("D:/IMPACT_ANALYTICS")
if str(IMPACT_ANALYTICS_PATH) not in sys.path:
    sys.path.insert(0, str(IMPACT_ANALYTICS_PATH))

logger = logging.getLogger(__name__)


@dataclass
class ImpactMetrics:
    """Container for impact metrics data."""

    safety_score: Optional[float] = None
    bias_reduction_index: Optional[float] = None
    total_evaluations: Optional[int] = None
    recent_milestones: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None


class ImpactAnalyticsConnector:
    """Connector for IMPACT_ANALYTICS system integration."""

    def __init__(self):
        """Initialize the connector with graceful fallback."""
        self.workflow_tracker = None
        self.connected = False

        try:
            # Try to import and initialize the workflow tracker
            from analytics.workflow_integration import WorkflowTracker

            self.workflow_tracker = WorkflowTracker()
            self.connected = self.workflow_tracker.enabled
            if self.connected:
                logger.info("Successfully connected to IMPACT_ANALYTICS system")
            else:
                logger.warning("IMPACT_ANALYTICS system available but not enabled")
        except ImportError as e:
            logger.warning(f"Could not import IMPACT_ANALYTICS: {e}")
        except Exception as e:
            logger.error(f"Error initializing IMPACT_ANALYTICS connector: {e}")

    def is_connected(self) -> bool:
        """Check if connector is successfully connected to IMPACT_ANALYTICS."""
        return self.connected and self.workflow_tracker is not None

    def record_evaluation(
        self,
        prompt: str,
        response: str,
        safety_score: float,
        bias_analysis: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Record an AI safety evaluation.

        Args:
            prompt: The evaluated prompt
            response: The AI response
            safety_score: Overall safety score (0-100)
            bias_analysis: Detailed bias analysis results
            metadata: Additional tracking metadata

        Returns:
            True if recorded successfully, False otherwise
        """
        if not self.is_connected():
            logger.warning(
                "IMPACT_ANALYTICS not connected, skipping evaluation recording"
            )
            return False

        try:
            self.workflow_tracker.record_ai_safety_evaluation(
                prompt=prompt,
                response=response,
                safety_score=safety_score,
                bias_analysis=bias_analysis,
                metadata=metadata,
            )
            logger.debug("Successfully recorded evaluation in IMPACT_ANALYTICS")
            return True
        except Exception as e:
            logger.error(f"Error recording evaluation: {e}")
            return False

    def record_milestone(
        self,
        milestone_name: str,
        completion_percentage: float,
        category: str = "research",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Record a research milestone achievement.

        Args:
            milestone_name: Name of the milestone
            completion_percentage: Completion percentage (0-100)
            category: Research category
            metadata: Additional metadata

        Returns:
            True if recorded successfully, False otherwise
        """
        if not self.is_connected():
            logger.warning(
                "IMPACT_ANALYTICS not connected, skipping milestone recording"
            )
            return False

        try:
            self.workflow_tracker.record_research_milestone(
                milestone_name=milestone_name,
                completion_percentage=completion_percentage,
                category=category,
                metadata=metadata,
            )
            logger.debug(
                f"Successfully recorded milestone '{milestone_name}' in IMPACT_ANALYTICS"
            )
            return True
        except Exception as e:
            logger.error(f"Error recording milestone: {e}")
            return False

    def get_metrics(self) -> ImpactMetrics:
        """Get current workflow metrics summary.

        Returns:
            ImpactMetrics object with current metrics
        """
        if not self.is_connected():
            return ImpactMetrics(error="IMPACT_ANALYTICS not connected")

        try:
            metrics = self.workflow_tracker.get_workflow_metrics()
            return ImpactMetrics(
                safety_score=metrics.get("latest_safety_score"),
                bias_reduction_index=metrics.get("bias_reduction_index"),
                total_evaluations=(
                    int(metrics.get("total_evaluations", 0))
                    if metrics.get("total_evaluations")
                    else None
                ),
                recent_milestones=metrics.get("recent_milestones", []),
            )
        except Exception as e:
            logger.error(f"Error getting metrics: {e}")
            return ImpactMetrics(error=str(e))

    def generate_report(self) -> Optional[str]:
        """Generate a workflow status report.

        Returns:
            Path to generated report, or None if failed
        """
        if not self.is_connected():
            logger.warning("IMPACT_ANALYTICS not connected, cannot generate report")
            return None

        try:
            report_path = self.workflow_tracker.generate_workflow_report()
            logger.info(
                f"Successfully generated IMPACT_ANALYTICS report: {report_path}"
            )
            return report_path
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            return None

    def get_metric_history(
        self,
        metric_name: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Get historical metric data.

        Args:
            metric_name: Filter by specific metric name
            category: Filter by category
            limit: Maximum number of results

        Returns:
            List of metric entries
        """
        if not self.is_connected():
            logger.warning("IMPACT_ANALYTICS not connected, cannot get history")
            return []

        try:
            # Access the underlying tracker directly for history
            from analytics import ImpactTracker

            tracker = ImpactTracker()
            return tracker.get_metric_history(
                metric_name=metric_name, category=category, limit=limit
            )
        except Exception as e:
            logger.error(f"Error getting metric history: {e}")
            return []


# Global instance
impact_connector = ImpactAnalyticsConnector()


def record_ai_evaluation(
    prompt: str,
    response: str,
    safety_score: float,
    bias_analysis: Dict[str, Any],
    metadata: Optional[Dict[str, Any]] = None,
) -> bool:
    """Convenience function to record AI evaluation in IMPACT_ANALYTICS."""
    return impact_connector.record_evaluation(
        prompt, response, safety_score, bias_analysis, metadata
    )


def record_research_progress(
    milestone_name: str,
    completion_percentage: float,
    category: str = "research",
    metadata: Optional[Dict[str, Any]] = None,
) -> bool:
    """Convenience function to record research milestone in IMPACT_ANALYTICS."""
    return impact_connector.record_milestone(
        milestone_name, completion_percentage, category, metadata
    )


def get_impact_status() -> ImpactMetrics:
    """Convenience function to get current IMPACT_ANALYTICS metrics."""
    return impact_connector.get_metrics()


def generate_impact_report() -> Optional[str]:
    """Convenience function to generate IMPACT_ANALYTICS workflow report."""
    return impact_connector.generate_report()
