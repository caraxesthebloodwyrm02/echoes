#!/usr/bin/env python3
"""
Test the Responses API migration
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

    # Test 1: Simple non-streaming message
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

    # Test 4: Tool calling with streaming
    print("\n4. Testing tool calling with streaming...")
    result = assistant.chat("Calculate 15 + 27 + 33", stream=True)
    print(f"   Result type: {type(result)}")
    print("   Streaming output: ", end="")
    for chunk in result:
        print(chunk, end="", flush=True)
    print()

    print("\n" + "=" * 60)
    print("✅ All tests completed successfully!")
    print("=" * 60)


def test_chat_completions_fallback():
    """Test fallback to Chat Completions API"""
    print("\n" + "=" * 60)
    print("Testing Chat Completions API Fallback")
    print("=" * 60)

    # Disable Responses API
    os.environ["USE_RESPONSES_API"] = "false"

    # Re-import to get fresh instance
    import importlib
    import assistant_v2_core

    importlib.reload(assistant_v2_core)
    from assistant_v2_core import EchoesAssistantV2

    assistant = EchoesAssistantV2(
        enable_streaming=False, enable_tools=True, enable_status=False
    )

    print(
        f"\n✓ Assistant initialized with Responses API: {assistant.use_responses_api}"
    )

    # Test simple message
    print("\n1. Testing simple message with Chat Completions API...")
    result = assistant.chat("Hello! How are you?", stream=False)
    print(
        f"   Result: {result[:100]}..." if len(result) > 100 else f"   Result: {result}"
    )
    print(f"   Type: {type(result)}")

    print("\n✅ Fallback to Chat Completions API works!")


if __name__ == "__main__":
    test_responses_api()
    test_chat_completions_fallback()
