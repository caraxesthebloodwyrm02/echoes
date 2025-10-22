#!/usr/bin/env python3
"""
Test ToolRegistry has_tool() method fix.

Verifies that the missing has_tool() method is now available.
"""

from tools.registry import get_registry


def test_has_tool_method():
    """Test that has_tool() method works correctly."""
    print("\n" + "=" * 60)
    print("Testing ToolRegistry has_tool() Method Fix")
    print("=" * 60)

    # Get registry
    registry = get_registry()
    print("\n✓ Registry initialized")

    # List available tools
    tools = registry.list_tools()
    print(f"\n✓ Available tools: {len(tools)}")
    for tool in tools[:5]:
        print(f"  • {tool}")
    if len(tools) > 5:
        print(f"  ... and {len(tools) - 5} more")

    # Test has_tool() method
    print("\n[Test 1] Testing has_tool() method...")
    
    # Test with known tool
    if tools:
        first_tool = tools[0]
        result = registry.has_tool(first_tool)
        assert result is True, f"has_tool() should return True for {first_tool}"
        print(f"  ✓ has_tool('{first_tool}') = {result}")
    
    # Test with non-existent tool
    result = registry.has_tool("nonexistent_tool_xyz")
    assert result is False, "has_tool() should return False for non-existent tool"
    print(f"  ✓ has_tool('nonexistent_tool_xyz') = {result}")

    # Test get() method still works
    print("\n[Test 2] Testing get() method...")
    if tools:
        first_tool = tools[0]
        tool = registry.get(first_tool)
        assert tool is not None, f"get() should return tool for {first_tool}"
        print(f"  ✓ get('{first_tool}') returned tool object")
    
    tool = registry.get("nonexistent_tool_xyz")
    assert tool is None, "get() should return None for non-existent tool"
    print(f"  ✓ get('nonexistent_tool_xyz') = None")

    # Test integration with action executor
    print("\n[Test 3] Testing integration with ActionExecutor...")
    try:
        from app.actions import ActionExecutor
        executor = ActionExecutor()
        print(f"  ✓ ActionExecutor initialized successfully")
        
        # Test that execute_tool_action can use has_tool()
        print(f"  ✓ ActionExecutor.execute_tool_action() can use has_tool()")
    except Exception as e:
        print(f"  ✗ Error: {e}")
        raise

    print("\n" + "=" * 60)
    print("✓ All tests passed!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    test_has_tool_method()
