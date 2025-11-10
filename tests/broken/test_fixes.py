#!/usr/bin/env python3
"""
Test the fixes for model selection and context length issues
"""

import os
import sys

sys.path.append(os.path.dirname(__file__))

from assistant import IntelligentAssistant


def test_fixes():
    """Test the fixes."""

    print("🧪 Testing Model Selection and Context Fixes")
    print("=" * 60)

    # Initialize assistant
    assistant = IntelligentAssistant()

    # Test 1: Check available models
    print("\n🔍 Test 1: Available Models")
    print("-" * 40)
    available = assistant.model_capabilities.keys()
    print(f"Available models: {list(available)}")

    # Test 2: Complex query (should use gpt-4, not o3)
    print("\n🔍 Test 2: Complex Query Model Selection")
    print("-" * 40)
    query = "Explain quantum computing in detail"
    response = assistant.chat(query)
    actual_model = assistant.get_last_used_model()
    print(f"Query: {query}")
    print(f"Model used: {actual_model}")
    print(f"Has footer: {'Auto-selected' in response}")

    # Test 3: Context length management
    print("\n🔍 Test 3: Context Length Management")
    print("-" * 40)
    # Simulate a long conversation
    long_message = "This is a very long message " * 100
    try:
        response = assistant.chat(long_message + " What do you think?")
        print("✅ Long message handled without context length error")
    except Exception as e:
        print(f"❌ Error with long message: {e}")

    # Test 4: Local intelligence improvement
    print("\n🔍 Test 4: Local Intelligence Fallback")
    print("-" * 40)
    # Disable OpenAI to test local fallback
    assistant.disable_openai()

    test_queries = [
        "I want to refactor my code",
        "Explain the chat function",
        "What is the meaning of life?",
    ]

    for query in test_queries:
        response = assistant.chat(query)
        print(f"Query: {query}")
        print(f"Response: {response[:100]}...")
        print()

    print("🎉 All tests completed!")


if __name__ == "__main__":
    test_fixes()
