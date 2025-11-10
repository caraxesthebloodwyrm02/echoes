#!/usr/bin/env python3
"""
Interactive Console for EchoesAssistantV2 with ValueSystem

Run this script to chat with the assistant and see the ValueSystem in action.
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from assistant_v2_core import EchoesAssistantV2


def interactive_chat():
    """Start an interactive chat session with the assistant."""
    print("🤖 Echoes Assistant V2 - Interactive Chat")
    print("=" * 50)
    print("Type 'quit' or 'exit' to end the session")
    print("Type 'stats' to see current value scores")
    print("Type 'help' for more commands")
    print()

    # Initialize assistant with value system enabled
    assistant = EchoesAssistantV2(
        enable_value_system=True,
        enable_tools=False,  # Disable for simpler demo
        enable_rag=False,  # Disable for simpler demo
        enable_streaming=False,
    )

    print("✅ Assistant ready with ValueSystem integration!")
    print(
        "📊 Current values:",
        {
            k: f"{v['score']:.2f}"
            for k, v in assistant.value_system.get_values_summary().items()
        },
    )
    print()

    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()

            if not user_input:
                continue

            # Handle special commands
            if user_input.lower() in ["quit", "exit", "q"]:
                print("👋 Goodbye!")
                break

            elif user_input.lower() == "stats":
                stats = assistant.get_stats()
                print("📊 Assistant Stats:")
                print(f"   Session: {stats['session_id']}")
                print(f"   Messages: {stats['messages']}")
                print(
                    f"   Value System: {'Enabled' if stats['value_system_enabled'] else 'Disabled'}"
                )
                if "value_system" in stats:
                    print("   Current Values:")
                    for value_name, value_data in stats["value_system"].items():
                        print(
                            f"     {value_name.title()}: {value_data['score']:.2f} (weight: {value_data['weight']})"
                        )
                print()

            elif user_input.lower() == "help":
                print("📋 Available Commands:")
                print("   'stats' - Show current value scores and stats")
                print("   'help' - Show this help message")
                print("   'quit'/'exit'/'q' - End the session")
                print("   Any other text - Chat with the assistant")
                print()

            else:
                # Regular chat
                print("🤖 Assistant: ", end="", flush=True)
                response = assistant.chat(user_input, stream=False)

                # Show response
                print(response)

                # Show value scores for this response
                if assistant.enable_value_system and assistant.value_system:
                    scores = assistant.value_system.evaluate_response(response)
                    overall = assistant.value_system.get_overall_score(scores)
                    print("📊 Response Values:")
                    print(
                        f"   Respect: {scores['respect']:.2f}, Accuracy: {scores['accuracy']:.2f}, Helpfulness: {scores['helpfulness']:.2f}"
                    )
                    print(f"   Overall: {overall:.2f}")
                    if overall < 0.6:
                        print(
                            "   ⚠️  Response was automatically improved by ValueSystem"
                        )
                print()

        except KeyboardInterrupt:
            print("\n👋 Session interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            print("Try again or type 'quit' to exit.")
            print()


if __name__ == "__main__":
    interactive_chat()
