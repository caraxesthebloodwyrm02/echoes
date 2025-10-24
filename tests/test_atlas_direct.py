#!/usr/bin/env python3
"""
Test direct ATLAS interaction.

Verifies that ATLAS can be accessed and used directly without CLI.
"""

from ATLAS import ATLASDirectAPI


def test_direct_atlas_interaction():
    """Test direct ATLAS API interaction."""
    print("\n" + "=" * 60)
    print("Testing Direct ATLAS Interaction")
    print("=" * 60)

    # Initialize API
    api = ATLASDirectAPI()
    print("\n✓ ATLAS API initialized")

    # Test 1: Add items
    print("\n[Test 1] Adding inventory items...")
    result = api.add_item(
        sku="TEST-001",
        name="Test Item 1",
        category="Testing",
        quantity=100,
        location="TEST-LOC-1",
        min_stock=10,
        max_stock=500,
    )
    assert result["success"], f"Failed to add item: {result['error']}"
    print(f"  ✓ Added: {result['item']['sku']} - {result['item']['name']}")

    result = api.add_item(
        sku="TEST-002",
        name="Test Item 2",
        category="Testing",
        quantity=50,
        location="TEST-LOC-2",
    )
    assert result["success"], f"Failed to add item: {result['error']}"
    print(f"  ✓ Added: {result['item']['sku']} - {result['item']['name']}")

    # Test 2: List items
    print("\n[Test 2] Listing inventory items...")
    result = api.list_items()
    assert result["success"], f"Failed to list items: {result['error']}"
    print(f"  ✓ Found {result['count']} items")
    for item in result["items"]:
        print(f"    • {item['sku']}: {item['name']} ({item['quantity']} @ {item['location']})")

    # Test 3: Filter by category
    print("\n[Test 3] Filtering by category...")
    result = api.list_items(category="Testing")
    assert result["success"], f"Failed to filter: {result['error']}"
    print(f"  ✓ Found {result['count']} items in Testing category")

    # Test 4: Get specific item
    print("\n[Test 4] Getting specific item...")
    result = api.get_item("TEST-001")
    assert result["success"], f"Failed to get item: {result['error']}"
    print(f"  ✓ Retrieved: {result['item']['sku']} - {result['item']['name']}")

    # Test 5: Adjust quantity
    print("\n[Test 5] Adjusting quantity...")
    result = api.adjust_quantity("TEST-001", -10)
    assert result["success"], f"Failed to adjust: {result['error']}"
    print(f"  ✓ Adjusted TEST-001: {result['item']['quantity']} units")

    # Test 6: Move item
    print("\n[Test 6] Moving item to new location...")
    result = api.move_item("TEST-002", "TEST-LOC-3")
    assert result["success"], f"Failed to move: {result['error']}"
    print(f"  ✓ Moved TEST-002 to {result['item']['location']}")

    # Test 7: Reports
    print("\n[Test 7] Generating reports...")
    result = api.report_summary()
    assert result["success"], f"Failed to generate report: {result['error']}"
    print("  ✓ Summary Report:")
    print(f"    - Total Items: {result['report']['total_items']}")
    print(f"    - Total Quantity: {result['report']['total_quantity']}")

    # Test 8: Statistics
    print("\n[Test 8] Getting statistics...")
    result = api.get_statistics()
    assert result["success"], f"Failed to get stats: {result['error']}"
    print("  ✓ Statistics:")
    print(f"    - Total Items: {result['total_items']}")
    print(f"    - Total Quantity: {result['total_quantity']}")
    print(f"    - Categories: {result['categories']}")
    print(f"    - Locations: {result['locations']}")

    # Test 9: Batch operations
    print("\n[Test 9] Batch adding items...")
    items = [
        {
            "sku": "BATCH-001",
            "name": "Batch Item 1",
            "category": "Batch",
            "quantity": 25,
            "location": "BATCH-LOC",
        },
        {
            "sku": "BATCH-002",
            "name": "Batch Item 2",
            "category": "Batch",
            "quantity": 30,
            "location": "BATCH-LOC",
        },
    ]
    result = api.bulk_add_items(items)
    assert result["success"], f"Failed batch add: {result}"
    print(f"  ✓ Added {result['successful']}/{result['total']} items")

    # Test 10: Category report
    print("\n[Test 10] Category breakdown...")
    result = api.report_by_category()
    assert result["success"], f"Failed to get category report: {result['error']}"
    print("  ✓ Categories:")
    for category, items in result["by_category"].items():
        print(f"    - {category}: {len(items)} items")

    print("\n" + "=" * 60)
    print("✓ All tests passed!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    test_direct_atlas_interaction()
