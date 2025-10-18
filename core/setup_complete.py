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

# MIT License
#
# Copyright (c) 2025 Echoes Project
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software, and to permit persons to whom
# the Software is furnished to do so, subject to the following conditions.
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
Echoes Complete Setup Script
One-command setup for the entire Echoes development environment
"""

import argparse
import subprocess
import sys
from pathlib import Path

# Add project to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))


def run_command(cmd, description, cwd=None, check=True):
    """Run a command with proper error handling"""
    print(f"\n🔧 {description}...")
    try:
        result = subprocess.run(
            cmd if isinstance(cmd, list) else cmd.split(),
            cwd=cwd or PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=check,
        )
        print("✓ Completed")
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed: {e.stderr}")
        if check:
            sys.exit(1)
        return e


def main():
    parser = argparse.ArgumentParser(
        description="Complete Echoes Development Environment Setup"
    )
    parser.add_argument(
        "--quick", action="store_true", help="Quick setup (skip profile alignment)"
    )
    parser.add_argument(
        "--no-validation", action="store_true", help="Skip final validation"
    )

    args = parser.parse_args()

    print("=" * 80)
    print("🚀 ECHOES COMPLETE ENVIRONMENT SETUP")
    print("=" * 80)
    print("This will set up your complete Echoes development environment")
    print("")

    # Step 1: Environment Bootstrap
    print("📦 STEP 1: Environment Bootstrap")
    run_command(
        [sys.executable, "bootstrap.py"],
        "Bootstrapping Python environment and dependencies",
    )

    # Step 2: Profile Setup (unless quick mode)
    if not args.quick:
        print("\n👤 STEP 2: Profile & IDE Setup")
        run_command(
            [sys.executable, "setup_profiles.py", "--all"],
            "Aligning IDE profiles and user settings",
        )
    else:
        print("\n⏭️  STEP 2: Skipping profile setup (--quick mode)")

    # Step 3: Final Validation
    if not args.no_validation:
        print("\n✅ STEP 3: Final Validation")
        run_command(
            [sys.executable, "tools/validate_configuration.py"],
            "Running final configuration validation",
        )

        # Comprehensive integration test
        print("\n🔍 STEP 4: Integration Test")
        test_cmd = [
            sys.executable,
            "-c",
            """
import sys
from utils.safe_imports import get_safe_kg_bridge, get_safe_agent_knowledge_layer
from utils.openai_integration import get_openai_integration
from prompting.core.context_manager import ContextManager
from ai_agents.orchestrator import AIAgentOrchestrator

print("Testing core integrations...")
kg = get_safe_kg_bridge(enable_kg=False)
akl = get_safe_agent_knowledge_layer(enable_kg=False)
openai = get_openai_integration()
cm = ContextManager(enable_kg=False)
orch = AIAgentOrchestrator(enable_knowledge_layer=False)

print("✓ All integrations working")
""",
        ]
        run_command(test_cmd, "Testing all system integrations")

    # Success message
    print("\n" + "=" * 80)
    print("🎉 ECHOES ENVIRONMENT SETUP COMPLETE!")
    print("=" * 80)
    print("")
    print("🚀 Quick Start Commands:")
    print("  .\\activate_environment.ps1    # Activate environment")
    print("  python main.py                 # Start development")
    print("  python tools/validate_configuration.py  # Check status")
    print("")
    print("📚 Available Scripts:")
    print("  python bootstrap.py           # Re-bootstrap environment")
    print("  python setup_profiles.py      # Re-align profiles")
    print("  python startup.py             # Quick validation")
    print("")
    print("Happy coding! 🎯")


if __name__ == "__main__":
    main()
