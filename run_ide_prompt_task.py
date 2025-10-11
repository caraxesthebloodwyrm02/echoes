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
