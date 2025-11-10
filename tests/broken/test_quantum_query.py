#!/usr/bin/env python3
"""
Test quantum computing query to verify model selection
"""

import os
import sys

sys.path.append(os.path.dirname(__file__))

from assistant import IntelligentAssistant


def test_quantum_query():
    """Test quantum computing query for model selection."""

    print("🧪 Testing Quantum Computing Query")
    print("=" * 50)

    # Initialize assistant
    assistant = IntelligentAssistant()

    # Test the quantum query
    query = "Explain quantum computing in detail"
    print(f"Query: {query}")
    print("-" * 50)

    try:
        # Get response
        response = assistant.chat(query)

        # Get the actual model used
        actual_model = assistant.get_last_used_model()

        print(f"Response: {response[:200]}...")
        print(f"Actual Model Used: {actual_model}")

        # Check if it's using an appropriate model
        if actual_model in ["gpt-4", "gpt-4o"]:
            print("✅ Using high-capability model for complex query")
        elif actual_model == "gpt-3.5-turbo":
            print("⚠️  Using standard model - may need complexity analysis adjustment")
        else:
            print(f"❌ Using unexpected model: {actual_model}")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    test_quantum_query()
