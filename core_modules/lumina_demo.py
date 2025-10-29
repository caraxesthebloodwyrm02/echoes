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
Lumina Demo - Showcase Lumina's Capabilities

Demonstrates:
1. Codebase organization and smart file management
2. Workflow analysis and automation improvements
3. Code refactoring and upgrades
4. Interactive assistance
"""

import asyncio
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from app.core.lumina import get_lumina

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables
load_dotenv()


async def demo_initialization():
    """Demo 1: Lumina Initialization."""
    print("\n" + "=" * 70)
    print("DEMO 1: Lumina Initialization")
    print("=" * 70 + "\n")

    # Initialize Lumina
    lumina = get_lumina(
        name="Lumina",
        user_config_path=None,  # Auto-discover
        mcp_config_path=None,  # Auto-discover
    )

    # Show stats
    stats = lumina.get_stats()
    print("\n📊 Lumina Statistics:")
    for key, value in stats.items():
        print(f"   {key}: {value}")

    return lumina


async def demo_codebase_organization(lumina):
    """Demo 2: Intelligent Codebase Organization."""
    print("\n" + "=" * 70)
    print("DEMO 2: Intelligent Codebase Organization")
    print("=" * 70 + "\n")

    project_root = Path(__file__).parent.parent

    print(f"📁 Analyzing project: {project_root}\n")

    # Analyze and organize
    result = await lumina.organize_codebase(
        str(project_root),
        dry_run=True,  # Safe preview mode
    )

    print(f"\n✅ Status: {result['status']}")
    print("📋 Organization Plan:\n")
    print(result["plan"][:500] + "..." if len(result["plan"]) > 500 else result["plan"])


async def demo_workflow_analysis(lumina):
    """Demo 3: Analyze Existing Automation Workflows."""
    print("\n" + "=" * 70)
    print("DEMO 3: Automation Workflow Analysis")
    print("=" * 70 + "\n")

    project_root = Path(__file__).parent.parent

    print(f"🔄 Analyzing workflows in: {project_root}\n")

    # Analyze workflows
    result = await lumina.analyze_workflows(str(project_root))

    print(f"\n✅ Status: {result['status']}")
    print("📊 Workflow Analysis:\n")
    print(result["analysis"][:500] + "..." if len(result["analysis"]) > 500 else result["analysis"])


async def demo_codebase_upgrade(lumina):
    """Demo 4: Plan Codebase Upgrades."""
    print("\n" + "=" * 70)
    print("DEMO 4: Codebase Upgrade Planning")
    print("=" * 70 + "\n")

    project_root = Path(__file__).parent.parent

    # Plan dependency upgrade
    print("📦 Planning dependency upgrades...\n")

    result = await lumina.upgrade_codebase(
        str(project_root),
        upgrade_type="dependencies",
    )

    print(f"\n✅ Status: {result['status']}")
    print("📋 Upgrade Plan:\n")
    print(result["plan"][:500] + "..." if len(result["plan"]) > 500 else result["plan"])


async def demo_interactive_chat(lumina):
    """Demo 5: Interactive Chat with Lumina."""
    print("\n" + "=" * 70)
    print("DEMO 5: Interactive Chat")
    print("=" * 70 + "\n")

    questions = [
        "What are the key components of this automation framework?",
        "How can I improve code organization in this project?",
        "What automation tasks are available?",
    ]

    for i, question in enumerate(questions, 1):
        print(f"\n[Q{i}] {question}")
        response = lumina.chat(question)
        print(f"[Lumina] {response[:300]}..." if len(response) > 300 else f"[Lumina] {response}")


async def demo_smart_refactor(lumina):
    """Demo 6: Smart Code Refactoring."""
    print("\n" + "=" * 70)
    print("DEMO 6: Smart Code Refactoring")
    print("=" * 70 + "\n")

    # Example: Refactor a test file
    test_file = project_root / "tests" / "test_assistant.py"

    if test_file.exists():
        print(f"🔨 Analyzing: {test_file}\n")

        result = await lumina.smart_refactor(
            str(test_file),
            refactor_goal="Improve test coverage and add docstrings",
        )

        print(f"\n✅ Status: {result['status']}")
        print("📝 Refactoring Result:\n")
        print(result["result"][:400] + "..." if len(result["result"]) > 400 else result["result"])
    else:
        print("Test file not found, skipping refactoring demo")


async def main():
    """Run all demos."""
    print("\n" + "=" * 70)
    print("✨ LUMINA - ADVANCED AGENTIC ASSISTANT DEMO ✨")
    print("=" * 70)

    try:
        # Check if GITHUB_TOKEN is set
        if not os.environ.get("GITHUB_TOKEN"):
            print("\n⚠️  WARNING: GITHUB_TOKEN not set.")
            print("Some features may be limited. Set it in .env file.\n")

        # Run demos
        lumina = await demo_initialization()

        input("\n▶ Press Enter to continue to Demo 2 (Codebase Organization)...")
        await demo_codebase_organization(lumina)

        input("\n▶ Press Enter to continue to Demo 3 (Workflow Analysis)...")
        await demo_workflow_analysis(lumina)

        input("\n▶ Press Enter to continue to Demo 4 (Upgrade Planning)...")
        await demo_codebase_upgrade(lumina)

        input("\n▶ Press Enter to continue to Demo 5 (Interactive Chat)...")
        await demo_interactive_chat(lumina)

        input("\n▶ Press Enter to continue to Demo 6 (Smart Refactoring)...")
        await demo_smart_refactor(lumina)

        # Final stats
        print("\n" + "=" * 70)
        print("📊 Final Session Statistics")
        print("=" * 70)
        stats = lumina.get_stats()
        for key, value in stats.items():
            print(f"   {key}: {value}")

        print("\n" + "=" * 70)
        print("✅ All demos completed successfully!")
        print("=" * 70 + "\n")

        print("💡 Next Steps:")
        print("  1. Try: python examples/lumina_demo.py")
        print("  2. Use: from app.core import get_lumina")
        print("  3. Interact: lumina = get_lumina(); lumina.chat('Your question')")
        print("  4. Organize: await lumina.organize_codebase('/path/to/project')")
        print("  5. Upgrade: await lumina.upgrade_codebase('/path/to/project')\n")

    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user.\n")
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
