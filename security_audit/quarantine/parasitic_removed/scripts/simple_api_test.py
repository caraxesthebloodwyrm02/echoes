#!/usr/bin/env python3
"""
Simple test client for Archer Framework FastAPI API
"""


import requests


def test_api():
    """Test the Archer Framework API"""
    base_url = "http://localhost:8001"

    print("🌐 Testing Archer Framework FastAPI API")
    print("=" * 50)

    # Test 1: Root endpoint
    print("\n1. Testing root endpoint...")
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success: {data.get('message', 'No message')}")
        else:
            print(f"   ❌ Failed: Status {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Test 2: Metrics endpoint
    print("\n2. Testing metrics endpoint...")
    try:
        response = requests.get(f"{base_url}/metrics")
        if response.status_code == 200:
            data = response.json()
            print(
                f"   ✅ Success: {data['total_messages']} messages, {data['active_communicators']} communicators"
            )
        else:
            print(f"   ❌ Failed: Status {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Test 3: Send message endpoint
    print("\n3. Testing send message endpoint...")
    try:
        message_data = {
            "content": "Hello from Python test client!",
            "receiver": "api_server",
            "message_type": "network",
            "priority": 8,
            "metadata": {"test": True},
        }

        response = requests.post(
            f"{base_url}/send-message",
            json=message_data,
            headers={"Content-Type": "application/json"},
        )

        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success: {data['success']}")
            print(f"   📝 Message: {data['message']}")
            print(f"   ⏱️  Response Time: {data['response_time']:.4f}s")
            print(f"   🆔 Message ID: {data['message_id'][:8]}...")
        else:
            print(f"   ❌ Failed: Status {response.status_code}")
            print(f"   📝 Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Test 4: List communicators
    print("\n4. Testing communicators endpoint...")
    try:
        response = requests.get(f"{base_url}/communicators")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success: {data['total']} communicators")
            for comm in data["communicators"][:3]:  # Show first 3
                print(f"      • {comm['type']} - Active: {comm['is_active']}")
        else:
            print(f"   ❌ Failed: Status {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Test 5: Psychological analysis
    print("\n5. Testing psychological analysis...")
    try:
        response = requests.post(f"{base_url}/test-psychological-analysis")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success: Analyzed {data['total_tested']} messages")
            for i, result in enumerate(data["test_results"][:2], 1):
                metadata = result.get("metadata", {})
                print(f"      {i}. Tone: {metadata.get('emotional_tone', 'unknown')}")
        else:
            print(f"   ❌ Failed: Status {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    print("\n🎯 API Test Complete!")
    print("\n💡 Access the interactive API docs at: http://localhost:8001/docs")


if __name__ == "__main__":
    test_api()
