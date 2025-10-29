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
Quickstart - Get started with the AI Assistant in 30 seconds!

This script shows the absolute simplest way to use the agentic assistant.
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables
load_dotenv()


def main():
    """Quick start demonstration."""

    # Check token
    if not os.environ.get("GITHUB_TOKEN"):
        print("\n⚠️  Set GITHUB_TOKEN in .env file first!")
        print("Get token at: https://github.com/settings/tokens\n")
        return

    print("\n" + "=" * 60)
    print("🚀 AI ASSISTANT QUICKSTART")
    print("=" * 60 + "\n")

    # METHOD 1: Ultra-simple (recommended for beginners)
    print("METHOD 1: One-liner convenience functions\n")
    print("```python")
    print("from app.core import chat, code, reason, plan")
    print()
    print("response = chat('Explain Docker in one sentence')")
    print("response = code('Write a function to find prime numbers')")
    print("response = reason('Why is Python dynamically typed?')")
    print("response = plan('Steps to build a REST API')")
    print("```\n")

    # Demo it
    from app.core import chat

    print("💬 Live example:")
    print("   chat('What is an API?')\n")
    response = chat("What is an API?")
    print(f"   Response: {response[:200]}...\n")

    print("-" * 60 + "\n")

    # METHOD 2: Full control
    print("METHOD 2: Full control with agentic assistant\n")
    print("```python")
    print("from app.core import create_agentic_assistant")
    print()
    print("assistant = create_agentic_assistant(")
    print("    user_name='YourName',")
    print("    model_id='qwq-32b',  # QwQ for reasoning")
    print(")")
    print()
    print("response = assistant.chat('Your question')")
    print("```\n")

    # Demo it
    from app.core import create_agentic_assistant

    print("🤖 Live example:")
    print("   Creating assistant with QwQ-32B...\n")
    assistant = create_agentic_assistant(
        user_name="QuickStart",
        model_id="qwq-32b",
    )

    print(f"   ✅ Assistant created: {assistant.model_info.name}")
    print(f"   ✅ Tools registered: {len(assistant.assistant.tools)}\n")

    response = assistant.chat("What can you help me with?")
    print(f"   Response: {response[:200]}...\n")

    print("-" * 60 + "\n")

    # METHOD 3: Orchestrator (most powerful)
    print("METHOD 3: Orchestrator for automatic routing\n")
    print("```python")
    print("from app.core import get_orchestrator, TaskType")
    print()
    print("orchestrator = get_orchestrator()")
    print()
    print("# Auto-routes to best model for task type")
    print("response = orchestrator.code_task('Write a REST API')")
    print("response = orchestrator.reasoning_task('Explain recursion')")
    print("response = orchestrator.planning_task('Plan a project')")
    print("```\n")

    # Demo it
    from app.core import get_orchestrator

    print("🎯 Live example:")
    print("   Getting orchestrator...\n")
    orchestrator = get_orchestrator()

    response = orchestrator.code_task("Write a hello world function")
    print(f"   Code task result: {response[:150]}...\n")

    print("-" * 60 + "\n")

    # Available models
    print("📋 AVAILABLE MODELS:\n")
    print("  qwq-32b        - QwQ 32B (best for reasoning)")
    print("  deepseek-coder - DeepSeek Coder (best for coding)")
    print("  qwen-coder     - Qwen 2.5 Coder (coding specialist)")
    print("  mistral-large  - Mistral Large (general purpose)")
    print("  mistral-small  - Mistral Small (fast & efficient)")
    print("  llama-3.3      - Llama 3.3 70B (open-source)")
    print("  gpt-4.1        - GPT-4.1 (advanced reasoning)\n")

    print("-" * 60 + "\n")

    # Next steps
    print("✨ NEXT STEPS:\n")
    print("1. Try different models:")
    print("   assistant = create_agentic_assistant(model_id='deepseek-coder')")
    print()
    print("2. Run comprehensive demos:")
    print("   python examples/agentic_assistant_demo.py")
    print("   python examples/orchestrator_demo.py")
    print()
    print("3. Interactive chat:")
    print("   python examples/assistant_interactive_demo.py")
    print()
    print("4. Read the docs:")
    print("   docs/AI_ASSISTANT_GUIDE.md")
    print()
    print("5. Check your stats:")
    print("   stats = assistant.get_stats()")
    print("   print(stats)\n")

    print("=" * 60)
    print("🎉 You're ready to use the AI Assistant!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
