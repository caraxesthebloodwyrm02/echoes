"""Glimpse package public API.

Avoid eager imports to prevent runpy warnings when executing
`python -m glimpse.Glimpse`. Symbols are exposed lazily via __getattr__.
"""

from importlib import import_module
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from .metrics_server import MetricsServer

__all__ = [
    # Core components
    "GlimpseEngine",
    "PrivacyGuard",
    "Draft",
    "GlimpseResult",
    "LatencyMonitor",
    "default_sampler",
    "local_default_sampler",
    "ClarifierEngine",
    # Metrics server components
    "start_metrics_server",
    "stop_metrics_server",
    "get_metrics_server",
    "MetricsServer",
]

_CORE_SYMBOLS = {
    "GlimpseEngine",
    "PrivacyGuard",
    "Draft",
    "GlimpseResult",
    "LatencyMonitor",
    "default_sampler",
    "local_default_sampler",
    "ClarifierEngine",
}

_METRICS_SYMBOLS = {
    "start_metrics_server",
    "stop_metrics_server",
    "get_metrics_server",
    "MetricsServer",
}


def __getattr__(name: str) -> Any:
    if name in _CORE_SYMBOLS:
        mod = import_module(".Glimpse", __name__)
        return getattr(mod, name)

    if name in _METRICS_SYMBOLS:
        mod = import_module(".metrics_server", __name__)
        return getattr(mod, name)

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
