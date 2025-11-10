#!/usr/bin/env python3
"""
Comprehensive tests for Glimpse integration tools.

Tests the GlimpseApiGetTool, GlimpseApiPostTool, and GlimpseConnectPlatformsTool
classes to ensure they work correctly with the EchoesAssistantV2 framework.
"""

import json
import time
from unittest.mock import Mock

from tools.glimpse_tools import (GlimpseApiGetTool, GlimpseApiPostTool,
                                 GlimpseConnectPlatformsTool,
                                 get_glimpse_tools)


class TestGlimpseApiGetTool:
    """Test suite for GlimpseApiGetTool."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_assistant = Mock()
        self.tool = GlimpseApiGetTool(self.mock_assistant)

    def test_initialization(self):
        """Test tool initialization."""
        assert self.tool.name == "glimpse_api_get"
        assert "trajectory tracking" in self.tool.description
        assert "readability metrics" in self.tool.description
        assert self.tool.input_schema is not None
        assert "url" in self.tool.input_schema["required"]

    def test_has_get_stats_method(self):
        """Test that get_stats method exists and works."""
        stats = self.tool.get_stats()

        assert isinstance(stats, dict)
        assert "name" in stats
        assert "description" in stats
        assert "total_calls" in stats
        assert "last_call_time" in stats
        assert "error_count" in stats
        assert "average_response_time" in stats

        assert stats["name"] == "glimpse_api_get"
        assert stats["total_calls"] == 0
        assert stats["error_count"] == 0
        assert stats["average_response_time"] == 0.0

    def test_has_to_openai_schema_method(self):
        """Test that to_openai_schema method exists and returns valid schema."""
        schema = self.tool.to_openai_schema()

        assert isinstance(schema, dict)
        assert schema["type"] == "function"
        assert "function" in schema
        assert schema["function"]["name"] == "glimpse_api_get"
        assert "parameters" in schema["function"]

        # Validate required fields are present
        parameters = schema["function"]["parameters"]
        assert "type" in parameters
        assert "properties" in parameters
        assert "required" in parameters

    def test_input_schema_structure(self):
        """Test that input schema has correct structure."""
        schema = self.tool.input_schema

        assert schema["type"] == "object"
        assert "properties" in schema

        props = schema["properties"]
        assert "url" in props
        assert "headers" in props
        assert "params" in props
        assert "timeout" in props

        # Check URL property
        url_prop = props["url"]
        assert url_prop["type"] == "string"
        assert "description" in url_prop

        # Check required fields
        assert "url" in schema["required"]

    def test_statistics_tracking(self):
        """Test that statistics are properly tracked."""
        initial_stats = self.tool.get_stats()
        assert initial_stats["total_calls"] == 0

        # Simulate some usage by directly modifying counters
        self.tool._total_calls = 5
        self.tool._error_count = 1
        self.tool._total_response_time = 2.5
        self.tool._last_call_time = time.time()

        updated_stats = self.tool.get_stats()
        assert updated_stats["total_calls"] == 5
        assert updated_stats["error_count"] == 1
        assert updated_stats["average_response_time"] == 0.5  # 2.5 / 5


class TestGlimpseApiPostTool:
    """Test suite for GlimpseApiPostTool."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_assistant = Mock()
        self.tool = GlimpseApiPostTool(self.mock_assistant)

    def test_initialization(self):
        """Test tool initialization."""
        assert self.tool.name == "glimpse_api_post"
        assert "data flow analysis" in self.tool.description
        assert "connectivity assessment" in self.tool.description
        assert self.tool.input_schema is not None
        assert "url" in self.tool.input_schema["required"]
        assert "data" in self.tool.input_schema["required"]

    def test_has_get_stats_method(self):
        """Test that get_stats method exists and works."""
        stats = self.tool.get_stats()

        assert isinstance(stats, dict)
        assert stats["name"] == "glimpse_api_post"
        assert stats["total_calls"] == 0
        assert stats["error_count"] == 0
        assert stats["average_response_time"] == 0.0

    def test_has_to_openai_schema_method(self):
        """Test that to_openai_schema method exists."""
        schema = self.tool.to_openai_schema()
        assert isinstance(schema, dict)
        assert schema["function"]["name"] == "glimpse_api_post"

    def test_input_schema_data_field(self):
        """Test that data field has correct oneOf specification."""
        schema = self.tool.input_schema
        data_prop = schema["properties"]["data"]

        assert "oneOf" in data_prop
        one_of_options = data_prop["oneOf"]

        # Should support string, object, and array types
        types_found = [opt.get("type") for opt in one_of_options]
        assert "string" in types_found
        assert "object" in types_found

        # Array option should have items specification
        array_option = next(opt for opt in one_of_options if opt.get("type") == "array")
        assert "items" in array_option
        assert array_option["items"]["type"] == "string"

    def test_execute_method_with_json_data(self):
        """Test execute method with JSON data."""
        # Mock the assistant's glimpse_api_post method
        mock_response = {"status": "success", "data": {"key": "value"}}
        self.mock_assistant.glimpse_api_post.return_value = mock_response

        result = self.tool.execute(
            url="https://api.example.com/test",
            data={"test": "data"},
            headers={"Content-Type": "application/json"},
        )

        assert result == mock_response
        self.mock_assistant.glimpse_api_post.assert_called_once()

        # Check that statistics were updated
        stats = self.tool.get_stats()
        assert stats["total_calls"] == 1

    def test_execute_method_with_form_data(self):
        """Test execute method with form data."""
        mock_response = {"status": "success"}
        self.mock_assistant.glimpse_api_post.return_value = mock_response

        result = self.tool.execute(
            url="https://api.example.com/form",
            data={"field1": "value1", "field2": "value2"},
            content_type="form",
        )

        assert result == mock_response
        self.mock_assistant.glimpse_api_post.assert_called_once()

    def test_execute_method_with_raw_string(self):
        """Test execute method with raw string data."""
        mock_response = {"status": "success"}
        self.mock_assistant.glimpse_api_post.return_value = mock_response

        result = self.tool.execute(
            url="https://api.example.com/raw", data="raw string data"
        )

        assert result == mock_response
        self.mock_assistant.glimpse_api_post.assert_called_once()


