from typing import Any

from .models import InventoryItem, utc_now_iso
from .storage import InventoryStorage


class InventoryService:
    def __init__(self, storage: InventoryStorage | None = None) -> None:
        self.storage = storage or InventoryStorage()

    def add_item(
        self,
        sku: str,
        name: str,
        category: str,
        quantity: int,
        location: str,
        min_stock: int = 0,
        max_stock: int = 0,
        attributes: dict[str, Any] | None = None,
    ) -> InventoryItem:
        data = self.storage.load()
        if sku in data:
            raise ValueError("SKU already exists")
        now = utc_now_iso()
        item = InventoryItem(
            sku=sku,
            name=name,
            category=category,
            quantity=int(quantity),
            location=location,
            min_stock=int(min_stock),
            max_stock=int(max_stock),
            created_at=now,
            updated_at=now,
            attributes=attributes,
        )
        data[sku] = item.to_dict()
        self.storage.save(data)
        return item

    def list_items(
        self, category: str | None = None, location: str | None = None
    ) -> list[InventoryItem]:
        data = self.storage.load()
        items = [InventoryItem.from_dict(d) for d in data.values()]
        if category:
            items = [i for i in items if i.category == category]
        if location:
            items = [i for i in items if i.location == location]
        return items

    def get_item(self, sku: str) -> InventoryItem | None:
        data = self.storage.load()
        d = data.get(sku)
        return InventoryItem.from_dict(d) if d else None

    def adjust_quantity(self, sku: str, delta: int) -> InventoryItem:
        data = self.storage.load()
        if sku not in data:
            raise ValueError("SKU not found")
        d = data[sku]
        d["quantity"] = max(0, int(d.get("quantity", 0)) + int(delta))
        d["updated_at"] = utc_now_iso()
        data[sku] = d
        self.storage.save(data)
        return InventoryItem.from_dict(d)

    def move_item(self, sku: str, new_location: str) -> InventoryItem:
        data = self.storage.load()
        if sku not in data:
            raise ValueError("SKU not found")
        d = data[sku]
        d["location"] = new_location
        d["updated_at"] = utc_now_iso()
        data[sku] = d
        self.storage.save(data)
        return InventoryItem.from_dict(d)

    def report(self, report_type: str = "summary") -> dict[str, Any]:
        items = self.list_items()
        total_items = len(items)
        total_qty = sum(i.quantity for i in items)
        low_stock = [i for i in items if i.min_stock and i.quantity <= i.min_stock]
        over_stock = [i for i in items if i.max_stock and i.quantity >= i.max_stock]
        by_category: dict[str, int] = {}
        for i in items:
            by_category[i.category] = by_category.get(i.category, 0) + i.quantity
        if report_type == "low":
            return {"low_stock": [i.to_dict() for i in low_stock]}
        if report_type == "over":
            return {"over_stock": [i.to_dict() for i in over_stock]}
        return {
            "total_items": total_items,
            "total_quantity": total_qty,
            "low_stock_count": len(low_stock),
            "over_stock_count": len(over_stock),
            "by_category": by_category,
        }
