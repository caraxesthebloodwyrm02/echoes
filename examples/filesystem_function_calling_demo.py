#!/usr/bin/env python3
"""
Filesystem Function Calling Demo for EchoesAssistantV2

Demonstrates the enhanced filesystem interaction capabilities using OpenAI's function calling.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from assistant_v2_core import EchoesAssistantV2


def demo_filesystem_operations():
    """Demonstrate filesystem operations through function calling."""

    print("=" * 80)
    print("🔧 Filesystem Function Calling Demo")
    print("=" * 80)

    # Initialize the assistant with filesystem tools enabled
    assistant = EchoesAssistantV2(
        enable_tools=True, enable_status=True, session_id="filesystem_demo"
    )

    # List available filesystem tools
    print("\n📋 Available Filesystem Tools:")
    filesystem_tools = assistant.list_tools(category="filesystem")
    for tool in filesystem_tools:
        print(f"  • {tool}")

    print("\n" + "=" * 80)
    print("🚀 Interactive Demo")
    print("=" * 80)
    print("\nThe assistant now has filesystem interaction capabilities!")
    print("You can ask it to:")
    print("  • Read files: 'Read the contents of README.md'")
    print("  • Write files: 'Create a new Python file called hello.py'")
    print("  • List directories: 'List all Python files in the current directory'")
    print("  • Search files: 'Search for files containing the word import'")
    print("  • Create directories: 'Create a directory called test_files'")
    print("  • Get file info: 'Show me information about assistant_v2_core.py'")
    print("\n" + "=" * 80)

    # Example interactions
    examples = [
        "List the contents of the current directory",
        "Read the first 50 lines of assistant_v2_core.py",
        "Create a new directory called demo_output",
        "Write a simple Python script to demo_output/test.py that prints 'Hello, World!'",
        "Search for all Python files in the project",
        "Get information about the tools directory",
    ]

    print("\n📝 Example prompts you can try:")
    for i, example in enumerate(examples, 1):
        print(f"  {i}. {example}")

    print("\n" + "=" * 80)
    print("💡 Safety Features")
    print("=" * 80)
    print("The filesystem tools include comprehensive safety measures:")
    print("  ✅ Path validation - Only allows access within the project directory")
    print("  ✅ Sensitive path filtering - Blocks .git, __pycache__, .env, etc.")
    print("  ✅ File size limits - Prevents reading extremely large files")
    print("  ✅ Binary file detection - Skips binary files for text operations")
    print("  ✅ System directory protection - Blocks access to system directories")
    print("  ✅ Error handling - Graceful error messages for all operations")

    print("\n" + "=" * 80)
    print("🎯 Starting Interactive Session")
    print("=" * 80)
    print("\nType your messages below (or 'quit' to exit):")

    # Interactive loop
    while True:
        try:
            user_input = input("\n💬 You: ").strip()

            if user_input.lower() in ["quit", "exit", "q"]:
                print("\n👋 Goodbye!")
                break

            if not user_input:
                continue

            print("\n🤖 Assistant: ", end="", flush=True)
            _response = assistant.chat(user_input, stream=True)

            # The stream=True option prints the response directly
            # If you want to capture it, use stream=False

        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")


def demo_tool_schemas():
    """Show the OpenAI function schemas for filesystem tools."""

    print("\n" + "=" * 80)
    print("📋 OpenAI Function Schemas")
    print("=" * 80)

    assistant = EchoesAssistantV2(enable_tools=True)

    if assistant.tool_registry:
        # Get filesystem tools
        filesystem_tools = []
        for tool_name in assistant.tool_registry.list_tools():
            tool = assistant.tool_registry.get(tool_name)
            if (
                tool
                and hasattr(tool, "name")
                and tool.name
                in [
                    "read_file",
                    "write_file",
                    "list_directory",
                    "search_files",
                    "create_directory",
                    "get_file_info",
                ]
            ):
                filesystem_tools.append(tool)

        for tool in filesystem_tools:
            schema = tool.to_openai_schema()
            print(f"\n🔧 {schema['function']['name']}")
            print(f"   Description: {schema['function']['description']}")
            print(
                f"   Parameters: {list(schema['function']['parameters']['properties'].keys())}"
            )


if __name__ == "__main__":
    print("🔧 Filesystem Function Calling Demo")
    print("This demo showcases the filesystem interaction capabilities.")
    print()

    choice = input(
        "Choose an option:\n"
        "1. Interactive Demo\n"
        "2. Show Tool Schemas\n"
        "3. Both\n"
        "Enter choice (1-3): "
    ).strip()

    if choice in ["1", "3"]:
        demo_filesystem_operations()

    if choice in ["2", "3"]:
        demo_tool_schemas()

    if choice not in ["1", "2", "3"]:
        print("Invalid choice. Running interactive demo...")
        demo_filesystem_operations()
