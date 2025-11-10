from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from typing import Any


def utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


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
    attributes: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "InventoryItem":
        return InventoryItem(**data)
