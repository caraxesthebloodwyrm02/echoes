#!/usr/bin/env python3
"""
Deep debug for Responses API to find root cause of empty responses
"""
import os
import json
from openai import OpenAI

# Set up OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def test_raw_responses_api():
    """Test the Responses API directly to understand the format"""
    print("=" * 60)
    print("Testing Raw Responses API")
    print("=" * 60)

    # Test 1: Minimal request
    print("\n1. Testing minimal request...")
    try:
        response = client.responses.create(
            model="gpt-4o",
            input=[{"role": "user", "type": "message", "content": "Say 'hello'"}],
            max_output_tokens=100,
            stream=False,
        )
        print(f"   Response type: {type(response)}")
        print(f"   Response attributes: {dir(response)}")
        if hasattr(response, "output"):
            print(f"   Output: {response.output}")
        if hasattr(response, "choices"):
            print(f"   Choices: {response.choices}")
    except Exception as e:
        print(f"   Error: {e}")

    # Test 2: Check actual API endpoint
    print("\n2. Testing with different input format...")
    try:
        # Try without type field
        response = client.responses.create(
            model="gpt-4o",
            input=[{"role": "user", "content": "Say 'hello'"}],
            max_output_tokens=100,
            stream=False,
        )
        print(f"   Response: {response}")
    except Exception as e:
        print(f"   Error: {e}")

    # Test 3: Check if responses endpoint exists
    print("\n3. Testing API endpoint availability...")
    try:
        # Try to access the responses endpoint directly
        import httpx

        headers = {"Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}"}
        r = httpx.post(
            "https://api.openai.com/v1/responses",
            headers=headers,
            json={"model": "gpt-4o", "input": "test"},
        )
        print(f"   Status: {r.status_code}")
        print(f"   Response: {r.text[:500]}...")
    except Exception as e:
        print(f"   Error: {e}")

    # Test 4: Check OpenAI client version
    print("\n4. Checking OpenAI library version...")
    try:
        import openai

        print(f"   OpenAI version: {openai.__version__}")

        # Check if responses method exists
        if hasattr(client, "responses"):
            print("   ✓ Client has responses attribute")
            print(f"   Responses attributes: {dir(client.responses)}")
        else:
            print("   ✗ Client does not have responses attribute")

        # Check available methods
        print(f"   Client methods: {[m for m in dir(client) if not m.startswith('_')]}")
    except Exception as e:
        print(f"   Error: {e}")


if __name__ == "__main__":
    test_raw_responses_api()
