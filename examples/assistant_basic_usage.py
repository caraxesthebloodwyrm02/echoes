"""
Basic usage examples for the AI Assistant module.

This script demonstrates:
1. Simple conversation
2. System prompts
3. Conversation history
4. Resetting conversations
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.assistant import Assistant, create_assistant
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def example_basic_conversation():
    """Example 1: Basic conversation with the assistant."""
    print("\n" + "=" * 60)
    print("Example 1: Basic Conversation")
    print("=" * 60 + "\n")

    # Create assistant
    assistant = create_assistant()

    # Send a message and get response
    response = assistant.chat("What is the capital of France?")
    print("User: What is the capital of France?")
    print(f"Assistant: {response}\n")

    # Continue the conversation
    response = assistant.chat("What is its population?")
    print("User: What is its population?")
    print(f"Assistant: {response}\n")


def example_with_system_prompt():
    """Example 2: Using a system prompt to set assistant behavior."""
    print("\n" + "=" * 60)
    print("Example 2: System Prompt")
    print("=" * 60 + "\n")

    # Create assistant with a system prompt
    system_prompt = (
        "You are a helpful coding assistant specialized in Python. "
        "Provide concise, practical answers with code examples when relevant."
    )
    assistant = create_assistant(system_prompt=system_prompt)

    response = assistant.chat("How do I read a JSON file in Python?")
    print("User: How do I read a JSON file in Python?")
    print(f"Assistant: {response}\n")


def example_conversation_history():
    """Example 3: Viewing conversation history."""
    print("\n" + "=" * 60)
    print("Example 3: Conversation History")
    print("=" * 60 + "\n")

    assistant = create_assistant()

    # Have a short conversation
    assistant.chat("Hello! My name is Alice.")
    assistant.chat("What's my name?")

    # Get and display history
    history = assistant.get_history()
    print("Conversation History:")
    for i, msg in enumerate(history, 1):
        role = msg["role"].capitalize()
        content = msg["content"][:100] + "..." if len(msg["content"]) > 100 else msg["content"]
        print(f"{i}. [{role}] {content}")
    print()


def example_reset_conversation():
    """Example 4: Resetting conversation while keeping system prompt."""
    print("\n" + "=" * 60)
    print("Example 4: Reset Conversation")
    print("=" * 60 + "\n")

    system_prompt = "You are a helpful assistant that speaks like a pirate."
    assistant = create_assistant(system_prompt=system_prompt)

    # First conversation
    response1 = assistant.chat("Hello!")
    print("First conversation:")
    print("User: Hello!")
    print(f"Assistant: {response1}\n")

    # Reset (keeping system prompt)
    assistant.reset(keep_system_prompt=True)

    # New conversation - should still speak like a pirate
    response2 = assistant.chat("Tell me about the weather.")
    print("After reset (keeping system prompt):")
    print("User: Tell me about the weather.")
    print(f"Assistant: {response2}\n")


def example_custom_parameters():
    """Example 5: Using custom model parameters."""
    print("\n" + "=" * 60)
    print("Example 5: Custom Parameters")
    print("=" * 60 + "\n")

    # Create assistant with lower temperature for more deterministic responses
    assistant = Assistant(
        model="openai/gpt-4.1",
        temperature=0.3,  # Lower temperature = more focused/deterministic
        top_p=0.9,
    )

    response = assistant.chat("Generate a random number between 1 and 10.")
    print("User: Generate a random number between 1 and 10.")
    print(f"Assistant (temp=0.3): {response}\n")


def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("AI ASSISTANT - BASIC USAGE EXAMPLES")
    print("=" * 60)

    try:
        # Check if GITHUB_TOKEN is set
        if not os.environ.get("GITHUB_TOKEN"):
            print("\n⚠️  ERROR: GITHUB_TOKEN environment variable is not set.")
            print("Please set it in your .env file or environment.")
            print("Get your token at: https://github.com/settings/tokens\n")
            return

        # Run examples
        example_basic_conversation()
        example_with_system_prompt()
        example_conversation_history()
        example_reset_conversation()
        example_custom_parameters()

        print("\n" + "=" * 60)
        print("All examples completed successfully!")
        print("=" * 60 + "\n")

    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
