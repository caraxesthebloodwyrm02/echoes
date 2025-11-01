"""Glimpse package public API.

Avoid eager imports to prevent runpy warnings when executing
`python -m glimpse.Glimpse`. Symbols are exposed lazily via __getattr__.
"""

from importlib import import_module
from typing import Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .metrics_server import MetricsServer

__all__ = [
    # Core components
    "GlimpseEngine",
    "PrivacyGuard",
    "Draft",
    "GlimpseResult",
    
    # Metrics
    "start_metrics_server",
    "stop_metrics_server",
    "get_metrics_server",
    "MetricsServer",
    "LatencyMonitor",
    "default_sampler",
]


def __getattr__(name: str) -> Any:
    # Core components
    if name in {"GlimpseEngine", "PrivacyGuard", "Draft", "GlimpseResult"}:
        mod = import_module(".Glimpse", __name__)
        return getattr(mod, name)
    
    # Metrics server
    if name in {"start_metrics_server", "stop_metrics_server", "get_metrics_server", "MetricsServer"}:
        mod = import_module(".metrics_server", __name__)
        return getattr(mod, name)
    
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
