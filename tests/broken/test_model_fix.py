#!/usr/bin/env python3
"""
Test script to verify the model selection fix
"""

import os
import sys

sys.path.append(os.path.dirname(__file__))

from assistant import IntelligentAssistant


def test_model_selection_fix():
    """Test that the footer now shows the actual model used."""

    print("🧪 Testing Model Selection Fix")
    print("=" * 50)

    # Initialize assistant
    assistant = IntelligentAssistant()

    # Test queries
    test_queries = [
        "What's the capital of France?",
        "Explain quantum computing in detail",
        "List 3 benefits of exercise",
    ]

    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Test {i}: {query}")
        print("-" * 40)

        try:
            # Get response
            response = assistant.chat(query)

            # Get the actual model used
            actual_model = assistant.get_last_used_model()

            print(f"Response: {response[:100]}...")
            print(f"Actual Model Used: {actual_model}")

            # Check if footer contains the model info
            if "Auto-selected" in response:
                print("✅ Footer shows model selection info")
            else:
                print("⚠️  Footer doesn't show model selection info")

        except Exception as e:
            print(f"❌ Error: {e}")

    print("\n📊 Test Complete!")
    print("The footer should now show the actual model used in each response.")


if __name__ == "__main__":
    test_model_selection_fix()
