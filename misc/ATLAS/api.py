"""
Direct ATLAS API for programmatic interaction.

Provides a clean interface for inventory operations without CLI overhead.
"""

from typing import Dict, Any, List, Optional
from .service import InventoryService


class ATLASDirectAPI:
    """Direct API for ATLAS inventory operations."""

    def __init__(self):
        """Initialize the ATLAS API."""
        self.service = InventoryService()

    # ========== Item Operations ==========

    def add_item(
        self,
        sku: str,
        name: str,
        category: str,
        quantity: int,
        location: str,
        min_stock: int = 0,
        max_stock: int = 0,
        attributes: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Add a new inventory item."""
        try:
            item = self.service.add_item(
                sku=sku,
                name=name,
                category=category,
                quantity=quantity,
                location=location,
                min_stock=min_stock,
                max_stock=max_stock,
                attributes=attributes,
            )
            return {"success": True, "item": item.to_dict()}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_item(self, sku: str) -> Dict[str, Any]:
        """Get a specific item by SKU."""
        try:
            item = self.service.get_item(sku)
            if item:
                return {"success": True, "item": item.to_dict()}
            else:
                return {"success": False, "error": f"Item {sku} not found"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def list_items(
        self,
        category: Optional[str] = None,
        location: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List inventory items with optional filters."""
        try:
            items = self.service.list_items(category=category, location=location)
            return {
                "success": True,
                "items": [i.to_dict() for i in items],
                "count": len(items),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ========== Quantity Operations ==========

    def adjust_quantity(self, sku: str, delta: int) -> Dict[str, Any]:
        """Adjust item quantity by delta."""
        try:
            item = self.service.adjust_quantity(sku, delta)
            return {"success": True, "item": item.to_dict()}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def set_quantity(self, sku: str, quantity: int) -> Dict[str, Any]:
        """Set item quantity to exact value."""
        try:
            item = self.service.get_item(sku)
            if not item:
                return {"success": False, "error": f"Item {sku} not found"}
            delta = quantity - item.quantity
            item = self.service.adjust_quantity(sku, delta)
            return {"success": True, "item": item.to_dict()}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ========== Location Operations ==========

    def move_item(self, sku: str, new_location: str) -> Dict[str, Any]:
        """Move item to a new location."""
        try:
            item = self.service.move_item(sku, new_location)
            return {"success": True, "item": item.to_dict()}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ========== Reporting ==========

    def report_summary(self) -> Dict[str, Any]:
        """Get inventory summary report."""
        try:
            report = self.service.report("summary")
            return {"success": True, "report": report}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def report_low_stock(self) -> Dict[str, Any]:
        """Get low stock report."""
        try:
            report = self.service.report("low")
            return {"success": True, "report": report}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def report_overstock(self) -> Dict[str, Any]:
        """Get overstock report."""
        try:
            report = self.service.report("over")
            return {"success": True, "report": report}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def report_by_category(self) -> Dict[str, Any]:
        """Get inventory breakdown by category."""
        try:
            items = self.service.list_items()
            by_category = {}
            for item in items:
                if item.category not in by_category:
                    by_category[item.category] = []
                by_category[item.category].append(item.to_dict())
            return {"success": True, "by_category": by_category}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def report_by_location(self) -> Dict[str, Any]:
        """Get inventory breakdown by location."""
        try:
            items = self.service.list_items()
            by_location = {}
            for item in items:
                if item.location not in by_location:
                    by_location[item.location] = []
                by_location[item.location].append(item.to_dict())
            return {"success": True, "by_location": by_location}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ========== Batch Operations ==========

    def bulk_add_items(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Add multiple items in batch."""
        results = []
        for item_data in items:
            result = self.add_item(**item_data)
            results.append(result)
        return {
            "success": all(r["success"] for r in results),
            "results": results,
            "total": len(results),
            "successful": sum(1 for r in results if r["success"]),
        }

    def bulk_adjust_quantities(self, adjustments: Dict[str, int]) -> Dict[str, Any]:
        """Adjust multiple items in batch."""
        results = {}
        for sku, delta in adjustments.items():
            results[sku] = self.adjust_quantity(sku, delta)
        return {
            "success": all(r["success"] for r in results.values()),
            "results": results,
            "total": len(results),
            "successful": sum(1 for r in results.values() if r["success"]),
        }

    # ========== Statistics ==========

    def get_statistics(self) -> Dict[str, Any]:
        """Get inventory statistics."""
        try:
            items = self.service.list_items()
            total_items = len(items)
            total_quantity = sum(i.quantity for i in items)
            categories = set(i.category for i in items)
            locations = set(i.location for i in items)

            return {
                "success": True,
                "total_items": total_items,
                "total_quantity": total_quantity,
                "categories": len(categories),
                "locations": len(locations),
                "avg_quantity_per_item": (
                    total_quantity / total_items if total_items > 0 else 0
                ),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
