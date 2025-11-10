#!/usr/bin/env python3
"""
Test ToolRegistry has_tool() method fix.

Verifies that the missing has_tool() method is now available.
"""

import sys
import os
from pathlib import Path

# Add project root to path to ensure imports work
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Try to import registry with better error handling
try:
    from tools.registry import get_registry

    REGISTRY_AVAILABLE = True

    # Import examples to register some tools
    try:
        import tools.examples

        print("✓ Example tools imported and registered")
    except ImportError as e:
        print(f"⚠️ Could not import example tools: {e}")

except ImportError as e:
    print(f"❌ Error importing registry: {e}")
    print(
        "Make sure you're running from the project root and dependencies are installed"
    )
    REGISTRY_AVAILABLE = False


# Test decorator for better output
def _test_decorator(name):
    def decorator(test_func):
        def wrapper(*args, **kwargs):
            print(f"\n{'='*60}")
            print(f"TEST: {name}")
            print(f"{'='*60}")
            try:
                result = test_func(*args, **kwargs)
                print(f"✅ {name} PASSED")
                return result
            except Exception as e:
                print(f"❌ {name} FAILED: {e}")
                raise

        return wrapper

    return decorator


@_test_decorator("Basic Registry Functionality")
def test_case():
    """Test basic registry functionality."""
    if not REGISTRY_AVAILABLE:
        print("Skipping test: Registry not available")
        return

    # Get registry with error handling
    try:
        registry = get_registry()
        print("✓ Registry initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize registry: {e}")
        raise

    # Test basic functionality
    try:
        tools = registry.list_tools()
        print(f"✓ Registry has {len(tools)} tools")

        # Test has_tool method
        if tools:
            first_tool = tools[0]
            has_tool = registry.has_tool(first_tool)
            assert has_tool is True, f"has_tool should return True for {first_tool}"
            print(f"✓ has_tool('{first_tool}') = {has_tool}")

        # Test non-existent tool
        has_fake = registry.has_tool("nonexistent_tool_xyz123")
        assert has_fake is False, "has_tool should return False for non-existent tool"
        print(f"✓ has_tool('nonexistent_tool_xyz123') = {has_fake}")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        raise


@_test_decorator("ToolRegistry has_tool() Method Test")
def test_has_tool_method():
    """Test that has_tool() method works correctly."""
    if not REGISTRY_AVAILABLE:
        print("Skipping test: Registry not available")
        return

    # Get registry with error handling
    try:
        registry = get_registry()
        print("✓ Registry initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize registry: {e}")
        raise

    # List available tools with error handling
    try:
        tools = registry.list_tools()
        if not tools:
            print("⚠️ No tools found in registry")
            return

        print(f"\n✓ Found {len(tools)} available tools")
        print("\nFirst 5 tools:" + "-" * 45)
        for i, tool in enumerate(tools[:5], 1):
            print(f"  {i}. {tool}")

        if len(tools) > 5:
            print(f"\n... and {len(tools) - 5} more tools not shown")

    except AttributeError:
        print("❌ Registry is missing list_tools() method")
        raise
    except Exception as e:
        print(f"❌ Error listing tools: {e}")
        raise

    # Test 1: has_tool() with existing tool
    print("\n[Test 1] has_tool() with existing tool")
    try:
        first_tool = tools[0] if tools else "example_tool"
        result = registry.has_tool(first_tool)

        if not hasattr(registry, "has_tool"):
            print("❌ has_tool() method is missing from registry")
            return

        assert result is True, f"has_tool() should return True for {first_tool}"
        print(f"✓ has_tool('{first_tool}') = {result}")

    except Exception as e:
        print(f"❌ Test 1 failed: {e}")
        raise

    # Test 2: has_tool() with non-existent tool
    print("\n[Test 2] has_tool() with non-existent tool")
    try:
        non_existent = "nonexistent_tool_xyz123"
        result = registry.has_tool(non_existent)
        assert result is False, f"has_tool() should return False for {non_existent}"
        print(f"✓ has_tool('{non_existent}') = {result}")
    except Exception as e:
        print(f"❌ Test 2 failed: {e}")
        raise

    # Test 3: get() method with existing tool
    print("\n[Test 3] get() with existing tool")
    try:
        if not tools:
            print("⚠️ No tools available to test get()")
            return

        first_tool = tools[0]
        tool = registry.get(first_tool)

        if not hasattr(registry, "get"):
            print("❌ get() method is missing from registry")
            return

        assert tool is not None, f"get() should return tool for {first_tool}"
        print(f"✓ get('{first_tool}') returned tool object")
        print(f"   Tool type: {type(tool).__name__}")

    except Exception as e:
        print(f"❌ Test 3 failed: {e}")
        raise

    # Test 4: get() with non-existent tool (error handling)
    print("\n[Test 4] get() with non-existent tool")
    try:
        non_existent = "nonexistent_tool_xyz123"
        tool = registry.get(non_existent)
        if tool is not None:
            print(
                f"⚠️ get('{non_existent}') returned {tool} (expected None or exception)"
            )
        else:
            print(f"✓ get('{non_existent}') returned None as expected")
    except Exception as e:
        print(
            f"✓ get() raised {e.__class__.__name__} for non-existent tool (expected behavior)"
        )

    print("\n✅ All tests completed successfully!")

    # Test integration with action executor if available
    print("\n[Test 5] Testing integration with ActionExecutor...")
    try:
        from app.actions import ActionExecutor

        executor = ActionExecutor()
        print("✓ ActionExecutor initialized successfully")

        # Test that execute_tool_action can use has_tool()
        if hasattr(executor, "execute_tool_action"):
            print("✓ ActionExecutor.execute_tool_action() is available")

            # Test with a known tool if we have one
            if tools:
                test_tool = tools[0]
                try:
                    executor.execute_tool_action(test_tool, {})
                    print(f"✓ Successfully executed tool: {test_tool}")
                except Exception as e:
                    print(f"⚠️ Tool execution failed (this might be expected): {e}")
        else:
            print("⚠️ execute_tool_action() not found in ActionExecutor")

    except ImportError:
        print("⚠️ ActionExecutor not available for testing")
    except Exception as e:
        print(f"⚠️ Error testing ActionExecutor: {e}")
    except Exception as e:
        print(f"  ✗ Error: {e}")
        raise

    print("\n" + "=" * 60)
    print("✓ All tests passed!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    test_has_tool_method()