class TestGlimpseConnectPlatformsTool:
    """Test suite for GlimpseConnectPlatformsTool."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_assistant = Mock()
        self.tool = GlimpseConnectPlatformsTool(self.mock_assistant)

    def test_initialization(self):
        """Test tool initialization."""
        assert self.tool.name == "glimpse_connect_platforms"
        assert "establish intelligent connections" in self.tool.description.lower()
        assert "automatic compatibility analysis" in self.tool.description
        assert self.tool.input_schema is not None
        assert "source_path" in self.tool.input_schema["required"]
        assert "target_path" in self.tool.input_schema["required"]

    def test_has_get_stats_method(self):
        """Test that get_stats method exists."""
        stats = self.tool.get_stats()

        assert isinstance(stats, dict)
        assert stats["name"] == "glimpse_connect_platforms"
        assert "average_operation_time" in stats  # Different from API tools

    def test_has_to_openai_schema_method(self):
        """Test that to_openai_schema method exists."""
        schema = self.tool.to_openai_schema()
        assert isinstance(schema, dict)
        assert schema["function"]["name"] == "glimpse_connect_platforms"

    def test_input_schema_integration_modes(self):
        """Test integration mode options."""
        schema = self.tool.input_schema
        integration_mode = schema["properties"]["integration_mode"]

        assert "enum" in integration_mode
        expected_modes = ["reference_bridge", "full_sync", "read_only", "write_only"]
        assert integration_mode["enum"] == expected_modes
        assert integration_mode["default"] == "reference_bridge"

    def test_execute_method(self):
        """Test execute method."""
        mock_response = {"status": "connected", "connection_id": "123"}
        self.mock_assistant.glimpse_connect_platforms.return_value = mock_response

        result = self.tool.execute(
            source_path="E:/Projects/Echoes/c_o_r_e",
            target_path="D:/Research",
            integration_mode="reference_bridge",
        )

        assert result == mock_response
        self.mock_assistant.glimpse_connect_platforms.assert_called_once_with(
            source_path="E:/Projects/Echoes/c_o_r_e",
            target_path="D:/Research",
            integration_mode="reference_bridge",
            sync_frequency="manual",
            conflict_resolution="source_priority",
        )


class TestGlimpseToolIntegration:
    """Integration tests for Glimpse tools."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_assistant = Mock()

    def test_get_glimpse_tools_returns_all_tools(self):
        """Test that get_glimpse_tools returns all three tool types."""
        tools = get_glimpse_tools(self.mock_assistant)

        assert len(tools) == 3
        tool_names = [tool.name for tool in tools]
        assert "glimpse_api_get" in tool_names
        assert "glimpse_api_post" in tool_names
        assert "glimpse_connect_platforms" in tool_names

    def test_all_tools_have_required_methods(self):
        """Test that all tools have required methods for registry."""
        tools = get_glimpse_tools(self.mock_assistant)

        for tool in tools:
            # All tools must have get_stats method
            assert hasattr(tool, "get_stats"), f"{tool.name} missing get_stats method"
            assert callable(tool.get_stats), f"{tool.name} get_stats not callable"

            # All tools must have to_openai_schema method
            assert hasattr(
                tool, "to_openai_schema"
            ), f"{tool.name} missing to_openai_schema method"
            assert callable(
                tool.to_openai_schema
            ), f"{tool.name} to_openai_schema not callable"

    def test_tool_schemas_are_valid_json(self):
        """Test that all tool schemas are valid JSON."""
        tools = get_glimpse_tools(self.mock_assistant)

        for tool in tools:
            schema = tool.to_openai_schema()

            # Should be able to serialize to JSON
            json_str = json.dumps(schema)
            parsed = json.loads(json_str)

            assert parsed == schema

    def test_tool_stats_initialization(self):
        """Test that tool statistics are properly initialized."""
        tools = get_glimpse_tools(self.mock_assistant)

        for tool in tools:
            stats = tool.get_stats()

            assert stats["total_calls"] == 0
            assert stats["error_count"] == 0
            assert stats["last_call_time"] is None


if __name__ == "__main__":
    # Run tests directly
    print("\n" + "=" * 80)
    print("🧪 Running Glimpse Tools Test Suite")
    print("=" * 80)

    # Simple test runner
    test_classes = [
        TestGlimpseApiGetTool,
        TestGlimpseApiPostTool,
        TestGlimpseConnectPlatformsTool,
        TestGlimpseToolIntegration,
    ]

    total_tests = 0
    passed_tests = 0

    for test_class in test_classes:
        print(f"\n📋 Running {test_class.__name__}...")

        instance = test_class()
        instance.setup_method()

        for method_name in dir(test_class):
            if method_name.startswith("test_"):
                total_tests += 1
                try:
                    method = getattr(instance, method_name)
                    method()
                    print(f"  ✅ {method_name}")
                    passed_tests += 1
                except Exception as e:
                    print(f"  ❌ {method_name}: {str(e)}")

    print("\n" + "=" * 80)
    print(f"📊 Test Results: {passed_tests}/{total_tests} tests passed")
    if passed_tests == total_tests:
        print("🎉 All tests passed! Glimpse integration is working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
    print("=" * 80)
