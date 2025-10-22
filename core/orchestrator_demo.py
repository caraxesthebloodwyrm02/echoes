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
Orchestrator Demo - High-Level Assistant Interface

Demonstrates the AssistantOrchestrator for seamless multi-model task execution
with automatic routing and management.
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from app.core import (
    AssistantConfig,
    TaskType,
    chat,
    code,
    get_orchestrator,
    plan,
    reason,
)
from automation.core.context import Context
from automation.core.logger import AutomationLogger

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables
load_dotenv()


def demo_convenience_functions():
    """Demo: Super simple convenience functions."""
    print("\n" + "=" * 60)
    print("DEMO 1: Convenience Functions (Easiest Way)")
    print("=" * 60 + "\n")

    print("💬 Just chat:")
    response = chat("What is Python used for?")
    print(f"   {response[:150]}...\n")

    print("💻 Code something:")
    response = code("Write a function to reverse a string")
    print(f"   {response[:150]}...\n")

    print("🧠 Reason through a problem:")
    response = reason("Should I use a list or set for unique values?")
    print(f"   {response[:150]}...\n")

    print("📋 Plan a project:")
    response = plan("I need to build a REST API. What are the steps?")
    print(f"   {response[:150]}...\n")


def demo_task_routing():
    """Demo: Automatic task routing."""
    print("\n" + "=" * 60)
    print("DEMO 2: Intelligent Task Routing")
    print("=" * 60 + "\n")

    orchestrator = get_orchestrator()

    print("📊 Different task types automatically route to best models:\n")

    # Coding task -> Qwen Coder
    print("Task: CODING")
    response = orchestrator.execute_task(
        "Write a binary search function",
        task_type=TaskType.CODING,
    )
    print(f"   Model used: {orchestrator.active_assistant.model_info.name}")
    print(f"   Response: {response[:100]}...\n")

    # Reasoning task -> QwQ
    print("Task: REASONING")
    response = orchestrator.execute_task(
        "Explain why sorting is O(n log n) at best",
        task_type=TaskType.REASONING,
    )
    print(f"   Model used: {orchestrator.active_assistant.model_info.name}")
    print(f"   Response: {response[:100]}...\n")

    # Planning task -> Agentic model
    print("Task: PLANNING")
    response = orchestrator.execute_task(
        "Create a plan to deploy a web application",
        task_type=TaskType.PLANNING,
    )
    print(f"   Model used: {orchestrator.active_assistant.model_info.name}")
    print(f"   Response: {response[:100]}...\n")


def demo_orchestrator_features():
    """Demo: Orchestrator advanced features."""
    print("\n" + "=" * 60)
    print("DEMO 3: Orchestrator Features")
    print("=" * 60 + "\n")

    # Create with custom config
    config = AssistantConfig(
        user_name="SuperDev",
        default_model="qwq-32b",
        model_routing=True,
        auto_register_tools=True,
        verbose_logging=True,
    )

    context = Context(dry_run=False)

    orchestrator = get_orchestrator(
        config=config,
        automation_context=context,
    )

    print("✅ Orchestrator initialized")
    print(f"   User: {config.user_name}")
    print(f"   Default model: {config.default_model}")
    print(f"   Routing enabled: {config.model_routing}\n")

    # List available models
    print("📋 Available Models:")
    models = orchestrator.list_available_models()
    for model in models[:5]:  # Show first 5
        print(f"   - {model['name']}: {model['description'][:50]}...")
    print()

    # Execute tasks
    print("💬 Executing chat task:")
    response = orchestrator.chat("What's the difference between Docker and Kubernetes?")
    print(f"   Response: {response[:150]}...\n")

    # Get statistics
    print("📊 Orchestrator Statistics:")
    stats = orchestrator.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    print()


def demo_model_switching():
    """Demo: Dynamic model switching."""
    print("\n" + "=" * 60)
    print("DEMO 4: Dynamic Model Switching")
    print("=" * 60 + "\n")

    orchestrator = get_orchestrator()

    # Start with one model
    print("🔄 Starting with Mistral Large:")
    response = orchestrator.chat("Hello! Which model are you?")
    print(f"   {orchestrator.active_assistant.model_info.name}\n")

    # Switch to QwQ for reasoning
    print("🔄 Switching to QwQ for reasoning task:")
    orchestrator.switch_model("qwq-32b")
    response = orchestrator.chat("Explain recursion with a simple example")
    print(f"   Model: {orchestrator.active_assistant.model_info.name}")
    print(f"   Response: {response[:150]}...\n")

    # Switch to DeepSeek for coding
    print("🔄 Switching to DeepSeek for coding:")
    orchestrator.switch_model("deepseek-coder")
    response = orchestrator.chat("Write a quicksort implementation")
    print(f"   Model: {orchestrator.active_assistant.model_info.name}")
    print(f"   Response: {response[:150]}...\n")


