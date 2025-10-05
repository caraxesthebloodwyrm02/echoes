"""
echoe-monitoring: Monitoring and observability for echoe-workspace.

Consolidates monitoring from:
- Root project's monitoring modules
- Project 3's guardrails
- Project 8's CI monitor
"""

__version__ = "0.1.0"

from .alerts import AlertManager
from .ci import CIMonitor
from .health import HealthChecker
from .metrics import MetricsCollector, SystemMetrics

__all__ = [
    "MetricsCollector",
    "SystemMetrics",
    "HealthChecker",
    "AlertManager",
    "CIMonitor",
]
