# MIT License
#
# Copyright (c) 2024 Echoes Project
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
Interactive demo: Chat with the AI Assistant.

This script provides an interactive command-line interface to chat with
the AI assistant. Type 'quit' or 'exit' to end the session.
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

from app.core.assistant import create_assistant

# Load environment variables
load_dotenv()


def print_banner():
    """Print welcome banner."""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                   AI ASSISTANT DEMO                          ║
║                                                              ║
║  Type your messages and press Enter to chat.                ║
║  Commands:                                                   ║
║    /reset    - Reset conversation                           ║
║    /history  - Show conversation history                    ║
║    /help     - Show this help message                       ║
║    /quit     - Exit the demo                                ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def print_help():
    """Print help message."""
    help_text = """
Available Commands:
  /reset    - Reset the conversation (clear history)
  /history  - Display the conversation history
  /help     - Show this help message
  /quit     - Exit the interactive demo

Tips:
  - Ask questions naturally
  - The assistant remembers context from previous messages
  - Use /reset if you want to start a fresh conversation
    """
    print(help_text)


def display_history(assistant):
    """Display conversation history."""
    history = assistant.get_history()

    if not history:
        print("\n📭 No conversation history yet.\n")
        return

    print("\n" + "=" * 60)
    print("CONVERSATION HISTORY")
    print("=" * 60)

    for i, msg in enumerate(history, 1):
        role = msg["role"].upper()
        content = msg["content"]

        # Format based on role
        if role == "SYSTEM":
            print(f"\n[{i}] 🔧 SYSTEM:")
            print(f"    {content[:100]}..." if len(content) > 100 else f"    {content}")
        elif role == "USER":
            print(f"\n[{i}] 👤 YOU:")
            print(f"    {content}")
        elif role == "ASSISTANT":
            print(f"\n[{i}] 🤖 ASSISTANT:")
            print(f"    {content}")
        elif role == "TOOL":
            print(f"\n[{i}] 🔧 TOOL:")
            print(f"    {content[:100]}..." if len(content) > 100 else f"    {content}")

    print("\n" + "=" * 60 + "\n")


def main():
    """Run interactive demo."""
    # Check if GITHUB_TOKEN is set
    if not os.environ.get("GITHUB_TOKEN"):
        print("\n⚠️  ERROR: GITHUB_TOKEN environment variable is not set.")
        print("Please set it in your .env file or environment.")
        print("Get your token at: https://github.com/settings/tokens\n")
        return

    # Print banner
    print_banner()

    # Create assistant with a friendly system prompt
    system_prompt = """
    You are a helpful, friendly AI assistant. You provide clear, concise,
    and accurate responses. You're knowledgeable about programming,
    automation, and general topics. Be conversational and helpful.
    """

    try:
        print("🔄 Initializing AI Assistant...")
        assistant = create_assistant(system_prompt=system_prompt)
        print("✅ Assistant ready!\n")
    except Exception as e:
        print(f"❌ Failed to initialize assistant: {e}")
        return

    # Main interaction loop
    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()

            # Handle empty input
            if not user_input:
                continue

            # Handle commands
            if user_input.lower() in ["/quit", "/exit", "quit", "exit"]:
                print("\n👋 Goodbye! Thanks for chatting.\n")
                break

            elif user_input.lower() == "/help":
                print_help()
                continue

            elif user_input.lower() == "/reset":
                assistant.reset(keep_system_prompt=True)
                print("\n🔄 Conversation reset. Starting fresh!\n")
                continue

            elif user_input.lower() == "/history":
                display_history(assistant)
                continue

            # Regular chat message
            print("🤖 Assistant: ", end="", flush=True)

            try:
                response = assistant.chat(user_input)
                print(response)
            except Exception as e:
                print(f"\n❌ Error: {e}")
                print("Please try again or type /help for assistance.")

            print()  # Empty line for readability

        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Goodbye!\n")
            break
        except EOFError:
            print("\n\n👋 Goodbye!\n")
            break
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            print("Type /quit to exit or continue chatting.\n")


if __name__ == "__main__":
    main()
