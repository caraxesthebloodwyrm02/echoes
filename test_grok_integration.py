#!/usr/bin/env python3
"""
Test script for Grok integration in EchoesAI.

This script demonstrates how to use Grok models through the intelligent client.
"""

import asyncio
import os
from core.ai.intelligent_openai_client import IntelligentOpenAIClient


async def test_grok_integration():
    """Test Grok model integration."""
    print("🔬 Testing Grok Integration with EchoesAI")

    # Check if xAI API key is available
    if not os.getenv("XAI_API_KEY"):
        print("❌ XAI_API_KEY environment variable not set")
        print("   Please set your xAI API key to test Grok integration:")
        print("   export XAI_API_KEY='your-xai-api-key'")
        return

    try:
        # Create and initialize the intelligent client
        print("🚀 Initializing intelligent client...")
        client = IntelligentOpenAIClient()
        await client.initialize()

        print(f"✅ Client initialized with {len(client.active_clients)} providers")

        # Test Grok-beta
        print("\n🤖 Testing Grok-beta model...")
        response = await client.chat_completion(
            messages=[
                {"role": "system", "content": "You are Grok, a helpful AI built by xAI."},
                {"role": "user", "content": "Hello! Can you tell me about yourself in one sentence?"}
            ],
            model="grok-beta",
            temperature=0.7,
            max_tokens=100
        )

        if response and "choices" in response:
            content = response["choices"][0]["message"]["content"]
            print(f"📝 Grok-beta response: {content}")
        else:
            print("❌ No valid response from Grok-beta")

        # Test Grok-vision-beta (text-only for now)
        print("\n🖼️  Testing Grok-vision-beta model...")
        response = await client.chat_completion(
            messages=[
                {"role": "system", "content": "You are Grok, a helpful AI built by xAI."},
                {"role": "user", "content": "What's the meaning of life according to xAI's philosophy?"}
            ],
            model="grok-vision-beta",
            temperature=0.8,
            max_tokens=150
        )

        if response and "choices" in response:
            content = response["choices"][0]["message"]["content"]
            print(f"📝 Grok-vision-beta response: {content}")
        else:
            print("❌ No valid response from Grok-vision-beta")

        # Get client status
        status = client.get_friendly_status()
        print(f"\n📊 Client Status: {status}")

        # Close the client
        await client.close()
        print("🛑 Client closed successfully")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Set up logging
    import logging
    logging.basicConfig(level=logging.INFO)

    # Run the test
    asyncio.run(test_grok_integration())
