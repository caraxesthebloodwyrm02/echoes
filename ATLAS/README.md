# ATLAS Inventory Prototype

A minimal, extensible inventory management prototype designed to evolve from the Echoes codebase organizer. ATLAS focuses on clear structure, fast iteration, and production-ready patterns (atomic writes, UTC timestamps, CLI and Python API).

---

## 1. Overview

- **Location**: `ATLAS/`
- **Core**:
  - `models.py`: `InventoryItem` dataclass, UTC helper
  - `storage.py`: JSON-backed storage at `data/atlas_inventory.json`
  - `service.py`: CRUD operations and reporting
  - `cli.py`: `argparse` CLI to manage inventory
  - `__main__.py`: Entry point for `python -m ATLAS`
- **Dependencies**: Standard library only (no external packages)

Use this as a foundation for a full inventory system with categorization, reorder logic, barcode integration, and dashboards.

---

## 2. Setup

- **Python**: 3.11+ recommended
- **Project root**: `e:\Projects\Echoes`

No extra dependencies required.

Optional: Ensure `data/` exists (will be created automatically on first write).

---

## 3. Quick Start (CLI)

Run from the project root:

```powershell
# Add items
python -m ATLAS add --sku SKU-001 --name "Wireless Mouse" --category Peripherals --qty 50 --loc A1 --min 5 --max 100
python -m ATLAS add --sku SKU-002 --name "USB-C Cable"    --category Accessories --qty 120 --loc B2 --min 10 --max 300

# List items
python -m ATLAS list
python -m ATLAS list --category Peripherals

# Adjust quantity
python -m ATLAS adjust --sku SKU-001 --delta -2

# Move item
python -m ATLAS move --sku SKU-002 --to C3

# Reports
python -m ATLAS report --type summary
python -m ATLAS report --type low
python -m ATLAS report --type over
```

Data is stored at `data/atlas_inventory.json` using atomic writes.

---

## 4. Python API

```python
from ATLAS.service import InventoryService

svc = InventoryService()
svc.add_item(
    sku="SKU-003", name="Keyboard", category="Peripherals", quantity=25, location="A2", min_stock=5, max_stock=100
)
items = svc.list_items(category="Peripherals")
report = svc.report("summary")
```

---

## 5. Code Structure

- **`ATLAS/models.py`**
  - `InventoryItem`: Lightweight data model for stock items
  - `utc_now_iso()`: Timezone-aware ISO timestamps

- **`ATLAS/storage.py`**
  - `InventoryStorage`: Simple JSON storage with atomic writes
  - Path defaults to `data/atlas_inventory.json`

- **`ATLAS/service.py`**
  - `InventoryService`: Business logic API
    - `add_item()`, `list_items()`, `get_item()`
    - `adjust_quantity()`, `move_item()`
    - `report(type)`: `summary | low | over`

- **`ATLAS/cli.py`**
  - `atlas` commands: `add`, `list`, `adjust`, `move`, `report`

- **`ATLAS/__main__.py`**
  - Enables `python -m ATLAS`

---

## 6. Demo Script (Suggested Flow)

1. Add two items (Peripherals, Accessories)
2. List all inventory
3. Adjust quantity to simulate a sale
4. Move an item to a new location
5. Show `summary` report and `low` report

Commands:

```powershell
python -m ATLAS add --sku SKU-101 --name "Label Printer" --category Devices --qty 8  --loc D1 --min 3 --max 20
python -m ATLAS add --sku SKU-102 --name "Thermal Labels" --category Supplies --qty 300 --loc D2 --min 100 --max 1000
python -m ATLAS list
python -m ATLAS adjust --sku SKU-101 --delta -2
python -m ATLAS move --sku SKU-102 --to D5
python -m ATLAS report --type summary
python -m ATLAS report --type low
```

---

## 7. Testing Guide

- **Smoke test**: Run the demo commands above; verify JSON in `data/atlas_inventory.json`.
- **Edge cases**:
  - Adding an existing SKU should raise an error
  - Adjusting a missing SKU should raise an error
  - Quantity never drops below 0
- **Suggested**:
  - Create ad-hoc tests by scripting `InventoryService` calls in a Python REPL
  - Later: add unit tests under `ATLAS/tests/` (opt-in to avoid impacting existing suite)

---

## 8. Docker Integration

ATLAS is standard-library only; to include it in the image, ensure the Dockerfile copies it:

```dockerfile
# In the final stage section
COPY --chown=appuser:appuser ATLAS ./ATLAS
```

You can run the CLI inside the container, e.g.:

```bash
docker exec -it echoes-production python -m ATLAS list
```

---

## 9. Roadmap / Next Steps

- **Categorization**: Leverage `automation/codebase_organizer/classifier.py` to suggest categories
- **Reorder logic**: Compute reorder points by min/max + lead time
- **Barcode/QR**: Support scan-based adjustments (mobile-friendly endpoints)
- **Dashboards**: Real-time visualization (Glimpse integration)
- **APIs**: FastAPI endpoints for CRUD and reports
- **Multi-location**: Location hierarchy, transfers, audit trails
- **Persistence**: Pluggable storage (SQLite/Postgres) via interface
- **Auth & Roles**: Admin/Operator separation and audit logs

---

## 10. Permissions & Access

If you need elevated roles to integrate with `EchoesAssistantV2` or to access deployment credentials, please coordinate with your admin to grant appropriate permissions.

---

## 11. Support

- Primary module: `ATLAS/`
- Data path: `data/atlas_inventory.json`
- Entry point: `python -m ATLAS`

Use this README to onboard quickly, demo capabilities, and guide further development.
