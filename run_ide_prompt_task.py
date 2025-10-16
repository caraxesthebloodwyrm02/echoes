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

from automation.core.context import Context
from prompting.system import PromptingSystem

# Ensure project root is on the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


async def main():
    prompt = (
        "Generate a list of concrete IDE development tasks to improve this codebase. "
        "Focus on refactoring opportunities, new feature suggestions, and ways to "
        "enhance the overall developer experience."
    )

    system = PromptingSystem()

    project_root = os.path.dirname(os.path.abspath(__file__))
    system.set_project_context(project_root)

    # Build automation Context and run the built-in task entrypoint
    ctx = Context(
        dry_run=False,
        extra_data={
            "prompt": prompt,
            "mode": "ide",
            # Keep fast and deterministic for now; set True to enable data loop
            "enable_data_loop": False,
        },
    )

    await system.process_prompt_task(ctx)


if __name__ == "__main__":
    asyncio.run(main())
