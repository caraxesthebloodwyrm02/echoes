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

# Example: Using the OpenAI Agents SDK in your Echoes project

import os
import sys

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_agents.orchestrator import create_code_analysis_workflow


async def analyze_codebase():
    """Example of using agents for codebase analysis"""

    # Create workflow with 3 specialized agents
    orchestrator = create_code_analysis_workflow()

    # Add specific tasks for your codebase
    orchestrator.add_task(
        "Review the pause_model.py file for code quality and potential improvements",
        "code_reviewer",
    )

    orchestrator.add_task(
        "Design an improved architecture for the speech processing pipeline",
        "architect",
    )

    orchestrator.add_task("Create unit tests for the orchestrator agent system", "test_engineer")

    # Execute the collaborative workflow
    print("Starting collaborative code analysis...")
    result = await orchestrator.execute_workflow()

    print(f"Analysis completed! Results: {len(result['result'])} tasks processed")

    # Process results
    for task_result in result["result"]:
        task = task_result["task"]
        output = task_result["output"]
        print(f"\n{task['agent_name'].upper()}: {task['description']}")
        print(f"Result: {output[:200]}...")


if __name__ == "__main__":
    # Uncomment when you have API quota available
    # asyncio.run(analyze_codebase())
    print("Agent orchestration system ready!")
    print("Uncomment the asyncio.run() line when API quota is available.")
