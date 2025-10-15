#!/usr/bin/env python3
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
Test script to verify OpenAI API key integration.

This script tests both the primary and secondary API keys to ensure they're working.
"""

import logging
import sys
from pathlib import Path

# Set up basic logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# Ensure the project root is on sys.path for package imports
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from minicon.config import Config

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
