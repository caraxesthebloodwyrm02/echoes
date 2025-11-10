"""
Echoes AI Workflow Routes

This module provides workflow-related endpoints for the Echoes AI Multi-Agent System.
"""

import logging
from typing import Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from ..exceptions import ValidationError, WorkflowError, create_success_response
from ..workflows import WorkflowConfig, WorkflowType, get_workflow_manager

logger = logging.getLogger(__name__)

router = APIRouter()


class WorkflowStepRequest(BaseModel):
    """Workflow step request model."""

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


class CreateWorkflowRequest(BaseModel):
    """Create workflow request model."""

    name: str = Field(..., description="Workflow name")
    description: str | None = Field(None, description="Workflow description")
    workflow_type: WorkflowType = Field(..., description="Workflow type")
    steps: list[WorkflowStepRequest] = Field(..., description="Workflow steps")
    config: dict[str, Any] = Field(
        default_factory=dict, description="Additional configuration"
    )
    timeout: int = Field(1800, description="Workflow timeout in seconds")
    retry_policy: dict[str, Any] = Field(
        default_factory=dict, description="Retry policy"
    )


class UpdateWorkflowRequest(BaseModel):
    """Update workflow request model."""

    name: str | None = Field(None, description="Workflow name")
    description: str | None = Field(None, description="Workflow description")
    workflow_type: WorkflowType | None = Field(None, description="Workflow type")
    steps: list[WorkflowStepRequest] | None = Field(None, description="Workflow steps")
    config: dict[str, Any] = Field(
        default_factory=dict, description="Additional configuration"
    )
    timeout: int | None = Field(None, description="Workflow timeout in seconds")
    retry_policy: dict[str, Any] = Field(
        default_factory=dict, description="Retry policy"
    )


class ExecuteWorkflowRequest(BaseModel):
    """Execute workflow request model."""

    input_data: dict[str, Any] = Field(
        default_factory=dict, description="Input data for workflow"
    )


class WorkflowResponse(BaseModel):
    """Workflow response model."""

    id: str
    name: str
    description: str | None
    user_id: str
    workflow_type: str
    step_count: int
    created_at: str
    updated_at: str
    status: str
    execution_count: int
    metadata: dict[str, Any]


class WorkflowExecutionResponse(BaseModel):
    """Workflow execution response model."""

    id: str
    workflow_id: str
    user_id: str
    input_data: dict[str, Any]
    output_data: dict[str, Any]
    status: str
    step_count: int
    started_at: str | None
    completed_at: str | None
    error_message: str | None
    metadata: dict[str, Any]


@router.post("/create", response_model=WorkflowResponse)
async def create_workflow(
    request: CreateWorkflowRequest, user_id: str = Query(..., description="User ID")
):
    """Create a new workflow."""
    try:
        workflow_manager = get_workflow_manager()

        # Convert step requests to workflow steps
        steps = []
        for step_req in request.steps:
            from ..workflows import WorkflowStep

            step = WorkflowStep(
                id=step_req.id,
                name=step_req.name,
                description=step_req.description,
                step_type=step_req.step_type,
                config=step_req.config,
                dependencies=step_req.dependencies,
                timeout=step_req.timeout,
                retry_count=step_req.retry_count,
            )
            steps.append(step)

        config = WorkflowConfig(
            name=request.name,
            description=request.description,
            workflow_type=request.workflow_type,
            steps=steps,
            config=request.config,
            timeout=request.timeout,
            retry_policy=request.retry_policy,
        )

        workflow = await workflow_manager.create_workflow(user_id, config)

        response = WorkflowResponse(
            id=workflow.id,
            name=workflow.name,
            description=workflow.description,
            user_id=workflow.user_id,
            workflow_type=workflow.config.workflow_type.value,
            step_count=len(workflow.config.steps),
            created_at=workflow.created_at.isoformat(),
            updated_at=workflow.updated_at.isoformat(),
            status=workflow.status.value,
            execution_count=workflow.execution_count,
            metadata=workflow.metadata,
        )

        logger.info(f"Created workflow {workflow.id} for user {user_id}")
        return response

    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except WorkflowError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create workflow: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/list", response_model=list[WorkflowResponse])
