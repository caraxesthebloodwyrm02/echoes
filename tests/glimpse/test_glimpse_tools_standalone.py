#!/usr/bin/env python3
"""
Standalone test runner for Glimpse tools.

This script can be run directly to test Glimpse tool functionality
without requiring pytest or complex module path setup.
"""

import json
import os
import sys
from unittest.mock import Mock

# Add the project root to Python path
sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

try:
    from tools.glimpse_tools import (
        GlimpseApiGetTool,
        GlimpseApiPostTool,
        GlimpseConnectPlatformsTool,
        get_glimpse_tools,
    )
except ImportError as e:
    print(f"❌ Failed to import Glimpse tools: {e}")
    print("Make sure you're running this from the project root directory.")
    sys.exit(1)


def run_test(test_name, test_func):
    """Run a single test and report results."""
    try:
        test_func()
        print(f"  ✅ {test_name}")
        return True
    except Exception as e:
        print(f"  ❌ {test_name}: {str(e)}")
        return False


def test_glimpse_api_get_tool():
    """Test GlimpseApiGetTool functionality."""
    print("Testing GlimpseApiGetTool...")

    mock_assistant = Mock()
    tool = GlimpseApiGetTool(mock_assistant)

    # Test initialization
    assert tool.name == "glimpse_api_get"
    assert "trajectory tracking" in tool.description

    # Test get_stats method
    stats = tool.get_stats()
    assert isinstance(stats, dict)
    assert stats["name"] == "glimpse_api_get"
    assert stats["total_calls"] == 0

    # Test to_openai_schema method
    schema = tool.to_openai_schema()
    assert schema["type"] == "function"
    assert schema["function"]["name"] == "glimpse_api_get"

    # Test schema is valid JSON
    json_str = json.dumps(schema)
    parsed = json.loads(json_str)
    assert parsed == schema


def test_glimpse_api_post_tool():
    """Test GlimpseApiPostTool functionality."""
    print("Testing GlimpseApiPostTool...")

    mock_assistant = Mock()
    tool = GlimpseApiPostTool(mock_assistant)

    # Test initialization
    assert tool.name == "glimpse_api_post"
    assert "data flow analysis" in tool.description

    # Test get_stats method
    stats = tool.get_stats()
    assert isinstance(stats, dict)
    assert stats["name"] == "glimpse_api_post"

    # Test schema data field
    schema = tool.input_schema
    data_prop = schema["properties"]["data"]
    assert "oneOf" in data_prop

    # Test execution with mock
    mock_response = {"status": "success"}
    mock_assistant.glimpse_api_post.return_value = mock_response

    result = tool.execute("https://api.example.com", {"test": "data"})
    assert result == mock_response
    assert tool.get_stats()["total_calls"] == 1


def test_glimpse_connect_platforms_tool():
    """Test GlimpseConnectPlatformsTool functionality."""
    print("Testing GlimpseConnectPlatformsTool...")

    mock_assistant = Mock()
    tool = GlimpseConnectPlatformsTool(mock_assistant)

    # Test initialization
    assert tool.name == "glimpse_connect_platforms"
    assert "establish intelligent connections" in tool.description.lower()

    # Test get_stats method
    stats = tool.get_stats()
    assert isinstance(stats, dict)
    assert "average_operation_time" in stats

    # Test schema integration modes
    schema = tool.input_schema
    integration_mode = schema["properties"]["integration_mode"]
    assert "enum" in integration_mode
    assert "reference_bridge" in integration_mode["enum"]


def test_integration():
    """Test integration functionality."""
    print("Testing integration...")

    mock_assistant = Mock()
    tools = get_glimpse_tools(mock_assistant)

    # Should return 3 tools
    assert len(tools) == 3

    # All tools should have required methods
    for tool in tools:
        assert hasattr(tool, "get_stats")
        assert hasattr(tool, "to_openai_schema")
        assert callable(tool.get_stats)
        assert callable(tool.to_openai_schema)

        # Test stats initialization
        stats = tool.get_stats()
        assert stats["total_calls"] == 0
        assert stats["error_count"] == 0


def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("🧪 Glimpse Tools Standalone Test Runner")
    print("=" * 80)
    print("Testing Glimpse integration functionality...\n")

    tests = [
        ("GlimpseApiGetTool", test_glimpse_api_get_tool),
        ("GlimpseApiPostTool", test_glimpse_api_post_tool),
        ("GlimpseConnectPlatformsTool", test_glimpse_connect_platforms_tool),
        ("Integration Tests", test_integration),
    ]

    total_tests = len(tests)
    passed_tests = 0

    for test_name, test_func in tests:
        print(f"📋 Running {test_name}...")
        if run_test(test_name, test_func):
            passed_tests += 1
        print()

    print("=" * 80)
    print(f"📊 Test Results: {passed_tests}/{total_tests} test suites passed")

    if passed_tests == total_tests:
        print("🎉 All tests passed! Glimpse integration is working correctly.")
        print("   ✅ Tool initialization")
        print("   ✅ Statistics tracking")
        print("   ✅ OpenAI schema generation")
        print("   ✅ Method execution")
        print("   ✅ Registry integration")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
