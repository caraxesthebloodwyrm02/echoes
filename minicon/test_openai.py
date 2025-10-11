#!/usr/bin/env python3
"""
Test script to verify OpenAI API key integration.

This script tests both the primary and secondary API keys to ensure they're working.
"""

import logging
import sys
from pathlib import Path

from minicon.config import Config

# Set up basic logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# Ensure the project root is on sys.path for package imports
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Set console encoding for Windows
if sys.platform == "win32":
    import io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")


def test_openai_integration():
    """Test the OpenAI integration with both API keys."""
    print("Testing OpenAI integration...\n")

    # Initialize config
    config = Config.from_env()

    # Test primary key
    print("Testing PRIMARY API key...")
    try:
        config.switch_api_key("PRIMARY")
        client = config.openai_client
        models = client.models.list()
        print(
            "[SUCCESS] Connected with PRIMARY key. Available models:", len(models.data)
        )
    except Exception as e:
        print("[ERROR] With PRIMARY key:", str(e))

    print("\nTesting SECONDARY API key...")
    try:
        config.switch_api_key("SECONDARY")
        client = config.openai_client
        models = client.models.list()
        print(
            "[SUCCESS] Connected with SECONDARY key. Available models:",
            len(models.data),
        )
    except Exception as e:
        print("[ERROR] With SECONDARY key:", str(e))

    print("\nTest complete!")


if __name__ == "__main__":
    test_openai_integration()
