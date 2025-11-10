"""ATLAS Inventory Management System.

A lightweight, extensible inventory management system with:
- JSON-backed storage
- CLI and Python API
- Real-time inventory tracking
- Report generation
"""

from .api import ATLASDirectAPI
from .models import InventoryItem
from .service import InventoryService
from .storage import InventoryStorage

__all__ = [
    "InventoryItem",
    "InventoryStorage",
    "InventoryService",
    "ATLASDirectAPI",
]

__version__ = "1.0.0"
__author__ = "Echoes AI"
