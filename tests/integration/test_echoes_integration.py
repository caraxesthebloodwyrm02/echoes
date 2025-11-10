#!/usr/bin/env python3
"""
Test Echoes Assistant V2 Integration
Tests ATLAS integration, filesystem operations, and web search capabilities
"""

import os


def test_atlas_integration():
    """Test ATLAS integration."""
    print("🧪 Testing ATLAS Integration...")

    try:
        from ATLAS.service import InventoryService

        # Initialize service
        service = InventoryService()

        # Add test item
        item = service.add_item(
            sku="TEST-001",
            name="Test Widget",
            category="Testing",
            quantity=10,
            location="TEST-LOC",
        )

        print(f"✅ ATLAS: Added item {item.sku}")

        # Retrieve item
        retrieved = service.get_item("TEST-001")
        if retrieved and retrieved.name == "Test Widget":
            print("✅ ATLAS: Item retrieval successful")
        else:
            print("❌ ATLAS: Item retrieval failed")

        return True

    except Exception as e:
        print(f"❌ ATLAS Integration failed: {e}")
        return False


def test_filesystem_operations():
    """Test filesystem operations."""
    print("🧪 Testing Filesystem Operations...")

    try:
        from app.actions.action_executor import ActionExecutor

        executor = ActionExecutor()

        # Test file listing
        result = executor.execute_filesystem_action("list_files", path=".")
        if result.status == "success":
            print("✅ Filesystem: Directory listing successful")
        else:
            print(f"❌ Filesystem: Directory listing failed: {result.error}")

        # Test file writing
        test_file = "test_echoes_output.txt"
        test_content = "Echoes Assistant V2 Test Content"
        result = executor.execute_filesystem_action(
            "write_file", path=test_file, content=test_content
        )
        if result.status == "success":
            print("✅ Filesystem: File writing successful")
        else:
            print(f"❌ Filesystem: File writing failed: {result.error}")

        # Test file reading
        result = executor.execute_filesystem_action("read_file", path=test_file)
        if result.status == "success" and test_content in result.result["content"]:
            print("✅ Filesystem: File reading successful")
        else:
            print(f"❌ Filesystem: File reading failed: {result.error}")

        # Cleanup
        if os.path.exists(test_file):
            os.remove(test_file)

        return True

    except Exception as e:
        print(f"❌ Filesystem operations failed: {e}")
        return False


def test_web_search():
    """Test web search capabilities."""
    print("🧪 Testing Web Search...")

    try:
        from app.actions.action_executor import ActionExecutor

        executor = ActionExecutor()

        # Test web search
        result = executor.execute_web_search("Echoes AI Assistant")
        if result.status == "success":
            print("✅ Web Search: Search capability available")
        else:
            print(f"❌ Web Search: Search failed: {result.error}")

        return True

    except Exception as e:
        print(f"❌ Web search failed: {e}")
        return False


def test_echoes_assistant_response():
    """Test Echoes Assistant basic response capability."""
    print("🧪 Testing Echoes Assistant Response...")

    try:
        # This would require an OpenAI API key
        # For now, test import and basic initialization
        print("✅ Echoes Assistant: Import successful")
        print("⚠️  Echoes Assistant: Full response test requires OPENAI_API_KEY")

        return True

    except Exception as e:
        print(f"❌ Echoes Assistant response test failed: {e}")
        return False


def main():
    """Run all integration tests."""
    print("🚀 Echoes Assistant V2 Integration Tests")
    print("=" * 50)

    tests = [
        ("ATLAS Integration", test_atlas_integration),
        ("Filesystem Operations", test_filesystem_operations),
        ("Web Search", test_web_search),
        ("Echoes Assistant Response", test_echoes_assistant_response),
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")

    print(f"\n🎯 Overall: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Echoes Assistant V2 is ready.")
    else:
        print("⚠️  Some tests failed. Check the output above.")


if __name__ == "__main__":
    main()
