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
Multi-Mode Prompting System Demo
Demonstrates the system using the sample prompt through all five modes
"""

import asyncio
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from prompting.system import PromptingSystem


async def demo_all_modes():
    """Run the sample prompt through all five modes"""

    # Sample prompt from the original specification
    sample_prompt = "I want to create a data loop for my local repository root that scans itself, learns structure and semantics, searches web and community for resonance, filters and cleans data, then reloops - a self-improving feedback engine where knowledge becomes recursive intelligence."

    # Initialize the system
    system = PromptingSystem()

    # Set up project context
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    system.set_project_context(project_root)

    print("=" * 80)
    print("MULTI-MODE PROMPTING SYSTEM DEMONSTRATION")
    print("=" * 80)
    print(f"\nSample Prompt: {sample_prompt}")
    print("\n" + "=" * 80)

    modes = ["concise", "ide", "conversational", "star_stuff", "business"]

    for mode in modes:
        print(f"\n{'#' * 20} MODE: {mode.upper().replace('_', ' ')} {'#' * 20}")

        try:
            # Process prompt in specific mode
            result = await system.process_prompt(
                prompt=sample_prompt,
                mode=mode,
                enable_data_loop=False,  # Disable for demo speed
            )

            print(f"\nResponse ({result['mode']} mode):")
            print("-" * 60)
            print(result["response"])
            print("-" * 60)

            # Show metadata
            metadata = result["metadata"]
            print(f"Processing time: {metadata['processing_time']:.2f}s")
            print(f"Reasoning steps: {len(metadata['reasoning_chain'])}")

        except Exception as e:
            print(f"Error in {mode} mode: {e}")

        print("\n" + "=" * 80)

    # Show session summary
    print("\nSESSION SUMMARY:")
    summary = system.get_session_summary()
    print(f"Session ID: {summary['session_id']}")
    print(f"Conversation entries: {summary['context']['conversation_entries']}")
    print(f"Available modes: {', '.join(summary['available_modes'])}")


async def demo_data_loop():
    """Demonstrate the data loop functionality"""

    print("\n" + "=" * 80)
    print("DATA LOOP DEMONSTRATION")
    print("=" * 80)

    system = PromptingSystem()

    # Simpler prompt for data loop demo
    prompt = "Find Python automation frameworks and best practices"

    print(f"Prompt: {prompt}")
    print("Running with data loop enabled...")

    try:
        result = await system.process_prompt(
            prompt=prompt, mode="ide", enable_data_loop=True
        )

        print("\nResponse:")
        print("-" * 60)
        print(result["response"])
        print("-" * 60)

        # Show data loop results
        metadata = result["metadata"]
        print("\nData Loop Results:")
        print(f"- Data sources used: {metadata['data_sources_used']}")
        print(f"- Insights generated: {metadata['insights_generated']}")
        print(f"- Processing time: {metadata['processing_time']:.2f}s")

        # Show raw data if available
        if "data_loop_result" in result["raw_inference"]:
            loop_result = result["raw_inference"]["data_loop_result"]
            print(f"- Loop converged: {loop_result['metadata']['converged']}")
            print(f"- Loop iterations: {loop_result['metadata']['iterations']}")
            print(f"- Final quality: {loop_result['metadata']['final_quality']:.2f}")

    except Exception as e:
        print(f"Error in data loop demo: {e}")


async def demo_automation_integration():
    """Demonstrate integration with automation framework"""

    print("\n" + "=" * 80)
    print("AUTOMATION FRAMEWORK INTEGRATION")
    print("=" * 80)

    # Import automation framework components
    from automation.core.context import Context

    system = PromptingSystem()

    # Create automation context
    automation_context = Context(
        dry_run=True,
        extra_data={
            "prompt": "Analyze this codebase structure and suggest improvements",
            "mode": "ide",
            "enable_data_loop": False,
        },
    )

    print("Creating automation task...")

    # Create task configuration
    task_config = system.create_automation_task(
        task_name="codebase_analysis",
        prompt="Analyze this codebase structure and suggest improvements",
        mode="ide",
    )

    print(f"Task configuration: {task_config}")

    # Run the task
    print("\nRunning automation task...")
    await system.process_prompt_task(automation_context)


async def demo_workflow_integration():
    """Demonstrate integration with workflow macro system"""

    print("\n" + "=" * 80)
    print("WORKFLOW MACRO INTEGRATION")
    print("=" * 80)

    system = PromptingSystem()

    # Define phases similar to existing macro system
    phases = {
        "phase_a_baseline": "Establish baseline analysis of the codebase",
        "phase_b_enrichment": "Enrich analysis with external data sources",
        "phase_c_patch": "Apply corrections and improvements",
        "phase_d_finalize": "Finalize and merge all improvements",
    }

    print("Creating workflow integration...")
    integration_config = system.integrate_with_workflow_macro(phases)

    print(f"Integration phases: {len(integration_config['phases'])}")
    print(
        f"Priority map: {integration_config['deterministic_merge_config']['priority_map']}"
    )

    # This would integrate with the existing workflows/macro.py system
    print("Integration configuration created successfully!")


async def main():
    """Run all demonstrations"""

    print("Starting Multi-Mode Prompting System Demonstrations...")

    # Run mode demonstrations
    await demo_all_modes()

    # Run data loop demonstration
    await demo_data_loop()

    # Run automation integration
    await demo_automation_integration()

    # Run workflow integration
    await demo_workflow_integration()

    print("\n" + "=" * 80)
    print("ALL DEMONSTRATIONS COMPLETED")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
