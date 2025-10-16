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
Echoes Automatic Startup Script
Validates and prepares the development environment
"""

import sys
from pathlib import Path

# Add project to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))


def main():
    try:
        # Quick validation
        from utils.openai_integration import get_openai_integration
        from utils.safe_imports import (
            get_safe_agent_knowledge_layer,
            get_safe_kg_bridge,
        )

        # Test core imports
        kg_bridge = get_safe_kg_bridge(enable_kg=False)
        akl = get_safe_agent_knowledge_layer(enable_kg=False)
        openai = get_openai_integration()

        print("Echoes development environment ready!")
        print(
            f"Knowledge Graph: {'Available' if kg_bridge.enabled else 'Fallback mode'}"
        )
        print(f"Agent Layer: {'Available' if akl.enabled else 'Fallback mode'}")
        print(f"OpenAI: {'Configured' if openai.is_configured else 'Not configured'}")

        return True

    except Exception as e:
        print(f"Startup validation failed: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
