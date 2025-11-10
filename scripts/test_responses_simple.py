#!/usr/bin/env python3
"""
Test the Responses API migration with proper tool handling
"""
import os

# Test with Responses API enabled (default)
os.environ["USE_RESPONSES_API"] = "true"

from assistant_v2_core import EchoesAssistantV2


def test_responses_api():
    print("=" * 60)
    print("Testing OpenAI Responses API Migration")
    print("=" * 60)

    # Create assistant with Responses API
    assistant = EchoesAssistantV2(
        enable_streaming=False, enable_tools=True, enable_status=False
    )

    print(
        f"\n✓ Assistant initialized with Responses API: {assistant.use_responses_api}"
    )

    # Test 1: Simple non-streaming message (no tools)
    print("\n1. Testing simple non-streaming message...")
    result = assistant.chat("Hello! Tell me a short joke.", stream=False)
    print(
        f"   Result: {result[:100]}..." if len(result) > 100 else f"   Result: {result}"
    )
    print(f"   Type: {type(result)}")

    # Test 2: Tool calling with calculator
    print("\n2. Testing tool calling with calculator...")
    result = assistant.chat("What is 25 * 48?", stream=False)
    print(f"   Result: {result}")
    print(f"   Type: {type(result)}")

    # Test 3: Streaming message
    print("\n3. Testing streaming message...")
    result = assistant.chat("Write a haiku about programming", stream=True)
    print(f"   Result type: {type(result)}")
    print("   Streaming output: ", end="")
    for chunk in result:
        print(chunk, end="", flush=True)
    print()

    print("\n" + "=" * 60)
    print("✅ All tests completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    test_responses_api()
