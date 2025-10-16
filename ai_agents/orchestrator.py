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
AI Agent Orchestration System
Provides human-AI collaboration workflows using OpenAI Agents SDK
Supports both OpenAI and local Ollama models for testing
"""

import asyncio
import logging
import random
import time
from typing import Any, Dict, List

from agents import Agent, Runner

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Rate limit mitigation: Advanced retry decorator with concurrency control
def retry_with_exponential_backoff(
    func,
    initial_delay: float = 1,
    exponential_base: float = 2,
    jitter: bool = True,
    max_retries: int = 4,
    errors: tuple = (Exception,),
):
    """Advanced retry decorator with exponential backoff and proper error handling."""

    def wrapper(*args, **kwargs):
        # Initialize variables
        num_retries = 0
        delay = initial_delay

        # Loop until a successful response or max_retries is hit
        while True:
            try:
                return func(*args, **kwargs)

            # Retry on specific errors
            except errors as e:
                error_code = (
                    getattr(e, "status_code", None)
                    or getattr(e, "code", None)
                    or "unknown"
                )
                error_type = getattr(e, "type", None) or "unknown"

                # Check if max retries has been reached
                if num_retries >= max_retries:
                    logger.error(
                        f"Maximum number of retries ({max_retries}) exceeded. Final error: {str(e)}"
                    )
                    raise Exception(
                        f"Maximum number of retries ({max_retries}) exceeded. Last error: {str(e)}"
                    )

                # Handle insufficient_quota - don't retry
                if error_code == 429 and error_type == "insufficient_quota":
                    logger.error(
                        "Quota exhausted. Halting workflow as per requirements."
                    )
                    raise RuntimeError("Quota exhausted. Halting workflow.")

                # Handle rate limit errors
                if error_code == 429 or "rate_limit" in str(e).lower():
                    num_retries += 1
                    # Calculate delay with exponential backoff and jitter
                    delay *= exponential_base * (1 + jitter * random.random())
                    # Cap delay at 8 seconds as per requirements
                    delay = min(delay, 8)

                    logger.warning(
                        f"[429] Rate limit hit. Retrying in {delay:.2f}s... (attempt {num_retries}/{max_retries})"
                    )
                    time.sleep(delay)
                else:
                    # For non-rate-limit errors, still retry but with shorter delays
                    num_retries += 1
                    delay = min(delay * 1.5, 4)  # Shorter delays for other errors

                    logger.warning(
                        f"API error encountered. Retrying in {delay:.2f}s... (attempt {num_retries}/{max_retries})"
                    )
                    time.sleep(delay)

            # Raise exceptions for any errors not specified
            except Exception as e:
                raise e

    return wrapper


def _infer_capabilities_from_type(agent_type: str, agent_name: str) -> List[str]:
    """Infer capabilities from agent type and name"""
    capabilities_map = {
        "architect": ["design", "planning", "architecture", "system_design"],
        "reviewer": ["code_review", "security", "quality_assurance", "best_practices"],
        "tester": ["testing", "automation", "quality_assurance", "test_design"],
        "implementer": ["coding", "implementation", "debugging"],
        "general": ["analysis", "problem_solving"],
    }

    base_caps = capabilities_map.get(agent_type.lower(), ["analysis"])

    # Add capabilities from agent name
    name_lower = agent_name.lower()
    if "security" in name_lower:
        base_caps.append("security")
    if "performance" in name_lower:
        base_caps.append("performance")
    if "api" in name_lower:
        base_caps.append("api_design")

    return list(set(base_caps))  # Remove duplicates


class AIAgentOrchestrator:
    """Orchestrates AI agents for collaborative task completion with advanced rate limiting"""

    def __init__(
        self,
        max_retries: int = 4,
        initial_delay: float = 1.0,
        max_concurrent: int = 2,
        enable_knowledge_layer: bool = True,
    ):
        self.agents = {}
        self.tasks = []
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.completed_tasks = set()  # Track completed tasks to avoid duplicates
        self.failed_tasks = set()  # Track failed tasks for adaptive throttling

        # Knowledge layer integration
        self.knowledge_layer = None
        if enable_knowledge_layer:
            try:
                from utils.safe_imports import get_safe_agent_knowledge_layer

                self.knowledge_layer = get_safe_agent_knowledge_layer(enable_kg=True)
                logger.info("Knowledge layer enabled for agent collaboration")
            except ImportError as e:
                logger.warning(
                    f"Knowledge layer not available - agents will work independently: {e}"
                )

    def create_agent(
        self,
        name: str,
        instructions: str,
        tools: List[Any] = None,
        handoffs: List[Agent] = None,
        model: str = "gpt-4o-mini",
        task_importance: str = "basic",
        agent_type: str = "general",
        capabilities: List[str] = None,
    ):
        """Create a new AI agent using OpenAI Agents SDK

        Args:
            model: Model to use (defaults to gpt-4o-mini for cost efficiency, can be overridden)
            task_importance: "important" (uses gpt-4o) or "basic" (uses gpt-4o-mini)
            agent_type: Type of agent (architect, reviewer, tester, etc.)
            capabilities: List of agent capabilities for knowledge layer
        """
        if model == "gpt-4o" and task_importance == "basic":
            model = "gpt-4o-mini"
        elif model is None:
            model = "gpt-4o" if task_importance == "important" else "gpt-4o-mini"

        agent = Agent(
            name=name,
            instructions=instructions,
            tools=tools or [],
            handoffs=handoffs or [],
            model=model,
        )
        self.agents[name] = agent

        # Register agent in knowledge layer
        if self.knowledge_layer:
            caps = capabilities or _infer_capabilities_from_type(agent_type, name)
            self.knowledge_layer.register_agent(
                agent_name=name,
                agent_type=agent_type,
                capabilities=caps,
                metadata={
                    "instructions": instructions[:200]
                },  # First 200 chars of instructions
            )
            logger.info(
                f"Agent {name} registered in knowledge layer with {len(caps)} capabilities"
            )

        return agent

    def add_task(self, description: str, agent_name: str, expected_output: str = ""):
        """Add a task for an agent to complete"""
        if agent_name not in self.agents:
            raise ValueError(f"Agent {agent_name} not found")

        task = {
            "description": description,
            "agent_name": agent_name,
            "expected_output": expected_output,
        }
        self.tasks.append(task)
        return task

    async def execute_workflow(self) -> Dict[str, Any]:
        """Execute the complete agent workflow with advanced rate limiting and concurrency control"""
        results = []
        total_tasks = len(self.tasks)

        logger.info(
            f"Starting workflow execution with {total_tasks} tasks, max_concurrent={self.max_concurrent}"
        )

        # Group tasks by agent type for sequential execution
        agent_groups = self._group_tasks_by_agent()

        for group_name, group_tasks in agent_groups.items():
            logger.info(f"Executing {group_name} group with {len(group_tasks)} tasks")

            # Execute tasks in this group concurrently (up to max_concurrent)
            group_results = await self._execute_task_group(group_tasks)
            results.extend(group_results)

            # Adaptive throttling: Reduce concurrency if too many failures
            failed_count = len(
                [r for r in group_results if r.get("status") == "failed"]
            )
            if failed_count > len(group_tasks) // 2:  # More than 50% failures
                self._reduce_concurrency()
                logger.warning(
                    f"High failure rate detected. Reduced concurrency to {self.max_concurrent}"
                )

        # Calculate final statistics
        successful_tasks = len([r for r in results if r.get("status") == "success"])
        failed_tasks = len([r for r in results if r.get("status") == "failed"])

        return {
            "status": "completed" if successful_tasks > 0 else "failed",
            "result": results,
            "agents_used": list(self.agents.keys()),
            "tasks_completed": successful_tasks,
            "tasks_failed": failed_tasks,
            "total_tasks": total_tasks,
            "retry_config": {
                "max_retries": self.max_retries,
                "initial_delay": self.initial_delay,
                "max_concurrent": self.max_concurrent,
            },
        }

    def _group_tasks_by_agent(self) -> Dict[str, List[Dict]]:
        """Group tasks by agent type for sequential execution"""
        groups = {"architect": [], "code_reviewer": [], "test_engineer": []}

        for task in self.tasks:
            agent_name = task.get("agent_name", "")
            if "architect" in agent_name.lower():
                groups["architect"].append(task)
            elif (
                "code_reviewer" in agent_name.lower()
                or "reviewer" in agent_name.lower()
            ):
                groups["code_reviewer"].append(task)
            elif "test" in agent_name.lower() or "engineer" in agent_name.lower():
                groups["test_engineer"].append(task)
            else:
                # Default to architect group for unknown agents
                groups["architect"].append(task)

        return groups

    async def _execute_task_group(self, group_tasks: List[Dict]) -> List[Dict]:
        """Execute a group of tasks concurrently with rate limiting"""
        results = []

        # Create tasks for concurrent execution
        concurrent_tasks = []
        for task in group_tasks:
            task_future = self._execute_single_task_with_retry(task)
            concurrent_tasks.append(task_future)

        # Execute all tasks in the group concurrently
        if concurrent_tasks:
            group_results = await asyncio.gather(
                *concurrent_tasks, return_exceptions=True
            )

            # Process results
            for i, result in enumerate(group_results):
                task = group_tasks[i]
                if isinstance(result, Exception):
                    # Task failed completely
                    logger.error(
                        f"Task failed permanently: {task['description'][:50]}... - {str(result)}"
                    )
                    results.append(
                        {
                            "task": task,
                            "output": f"Task failed: {str(result)}",
                            "status": "failed",
                        }
                    )
                else:
                    results.append(result)

        return results

    async def _execute_single_task_with_retry(self, task: Dict) -> Dict:
        """Execute a single task with scoped retry logic and jitter"""
        task_id = f"{task['agent_name']}_{hash(task['description'])}"

        # Skip if already completed
        if task_id in self.completed_tasks:
            logger.info(
                f"Skipping already completed task: {task['description'][:50]}..."
            )
            return {
                "task": task,
                "output": "Task already completed in previous run",
                "status": "skipped",
            }

        agent = self.agents[task["agent_name"]]
        input_text = task["description"]

        logger.info(
            f"Executing task: {task['description'][:50]}... with {task['agent_name']}"
        )

        # Add random jitter to prevent synchronized spikes
        jitter_delay = random.uniform(0.5, 2.0)
        logger.debug(f"Adding jitter delay: {jitter_delay:.2f}s")
        await asyncio.sleep(jitter_delay)

        # Implement retry logic with semaphore
        delay = self.initial_delay
        for attempt in range(self.max_retries + 1):  # +1 for initial attempt
            try:
                async with self.semaphore:  # Concurrency control
                    result = await Runner.run(agent, input_text)

                # Success - mark as completed and log
                self.completed_tasks.add(task_id)
                logger.info(f"Task completed successfully after {attempt} attempts")

                return {
                    "task": task,
                    "output": result.final_output,
                    "status": "success",
                    "attempts": attempt + 1,
                }

            except Exception as e:
                error_code = (
                    getattr(e, "status_code", None)
                    or getattr(e, "code", None)
                    or "unknown"
                )
                error_type = getattr(e, "type", None) or "unknown"

                # Handle insufficient_quota - don't retry
                if error_code == 429 and error_type == "insufficient_quota":
                    logger.error(
                        "Quota exhausted. Halting workflow as per requirements."
                    )
                    self.failed_tasks.add(task_id)
                    raise RuntimeError("Quota exhausted. Halting workflow.")

                # Check if we should retry
                if attempt >= self.max_retries:
                    logger.error(
                        f"Task failed after {self.max_retries} retries: {task['description'][:50]}... - {str(e)}"
                    )
                    self.failed_tasks.add(task_id)
                    return {
                        "task": task,
                        "output": f"Failed after {self.max_retries} retries: {str(e)}",
                        "status": "failed",
                        "attempts": attempt + 1,
                    }

                # Calculate delay for retry
                if error_code == 429 or "rate_limit" in str(e).lower():
                    # Exponential backoff for rate limits
                    delay *= 2 * (1 + random.random() * 0.5)  # Add jitter
                    delay = min(delay, 8)  # Cap at 8 seconds
                    logger.warning(
                        f"[429] Rate limit hit. Retrying in {delay:.2f}s... (attempt {attempt + 1}/{self.max_retries + 1})"
                    )
                else:
                    # Shorter delay for other errors
                    delay = min(delay * 1.5, 4)
                    logger.warning(
                        f"API error. Retrying in {delay:.2f}s... (attempt {attempt + 1}/{self.max_retries + 1})"
                    )

                await asyncio.sleep(delay)

    def _reduce_concurrency(self):
        """Reduce concurrency when high failure rates are detected"""
        if self.max_concurrent > 1:
            self.max_concurrent -= 1
            self.semaphore = asyncio.Semaphore(self.max_concurrent)
            logger.info(
                f"Adaptive throttling: Reduced concurrency to {self.max_concurrent}"
            )


# Pre-configured agent templates
class AgentTemplates:
    """Factory for common AI agent types"""

    @staticmethod
    def create_code_reviewer():
        """Create a code review agent (important task - uses gpt-4o for complex analysis)"""
        return {
            "name": "code_reviewer",
            "instructions": "You are an expert Senior Code Reviewer. Analyze code for quality, security, best practices, and architectural concerns. Provide detailed, actionable recommendations with specific code examples where relevant.",
            "tools": [],  # Add code analysis tools here
            "handoffs": [],
            "task_importance": "important",  # Uses gpt-4o for detailed analysis
        }

    @staticmethod
    def create_test_engineer():
        """Create a test engineering agent (basic task - uses gpt-4o-mini for efficiency)"""
        return {
            "name": "test_engineer",
            "instructions": "You are an expert Test Automation Engineer. Create comprehensive test strategies, identify test cases, and evaluate testing approaches. Focus on practical, implementable testing solutions.",
            "tools": [],  # Add testing tools here
            "handoffs": [],
            "task_importance": "basic",  # Uses gpt-4o-mini for cost efficiency
        }

    @staticmethod
    def create_architect():
        """Create a system architect agent (important task - uses gpt-4o for complex design)"""
        return {
            "name": "architect",
            "instructions": "You are an expert System Architect. Design scalable, maintainable system architectures and provide strategic technical direction. Consider trade-offs, scalability, and long-term maintainability.",
            "tools": [],  # Add design tools here
            "handoffs": [],
            "task_importance": "important",  # Uses gpt-4o for architectural reasoning
        }


# Example usage
async def demo_agent_workflow():
    """Demonstrate agent collaboration with handoffs"""
    orchestrator = AIAgentOrchestrator()

    # Create agents
    reviewer_config = AgentTemplates.create_code_reviewer()
    reviewer = orchestrator.create_agent(**reviewer_config)

    architect_config = AgentTemplates.create_architect()
    architect = orchestrator.create_agent(**architect_config)

    # Set up handoffs for collaboration
    reviewer.handoffs = [architect]
    architect.handoffs = [reviewer]

    # Add tasks
    orchestrator.add_task(
        "Review the codebase_visualizer.py for code quality issues",
        "code_reviewer",
        "Detailed code review report with recommendations",
    )

    orchestrator.add_task(
        "Design an improved architecture for the visualization system based on the code review",
        "architect",
        "Architecture diagram and implementation plan",
    )

    # Execute workflow
    result = await orchestrator.execute_workflow()
    return result


# Example usage with cheaper OpenAI models
async def demo_agent_workflow_cheap():
    """Demonstrate agent collaboration using cost-effective OpenAI models"""
    try:
        orchestrator = AIAgentOrchestrator()

        # Create agents with basic task importance (uses gpt-4o-mini)
        reviewer = orchestrator.create_agent(
            name="code_reviewer",
            instructions="You are an expert Senior Code Reviewer. Review code for quality, security, and best practices. Provide detailed recommendations.",
            task_importance="basic",  # Forces gpt-4o-mini usage
        )

        architect = orchestrator.create_agent(
            name="architect",
            instructions="You are an expert System Architect. Design scalable, maintainable system architectures.",
            task_importance="basic",  # Forces gpt-4o-mini usage
        )

        # Set up handoffs for collaboration
        reviewer.handoffs = [architect]
        architect.handoffs = [reviewer]

        # Add tasks
        orchestrator.add_task(
            "Review this Python function for code quality: def hello(): print('Hello World')",
            "code_reviewer",
            "Detailed code review report with recommendations",
        )

        orchestrator.add_task(
            "Design an improved architecture for a simple greeting application",
            "architect",
            "Architecture diagram and implementation plan",
        )

        # Execute workflow
        result = await orchestrator.execute_workflow()
        return result

    except Exception as e:
        print(f"Cheap model demo failed: {e}")
        return {"status": "failed", "error": str(e)}


# Ollama integration (requires custom setup)
async def demo_agent_workflow_ollama():
    """Note: OpenAI Agents SDK doesn't natively support Ollama.
    For local models, consider using LiteLLM or custom model providers.

    Alternative approaches:
    1. Use LiteLLM: pip install litellm
    2. Use vLLM or other local inference servers
    3. Wait for OpenAI budget reset (17 days)
    4. Use free tiers from other providers
    """
    print("Ollama integration not supported in current OpenAI Agents SDK")
    print("Recommended alternatives:")
    print("- Use LiteLLM for Ollama: https://docs.litellm.ai/")
    print("- Use cheaper OpenAI models: gpt-4o-mini, gpt-3.5-turbo")
    print("- Wait for budget reset in 17 days")
    return {"status": "not_supported"}


# Practical code analysis example
def create_code_analysis_workflow(
    max_retries: int = 4, initial_delay: float = 1.0, max_concurrent: int = 3
):
    """Create a workflow for analyzing codebase files with optimized settings"""
    orchestrator = AIAgentOrchestrator(
        max_retries=max_retries,
        initial_delay=initial_delay,
        max_concurrent=max_concurrent,
    )

    # Create specialized agents for different aspects
    reviewer = orchestrator.create_agent(**AgentTemplates.create_code_reviewer())
    architect = orchestrator.create_agent(**AgentTemplates.create_architect())
    tester = orchestrator.create_agent(**AgentTemplates.create_test_engineer())

    # Set up collaborative handoffs
    reviewer.handoffs = [architect, tester]
    architect.handoffs = [tester, reviewer]
    tester.handoffs = [reviewer]

    return orchestrator


async def demo_practical_usage():
    """Demonstrate practical usage of agents for codebase analysis with rate limit handling"""
    print("=== Practical Codebase Analysis Demo with Rate Limit Handling ===")
    print("This demo shows how agents handle API rate limits automatically")
    print()

    # Setup workflow with custom rate limit settings
    print("Setting up workflow with aggressive retry settings...")
    orchestrator = create_code_analysis_workflow(max_retries=3, initial_delay=0.5)

    # Example tasks that would be performed on actual codebase
    tasks = [
        ("Review the authentication logic in the codebase", "code_reviewer"),
        ("Design a better error handling system", "architect"),
        ("Create comprehensive tests for API endpoints", "test_engineer"),
        ("Analyze security vulnerabilities in data processing", "code_reviewer"),
        ("Architect a scalable caching layer", "architect"),
    ]

    # Add tasks to workflow
    for task_desc, agent_name in tasks:
        orchestrator.add_task(task_desc, agent_name)

    print(
        f"Workflow created with {len(orchestrator.agents)} agents and {len(orchestrator.tasks)} tasks"
    )
    print(
        f"Rate limit config: max_retries={orchestrator.max_retries}, initial_delay={orchestrator.initial_delay}s"
    )
    print()

    # Show agent configurations
    print("Agents configured:")
    for name, agent in orchestrator.agents.items():
        model = getattr(agent, "model", "unknown")
        handoffs = [h.name for h in agent.handoffs] if agent.handoffs else []
        print(f"  - {name}: {model} with {len(handoffs)} handoff options")

    print()
    print("Tasks queued:")
    for i, task in enumerate(orchestrator.tasks, 1):
        print(f"  {i}. {task['description']}")
        print(f"     -> Assigned to: {task['agent_name']}")

    print()
    print("=== Rate Limit Handling Features ===")
    print("* Exponential backoff with jitter")
    print("* Automatic retry on API errors")
    print("* Configurable retry limits")
    print("* Progress tracking and error reporting")
    print("* Graceful failure handling")
    print()

    print("=== Workflow Ready for Execution ===")
    print("When API quota is available, run:")
    print("  result = await orchestrator.execute_workflow()")
    print()
    print("The system will automatically handle rate limits by:")
    print("1. Retrying failed requests with increasing delays")
    print("2. Adding random jitter to prevent thundering herd")
    print("3. Tracking success/failure rates")
    print("4. Providing detailed error reporting")

    return {
        "status": "ready",
        "agents_count": len(orchestrator.agents),
        "tasks_count": len(orchestrator.tasks),
        "orchestrator": orchestrator,
        "rate_limit_config": {
            "max_retries": orchestrator.max_retries,
            "initial_delay": orchestrator.initial_delay,
        },
    }


if __name__ == "__main__":
    # Run practical demo
    asyncio.run(demo_practical_usage())
