"""
Glimpse module - Core components.

This module provides the core Glimpse components for the assistant.
"""

import importlib.util

# Import optional performance and clarifier modules to check availability
try:
    importlib.util.find_spec("glimpse.performance_optimizer")
    PERFORMANCE_AVAILABLE = True
except (ImportError, AttributeError):
    PERFORMANCE_AVAILABLE = False

try:
    importlib.util.find_spec("glimpse.clarifier_engine")
    CLARIFIER_AVAILABLE = True
except (ImportError, AttributeError):
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
