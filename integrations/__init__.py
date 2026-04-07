"""Optional IMPACT_ANALYTICS-style connectors with graceful offline fallback."""

from integrations.impact_analytics_connector import (
    ImpactAnalyticsConnector,
    ImpactMetrics,
    generate_impact_report,
    get_impact_status,
    impact_connector,
    record_ai_evaluation,
    record_research_progress,
)
from integrations.turbo_bridge import (
    TurboBridge,
    create_bridge,
    get_bridge_health,
    turbo_bridge,
    unified_analysis,
)

__all__ = [
    "ImpactAnalyticsConnector",
    "ImpactMetrics",
    "TurboBridge",
    "create_bridge",
    "generate_impact_report",
    "get_bridge_health",
    "get_impact_status",
    "impact_connector",
    "record_ai_evaluation",
    "record_research_progress",
    "turbo_bridge",
    "unified_analysis",
]
