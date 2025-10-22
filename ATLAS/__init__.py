"""ATLAS Inventory Management System.

A lightweight, extensible inventory management system with:
- JSON-backed storage
- CLI and Python API
- Real-time inventory tracking
- Report generation
"""

from .models import InventoryItem
from .storage import InventoryStorage
from .service import InventoryService
from .api import ATLASDirectAPI

__all__ = [
    "InventoryItem",
    "InventoryStorage",
    "InventoryService",
    "ATLASDirectAPI",
]

__version__ = "1.0.0"
__author__ = "Echoes AI"
