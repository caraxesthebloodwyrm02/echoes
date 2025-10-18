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

import asyncio
import os
import sys

from prompting.system import PromptingSystem

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


async def generate_tasks():
    """Use the PromptingSystem in 'ide' mode to generate development tasks."""

    prompt = (
        "Generate a list of concrete IDE development tasks to improve this codebase. "
        "Focus on refactoring opportunities, new feature suggestions, and ways to "
        "enhance the overall developer experience."
    )

    print("Initializing Prompting System...")
    system = PromptingSystem()

    project_root = os.path.dirname(os.path.abspath(__file__))
    system.set_project_context(project_root)

    print("Processing prompt in 'ide' mode...")
    print("-" * 80)
    print(f"Prompt: {prompt}")
    print("-" * 80)

    try:
        result = await system.process_prompt(
            prompt=prompt,
            mode="ide",
            enable_data_loop=False,  # Keep this fast for a single generation
        )

        print("\nGenerated IDE Development Tasks:")
        print("=" * 80)
        print(result["response"])
        print("=" * 80)

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    asyncio.run(generate_tasks())
