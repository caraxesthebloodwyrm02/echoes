#!/usr/bin/env python3
"""
Simple CLI demonstration for the modular Echoes Assistant V2
"""

from echoes.cli import main

if __name__ == "__main__":
    # Demonstrate the ask command
    print("🤖 Echoes Assistant V2 - CLI Demo")
    print("=" * 40)

    try:
        # Use the CLI to ask a question
        main(["ask", "What is modular architecture and why is it important?"])
    except Exception as e:
        print(f"CLI Error: {e}")

    print("\n✅ CLI demonstration complete")
