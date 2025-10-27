# Consent-Based License
#
# Version 1.0
# Effective Date: October 27, 2025
#
# This module is part of the Echoes AI Assistant project and requires explicit consent for use.
# Please read the main LICENSE file and contact the licensor for usage terms.
#
# Author Contact Information
# Erfan Kabir
# irfankabir02@gmail.com
# GitHub: caraxesthebloodwyrm02


"""Core scientific computing and statistical analysis module for Echoes AI Assistant.

This module provides foundational scientific computing capabilities including:
- Statistical distributions and analysis
- Continuous and discrete probability distributions
- Infrastructure for distribution-based computations
- Optimized performance for AI and ML workflows

Part of the Echoes multimodal AI assistant platform.
"""

# ============================================================================
# CRITICAL: Pre-initialize pyarrow to break circular dependency
# ============================================================================
import sys
import importlib

# Pre-initialize pyarrow to break circular dependency
if 'pyarrow' not in sys.modules:
    try:
        import pyarrow as _pa
    except ImportError:
        pass

# ============================================================================
# Core module imports
# ============================================================================
from . import _stats_py as _stats
from . import _distn_infrastructure
from . import _continuous_distns
from . import _discrete_distns

# ============================================================================
# Public API exports
# ============================================================================
__all__ = [
    '_stats',
    '_distn_infrastructure',
    '_continuous_distns',
    '_discrete_distns',
]