async def list_workflows(
    user_id: str | None = Query(None, description="Filter by user ID")
):
    """List workflows."""
    try:
        workflow_manager = get_workflow_manager()
        workflows = await workflow_manager.list_workflows(user_id)

        responses = []
        for workflow in workflows:
            response = WorkflowResponse(
                id=workflow.id,
                name=workflow.name,
                description=workflow.description,
                user_id=workflow.user_id,
                workflow_type=workflow.config.workflow_type.value,
                step_count=len(workflow.config.steps),
                created_at=workflow.created_at.isoformat(),
                updated_at=workflow.updated_at.isoformat(),
                status=workflow.status.value,
                execution_count=workflow.execution_count,
                metadata=workflow.metadata,
            )
            responses.append(response)

        logger.info(f"Listed {len(responses)} workflows")
        return responses

    except Exception as e:
        logger.error(f"Failed to list workflows: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(workflow_id: str):
    """Get a workflow by ID."""
    try:
        workflow_manager = get_workflow_manager()
        workflow = await workflow_manager.get_workflow(workflow_id)

        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")

        response = WorkflowResponse(
            id=workflow.id,
            name=workflow.name,
            description=workflow.description,
            user_id=workflow.user_id,
            workflow_type=workflow.config.workflow_type.value,
            step_count=len(workflow.config.steps),
            created_at=workflow.created_at.isoformat(),
            updated_at=workflow.updated_at.isoformat(),
            status=workflow.status.value,
            execution_count=workflow.execution_count,
            metadata=workflow.metadata,
        )

        logger.info(f"Retrieved workflow {workflow_id}")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get workflow {workflow_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/{workflow_id}", response_model=WorkflowResponse)
async def update_workflow(
    workflow_id: str,
    request: UpdateWorkflowRequest,
    user_id: str = Query(..., description="User ID"),
):
    """Update a workflow."""
    try:
        workflow_manager = get_workflow_manager()

        # Get existing workflow
        existing_workflow = await workflow_manager.get_workflow(workflow_id)
        if not existing_workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")

        if existing_workflow.user_id != user_id:
            raise HTTPException(
                status_code=403, detail="Workflow does not belong to user"
            )

        # Convert step requests to workflow steps if provided
        steps = None
        if request.steps is not None:
            steps = []
            for step_req in request.steps:
                from ..workflows import WorkflowStep

                step = WorkflowStep(
                    id=step_req.id,
                    name=step_req.name,
                    description=step_req.description,
                    step_type=step_req.step_type,
                    config=step_req.config,
                    dependencies=step_req.dependencies,
                    timeout=step_req.timeout,
                    retry_count=step_req.retry_count,
                )
                steps.append(step)

        # Create updated config
        config = WorkflowConfig(
            name=request.name
            if request.name is not None
            else existing_workflow.config.name,
            description=request.description
            if request.description is not None
            else existing_workflow.config.description,
            workflow_type=request.workflow_type
            if request.workflow_type is not None
            else existing_workflow.config.workflow_type,
            steps=steps if steps is not None else existing_workflow.config.steps,
            config=request.config
            if request.config
            else existing_workflow.config.config,
            timeout=request.timeout
            if request.timeout is not None
            else existing_workflow.config.timeout,
            retry_policy=request.retry_policy
            if request.retry_policy
            else existing_workflow.config.retry_policy,
        )

        workflow = await workflow_manager.update_workflow(workflow_id, config)

        response = WorkflowResponse(
            id=workflow.id,
            name=workflow.name,
            description=workflow.description,
            user_id=workflow.user_id,
            workflow_type=workflow.config.workflow_type.value,
            step_count=len(workflow.config.steps),
            created_at=workflow.created_at.isoformat(),
            updated_at=workflow.updated_at.isoformat(),
            status=workflow.status.value,
            execution_count=workflow.execution_count,
            metadata=workflow.metadata,
        )

        logger.info(f"Updated workflow {workflow_id}")
        return response

    except HTTPException:
        raise
    except WorkflowError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to update workflow {workflow_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{workflow_id}")
async def delete_workflow(
    workflow_id: str, user_id: str = Query(..., description="User ID")
):
    """Delete a workflow."""
    try:
        workflow_manager = get_workflow_manager()

        # Get existing workflow
        existing_workflow = await workflow_manager.get_workflow(workflow_id)
        if not existing_workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")

        if existing_workflow.user_id != user_id:
            raise HTTPException(
                status_code=403, detail="Workflow does not belong to user"
            )

        await workflow_manager.delete_workflow(workflow_id)

        logger.info(f"Deleted workflow {workflow_id}")
        return create_success_response(data={}, message="Workflow deleted successfully")

    except HTTPException:
        raise
    except WorkflowError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to delete workflow {workflow_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/{workflow_id}/execute", response_model=WorkflowExecutionResponse)
async def execute_workflow(
    workflow_id: str,
    request: ExecuteWorkflowRequest,
    user_id: str = Query(..., description="User ID"),
):
    """Execute a workflow."""
    try:
        workflow_manager = get_workflow_manager()

        # Verify workflow exists and belongs to user
        workflow = await workflow_manager.get_workflow(workflow_id)
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")

        if workflow.user_id != user_id:
            raise HTTPException(
                status_code=403, detail="Workflow does not belong to user"
            )

        execution = await workflow_manager.execute_workflow(
            workflow_id, user_id, request.input_data
        )

        response = WorkflowExecutionResponse(
            id=execution.id,
            workflow_id=execution.workflow_id,
            user_id=execution.user_id,
            input_data=execution.input_data,
            output_data=execution.output_data,
            status=execution.status.value,
            step_count=len(execution.steps),
            started_at=execution.started_at.isoformat()
            if execution.started_at
            else None,
            completed_at=execution.completed_at.isoformat()
            if execution.completed_at
            else None,
            error_message=execution.error_message,
            metadata=execution.metadata,
        )

        logger.info(
            f"Started workflow execution {execution.id} for workflow {workflow_id}"
        )
        return response

    except HTTPException:
        raise
    except WorkflowError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to execute workflow: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{workflow_id}/executions", response_model=list[WorkflowExecutionResponse])
async def list_workflow_executions(
    workflow_id: str, user_id: str = Query(..., description="User ID")
):
    """List executions for a workflow."""
    try:
        workflow_manager = get_workflow_manager()

        # Verify workflow exists and belongs to user
        workflow = await workflow_manager.get_workflow(workflow_id)
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")

        if workflow.user_id != user_id:
            raise HTTPException(
                status_code=403, detail="Workflow does not belong to user"
            )

        # Get all executions and filter by workflow
        all_executions = list(workflow_manager.executions.values())
        workflow_executions = [
            exec
            for exec in all_executions
            if exec.workflow_id == workflow_id and exec.user_id == user_id
        ]

        responses = []
        for execution in workflow_executions:
            response = WorkflowExecutionResponse(
                id=execution.id,
                workflow_id=execution.workflow_id,
                user_id=execution.user_id,
                input_data=execution.input_data,
                output_data=execution.output_data,
                status=execution.status.value,
                step_count=len(execution.steps),
                started_at=execution.started_at.isoformat()
                if execution.started_at
                else None,
                completed_at=execution.completed_at.isoformat()
                if execution.completed_at
                else None,
                error_message=execution.error_message,
                metadata=execution.metadata,
            )
            responses.append(response)

        logger.info(f"Listed {len(responses)} executions for workflow {workflow_id}")
        return responses

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list workflow executions: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/executions/{execution_id}", response_model=WorkflowExecutionResponse)
async def get_workflow_execution(execution_id: str):
    """Get a workflow execution by ID."""
    try:
        workflow_manager = get_workflow_manager()
        execution = await workflow_manager.get_execution(execution_id)

        if not execution:
            raise HTTPException(status_code=404, detail="Execution not found")

        response = WorkflowExecutionResponse(
            id=execution.id,
            workflow_id=execution.workflow_id,
            user_id=execution.user_id,
            input_data=execution.input_data,
            output_data=execution.output_data,
            status=execution.status.value,
            step_count=len(execution.steps),
            started_at=execution.started_at.isoformat()
            if execution.started_at
            else None,
            completed_at=execution.completed_at.isoformat()
            if execution.completed_at
            else None,
            error_message=execution.error_message,
            metadata=execution.metadata,
        )

        logger.info(f"Retrieved workflow execution {execution_id}")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get workflow execution {execution_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/executions/{execution_id}/cancel")
async def cancel_workflow_execution(execution_id: str):
    """Cancel a workflow execution."""
    try:
        workflow_manager = get_workflow_manager()

        execution = await workflow_manager.cancel_execution(execution_id)

        response = WorkflowExecutionResponse(
            id=execution.id,
            workflow_id=execution.workflow_id,
            user_id=execution.user_id,
            input_data=execution.input_data,
            output_data=execution.output_data,
            status=execution.status.value,
            step_count=len(execution.steps),
            started_at=execution.started_at.isoformat()
            if execution.started_at
            else None,
            completed_at=execution.completed_at.isoformat()
            if execution.completed_at
            else None,
            error_message=execution.error_message,
            metadata=execution.metadata,
        )

        logger.info(f"Cancelled workflow execution {execution_id}")
        return response

    except WorkflowError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to cancel workflow execution {execution_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/types")
async def list_workflow_types():
    """List available workflow types."""
    types = [
        {
            "name": "business_initiative",
            "description": "Business initiative workflow with triage and execution steps",
            "steps": ["triage", "launch_helper", "get_data"],
        },
        {
            "name": "data_processing",
            "description": "Data processing workflow for ETL operations",
            "steps": ["extract", "transform", "load"],
        },
        {
            "name": "content_generation",
            "description": "Content generation workflow for creating various content types",
            "steps": ["research", "draft", "review", "publish"],
        },
        {
            "name": "automation",
            "description": "Automation workflow for repetitive tasks",
            "steps": ["trigger", "process", "notify"],
        },
        {
            "name": "custom",
            "description": "Custom workflow with user-defined steps",
            "steps": ["custom"],
        },
    ]

    logger.info("Retrieved list of workflow types")
    return types
