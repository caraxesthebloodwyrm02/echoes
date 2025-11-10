#!/usr/bin/env python3
"""
Simple test for !contact command functionality
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.assistant import LogicCommunicationAssistant


def test_contact_command():
    """Test the !contact command parsing and execution."""

    # Create assistant instance
    print("Initializing LogicCommunicationAssistant...")
    assistant = LogicCommunicationAssistant()

    # Test command
    command = '!contact psychological user "Hello, world!"'
    print(f"\nTesting command: {command}")

    # Execute command
    result = assistant.execute_command(command)

    print("\nResult:")
    print(f"  Success: {result.success}")
    print(f"  Execution Time: {result.execution_time:.3f}s")
    print(f"  Complexity: {result.complexity}")
    print(f"  Confidence: {result.confidence}")
    print(f"  Output: {result.output}")
    print(f"  Error: {result.error}")
    print(f"  Metadata: {result.metadata}")

    if hasattr(result, "_metadata") and result._metadata:
        print(f"  Raw metadata: {result._metadata}")

    # Let's also test the _comm_send_message directly
    print("\nTesting _comm_send_message directly:")
    direct_result = assistant._comm_send_message(
        "psychological", "Hello, world!", "user", 5
    )
    print(f"  Direct result: {direct_result}")


if __name__ == "__main__":
    test_contact_command()
