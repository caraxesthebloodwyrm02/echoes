"""
Business Initiative Workflow

This module implements a multi-agent workflow for business initiative planning.
It includes agents for triaging requests, generating launch plans, and collecting missing information.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from .agent import Agent
from .models import AgentConfig, ModelSettings


class AgentRole(str, Enum):
    """Roles that agents can take in the workflow."""

    TRIAGE = "triage"
    LAUNCH_HELPER = "launch_helper"
    GET_DATA = "get_data"


@dataclass
class AgentStep:
    """Represents a single step in the workflow."""

    agent_name: str
    role: AgentRole
    instructions: str
    input_data: Dict[str, Any]
    timestamp: str
    output: Optional[Dict[str, Any]] = None
    success: Optional[bool] = None
    duration_ms: Optional[float] = None


@dataclass
class WorkflowResult:
    """Result of a workflow execution."""

    success: bool
    output: Dict[str, Any]
    steps: List[Dict[str, Any]]
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class TriageSchema(BaseModel):
    """Schema for Triage agent output."""

    has_all_details: bool = Field(
        ..., description="Whether all required details are present"
    )
    initiative_goal: str = Field(..., description="The goal of the initiative")
    target_timeframe: str = Field(
        ..., description="Target completion date or timeframe"
    )
    current_resources: str = Field(..., description="Available resources or capacity")


class BusinessInitiativeWorkflow:
    """Orchestrates the business initiative planning workflow."""

    def __init__(self, assistant):
        """Initialize with reference to assistant."""
        self.assistant = assistant
        self.conversation_history: List[Dict[str, Any]] = []
        self.workflow_counter = 0

        # Initialize agents
        self.triage_agent = self._create_triage_agent()
        self.launch_helper_agent = self._create_launch_helper_agent()
        self.get_data_agent = self._create_get_data_agent()

    def _create_triage_agent(self) -> Agent:
        """Create and configure the Triage agent."""
        return Agent(
            name="Triage",
            config=AgentConfig(
                model_settings=ModelSettings(
                    model_name="gpt-4",
                    temperature=0.2,
                    max_tokens=1000,
                ),
                system_prompt="""You are an assistant that gathers the key details needed to create a business initiative plan.

Look through the conversation to extract the following:
1. Initiative goal (what the team or organization aims to achieve)
2. Target completion date or timeframe
3. Available resources or current capacity (e.g., headcount, budget, or tool access)

If all three details are present anywhere in the conversation, respond with a JSON object containing:
- has_all_details: true
- initiative_goal: <user-provided goal>
- target_timeframe: <user-provided date or period>
- current_resources: <user-provided resources>""",
            ),
        )

    def _create_launch_helper_agent(self) -> Agent:
        """Create and configure the Launch Helper agent."""
        return Agent(
            name="Launch Helper",
            config=AgentConfig(
                model_settings=ModelSettings(
                    model_name="gpt-4",
                    temperature=0.7,
                    max_tokens=2000,
                ),
                system_prompt="""You are an expert at helping teams launch new business initiatives.

Your task is to create a comprehensive, actionable plan that includes:
1. Clear objectives and success metrics
2. Key milestones and timeline
3. Resource allocation
4. Risk assessment and mitigation strategies
5. Dependencies and requirements

Provide your response in a structured markdown format with clear sections and bullet points.

