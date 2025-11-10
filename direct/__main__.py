#!/usr/bin/env python3
"""
EchoesAI Direct Connection Main Entry Point
Run with: python -m Echoes.direct
"""

import asyncio
import sys
import os
from datetime import datetime

# Add echoes root to path
echoes_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, echoes_root)

from . import get_direct_connection, test_direct_connection


async def demo_direct_connection():
    """Demonstrate direct connection capabilities."""
    print("🚀 EchoesAI Direct Connection Demo")
    print("=" * 50)

    try:
        # Initialize direct connection
        connection = get_direct_connection()

        # Show connection status
        status = connection.get_connection_status()
        print("📊 Connection Status:")
        for key, value in status.items():
            if key != "api_key":
                print(f"   • {key.replace('_', ' ').title()}: {value}")

        print("\n🧪 Testing Direct Connection...")
        success = await test_direct_connection()

        if success:
            print("✅ Direct connection verified")

            # Test authentic I/O properties
            print("\n🎯 Testing Authentic I/O Properties...")

            test_messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {
                    "role": "user",
                    "content": "Explain quantum computing in one sentence.",
                },
            ]

            response = await connection.direct_chat(
                messages=test_messages, max_tokens=50, temperature=0.7
            )

            print(f"✅ Authentic Response: {response['content']}")
            print(f"📊 Token Usage: {response['usage']['total_tokens']}")
            print(f"🤖 Model: {response['model']}")
            print(f"🔗 Direct Connection: {response['direct_connection']}")
            print(f"🚫 Middleware Bypassed: {response['middleware_bypassed']}")

            # Test streaming
            print("\n🌊 Testing Direct Streaming...")
            print("Stream: ", end="", flush=True)

            async for chunk in connection.direct_stream(
                messages=[{"role": "user", "content": "Count to 5"}], max_tokens=20
            ):
                print(chunk["content"], end="", flush=True)

            print("\n✅ Direct streaming successful")

            return True

        else:
            print("❌ Direct connection test failed")
            return False

    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return False


async def main():
    """Main direct connection function."""
    print("🚀 EchoesAI Direct Connection System")
    print("=" * 60)
    print("Zero Middleware - Authentic Input-Output Properties")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("")

    # Run demo
    success = await demo_direct_connection()

    print("\n" + "=" * 60)
    if success:
        print("🎉 DIRECT CONNECTION ESTABLISHED!")
        print("✅ Zero middleware interference")
        print("✅ Authentic input-output properties")
        print("✅ Direct OpenAI API connection")
        print("✅ Unmodified request/response flow")
        print("✅ Raw token tracking")
        print("\n🎯 EchoesAI is now operating with direct connection!")
    else:
        print("❌ DIRECT CONNECTION FAILED!")
        print("⚠️ Unable to establish zero-middleware connection")
        print("🔧 Check error messages above")

    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
