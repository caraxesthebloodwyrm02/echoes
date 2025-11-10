#!/usr/bin/env python3
"""
Inventory Optimization Demo
Demonstrates the performance improvements and new features of the optimized ATLAS system.
"""

import json
import os
import time
from pathlib import Path


def demo_performance_improvements():
    """Demonstrate caching and performance improvements."""
    print("🔧 Testing Inventory Performance Optimizations")
    print("=" * 60)

    # Import ATLAS components
    try:
        from ATLAS.cli import main as atlas_cli
        from ATLAS.service import InventoryService
    except ImportError:
        print("❌ Could not import ATLAS components")
        return

    svc = InventoryService()

    print("\n⚡ Cache Performance Test:")
    print("-" * 30)

    # Test caching performance
    start_time = time.time()
    for i in range(10):
        data = svc._get_cached_data()
    cache_time = time.time() - start_time

    print(".4f")

    # Test smart summary
    print("\n📊 Smart Summary Feature:")
    print("-" * 30)
    summary = svc.smart_summary()
    print(summary)

    # Test suggestions
    print("\n🏷️ Auto-complete Suggestions:")
    print("-" * 30)
    categories = svc.suggest_categories()
    locations = svc.suggest_locations()
    print(f"Categories ({len(categories)}): {', '.join(categories[:5])}...")
    print(f"Locations ({len(locations)}): {', '.join(locations[:5])}...")

    # Test performance stats
    print("\n📈 Performance Statistics:")
    print("-" * 30)
    stats = svc.get_performance_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")

def demo_batch_operations():
    """Demonstrate batch operations capability."""
    print("\n🔄 Batch Operations Demo")
    print("=" * 60)

    try:
        from ATLAS.service import InventoryService
    except ImportError:
        print("❌ Could not import ATLAS components")
        return

    svc = InventoryService()

    # Create sample batch operations
    batch_ops = [
        {
            "type": "add",
            "sku": "DEMO001",
            "name": "Demo Widget",
            "category": "widgets",
            "quantity": 100,
            "location": "warehouse-a",
            "min_stock": 10,
            "max_stock": 500
        },
        {
            "type": "add",
            "sku": "DEMO002",
            "name": "Demo Gadget",
            "category": "gadgets",
            "quantity": 50,
            "location": "warehouse-b",
            "min_stock": 5,
            "max_stock": 200
        },
        {
            "type": "adjust",
            "sku": "DEMO001",
            "delta": 25
        },
        {
            "type": "move",
            "sku": "DEMO002",
            "location": "warehouse-c"
        }
    ]

    print("📋 Processing batch operations...")
    print(f"Operations: {len(batch_ops)}")

    start_time = time.time()
    results = svc.batch_operations(batch_ops)
    duration = time.time() - start_time

    successful = sum(1 for r in results if r.get('success', False))

    print("
✅ Results:"    print(f"Successful: {successful}/{len(results)}")
    print(".2f")

    for i, result in enumerate(results):
        status = "✅" if result.get('success', False) else "❌"
        print(f"  {i+1}. {status} {result.get('operation', 'unknown')}: {result.get('sku', 'N/A')}")

def demo_pagination():
    """Demonstrate pagination and sorting features."""
    print("\n📄 Pagination & Sorting Demo")
    print("=" * 60)

    try:
        from ATLAS.service import InventoryService
    except ImportError:
        print("❌ Could not import ATLAS components")
        return

    svc = InventoryService()

    print("📊 Testing pagination with sorting...")

    # Test different sorting options
    sort_options = ['sku', 'name', 'quantity', 'category']

    for sort_by in sort_options:
        result = svc.list_items_paginated(
            page=1,
            per_page=5,
            sort_by=sort_by,
            sort_order='asc'
        )

        print(f"\n🔤 Sorted by {sort_by} (Page {result['pagination']['page']}):")
        print(f"   Total: {result['pagination']['total_items']} items")

        for item in result['items'][:3]:  # Show first 3
            print(f"   • {item.sku}: {item.name} ({item.quantity} @ {item.location})")

def demo_cli_features():
    """Demonstrate new CLI features."""
    print("\n💻 New CLI Features Demo")
    print("=" * 60)

    try:
        from ATLAS.cli import main as atlas_cli
    except ImportError:
        print("❌ Could not import ATLAS CLI")
        return

    print("🆕 Available Commands:")
    print("  • atlas summary              - Smart inventory summary")
    print("  • atlas suggest categories   - Auto-complete categories")
    print("  • atlas suggest locations    - Auto-complete locations")
    print("  • atlas batch <file>         - Process batch operations")
    print("  • atlas stats                - Performance statistics")
    print("  • atlas list --page 2        - Paginated listings")
    print("  • atlas list --sort-by quantity - Sorted listings")

    print("\n📝 Example batch file format:")
    batch_example = [
        {
            "type": "add",
            "sku": "BATCH001",
            "name": "Batch Item",
            "category": "batch_demo",
            "quantity": 10,
            "location": "demo_warehouse"
        },
        {
            "type": "adjust",
            "sku": "BATCH001",
            "delta": 5
        }
    ]

    print(json.dumps(batch_example, indent=2))

def create_sample_data():
    """Create some sample data for demonstration."""
    print("\n🧪 Creating Sample Data")
    print("=" * 60)

    try:
        from ATLAS.service import InventoryService
    except ImportError:
        print("❌ Could not import ATLAS components")
        return

    svc = InventoryService()

    sample_items = [
        ("WIDGET001", "Small Widget", "widgets", 150, "warehouse-a", 10, 200),
        ("WIDGET002", "Large Widget", "widgets", 75, "warehouse-b", 5, 100),
        ("GADGET001", "Basic Gadget", "gadgets", 200, "warehouse-a", 20, 300),
        ("GADGET002", "Advanced Gadget", "gadgets", 50, "warehouse-c", 8, 150),
        ("TOOL001", "Standard Tool", "tools", 100, "warehouse-b", 15, 250),
        ("TOOL002", "Precision Tool", "tools", 25, "warehouse-c", 3, 75),
    ]

    added = 0
    for sku, name, category, qty, location, min_stock, max_stock in sample_items:
        try:
            svc.add_item(sku, name, category, qty, location, min_stock, max_stock)
            added += 1
        except ValueError:
            pass  # Item might already exist

    print(f"✅ Added {added} sample items")

def main():
    """Run the complete inventory optimization demo."""
    print("🚀 ATLAS Inventory Optimization Demo")
    print("=" * 80)
    print("Demonstrating performance improvements and new features")
    print("=" * 80)

    # Create sample data first
    create_sample_data()

    # Run demonstrations
    demo_performance_improvements()
    demo_batch_operations()
    demo_pagination()
    demo_cli_features()

    print("\n" + "=" * 80)
    print("✅ Inventory Optimization Demo Complete!")
    print("=" * 80)
    print("\n🎯 Key Improvements:")
    print("  • ⚡ 30-second caching for instant responses")
    print("  • 🔄 Batch operations for bulk processing")
    print("  • 📄 Pagination & sorting for large datasets")
    print("  • 📊 Smart summaries (no information overload)")
    print("  • 🔍 Auto-complete suggestions")
    print("  • 📈 Performance monitoring & statistics")
    print("  • 🛡️ Thread-safe operations")
    print("\n💡 Ready for Kardashev-scale inventory management!")

if __name__ == "__main__":
    main()
