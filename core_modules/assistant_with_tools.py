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
Advanced usage example: AI Assistant with tool/function calling.

This script demonstrates how to register custom tools that the assistant
can call to perform actions or retrieve information.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

from app.core.assistant import create_assistant

# Load environment variables
load_dotenv()


# Define tool functions
def get_current_time() -> str:
    """Get the current time."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def calculate(operation: str, a: float, b: float) -> float:
    """
    Perform a mathematical calculation.

    Args:
        operation: The operation to perform (add, subtract, multiply, divide)
        a: First number
        b: Second number

    Returns:
        Result of the calculation
    """
    operations = {
        "add": lambda x, y: x + y,
        "subtract": lambda x, y: x - y,
        "multiply": lambda x, y: x * y,
        "divide": lambda x, y: x / y if y != 0 else "Error: Division by zero",
    }

    if operation not in operations:
        return f"Error: Unknown operation '{operation}'"

    result = operations[operation](a, b)
    return result


def get_file_info(file_path: str) -> str:
    """
    Get information about a file.

    Args:
        file_path: Path to the file

    Returns:
        JSON string with file information
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return json.dumps({"error": f"File not found: {file_path}"})

        info = {
            "name": path.name,
            "size_bytes": path.stat().st_size,
            "is_file": path.is_file(),
            "is_directory": path.is_dir(),
            "modified": datetime.fromtimestamp(path.stat().st_mtime).isoformat(),
        }
        return json.dumps(info, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


def example_with_time_tool():
    """Example: Assistant with time-checking tool."""
    print("\n" + "=" * 60)
    print("Example 1: Time Tool")
    print("=" * 60 + "\n")

    # Create assistant
    assistant = create_assistant(system_prompt="You are a helpful assistant with access to tools.")

    # Register the time tool
    assistant.register_tool(
        name="get_current_time",
        description="Get the current date and time",
        parameters={
            "type": "object",
            "properties": {},
            "required": [],
        },
        function=get_current_time,
    )

    # Ask for the time
    response = assistant.chat("What time is it right now?")
    print("User: What time is it right now?")
    print(f"Assistant: {response}\n")


def example_with_calculator_tool():
    """Example: Assistant with calculator tool."""
    print("\n" + "=" * 60)
    print("Example 2: Calculator Tool")
    print("=" * 60 + "\n")

    assistant = create_assistant(system_prompt="You are a helpful math assistant with access to a calculator.")

    # Register calculator tool
    assistant.register_tool(
        name="calculate",
        description="Perform mathematical calculations (add, subtract, multiply, divide)",
        parameters={
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["add", "subtract", "multiply", "divide"],
                    "description": "The mathematical operation to perform",
                },
                "a": {
                    "type": "number",
                    "description": "First number",
                },
                "b": {
                    "type": "number",
                    "description": "Second number",
                },
            },
            "required": ["operation", "a", "b"],
        },
        function=calculate,
    )

    # Ask for calculations
    response = assistant.chat("What is 15 multiplied by 7?")
    print("User: What is 15 multiplied by 7?")
    print(f"Assistant: {response}\n")

    response = assistant.chat("Now add 100 to that result.")
    print("User: Now add 100 to that result.")
    print(f"Assistant: {response}\n")


def example_with_file_tool():
    """Example: Assistant with file information tool."""
    print("\n" + "=" * 60)
    print("Example 3: File Information Tool")
    print("=" * 60 + "\n")

    assistant = create_assistant(system_prompt="You are a helpful assistant that can check file information.")

    # Register file info tool
    assistant.register_tool(
        name="get_file_info",
        description="Get information about a file or directory",
        parameters={
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the file or directory",
                },
            },
            "required": ["file_path"],
        },
        function=get_file_info,
    )

    # Ask about a file
    response = assistant.chat("Can you tell me about the requirements.txt file?")
    print("User: Can you tell me about the requirements.txt file?")
    print(f"Assistant: {response}\n")


def example_multiple_tools():
    """Example: Assistant with multiple tools."""
    print("\n" + "=" * 60)
    print("Example 4: Multiple Tools")
    print("=" * 60 + "\n")

    assistant = create_assistant(
        system_prompt=(
            "You are a helpful assistant with access to multiple tools. "
            "Use them when appropriate to answer user questions."
        )
    )

    # Register all tools
    assistant.register_tool(
        name="get_current_time",
        description="Get the current date and time",
        parameters={"type": "object", "properties": {}, "required": []},
        function=get_current_time,
    )

    assistant.register_tool(
        name="calculate",
        description="Perform mathematical calculations",
        parameters={
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["add", "subtract", "multiply", "divide"],
                },
                "a": {"type": "number"},
                "b": {"type": "number"},
            },
            "required": ["operation", "a", "b"],
        },
        function=calculate,
    )

    assistant.register_tool(
        name="get_file_info",
        description="Get information about a file",
        parameters={
            "type": "object",
            "properties": {
                "file_path": {"type": "string"},
            },
            "required": ["file_path"],
        },
        function=get_file_info,
    )

    # Complex query requiring multiple tools
    response = assistant.chat("What time is it, and what is 25 times 4?")
    print("User: What time is it, and what is 25 times 4?")
    print(f"Assistant: {response}\n")


def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("AI ASSISTANT - TOOL CALLING EXAMPLES")
    print("=" * 60)

    try:
        # Check if GITHUB_TOKEN is set
        if not os.environ.get("GITHUB_TOKEN"):
            print("\n⚠️  ERROR: GITHUB_TOKEN environment variable is not set.")
            print("Please set it in your .env file or environment.")
            print("Get your token at: https://github.com/settings/tokens\n")
            return

        # Run examples
        example_with_time_tool()
        example_with_calculator_tool()
        example_with_file_tool()
        example_multiple_tools()

        print("\n" + "=" * 60)
        print("All examples completed successfully!")
        print("=" * 60 + "\n")

    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
