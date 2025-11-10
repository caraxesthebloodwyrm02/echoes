#!/usr/bin/env python3
"""
FastAPI Archer Framework Client

This client script demonstrates how to interact with the Archer Framework
through the FastAPI web interface.
"""

import time
from typing import Any

import requests


class ArcherAPIClient:
    """Client for interacting with Archer Framework API"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()

    def send_message(
        self,
        content: Any,
        receiver: str,
        message_type: str = "network",
        sender: str = "api_client",
        priority: int = 5,
        metadata: dict[str, Any] = None,
    ) -> dict[str, Any]:
        """Send a message through the API"""
        url = f"{self.base_url}/send-message"

        payload = {
            "content": content,
            "sender": sender,
            "receiver": receiver,
            "message_type": message_type,
            "priority": priority,
            "metadata": metadata or {},
        }

        response = self.session.post(url, json=payload)
        response.raise_for_status()
        return response.json()

    def get_metrics(self) -> dict[str, Any]:
        """Get performance metrics"""
        url = f"{self.base_url}/metrics"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def get_history(self, limit: int = 50, offset: int = 0) -> dict[str, Any]:
        """Get message history"""
        url = f"{self.base_url}/history"
        params = {"limit": limit, "offset": offset}
        response = self.session.get(url, params)
        response.raise_for_status()
        return response.json()

    def register_communicator(
        self, communicator_type: str, config: dict[str, Any] = None
    ) -> dict[str, Any]:
        """Register a new communicator"""
        url = f"{self.base_url}/register-communicator"

        payload = {"communicator_type": communicator_type, "config": config or {}}

        response = self.session.post(url, json=payload)
        response.raise_for_status()
        return response.json()

    def list_communicators(self) -> dict[str, Any]:
        """List all active communicators"""
        url = f"{self.base_url}/communicators"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def test_psychological_analysis(self) -> dict[str, Any]:
        """Test psychological communication analysis"""
        url = f"{self.base_url}/test-psychological-analysis"
        response = self.session.post(url)
        response.raise_for_status()
        return response.json()

    def test_physics_simulation(self) -> dict[str, Any]:
        """Test physics signal transmission simulation"""
        url = f"{self.base_url}/test-physics-simulation"
        response = self.session.post(url)
        response.raise_for_status()
        return response.json()


def test_basic_communication(client: ArcherAPIClient):
    """Test basic communication through the API"""
    print("📡 Testing Basic Communication")
    print("-" * 35)

    test_messages = [
        {
            "content": "Hello from FastAPI client!",
            "receiver": "api_server",
            "message_type": "network",
            "priority": 8,
        },
        {
            "content": "IPC test message",
            "receiver": "process_handler",
            "message_type": "interprocess",
            "priority": 6,
        },
        {
            "content": "I appreciate your help with this integration",
            "receiver": "assistant",
            "message_type": "psychological",
            "priority": 7,
        },
    ]

    for i, msg in enumerate(test_messages, 1):
        print(f"\n📤 Sending message {i}:")

        try:
            result = client.send_message(**msg)

            print(f"   ✅ Success: {result['success']}")
            print(f"   📝 Message: {result['message']}")
            print(f"   🆔 ID: {result['message_id'][:8]}...")
            print(f"   ⏱️  Response Time: {result['response_time']:.4f}s")

            if result["metadata"]:
                print(f"   📊 Metadata: {result['metadata']}")

        except Exception as e:
            print(f"   ❌ Error: {e}")


def test_performance_monitoring(client: ArcherAPIClient):
    """Test performance monitoring capabilities"""
    print("\n📊 Testing Performance Monitoring")
    print("-" * 40)

    # Send multiple messages to generate metrics
    print("🔄 Sending multiple messages for metrics...")

    for i in range(10):
        client.send_message(
            content=f"Performance test message {i+1}",
            receiver="metrics_collector",
            message_type="network",
            priority=5,
        )
        time.sleep(0.1)

    # Get metrics
    print("\n📈 Current Performance Metrics:")
    try:
        metrics = client.get_metrics()

        print(f"   📨 Total Messages: {metrics['total_messages']}")
        print(f"   🎯 Active Communicators: {metrics['active_communicators']}")

        for key, value in metrics["metrics"].items():
            if "avg_response" in key:
                print(f"   ⏱️  {key}: {value:.4f}s")
            elif "success_rate" in key:
                print(f"   ✅ {key}: {value:.2%}")
            else:
                print(f"   📊 {key}: {value:.4f}")

    except Exception as e:
        print(f"   ❌ Error getting metrics: {e}")


def test_psychological_features(client: ArcherAPIClient):
    """Test psychological communication features"""
    print("\n🧠 Testing Psychological Communication")
    print("-" * 42)

    try:
        result = client.test_psychological_analysis()

        print(f"📝 Analyzed {result['total_tested']} messages:")

        for i, test_result in enumerate(result["test_results"], 1):
            content = test_result["content"]
            success = test_result["success"]
            metadata = test_result.get("metadata", {})

            print(f"\n   {i}. '{content[:40]}...'")
            print(f"      ✅ Success: {success}")

            if metadata:
                tone = metadata.get("emotional_tone", "unknown")
                clarity = metadata.get("clarity_score", 0)
                empathy = metadata.get("empathy_score", 0)

                print(f"      🎭 Tone: {tone}")
                print(f"      📊 Clarity: {clarity:.2f}")
                print(f"      💝 Empathy: {empathy:.2f}")

    except Exception as e:
        print(f"   ❌ Error testing psychological features: {e}")


def test_physics_simulation(client: ArcherAPIClient):
    """Test physics signal transmission simulation"""
    print("\n📡 Testing Physics Signal Simulation")
    print("-" * 42)

    try:
        result = client.test_physics_simulation()

        print(f"🌊 Tested {result['total_scenarios']} scenarios:")

        for i, sim_result in enumerate(result["simulation_results"], 1):
            scenario = sim_result["scenario"]
            success = sim_result["success"]
            metadata = sim_result.get("metadata", {})

            print(f"\n   {i}. {scenario['medium'].upper()} medium:")
            print(f"      ✅ Success: {success}")

            if metadata:
                strength = metadata.get("signal_strength", 0)
                attenuation = metadata.get("attenuation", 0)

                print(f"      💪 Signal Strength: {strength:.3f}")
                print(f"      📉 Attenuation: {attenuation:.2f} dB")
                print(f"      📊 Frequency: {scenario['frequency']:.2e} Hz")
                print(f"      📍 Distance: {scenario['distance']} m")

    except Exception as e:
        print(f"   ❌ Error testing physics simulation: {e}")


def test_communicator_management(client: ArcherAPIClient):
    """Test communicator registration and listing"""
    print("\n🔧 Testing Communicator Management")
    print("-" * 38)

    try:
        # List current communicators
        print("📋 Current communicators:")
        communicators = client.list_communicators()

        for comm in communicators["communicators"]:
            print(
                f"   • {comm['type']} ({comm['class']}) - Active: {comm['is_active']}"
            )

        # Register a new communicator
        print("\n➕ Registering custom psychological communicator:")
        result = client.register_communicator(
            communicator_type="psychological",
            config={"style": "assertive", "ei_level": 0.9},
        )

        print(f"   ✅ {result['message']}")

        # List updated communicators
        print(f"\n📋 Updated communicators ({communicators['total'] + 1} total):")
        updated = client.list_communicators()

        for comm in updated["communicators"]:
            print(
                f"   • {comm['type']} ({comm['class']}) - Active: {comm['is_active']}"
            )

    except Exception as e:
        print(f"   ❌ Error managing communicators: {e}")


def test_message_history(client: ArcherAPIClient):
    """Test message history retrieval"""
    print("\n📚 Testing Message History")
    print("-" * 30)

    try:
        history = client.get_history(limit=10)

        print(f"📊 Retrieved {len(history['messages'])} messages:")
        print(f"   Total messages: {history['total']}")
        print(f"   Has more: {history['has_more']}")

        for i, msg in enumerate(history["messages"][:5], 1):
            print(f"\n   {i}. Message {msg['id'][:8]}...")
            print(f"      📝 Content: {str(msg['content'])[:30]}...")
            print(f"      👤 From: {msg['sender']} → {msg['receiver']}")
            print(f"      🏷️  Type: {msg['message_type']}")
            print(f"      ⭐ Priority: {msg['priority']}")
            print(
                f"      📅 Time: {time.strftime('%H:%M:%S', time.localtime(msg['timestamp']))}"
            )

    except Exception as e:
        print(f"   ❌ Error retrieving history: {e}")


def main():
    """Run all API client tests"""
    print("🌐 Archer Framework FastAPI Client Tests")
    print("=" * 50)

    # Initialize client
    client = ArcherAPIClient()

    # Check if server is running
    try:
        response = requests.get(f"{client.base_url}/", timeout=5)
        if response.status_code != 200:
            print("❌ Server is not responding correctly")
            return
    except requests.exceptions.RequestException:
        print(f"❌ Cannot connect to server at {client.base_url}")
        print("💡 Make sure the FastAPI server is running:")
        print("   python examples/fastapi_archer_integration.py")
        return

    print("✅ Connected to Archer Framework API")
    print()

    # Run tests
    tests = [
        test_basic_communication,
        test_performance_monitoring,
        test_psychological_features,
        test_physics_simulation,
        test_communicator_management,
        test_message_history,
    ]

    for test in tests:
        try:
            test(client)
        except Exception as e:
            print(f"❌ Test failed: {e}")

        print("\n" + "=" * 50 + "\n")

    print("🎉 All API Client Tests Completed!")

    print("\n💡 API Usage Examples:")
    print("   # Send a message")
    print("   curl -X POST http://localhost:8000/send-message \\")
    print('        -H "Content-Type: application/json" \\')
    print('        -d \'{"content": "Hello", "receiver": "server"}\'')
    print()
    print("   # Get metrics")
    print("   curl http://localhost:8000/metrics")
    print()
    print("   # View API docs")
    print("   Open http://localhost:8000/docs in your browser")


if __name__ == "__main__":
    main()
