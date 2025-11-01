#!/usr/bin/env python3
"""
Test both Responses API and Chat Completions API
"""
import os

# Test with Chat Completions API (fallback)
os.environ["USE_RESPONSES_API"] = "false"

from assistant_v2_core import EchoesAssistantV2

def test_chat_completions():
    print("=" * 60)
    print("Testing Chat Completions API (Fallback)")
    print("=" * 60)
    
    # Create assistant with Chat Completions API
    assistant = EchoesAssistantV2(
        enable_streaming=False,
        enable_tools=True,
        enable_status=False
    )
    
    print(f"\n✓ Assistant initialized with Responses API: {assistant.use_responses_api}")
    
    # Test 1: Simple message
    print("\n1. Testing simple message...")
    result = assistant.chat("Hello! Say 'Chat Completions API works!' if you can read this.", stream=False)
    print(f"   Result: {result}")
    print(f"   Type: {type(result)}")
    
    # Test 2: Tool calling
    print("\n2. Testing tool calling...")
    result = assistant.chat("What is 15 * 27?", stream=False)
    print(f"   Result: {result}")
    print(f"   Type: {type(result)}")
    
    # Test 3: Streaming
    print("\n3. Testing streaming...")
    result = assistant.chat("Write a short poem about AI", stream=True)
    print(f"   Result type: {type(result)}")
    print("   Streaming output: ", end="")
    for chunk in result:
        print(chunk, end='', flush=True)
    print()
    
    print("\n✅ Chat Completions API test completed!")

if __name__ == "__main__":
    test_chat_completions()
