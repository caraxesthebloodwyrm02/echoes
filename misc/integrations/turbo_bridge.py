"""
Turbo Bridge - Unified Cross-Platform Integration

Connects Echoes platform with multiple research platforms on D: drive:
- IMPACT_ANALYTICS: Automated impact tracking and AI safety metrics
- GlimpsePreview: Trajectory analysis and real-time visualization
- TurboBookshelf: Bias detection and web interface

Provides unified API for cross-platform analysis and data exchange.
"""

import logging
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
import sys

from .impact_analytics_connector import ImpactAnalyticsConnector, ImpactMetrics

logger = logging.getLogger(__name__)


class TurboBridge:
    """Unified bridge for cross-platform research integration."""

    def __init__(self):
        """Initialize connections to all available platforms."""
        self.platforms = {}

        # Initialize IMPACT_ANALYTICS connection
        self.platforms["impact_analytics"] = ImpactAnalyticsConnector()

        # Initialize other platforms with graceful fallback
        self._init_glimpse_preview()
        self._init_turbo_bookshelf()

        logger.info(
            f"TurboBridge initialized with platforms: {list(self.platforms.keys())}"
        )

    def _init_glimpse_preview(self):
        """Initialize GlimpsePreview connection."""
        try:
            glimpse_path = Path("D:/GlimpsePreview")
            if glimpse_path.exists():
                if str(glimpse_path) not in sys.path:
                    sys.path.insert(0, str(glimpse_path))
                # Import would go here if available
                self.platforms["glimpse_preview"] = (
                    "GlimpsePreview connection placeholder"
                )
                logger.info("GlimpsePreview platform detected")
            else:
                logger.debug("GlimpsePreview platform not found")
        except Exception as e:
            logger.warning(f"Could not initialize GlimpsePreview: {e}")

    def _init_turbo_bookshelf(self):
        """Initialize TurboBookshelf connection."""
        try:
            bookshelf_path = Path("D:/TurboBookshelf")
            if bookshelf_path.exists():
                if str(bookshelf_path) not in sys.path:
                    sys.path.insert(0, str(bookshelf_path))
                # Import would go here if available
                self.platforms["turbo_bookshelf"] = (
                    "TurboBookshelf connection placeholder"
                )
                logger.info("TurboBookshelf platform detected")
            else:
                logger.debug("TurboBookshelf platform not found")
        except Exception as e:
            logger.warning(f"Could not initialize TurboBookshelf: {e}")

    def is_platform_connected(self, platform: str) -> bool:
        """Check if a specific platform is connected."""
        connector = self.platforms.get(platform)
        if isinstance(connector, ImpactAnalyticsConnector):
            return connector.is_connected()
        return connector is not None

    def get_connected_platforms(self) -> List[str]:
        """Get list of successfully connected platforms."""
        connected = []
        for platform, connector in self.platforms.items():
            if isinstance(connector, ImpactAnalyticsConnector):
                if connector.is_connected():
                    connected.append(platform)
            elif connector is not None:
                connected.append(platform)
        return connected

    def unified_analysis(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Perform unified analysis across all connected platforms.

        Args:
            request: Analysis request containing:
                - text: List of text to analyze
                - query: Search query
                - include_impact_metrics: Whether to include IMPACT_ANALYTICS metrics

        Returns:
            Unified analysis results
        """
        results = {
            "platforms_connected": self.get_connected_platforms(),
            "analysis_results": {},
            "errors": [],
        }

        # IMPACT_ANALYTICS analysis
        if self.is_platform_connected("impact_analytics"):
            try:
                impact_connector = self.platforms["impact_analytics"]

                # Get current metrics
                metrics = impact_connector.get_metrics()
                results["analysis_results"]["impact_analytics"] = {
                    "connected": True,
                    "metrics": {
                        "safety_score": metrics.safety_score,
                        "bias_reduction_index": metrics.bias_reduction_index,
                        "total_evaluations": metrics.total_evaluations,
                        "recent_milestones": metrics.recent_milestones,
                    },
                }

                # If text provided, record as evaluation (if it looks like an evaluation)
                if "text" in request and len(request["text"]) > 0:
                    # This is a simplified example - in practice, you'd need actual safety scoring
                    logger.debug(
                        "IMPACT_ANALYTICS: Text analysis requested but safety scoring not implemented"
                    )

            except Exception as e:
                results["errors"].append(f"IMPACT_ANALYTICS error: {e}")
                results["analysis_results"]["impact_analytics"] = {
                    "connected": False,
                    "error": str(e),
                }

        # Placeholder for other platforms
        for platform in ["glimpse_preview", "turbo_bookshelf"]:
            if platform in self.platforms and self.platforms[platform] is not None:
                results["analysis_results"][platform] = {
                    "connected": True,
                    "status": "Platform detected but integration not fully implemented",
                }

        return results

    def record_evaluation(
        self,
        prompt: str,
        response: str,
        safety_score: float,
        bias_analysis: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Record an AI safety evaluation in IMPACT_ANALYTICS."""
        if not self.is_platform_connected("impact_analytics"):
            return False

        return self.platforms["impact_analytics"].record_evaluation(
            prompt, response, safety_score, bias_analysis, metadata
        )

    def record_milestone(
        self,
        milestone_name: str,
        completion_percentage: float,
        category: str = "research",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Record a research milestone in IMPACT_ANALYTICS."""
        if not self.is_platform_connected("impact_analytics"):
            return False

        return self.platforms["impact_analytics"].record_milestone(
            milestone_name, completion_percentage, category, metadata
        )

    def get_impact_metrics(self) -> ImpactMetrics:
        """Get current IMPACT_ANALYTICS metrics."""
        if not self.is_platform_connected("impact_analytics"):
            return ImpactMetrics(error="IMPACT_ANALYTICS not connected")

        return self.platforms["impact_analytics"].get_metrics()

    def generate_impact_report(self) -> Optional[str]:
        """Generate IMPACT_ANALYTICS workflow report."""
        if not self.is_platform_connected("impact_analytics"):
            return None

        return self.platforms["impact_analytics"].generate_report()

    def health_check(self) -> Dict[str, Any]:
        """Perform health check on all platforms."""
        health = {
            "overall_status": "healthy",
            "platform_health": {},
            "timestamp": "auto",
        }

        for platform, connector in self.platforms.items():
            try:
                if isinstance(connector, ImpactAnalyticsConnector):
                    health["platform_health"][platform] = {
                        "status": (
                            "connected" if connector.is_connected() else "disconnected"
                        ),
                        "type": "impact_analytics",
                    }
                else:
                    health["platform_health"][platform] = {
                        "status": "detected" if connector is not None else "not_found",
                        "type": "placeholder",
                    }
            except Exception as e:
                health["platform_health"][platform] = {
                    "status": "error",
                    "error": str(e),
                }
                health["overall_status"] = "degraded"

        return health


# Global instance
turbo_bridge = TurboBridge()


def create_bridge() -> TurboBridge:
    """Create and return a new TurboBridge instance."""
    return TurboBridge()


def unified_analysis(request: Dict[str, Any]) -> Dict[str, Any]:
    """Convenience function for unified analysis."""
    return turbo_bridge.unified_analysis(request)


def get_bridge_health() -> Dict[str, Any]:
    """Convenience function to check bridge health."""
    return turbo_bridge.health_check()
