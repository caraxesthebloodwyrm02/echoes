"""
Glimpse module - Core components.

This module provides the core Glimpse components for the assistant.
"""

# Import optional performance and clarifier modules to check availability
try:
    from .performance_optimizer import PerformanceOptimizer
    PERFORMANCE_AVAILABLE = True
except ImportError:
    PERFORMANCE_AVAILABLE = False

try:
    from .clarifier_engine import ClarifierEngine, enhanced_sampler_with_clarifiers
    CLARIFIER_AVAILABLE = True
except ImportError:
    CLARIFIER_AVAILABLE = False

# Import all core components from engine module
from .clarifier_engine import ClarifierEngine
from .engine import (
    Draft,
    GlimpseEngine,
    GlimpseResult,
    LatencyMonitor,
    PrivacyGuard,
    default_sampler,
)

__all__ = [
    "GlimpseEngine",
    "PrivacyGuard",
    "Draft",
    "GlimpseResult",
    "LatencyMonitor",
    "default_sampler",
    "ClarifierEngine",
    "PERFORMANCE_AVAILABLE",
    "CLARIFIER_AVAILABLE",
]
