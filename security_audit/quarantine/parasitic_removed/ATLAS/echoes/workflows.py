"""
Echoes AI Workflow System

This module provides workflow management functionality for the Echoes AI Multi-Agent System.
"""

import asyncio
import logging
import uuid
from collections.abc import Callable
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from .config import Settings
from .exceptions import ValidationError, WorkflowError

logger = logging.getLogger(__name__)


class WorkflowStatus(str, Enum):
    """Workflow status enumeration."""

    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WorkflowType(str, Enum):
    """Workflow type enumeration."""

    BUSINESS_INITIATIVE = "business_initiative"
    DATA_PROCESSING = "data_processing"
    CONTENT_GENERATION = "content_generation"
    AUTOMATION = "automation"
    CUSTOM = "custom"


class WorkflowStep(BaseModel):
    """Workflow step model."""

    id: str = Field(..., description="Step ID")
    name: str = Field(..., description="Step name")
    description: str | None = Field(None, description="Step description")
    step_type: str = Field(..., description="Step type")
    config: dict[str, Any] = Field(
        default_factory=dict, description="Step configuration"
    )
    dependencies: list[str] = Field(
        default_factory=list, description="Step dependencies"
    )
    timeout: int = Field(300, description="Step timeout in seconds")
    retry_count: int = Field(3, description="Number of retries")
    status: str = Field("pending", description="Step status")
    result: dict[str, Any] | None = Field(None, description="Step result")
    error: str | None = Field(None, description="Step error message")
    started_at: datetime | None = Field(None, description="Step start time")
    completed_at: datetime | None = Field(None, description="Step completion time")


class WorkflowConfig(BaseModel):
    """Workflow configuration model."""

    name: str = Field(..., description="Workflow name")
    description: str | None = Field(None, description="Workflow description")
    workflow_type: WorkflowType = Field(..., description="Workflow type")
    steps: list[WorkflowStep] = Field(..., description="Workflow steps")
    config: dict[str, Any] = Field(
        default_factory=dict, description="Additional configuration"
    )
    timeout: int = Field(1800, description="Workflow timeout in seconds")
    retry_policy: dict[str, Any] = Field(
        default_factory=dict, description="Retry policy"
    )


class WorkflowExecution(BaseModel):
    """Workflow execution model."""

    id: str = Field(..., description="Execution ID")
    workflow_id: str = Field(..., description="Workflow ID")
    user_id: str = Field(..., description="User ID")
    input_data: dict[str, Any] = Field(default_factory=dict, description="Input data")
    output_data: dict[str, Any] = Field(default_factory=dict, description="Output data")
    status: WorkflowStatus = Field(WorkflowStatus.DRAFT, description="Execution status")
    steps: list[WorkflowStep] = Field(
        default_factory=list, description="Execution steps"
    )
    started_at: datetime | None = Field(None, description="Execution start time")
    completed_at: datetime | None = Field(None, description="Execution completion time")
    error_message: str | None = Field(None, description="Error message")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )


class Workflow(BaseModel):
    """Workflow model."""

    id: str = Field(..., description="Workflow ID")
    name: str = Field(..., description="Workflow name")
    description: str | None = Field(None, description="Workflow description")
    user_id: str = Field(..., description="User ID who owns the workflow")
    config: WorkflowConfig = Field(..., description="Workflow configuration")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    status: WorkflowStatus = Field(WorkflowStatus.DRAFT, description="Workflow status")
    execution_count: int = Field(0, description="Number of executions")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )


