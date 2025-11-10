#!/usr/bin/env python3
"""
Debug test for Responses API
"""
import json
import os

# Test with Responses API enabled (default)
os.environ["USE_RESPONSES_API"] = "true"

from assistant_v2_core import EchoesAssistantV2


def debug_responses_api():
    print("=" * 60)
    print("Debug: OpenAI Responses API")
    print("=" * 60)

    # Create assistant with Responses API
    assistant = EchoesAssistantV2(
        enable_streaming=False,
        enable_tools=False,  # Disable tools first
        enable_status=False,
    )

    print(
        f"\n✓ Assistant initialized with Responses API: {assistant.use_responses_api}"
    )

    # Test simple message
    print("\n1. Testing simple message (no tools)...")
    try:
        result = assistant.chat(
            "Hello! Say 'API test successful' if you can read this.", stream=False
        )
        print(f"   Result length: {len(result) if result else 0}")
        print(f"   Result: {repr(result)}")
        print(f"   Type: {type(result)}")
    except Exception as e:
        print(f"   Error: {e}")

    # Test with tools
    print("\n2. Testing with tools enabled...")
    assistant2 = EchoesAssistantV2(
        enable_streaming=False, enable_tools=True, enable_status=False
    )

    try:
        result = assistant2.chat(
            "What is 2 + 2? Use the calculator tool.", stream=False
        )
        print(f"   Result length: {len(result) if result else 0}")
        print(f"   Result: {repr(result)}")
        print(f"   Type: {type(result)}")
    except Exception as e:
        print(f"   Error: {e}")

    # Test the conversion functions directly
    print("\n3. Testing message conversion...")
    test_messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"},
    ]

    converted = assistant._convert_to_responses_input(test_messages)
    print(f"   Original: {json.dumps(test_messages, indent=2)}")
    print(f"   Converted: {json.dumps(converted, indent=2)}")

    # Test tool conversion
    print("\n4. Testing tool conversion...")
    if assistant2.tool_registry:
        tools = assistant2.tool_registry.get_openai_schemas()
        if tools:
            print(f"   Original tool schema: {json.dumps(tools[0], indent=2)}")
            converted_tools = assistant2._convert_tools_to_responses_format(tools)
            if converted_tools:
                print(
                    f"   Converted tool schema: {json.dumps(converted_tools[0], indent=2)}"
                )


if __name__ == "__main__":
    debug_responses_api()
