"""
ATLAS Database Models for Echoes Assistant V2
Database-backed versions of ATLAS models
"""

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import JSON, Column, DateTime, Integer, String

from config.database_config import get_database_manager

Base = get_database_manager().Base


class InventoryItemModel(Base):
    """Database model for ATLAS inventory items."""

    __tablename__ = "inventory_items"

    # Primary Fields
    sku = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)

    # Inventory Data
    quantity = Column(Integer, nullable=False)
    location = Column(String, nullable=False)
    min_stock = Column(Integer, default=0)
    max_stock = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(
        DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    )

    # Additional Attributes
    attributes = Column(JSON, nullable=True)

    def to_dict(self) -> dict[str, Any]:
        """Convert model to dictionary."""
        return {
            "sku": self.sku,
            "name": self.name,
            "category": self.category,
            "quantity": self.quantity,
            "location": self.location,
            "min_stock": self.min_stock,
            "max_stock": self.max_stock,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "attributes": self.attributes,
        }

    @classmethod
    def from_inventory_item(cls, item) -> "InventoryItemModel":
        """Create database model from ATLAS InventoryItem."""
        return cls(
            sku=item.sku,
            name=item.name,
            category=item.category,
            quantity=item.quantity,
            location=item.location,
            min_stock=item.min_stock,
            max_stock=item.max_stock,
            created_at=datetime.fromisoformat(item.created_at)
            if item.created_at
            else datetime.now(UTC),
            updated_at=datetime.fromisoformat(item.updated_at)
            if item.updated_at
            else datetime.now(UTC),
            attributes=item.attributes,
        )

    def to_atlas_item(self):
        """Convert to ATLAS InventoryItem format."""
        from ATLAS.models import InventoryItem

        return InventoryItem(
            sku=self.sku,
            name=self.name,
            category=self.category,
            quantity=self.quantity,
            location=self.location,
            min_stock=self.min_stock,
            max_stock=self.max_stock,
            created_at=self.created_at.isoformat(),
            updated_at=self.updated_at.isoformat(),
            attributes=self.attributes,
        )
