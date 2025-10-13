"""
AI Agent Orchestration System
Provides human-AI collaboration workflows using CrewAI framework
"""

import asyncio
from typing import Any, Dict, List

from crewai import Agent, Crew, Task
from langchain.tools import Tool


class AIAgentOrchestrator:
    """Orchestrates AI agents for collaborative task completion"""

    def __init__(self):
        self.agents = {}
        self.tasks = []

    def create_agent(self, name: str, role: str, goal: str, tools: List[Tool] = None):
        """Create a new AI agent"""
        agent = Agent(
            role=role,
            goal=goal,
            backstory=f"You are an expert {role} AI assistant working collaboratively on complex tasks.",
            tools=tools or [],
            verbose=True,
        )
        self.agents[name] = agent
        return agent

    def add_task(self, description: str, agent_name: str, expected_output: str):
        """Add a task for an agent to complete"""
        if agent_name not in self.agents:
            raise ValueError(f"Agent {agent_name} not found")

        task = Task(description=description, agent=self.agents[agent_name], expected_output=expected_output)
        self.tasks.append(task)
        return task

    async def execute_workflow(self) -> Dict[str, Any]:
        """Execute the complete agent workflow"""
        crew = Crew(agents=list(self.agents.values()), tasks=self.tasks, verbose=True)

        result = await crew.kickoff_async()
        return {
            "status": "completed",
            "result": str(result),
            "agents_used": list(self.agents.keys()),
            "tasks_completed": len(self.tasks),
        }


# Pre-configured agent templates
class AgentTemplates:
    """Factory for common AI agent types"""

    @staticmethod
    def create_code_reviewer():
        """Create a code review agent"""
        return {
            "name": "code_reviewer",
            "role": "Senior Code Reviewer",
            "goal": "Review code for quality, security, and best practices",
            "tools": [],  # Add code analysis tools
        }

    @staticmethod
    def create_test_engineer():
        """Create a test engineering agent"""
        return {
            "name": "test_engineer",
            "role": "Test Automation Engineer",
            "goal": "Create comprehensive test suites and validate functionality",
            "tools": [],  # Add testing tools
        }

    @staticmethod
    def create_architect():
        """Create a system architect agent"""
        return {
            "name": "architect",
            "role": "System Architect",
            "goal": "Design scalable, maintainable system architectures",
            "tools": [],  # Add design tools
        }


# Example usage
async def demo_agent_workflow():
    """Demonstrate agent collaboration"""
    orchestrator = AIAgentOrchestrator()

    # Create agents
    reviewer_config = AgentTemplates.create_code_reviewer()
    orchestrator.create_agent(**reviewer_config)

    architect_config = AgentTemplates.create_architect()
    orchestrator.create_agent(**architect_config)

    # Add tasks
    orchestrator.add_task(
        "Review the codebase_visualizer.py for code quality issues",
        "code_reviewer",
        "Detailed code review report with recommendations",
    )

    orchestrator.add_task(
        "Design an improved architecture for the visualization system",
        "architect",
        "Architecture diagram and implementation plan",
    )

    # Execute workflow
    result = await orchestrator.execute_workflow()
    return result


if __name__ == "__main__":
    # Run demo
    asyncio.run(demo_agent_workflow())
