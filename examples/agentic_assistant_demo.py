"""
Agentic Assistant Demo - Multi-Model Intelligence

Demonstrates the full agentic assistant system with:
- Multi-model support (QwQ, DeepSeek, Mistral, Qwen, Llama, GPT-4)
- Intelligent task routing
- Tool calling and autonomous action
- Seamless automation framework integration
"""

import os
import sys
from pathlib import Path

from app.core import AssistantConfig, ModelRegistry, create_agentic_assistant
from dotenv import load_dotenv

from automation.core.context import Context
from automation.core.logger import AutomationLogger

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables
load_dotenv()


def demo_model_selection():
    """Demo: Different models for different tasks."""
    print("\n" + "=" * 60)
    print("DEMO 1: Intelligent Model Selection")
    print("=" * 60 + "\n")

    logger = AutomationLogger()

    # Show available models
    print("📋 Available Models:")
    for key, model in ModelRegistry.MODELS.items():
        print(f"  - {key}: {model.name} ({model.provider.value})")
        print(f"    Capabilities: {[c.value for c in model.capabilities]}")

    print("\n" + "-" * 60 + "\n")

    # Use QwQ for reasoning
    logger.info("Creating assistant with QwQ-32B (reasoning specialist)")
    assistant = create_agentic_assistant(
        user_name="Developer",
        model_id="qwq-32b",
        use_case="reasoning",
    )

    response = assistant.chat("Explain the time complexity of binary search and why it's O(log n).")
    print(f"🤖 QwQ Response:\n{response}\n")

    # Switch to DeepSeek for coding
    logger.info("Switching to DeepSeek-Coder for coding task")
    assistant.switch_model("deepseek-coder")

    response = assistant.chat("Write a Python function to find the longest palindrome in a string.")
    print(f"\n💻 DeepSeek Response:\n{response}\n")


def demo_tool_calling():
    """Demo: Autonomous tool usage."""
    print("\n" + "=" * 60)
    print("DEMO 2: Autonomous Tool Calling")
    print("=" * 60 + "\n")

    # Create assistant with Mistral Large (excellent at tool calling)
    assistant = create_agentic_assistant(
        user_name="Developer",
        model_id="mistral-large",
    )

    # Tools are auto-registered
    print(f"✅ {len(assistant.assistant.tools)} tools registered automatically\n")

    # Ask a question that requires tool usage
    response = assistant.chat("What time is it right now? Also, calculate 157 * 234 for me.")
    print(f"🤖 Response (with tool usage):\n{response}\n")

    # File operations
    response = assistant.chat("List the Python files in the current directory " "and tell me about the largest one.")
    print(f"\n📁 File operations response:\n{response}\n")


def demo_agentic_behavior():
    """Demo: Proactive, agentic behavior."""
    print("\n" + "=" * 60)
    print("DEMO 3: Agentic & Proactive Behavior")
    print("=" * 60 + "\n")

    # Use QwQ for best agentic behavior
    assistant = create_agentic_assistant(
        user_name="Developer",
        model_id="qwq-32b",
        use_case="agentic",
    )

    # Give a complex task
    response = assistant.chat("I need to prepare my Python project for production deployment. " "What should I do?")
    print(f"🤖 Agentic Response:\n{response}\n")

    # Follow-up - assistant should maintain context
    response = assistant.chat("How do I ensure my dependencies are properly managed?")
    print(f"\n🔄 Context-aware follow-up:\n{response}\n")


def demo_automation_integration():
    """Demo: Integration with automation framework."""
    print("\n" + "=" * 60)
    print("DEMO 4: Automation Framework Integration")
    print("=" * 60 + "\n")

    # Create automation context
    context = Context(
        dry_run=False,
        user_info={"name": "Developer", "role": "Engineer"},
        env={"environment": "development", "project": "AI Assistant"},
    )

    logger = AutomationLogger()

    # Create assistant with context
    assistant = create_agentic_assistant(
        user_name="Developer",
        model_id="mistral-large",
        automation_context=context,
        logger=logger,
    )

    logger.info("Assistant integrated with automation framework")

    # Ask about context
    response = assistant.chat("What's my current automation context? What environment am I in?")
    print(f"🤖 Response:\n{response}\n")

    # Get stats
    stats = assistant.get_stats()
    print("\n📊 Assistant Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")


def demo_configuration():
    """Demo: Configuration and customization."""
    print("\n" + "=" * 60)
    print("DEMO 5: Configuration & Customization")
    print("=" * 60 + "\n")

    # Create custom configuration
    config = AssistantConfig(
        user_name="CustomUser",
        default_model="qwen-coder",  # Prefer Qwen for coding
        temperature=0.3,  # Lower temperature for deterministic responses
        auto_register_tools=True,
        proactive_suggestions=True,
        verbose_logging=True,
    )

    print("⚙️  Custom Configuration:")
    print(f"  User: {config.user_name}")
    print(f"  Default Model: {config.default_model}")
    print(f"  Temperature: {config.temperature}")
    print(f"  Auto-register tools: {config.auto_register_tools}")

    # Create assistant with config
    assistant = create_agentic_assistant(
        user_name=config.user_name,
        model_id=config.default_model,
        temperature=config.temperature,
    )

    print("\n✅ Created assistant with custom config")
    print(f"   Model: {assistant.model_info.name}\n")

    response = assistant.chat("Write a Python function to read a JSON file safely.")
    print(f"💻 Response:\n{response}\n")


def demo_model_comparison():
    """Demo: Compare responses from different models."""
    print("\n" + "=" * 60)
    print("DEMO 6: Model Comparison")
    print("=" * 60 + "\n")

    question = "What are the key principles of clean code?"

    models_to_test = ["qwq-32b", "mistral-large", "llama-3.3"]

    for model_id in models_to_test:
        print(f"\n--- {model_id.upper()} ---\n")

        assistant = create_agentic_assistant(
            user_name="Developer",
            model_id=model_id,
        )

        response = assistant.chat(question)
        # Print first 200 chars
        preview = response[:200] + "..." if len(response) > 200 else response
        print(f"{preview}\n")


def main():
    """Run all demos."""
    print("\n" + "=" * 60)
    print("AGENTIC ASSISTANT - COMPREHENSIVE DEMO")
    print("Multi-Model AI with Intelligence Routing")
    print("=" * 60)

    try:
        # Check if GITHUB_TOKEN is set
        if not os.environ.get("GITHUB_TOKEN"):
            print("\n⚠️  ERROR: GITHUB_TOKEN environment variable is not set.")
            print("Please set it in your .env file or environment.")
            print("Get your token at: https://github.com/settings/tokens\n")
            return

        # Run demos
        demo_model_selection()

        input("\nPress Enter to continue to next demo...")
        demo_tool_calling()

        input("\nPress Enter to continue to next demo...")
        demo_agentic_behavior()

        input("\nPress Enter to continue to next demo...")
        demo_automation_integration()

        input("\nPress Enter to continue to next demo...")
        demo_configuration()

        input("\nPress Enter to see model comparison...")
        demo_model_comparison()

        print("\n" + "=" * 60)
        print("All demos completed successfully!")
        print("=" * 60 + "\n")

        print("💡 Next Steps:")
        print("  1. Try the orchestrator demo: python examples/orchestrator_demo.py")
        print("  2. Experiment with different models")
        print("  3. Create custom tools for your workflows")
        print("  4. Integrate with your automation tasks\n")

    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
