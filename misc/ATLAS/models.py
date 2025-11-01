from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Optional, Dict, Any


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class InventoryItem:
    sku: str
    name: str
    category: str
    quantity: int
    location: str
    min_stock: int = 0
    max_stock: int = 0
    created_at: str = ""
    updated_at: str = ""
    attributes: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "InventoryItem":
        return InventoryItem(**data)
