import json
import os
from pathlib import Path
from typing import Any


class InventoryStorage:
    def __init__(self, storage_path: str | None = None) -> None:
        if storage_path:
            self.path = Path(storage_path)
        else:
            root = Path(__file__).resolve().parent.parent
            self.path = root / "data" / "atlas_inventory.json"
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> dict[str, Any]:
        if not self.path.exists():
            return {}
        try:
            with open(self.path, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def save(self, data: dict[str, Any]) -> None:
        tmp = self.path.with_suffix(".tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        os.replace(tmp, self.path)
