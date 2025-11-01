"""
Echoes Platform Integrations

Cross-platform connectors for research and development tools.
"""

# IMPACT Analytics Integration
from .impact_analytics_connector import (
    ImpactAnalyticsConnector,
    ImpactMetrics,
    impact_connector,
    record_ai_evaluation,
    record_research_progress,
    get_impact_status,
    generate_impact_report
)

# Turbo Bridge - Unified Cross-Platform Integration
from .turbo_bridge import (
    TurboBridge,
    turbo_bridge,
    create_bridge,
    unified_analysis,
    get_bridge_health
)

__all__ = [
    # IMPACT Analytics
    'ImpactAnalyticsConnector',
    'ImpactMetrics',
    'impact_connector',
    'record_ai_evaluation',
    'record_research_progress',
    'get_impact_status',
    'generate_impact_report',

    # Turbo Bridge
    'TurboBridge',
    'turbo_bridge',
    'create_bridge',
    'unified_analysis',
    'get_bridge_health',
]
