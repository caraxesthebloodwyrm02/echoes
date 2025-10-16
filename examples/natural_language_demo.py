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
Natural Language Interface Demo

Demonstrates executing tasks via simple natural language requests.
"""

import asyncio
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from app.core import execute_task

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables
load_dotenv()


async def demo_basic_execution():
    """Demo 1: Basic natural language execution."""
    print("\n" + "=" * 70)
    print("DEMO 1: Basic Natural Language Execution")
    print("=" * 70 + "\n")

    request = (
        "Use assistant to organize the codebase with goal to improve maintainability"
    )

    print(f"Request: {request}\n")

    result = await execute_task(
        request,
        project_root=str(project_root),
        dry_run=True,  # Safe simulation
    )

    print(f"\nSuccess: {result.success}")
    print(f"Duration: {result.duration}")


async def demo_multiple_requests():
    """Demo 2: Multiple different requests."""
    print("\n" + "=" * 70)
    print("DEMO 2: Multiple Task Types")
    print("=" * 70 + "\n")

    requests = [
        "Use assistant to analyze workflows with goal to find automation opportunities",
        "Use assistant to refactor code with goal to improve readability",
        "Use assistant to upgrade dependencies with goal to use latest versions",
    ]

    for i, request in enumerate(requests, 1):
        print(f"\n--- Request {i} ---")
        print(f"{request}\n")

        result = await execute_task(
            request,
            project_root=str(project_root),
            dry_run=True,
        )

        print(f"Status: {'✅' if result.success else '❌'}")
        print(f"Phases: {len(result.completed_phases)}")

        input("\nPress Enter to continue...")


async def demo_with_constraints():
    """Demo 3: Request with constraints."""
    print("\n" + "=" * 70)
    print("DEMO 3: Request with Constraints")
    print("=" * 70 + "\n")

    request = """
    Use assistant to organize the codebase with goal to improve structure.
    Only touch Python files. Don't modify tests. Must preserve existing functionality.
    """

    print(f"Request: {request}\n")

    result = await execute_task(
        request,
        project_root=str(project_root),
        dry_run=True,
    )

    print(f"\nConstraints detected: {result.plan.risks}")


async def demo_interactive():
    """Demo 4: Interactive mode."""
    print("\n" + "=" * 70)
    print("DEMO 4: Interactive Mode")
    print("=" * 70 + "\n")

    print("Enter natural language requests (or 'quit' to exit):\n")

    while True:
        request = input("You: ").strip()

        if request.lower() in ["quit", "exit", "q"]:
            print("\nGoodbye!")
            break

        if not request:
            continue

        print()
        result = await execute_task(
            request,
            project_root=str(project_root),
            dry_run=True,
        )

        print(f"\nLumina: {result.final_output[:300]}...")
        print()


async def main():
    """Run all demos."""
    print("\n" + "=" * 70)
    print("✨ NATURAL LANGUAGE INTERFACE DEMO ✨")
    print("=" * 70)

    try:
        # Check if GITHUB_TOKEN is set
        if not os.environ.get("GITHUB_TOKEN"):
            print("\n⚠️  WARNING: GITHUB_TOKEN not set.")
            print("Some features may be limited. Set it in .env file.\n")

        # Run demos
        await demo_basic_execution()

        input("\n▶ Press Enter to continue to Demo 2...")
        await demo_multiple_requests()

        input("\n▶ Press Enter to continue to Demo 3...")
        await demo_with_constraints()

        input("\n▶ Press Enter to continue to Demo 4 (Interactive)...")
        await demo_interactive()

        print("\n" + "=" * 70)
        print("✅ All demos completed!")
        print("=" * 70 + "\n")

        print("💡 Usage in your code:")
        print(
            """
from app.core import execute_task

result = await execute_task(
    "Use assistant to organize the codebase with goal to improve maintainability",
    dry_run=True
)

print(result.final_output)
        """
        )

    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user.\n")
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
