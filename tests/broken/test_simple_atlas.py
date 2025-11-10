#!/usr/bin/env python3
"""
Simple ATLAS test to verify integration
"""

from ATLAS.service import InventoryService

try:
    service = InventoryService()
    print("✅ ATLAS service initialized successfully")

    # Try to add a unique item
    import time

    sku = f"TEST-{int(time.time())}"
    item = service.add_item(
        sku=sku,
        name="Test Widget",
        category="Testing",
        quantity=10,
        location="TEST-LOC",
    )
    print(f"✅ ATLAS: Added item {item.sku}")

    # Retrieve the item
    retrieved = service.get_item(sku)
    if retrieved and retrieved.name == "Test Widget":
        print("✅ ATLAS: Item retrieval successful")
    else:
        print("❌ ATLAS: Item retrieval failed")

except Exception as e:
    print(f"❌ ATLAS test failed: {e}")