Consider the user's initiative goal, target timeframe, and available resources when creating the plan.""",
            ),
        )

    def _create_get_data_agent(self) -> Agent:
        """Create and configure the Get Data agent."""
        return Agent(
            name="Get Data",
            config=AgentConfig(
                model_settings=ModelSettings(
                    model_name="gpt-4",
                    temperature=0.3,
                    max_tokens=500,
                ),
                system_prompt="""Your role is to collect missing information needed to create a business initiative plan.

Politely ask the user for any of the following that are missing:
1. Initiative goal (what are you trying to achieve?)
2. Target completion date or timeframe
3. Available resources (team size, budget, tools)

Be concise and ask one clear question at a time. Once you have all the information, summarize it back to the user for confirmation.""",
            ),
        )

    async def run_workflow(
        self, user_input: str, context: Optional[Dict[str, Any]] = None
    ) -> WorkflowResult:
        """
        Run the business initiative planning workflow.

        Args:
            user_input: The user's initial request or query
            context: Additional context for the workflow

        Returns:
            WorkflowResult containing the execution results
        """
        self.workflow_counter += 1
        workflow_id = f"biz_init_{self.workflow_counter}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"

        # Initialize workflow result
        result = WorkflowResult(
            success=False, output={"workflow_id": workflow_id}, steps=[]
        )

        # Add user input to conversation history
        self.conversation_history.append(
            {
                "role": "user",
                "content": user_input,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

        try:
            # Step 1: Triage the request
            triage_step = await self._execute_step(
                agent=self.triage_agent,
                role=AgentRole.TRIAGE,
                input_data={"query": user_input, "context": context or {}},
                workflow_id=workflow_id,
            )
            result.steps.append(self._format_step_result(triage_step))

            # Parse triage result
            try:
                triage_result = TriageSchema.model_validate_json(
                    triage_step.output["response"]
                )
                result.output["triage"] = triage_result.model_dump()

                if triage_result.has_all_details:
                    # Step 2: If we have all details, generate a launch plan
                    launch_step = await self._execute_step(
                        agent=self.launch_helper_agent,
                        role=AgentRole.LAUNCH_HELPER,
                        input_data={
                            "initiative_goal": triage_result.initiative_goal,
                            "target_timeframe": triage_result.target_timeframe,
                            "current_resources": triage_result.current_resources,
                            "context": context or {},
                        },
                        workflow_id=workflow_id,
                    )
                    result.steps.append(self._format_step_result(launch_step))
                    result.output["launch_plan"] = launch_step.output["response"]
                    result.success = True
                else:
                    # Step 2a: If we're missing details, ask for them
                    data_step = await self._execute_step(
                        agent=self.get_data_agent,
                        role=AgentRole.GET_DATA,
                        input_data={
                            "missing_fields": {
                                "initiative_goal": not bool(
                                    triage_result.initiative_goal
                                ),
                                "target_timeframe": not bool(
                                    triage_result.target_timeframe
                                ),
                                "current_resources": not bool(
                                    triage_result.current_resources
                                ),
                            },
                            "context": context or {},
                        },
                        workflow_id=workflow_id,
                    )
                    result.steps.append(self._format_step_result(data_step))
                    result.output["missing_info_request"] = data_step.output["response"]
                    result.success = False  # Incomplete, needs user input

            except Exception as e:
                self._log_error(f"Error parsing triage result: {str(e)}")
                result.output["error"] = f"Failed to process request: {str(e)}"
                result.success = False

        except Exception as e:
            self._log_error(f"Workflow execution failed: {str(e)}")
            result.output["error"] = f"Workflow execution failed: {str(e)}"
            result.success = False

        return result

    async def _execute_step(
        self,
        agent: Agent,
        role: AgentRole,
        input_data: Dict[str, Any],
        workflow_id: str,
    ) -> AgentStep:
        """Execute a single agent step in the workflow."""
        start_time = datetime.now(timezone.utc)
        step = AgentStep(
            agent_name=agent.name,
            role=role,
            instructions=agent.config.system_prompt,
            input_data=input_data,
            timestamp=start_time.isoformat(),
        )

        try:
            # Execute the agent
            response = await agent.process(
                query=input_data.get("query", ""), context=input_data.get("context", {})
            )

            # Record successful execution
            step.output = {"response": response}
            step.success = True

            # Add to conversation history
            self.conversation_history.append(
                {
                    "role": "assistant",
                    "content": response,
                    "agent": agent.name,
                    "workflow_id": workflow_id,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            )

        except Exception as e:
            error_msg = f"{agent.name} execution failed: {str(e)}"
            self._log_error(error_msg)
            step.output = {"error": error_msg}
            step.success = False

        # Calculate duration
        step.duration_ms = (
            datetime.now(timezone.utc) - start_time
        ).total_seconds() * 1000

        return step

    def _format_step_result(self, step: AgentStep) -> Dict[str, Any]:
        """Format a step result for the workflow output."""
        return {
            "agent": step.agent_name,
            "role": step.role.value,
            "timestamp": step.timestamp,
            "duration_ms": step.duration_ms,
            "success": step.success,
            "input": step.input_data,
            "output": step.output,
        }

    def _log_error(self, message: str):
        """Log an error message."""
        # In a real implementation, this would use proper logging
        print(f"[ERROR] {message}", flush=True)


# Example usage
if __name__ == "__main__":
    import asyncio
    from ..core import EchoesAssistantV2  # Assuming this is the correct import path

    async def test_workflow():
        assistant = EchoesAssistantV2()  # Initialize with appropriate config
        workflow = BusinessInitiativeWorkflow(assistant)

        # Test with a sample input
        result = await workflow.run_workflow(
            "We need to launch a new customer portal by Q2 2024. "
            "We have a team of 3 developers and a budget of $50,000. "
            "The goal is to improve customer self-service and reduce support tickets by 30%."
        )

        print("\nWorkflow Result:")
        print(f"Success: {result.success}")
        print("Output:", result.output)

        if result.success:
            print("\nLaunch Plan:")
            print(result.output.get("launch_plan", "No launch plan generated"))

    asyncio.run(test_workflow())
