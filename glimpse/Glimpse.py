"""
Glimpse module - Core components.

This module provides the core Glimpse components for the assistant.
"""

# Import all core components from engine module
from .clarifier_engine import ClarifierEngine
from .engine import (
    Draft,
    GlimpseEngine,
    GlimpseResult,
    LatencyMonitor,
    PrivacyGuard,
    default_sampler,
    local_default_sampler,
)

try:
    from .clarifier_engine import ENHANCED_CLARIFIER_AVAILABLE as CLARIFIER_AVAILABLE
except Exception:
    CLARIFIER_AVAILABLE = False

__all__ = [
    "Glimpse",
    "GlimpseEngine",
    "PrivacyGuard",
    "Draft",
    "GlimpseResult",
    "LatencyMonitor",
    "default_sampler",
    "local_default_sampler",
    "ClarifierEngine",
]

# Backward-compatible shared engine instance for callers that expect `Glimpse` as a module-level
# object following the legacy API style.
Glimpse = GlimpseEngine()