class WorkflowManager:
    """Manager for workflow operations."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.workflows: dict[str, Workflow] = {}
        self.executions: dict[str, WorkflowExecution] = {}
        self.step_handlers: dict[str, Callable] = {}
        self._initialized = False

    async def initialize(self):
        """Initialize the workflow manager."""
        if self._initialized:
            return

        logger.info("Initializing WorkflowManager...")

        # Register step handlers
        await self._register_step_handlers()

        # Load workflows from storage
        await self._load_workflows()

        self._initialized = True
        logger.info("WorkflowManager initialized successfully")

    async def cleanup(self):
        """Cleanup the workflow manager."""
        if not self._initialized:
            return

        logger.info("Cleaning up WorkflowManager...")

        # Save workflows to storage
        await self._save_workflows()

        self._initialized = False
        logger.info("WorkflowManager cleaned up successfully")

    async def create_workflow(self, user_id: str, config: WorkflowConfig) -> Workflow:
        """Create a new workflow."""
        # Validate configuration
        if not config.name.strip():
            raise ValidationError("Workflow name cannot be empty")

        if not config.steps:
            raise ValidationError("Workflow must have at least one step")

        # Check if user has reached workflow limit
        user_workflows = [w for w in self.workflows.values() if w.user_id == user_id]
        if len(user_workflows) >= self.settings.max_workflows_per_user:
            raise WorkflowError(
                f"User has reached maximum workflow limit of {self.settings.max_workflows_per_user}"
            )

        # Create workflow
        workflow_id = f"workflow_{len(self.workflows) + 1}"
        workflow = Workflow(
            id=workflow_id,
            name=config.name,
            description=config.description,
            user_id=user_id,
            config=config,
        )

        # Store workflow
        self.workflows[workflow_id] = workflow

        logger.info(f"Created workflow {workflow_id} for user {user_id}")
        return workflow

    async def get_workflow(self, workflow_id: str) -> Workflow | None:
        """Get a workflow by ID."""
        return self.workflows.get(workflow_id)

    async def update_workflow(
        self, workflow_id: str, config: WorkflowConfig
    ) -> Workflow:
        """Update a workflow's configuration."""
        workflow = await self.get_workflow(workflow_id)
        if not workflow:
            raise WorkflowError(
                f"Workflow not found: {workflow_id}", workflow_id=workflow_id
            )

        # Update workflow
        workflow.config = config
        workflow.updated_at = datetime.now(UTC)

        logger.info(f"Updated workflow {workflow_id}")
        return workflow

    async def delete_workflow(self, workflow_id: str) -> bool:
        """Delete a workflow."""
        if workflow_id not in self.workflows:
            raise WorkflowError(
                f"Workflow not found: {workflow_id}", workflow_id=workflow_id
            )

        # Delete workflow and its executions
        del self.workflows[workflow_id]

        # Remove executions for this workflow
        executions_to_delete = [
            exec_id
            for exec_id, execution in self.executions.items()
            if execution.workflow_id == workflow_id
        ]
        for exec_id in executions_to_delete:
            del self.executions[exec_id]

        logger.info(f"Deleted workflow {workflow_id}")
        return True

    async def list_workflows(self, user_id: str | None = None) -> list[Workflow]:
        """List workflows, optionally filtered by user."""
        workflows = list(self.workflows.values())
        if user_id:
            workflows = [w for w in workflows if w.user_id == user_id]
        return workflows

    async def execute_workflow(
        self, workflow_id: str, user_id: str, input_data: dict[str, Any]
    ) -> WorkflowExecution:
        """Execute a workflow."""
        workflow = await self.get_workflow(workflow_id)
        if not workflow:
            raise WorkflowError(
                f"Workflow not found: {workflow_id}", workflow_id=workflow_id
            )

        if workflow.user_id != user_id:
            raise WorkflowError(
                "Workflow does not belong to user", workflow_id=workflow_id
            )

        # Create execution
        execution_id = str(uuid.uuid4())
        execution = WorkflowExecution(
            id=execution_id,
            workflow_id=workflow_id,
            user_id=user_id,
            input_data=input_data,
            steps=[step.copy() for step in workflow.config.steps],
        )

        # Store execution
        self.executions[execution_id] = execution

        # Update workflow execution count
        workflow.execution_count += 1

        # Execute workflow asynchronously
        asyncio.create_task(self._run_workflow_execution(execution_id))

        logger.info(
            f"Started workflow execution {execution_id} for workflow {workflow_id}"
        )
        return execution

    async def get_execution(self, execution_id: str) -> WorkflowExecution | None:
        """Get a workflow execution by ID."""
        return self.executions.get(execution_id)

    async def cancel_execution(self, execution_id: str) -> WorkflowExecution:
        """Cancel a workflow execution."""
        execution = await self.get_execution(execution_id)
        if not execution:
            raise WorkflowError(f"Execution not found: {execution_id}")

        if execution.status in [
            WorkflowStatus.COMPLETED,
            WorkflowStatus.FAILED,
            WorkflowStatus.CANCELLED,
        ]:
            raise WorkflowError(
                f"Cannot cancel execution in status: {execution.status}"
            )

        execution.status = WorkflowStatus.CANCELLED
        execution.completed_at = datetime.now(UTC)

        logger.info(f"Cancelled workflow execution {execution_id}")
        return execution

    async def _run_workflow_execution(self, execution_id: str):
        """Run a workflow execution."""
        execution = await self.get_execution(execution_id)
        if not execution:
            return

        try:
            execution.status = WorkflowStatus.ACTIVE
            execution.started_at = datetime.now(UTC)

            # Execute steps in order
            for step in execution.steps:
                if execution.status != WorkflowStatus.ACTIVE:
                    break

                await self._execute_step(execution, step)

                # Check if step failed
                if step.status == "failed":
                    execution.status = WorkflowStatus.FAILED
                    execution.error_message = step.error
                    break

            # Mark as completed if successful
            if execution.status == WorkflowStatus.ACTIVE:
                execution.status = WorkflowStatus.COMPLETED

        except Exception as e:
            execution.status = WorkflowStatus.FAILED
            execution.error_message = str(e)
            logger.error(f"Workflow execution {execution_id} failed: {e}")

        finally:
            execution.completed_at = datetime.now(UTC)
            logger.info(
                f"Completed workflow execution {execution_id} with status: {execution.status}"
            )

    async def _execute_step(self, execution: WorkflowExecution, step: WorkflowStep):
        """Execute a single workflow step."""
        step.status = "running"
        step.started_at = datetime.now(UTC)

        try:
            # Get step handler
            handler = self.step_handlers.get(step.step_type)
            if not handler:
                raise WorkflowError(f"No handler for step type: {step.step_type}")

            # Execute step with timeout
            result = await asyncio.wait_for(
                handler(execution, step), timeout=step.timeout
            )

            step.status = "completed"
            step.result = result
            step.completed_at = datetime.now(UTC)

        except TimeoutError:
            step.status = "failed"
            step.error = f"Step timed out after {step.timeout} seconds"
            step.completed_at = datetime.now(UTC)

        except Exception as e:
            step.status = "failed"
            step.error = str(e)
            step.completed_at = datetime.now(UTC)

    async def _register_step_handlers(self):
        """Register step handlers."""
        # Register business initiative step handler
        self.step_handlers[
            "business_initiative_triage"
        ] = self._handle_business_initiative_triage
        self.step_handlers[
            "business_initiative_launch"
        ] = self._handle_business_initiative_launch
        self.step_handlers[
            "business_initiative_get_data"
        ] = self._handle_business_initiative_get_data

        # Register data processing step handler
        self.step_handlers["data_processing"] = self._handle_data_processing

        # Register content generation step handler
        self.step_handlers["content_generation"] = self._handle_content_generation

    async def _handle_business_initiative_triage(
        self, execution: WorkflowExecution, step: WorkflowStep
    ) -> dict[str, Any]:
        """Handle business initiative triage step."""
        # This would integrate with AI to triage the initiative
        await asyncio.sleep(1)  # Simulate processing

        # Simple triage logic
        initiative_type = execution.input_data.get("initiative_type", "unknown")

        if initiative_type in ["launch", "product", "service"]:
            return {"next_step": "launch_helper", "triage_result": "launch"}
        else:
            return {"next_step": "get_data", "triage_result": "data_request"}

    async def _handle_business_initiative_launch(
        self, execution: WorkflowExecution, step: WorkflowStep
    ) -> dict[str, Any]:
        """Handle business initiative launch step."""
        # This would integrate with launch helper system
        await asyncio.sleep(2)  # Simulate processing

        return {
            "launch_plan": "Created launch plan",
            "timeline": "30 days",
            "resources": ["team", "budget", "tools"],
        }

    async def _handle_business_initiative_get_data(
        self, execution: WorkflowExecution, step: WorkflowStep
    ) -> dict[str, Any]:
        """Handle business initiative get data step."""
        # This would integrate with data gathering systems
        await asyncio.sleep(1)  # Simulate processing

        return {
            "data_collected": "Market research data",
            "sources": ["industry_reports", "competitor_analysis", "market_trends"],
        }

    async def _handle_data_processing(
        self, execution: WorkflowExecution, step: WorkflowStep
    ) -> dict[str, Any]:
        """Handle data processing step."""
        # This would integrate with data processing systems
        await asyncio.sleep(2)  # Simulate processing

        return {
            "processed_data": "Data processed successfully",
            "records_processed": 1000,
            "output_format": "json",
        }

    async def _handle_content_generation(
        self, execution: WorkflowExecution, step: WorkflowStep
    ) -> dict[str, Any]:
        """Handle content generation step."""
        # This would integrate with AI content generation
        await asyncio.sleep(3)  # Simulate processing

        return {
            "generated_content": "Content generated successfully",
            "content_type": "blog_post",
            "word_count": 500,
        }

    async def _load_workflows(self):
        """Load workflows from storage (placeholder)."""
        # In production, this would load from database
        pass

    async def _save_workflows(self):
        """Save workflows to storage (placeholder)."""
        # In production, this would save to database
        pass


# Global workflow manager instance
_workflow_manager: WorkflowManager | None = None


def get_workflow_manager() -> WorkflowManager:
    """Get the global workflow manager instance."""
    global _workflow_manager
    if _workflow_manager is None:
        _workflow_manager = WorkflowManager(get_settings())
    return _workflow_manager


async def initialize_workflow_manager():
    """Initialize the global workflow manager."""
    manager = get_workflow_manager()
    await manager.initialize()


async def cleanup_workflow_manager():
    """Cleanup the global workflow manager."""
    manager = get_workflow_manager()
    await manager.cleanup()
