"""
echoe-security: Security utilities for echoe-workspace.

Consolidates security functionality from:
- Root project's src/security
- Project 3's security modules
- Project 6's quantum_shield
"""

__version__ = "0.1.0"

from .auth import AuthManager
from .encryption import QuantumShield
from .scanning import CodeReviewer, VulnerabilityScanner

__all__ = [
    "VulnerabilityScanner",
    "CodeReviewer",
    "AuthManager",
    "QuantumShield",
]
