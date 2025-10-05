"""
API Routes Package

Organized route modules for different domains and system functions.
"""

from .auth import router as auth_router
from .system import router as system_router

__all__ = ["system_router", "auth_router"]
