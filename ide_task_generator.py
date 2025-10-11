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