def demo_conversation_management():
    """Demo: Conversation history and management."""
    print("\n" + "=" * 60)
    print("DEMO 5: Conversation Management")
    print("=" * 60 + "\n")

    orchestrator = get_orchestrator()

    print("📝 Having a multi-turn conversation:\n")

    # First message
    response = orchestrator.chat("My name is Alex")
    print("User: My name is Alex")
    print(f"Assistant: {response[:100]}...\n")

    # Context retained
    response = orchestrator.chat("What's my name?")
    print("User: What's my name?")
    print(f"Assistant: {response}\n")

    # More context
    response = orchestrator.chat("I'm working on a Python project")
    print("User: I'm working on a Python project")
    print(f"Assistant: {response[:100]}...\n")

    response = orchestrator.chat("What language am I using?")
    print("User: What language am I using?")
    print(f"Assistant: {response}\n")

    # Show stats
    print("📊 Conversation Stats:")
    if orchestrator.active_assistant:
        stats = orchestrator.active_assistant.get_stats()
        print(f"   Messages: {stats['messages_exchanged']}")
        print(f"   Tasks: {stats['tasks_completed']}")

    # Reset
    print("\n🔄 Resetting conversation...")
    orchestrator.reset_conversation()

    response = orchestrator.chat("What's my name?")
    print("User: What's my name?")
    print(f"Assistant: {response}\n")


def demo_real_world_workflow():
    """Demo: Real-world development workflow."""
    print("\n" + "=" * 60)
    print("DEMO 6: Real-World Development Workflow")
    print("=" * 60 + "\n")

    logger = AutomationLogger()
    context = Context(dry_run=False)

    config = AssistantConfig(
        user_name="Developer",
        default_model="qwq-32b",
        model_routing=True,
    )

    orchestrator = get_orchestrator(config=config, automation_context=context)

    logger.info("Starting development workflow")

    # Planning phase
    logger.info("Phase 1: Planning")
    plan_response = orchestrator.planning_task(
        "I need to add user authentication to my FastAPI app. "
        "What components do I need and what order should I implement them?"
    )
    print(f"\n📋 Plan:\n{plan_response[:300]}...\n")

    # Coding phase
    logger.info("Phase 2: Implementation")
    code_response = orchestrator.code_task("Write a FastAPI endpoint for user login with JWT token generation")
    print(f"\n💻 Code:\n{code_response[:300]}...\n")

    # Review phase
    logger.info("Phase 3: Review")
    review_response = orchestrator.execute_task(
        "What security considerations should I check for in authentication code?",
        task_type=TaskType.CODE_REVIEW,
    )
    print(f"\n🔍 Review:\n{review_response[:300]}...\n")

    logger.success("Workflow completed")

    # Final stats
    print("\n📊 Workflow Statistics:")
    stats = orchestrator.get_stats()
    print(f"   Total tasks: {stats['total_tasks']}")
    print(f"   Models used: {', '.join(stats['models_used'])}")


def main():
    """Run all demos."""
    print("\n" + "=" * 60)
    print("ORCHESTRATOR DEMO - High-Level Interface")
    print("Seamless Multi-Model Task Execution")
    print("=" * 60)

    try:
        # Check if GITHUB_TOKEN is set
        if not os.environ.get("GITHUB_TOKEN"):
            print("\n⚠️  ERROR: GITHUB_TOKEN environment variable is not set.")
            print("Please set it in your .env file or environment.")
            print("Get your token at: https://github.com/settings/tokens\n")
            return

        # Run demos
        demo_convenience_functions()

        input("\nPress Enter to continue...")
        demo_task_routing()

        input("\nPress Enter to continue...")
        demo_orchestrator_features()

        input("\nPress Enter to continue...")
        demo_model_switching()

        input("\nPress Enter to continue...")
        demo_conversation_management()

        input("\nPress Enter to see real-world workflow...")
        demo_real_world_workflow()

        print("\n" + "=" * 60)
        print("✅ All demos completed!")
        print("=" * 60 + "\n")

        print("🎯 Key Takeaways:")
        print("  1. Use chat(), code(), reason(), plan() for quick tasks")
        print("  2. Orchestrator handles model routing automatically")
        print("  3. Switch models dynamically based on task needs")
        print("  4. Conversations maintain context across turns")
        print("  5. Integrates seamlessly with automation framework\n")

        print("💡 Try it yourself:")
        print("  from app.core import chat, code, reason")
        print("  response = chat('Your question here')\n")

    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
