"""
Integration example: Using AI Assistant with the Automation Framework.

This script demonstrates how to integrate the AI Assistant with the
automation framework's Context, Logger, and Orchestrator components.
"""

import os
import sys
from pathlib import Path

from app.core.assistant import create_assistant
from dotenv import load_dotenv

from automation.core.context import Context
from automation.core.logger import AutomationLogger

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables
load_dotenv()


def example_assistant_with_context():
    """Example: Using assistant with automation context."""
    print("\n" + "=" * 60)
    print("Example 1: Assistant with Automation Context")
    print("=" * 60 + "\n")

    # Create automation context
    context = Context(
        dry_run=False,
        user_info={"name": "Developer", "role": "Engineer"},
        env={"environment": "development"},
    )

    # Create logger
    logger = AutomationLogger()

    # Create assistant with context-aware system prompt
    system_prompt = f"""
    You are an AI assistant integrated with an automation framework.
    Current context:
    - User: {context.user_info.get('name', 'Unknown')}
    - Role: {context.user_info.get('role', 'Unknown')}
    - Environment: {context.env.get('environment', 'Unknown')}
    - Dry Run Mode: {context.dry_run}

    Help the user with automation tasks and provide relevant suggestions.
    """

    assistant = create_assistant(system_prompt=system_prompt)

    # Log assistant creation
    logger.info("AI Assistant initialized with automation context")

    # Use assistant
    response = assistant.chat(
        "What automation tasks should I prioritize for a development environment?"
    )

    print(
        "User: What automation tasks should I prioritize for a development environment?"
    )
    print(f"Assistant: {response}\n")

    logger.success("Assistant query completed successfully")


def example_assistant_task_helper():
    """Example: Assistant as a task planning helper."""
    print("\n" + "=" * 60)
    print("Example 2: Assistant as Task Planning Helper")
    print("=" * 60 + "\n")

    logger = AutomationLogger()

    # Create assistant specialized for task planning
    system_prompt = """
    You are an AI assistant specialized in automation task planning.
    Help users break down complex tasks into manageable steps.
    Provide clear, actionable recommendations.
    """

    assistant = create_assistant(system_prompt=system_prompt)

    # Register a tool to list available automation tasks
    def list_available_tasks() -> str:
        """List available automation tasks in the framework."""
        tasks = [
            "sanitize_codebase - Clean up codebase and remove unused files",
            "deps_update - Update project dependencies",
            "perf_bench - Run performance benchmarks",
            "release_notes - Generate release notes",
            "check_test_coverage - Analyze test coverage",
        ]
        return "\n".join(tasks)

    assistant.register_tool(
        name="list_available_tasks",
        description="List all available automation tasks in the framework",
        parameters={"type": "object", "properties": {}, "required": []},
        function=list_available_tasks,
    )

    logger.info("Querying assistant for task recommendations")

    # Ask for task recommendations
    response = assistant.chat(
        "I need to prepare my codebase for a production release. "
        "What automation tasks should I run and in what order?"
    )

    print("User: I need to prepare my codebase for a production release.")
    print("      What automation tasks should I run and in what order?")
    print(f"\nAssistant: {response}\n")

    logger.success("Task recommendations generated")


def example_interactive_assistant():
    """Example: Interactive assistant session."""
    print("\n" + "=" * 60)
    print("Example 3: Interactive Assistant Session")
    print("=" * 60 + "\n")

    logger = AutomationLogger()

    # Create assistant
    assistant = create_assistant(
        system_prompt=(
            "You are a helpful automation assistant. "
            "Provide concise, practical advice for automation tasks."
        )
    )

    # Simulate an interactive session
    questions = [
        "How can I automate dependency updates?",
        "What's the best way to handle test coverage checks?",
        "Should I run these tasks in parallel or sequentially?",
    ]

    logger.info("Starting interactive assistant session")

    for i, question in enumerate(questions, 1):
        print(f"\n[Question {i}]")
        print(f"User: {question}")

        response = assistant.chat(question)
        print(f"Assistant: {response}")

        logger.info(f"Processed question {i}/{len(questions)}")

    print("\n")
    logger.success("Interactive session completed")

    # Show conversation history
    print("\n[Conversation Summary]")
    history = assistant.get_history()
    print(f"Total messages exchanged: {len(history)}")


def example_assistant_with_confirmation():
    """Example: Assistant helping with confirmation decisions."""
    print("\n" + "=" * 60)
    print("Example 4: Assistant with Confirmation Logic")
    print("=" * 60 + "\n")

    context = Context(dry_run=False)
    logger = AutomationLogger()

    # Create assistant
    assistant = create_assistant(
        system_prompt=(
            "You are an AI assistant that helps users make informed decisions "
            "about automation tasks. Provide risk assessments and recommendations."
        )
    )

    # Simulate a risky operation
    task_description = "Delete all temporary files and clear cache directories"

    logger.warning(f"Considering risky operation: {task_description}")

    # Ask assistant for risk assessment
    response = assistant.chat(
        f"I'm about to perform this operation: '{task_description}'. "
        f"What are the risks and what should I confirm before proceeding?"
    )

    print(f"User: I'm about to perform this operation: '{task_description}'.")
    print("      What are the risks and what should I confirm before proceeding?")
    print(f"\nAssistant: {response}\n")

    # Use context confirmation with assistant's advice
    if context.require_confirmation(f"Proceed with: {task_description}?"):
        logger.success("User confirmed - operation would proceed")
    else:
        logger.info("User declined - operation cancelled")


def main():
    """Run all integration examples."""
    print("\n" + "=" * 60)
    print("AI ASSISTANT - AUTOMATION FRAMEWORK INTEGRATION")
    print("=" * 60)

    try:
        # Check if GITHUB_TOKEN is set
        if not os.environ.get("GITHUB_TOKEN"):
            print("\n⚠️  ERROR: GITHUB_TOKEN environment variable is not set.")
            print("Please set it in your .env file or environment.")
            print("Get your token at: https://github.com/settings/tokens\n")
            return

        # Run examples
        example_assistant_with_context()
        example_assistant_task_helper()
        example_interactive_assistant()
        example_assistant_with_confirmation()

        print("\n" + "=" * 60)
        print("All integration examples completed successfully!")
        print("=" * 60 + "\n")

    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
