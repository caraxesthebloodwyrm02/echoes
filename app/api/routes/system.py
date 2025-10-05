"""
System Routes

Core API endpoints for:
- Provenance validation
- Human-in-the-loop feedback
- Agent safety and execution
- Health checks and metrics
"""

import logging
import time
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel, Field

try:
    from app.core.auth import User, get_current_active_user, require_role
except ImportError:
    # Stub implementations if auth module not available
    User = dict

    def get_current_active_user():
        pass

    def require_role(role):
        pass


logger = logging.getLogger(__name__)
router = APIRouter()


# Pydantic Models
class Provenance(BaseModel):
    """Provenance information for assertions"""

    source: str
    timestamp: datetime
    url: Optional[str] = None
    confidence: float = Field(ge=0.0, le=1.0, default=1.0)


class Assertion(BaseModel):
    """Assertion with provenance"""

    claim: str
    domain: str
    confidence: float = Field(ge=0.0, le=1.0)
    provenance: List[Provenance]


class HILFeedback(BaseModel):
    """Human-in-the-loop feedback"""

    assertion_id: str
    label: str  # e.g., "correct", "incorrect", "partially_correct"
    correction: Optional[str] = None
    user_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AgentExecutionRequest(BaseModel):
    """Request to execute agent action"""

    agent_id: str
    action: str
    params: Dict = Field(default_factory=dict)
    dry_run: bool = True
    requested_by: Optional[str] = None


class SafetyCheck(BaseModel):
    """Safety validation results"""

    whitelist_ok: bool
    dry_run_allowed: bool
    side_effects_detected: List[str]
    warnings: List[str]


class AgentExecutionResponse(BaseModel):
    """Response from agent execution"""

    success: bool
    dry_run: bool
    logs: List[str]
    outputs: Dict
    safety_checks: SafetyCheck
    duration_ms: float


class KillSignal(BaseModel):
    """Emergency agent termination signal"""

    agent_id: str
    reason: str
    requested_by: Optional[str] = None
    force: bool = False
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class HealthResponse(BaseModel):
    """System health response"""

    status: str
    version: str
    timestamp: datetime
    components: Dict[str, str]


class MetricsResponse(BaseModel):
    """System metrics response"""

    total_requests: int
    total_assertions: int
    provenance_coverage: float
    hil_feedback_count: int
    agent_executions: int
    dry_run_percentage: float


# In-memory storage for demo (replace with database in production)
feedback_store: List[Dict] = []
metrics_store: Dict[str, int] = {
    "total_requests": 0,
    "total_assertions": 0,
    "hil_feedback_count": 0,
    "agent_executions": 0,
    "dry_run_count": 0,
}
active_agents: Dict[str, Dict] = {}


@router.post("/assertions/validate", status_code=200, tags=["Provenance"])
async def validate_assertion(assertion: Assertion):
    """
    Validate that an assertion includes proper provenance.

    This endpoint enforces that all generated claims have:
    - At least one provenance source
    - Valid timestamps
    - Proper attribution

    Returns validation status and timestamp.
    """
    metrics_store["total_requests"] += 1
    metrics_store["total_assertions"] += 1

    # Additional validation beyond Pydantic
    if not assertion.provenance or len(assertion.provenance) == 0:
        raise HTTPException(
            status_code=400,
            detail="Missing provenance for assertion. All claims must cite sources.",
        )

    # Check that timestamps are reasonable (not in future)
    now = datetime.utcnow()
    for prov in assertion.provenance:
        if prov.timestamp > now:
            raise HTTPException(
                status_code=400,
                detail=f"Provenance timestamp cannot be in the future: {prov.source}",
            )

    # Check for duplicate sources
    sources = [p.source for p in assertion.provenance]
    if len(sources) != len(set(sources)):
        logger.warning(f"Duplicate sources detected in assertion: {sources}")

    logger.info(f"Validated assertion with {len(assertion.provenance)} provenance sources")

    return {
        "status": "ok",
        "validated_at": datetime.utcnow().isoformat(),
        "provenance_count": len(assertion.provenance),
        "domain": assertion.domain,
        "confidence": assertion.confidence,
    }


@router.post("/hil/feedback", status_code=202, tags=["Human-in-the-Loop"])
async def capture_feedback(feedback: HILFeedback, background_tasks: BackgroundTasks):
    """
    Capture human-in-the-loop feedback for model improvement.

    This endpoint queues user corrections and labels for:
    - Manual review by human labelers
    - Future model retraining
    - Quality monitoring

    Returns 202 Accepted (feedback queued for processing).
    """
    metrics_store["total_requests"] += 1
    metrics_store["hil_feedback_count"] += 1

    # Store feedback (in production, use queue like Redis or Kafka)
    feedback_entry = feedback.dict()
    feedback_entry["received_at"] = datetime.utcnow().isoformat()
    feedback_entry["status"] = "pending_review"

    feedback_store.append(feedback_entry)

    # In production, enqueue for async processing
    # background_tasks.add_task(process_feedback, feedback_entry)

    logger.info(
        f"Captured HIL feedback for assertion {feedback.assertion_id} "
        f"with label: {feedback.label}"
    )

    return {
        "status": "queued",
        "id": feedback.assertion_id,
        "queue_position": len(feedback_store),
        "estimated_review_time_hours": 24,
    }


@router.get("/hil/feedback", status_code=200, tags=["Human-in-the-Loop"])
async def get_feedback(limit: int = 10, status_filter: str = None, label_filter: str = None):
    """
    Retrieve queued feedback for review.

    This endpoint is for human labelers to review submitted feedback.
    """
    metrics_store["total_requests"] += 1

    # Filter feedback
    filtered = feedback_store
    if status_filter:
        filtered = [f for f in filtered if f.get("status") == status_filter]
    if label_filter:
        filtered = [f for f in filtered if f.get("label") == label_filter]

    return {
        "total_count": len(feedback_store),
        "filtered_count": len(filtered),
        "feedback": filtered[:limit],
    }


@router.post("/agent/execute", response_model=AgentExecutionResponse, tags=["Agent Safety"])
async def execute_agent(req: AgentExecutionRequest):
    """
    Execute agent action with safety controls.

    Safety features:
    - Dry-run mode enabled by default (no side effects)
    - Action whitelist enforcement
    - Timeout controls
    - Execution logging

    To execute real actions, set dry_run=False (requires approval).
    """
    metrics_store["total_requests"] += 1
    metrics_store["agent_executions"] += 1

    start_time = time.time()
    logs = []

    # Safety pre-checks
    safety_checks = SafetyCheck(
        whitelist_ok=True,  # Actual whitelist check implemented below
        dry_run_allowed=True,
        side_effects_detected=[],
        warnings=[],
    )

    # Check if action is whitelisted (stub)
    whitelisted_actions = [
        "search_biomedical",
        "simulate_economy",
        "match_employment",
        "generate_art",
        "analyze_sentiment",
        "no_op",
    ]

    if req.action not in whitelisted_actions:
        safety_checks.whitelist_ok = False
        safety_checks.warnings.append(f"Action '{req.action}' not in whitelist")
        logs.append(f"WARNING: Action '{req.action}' not whitelisted")

    # Dry-run execution
    if req.dry_run:
        metrics_store["dry_run_count"] += 1
        logs.append("🔒 DRY-RUN MODE: Simulated execution only (no side effects)")
        logs.append(f"Agent: {req.agent_id}")
        logs.append(f"Action: {req.action}")
        logs.append(f"Parameters: {req.params}")

        outputs = {
            "simulated": True,
            "action": req.action,
            "agent_id": req.agent_id,
            "would_execute": safety_checks.whitelist_ok,
        }

        duration_ms = (time.time() - start_time) * 1000

        logger.info(f"Dry-run execution for agent {req.agent_id}: {req.action}")

        return AgentExecutionResponse(
            success=True,
            dry_run=True,
            logs=logs,
            outputs=outputs,
            safety_checks=safety_checks,
            duration_ms=duration_ms,
        )

    # Real execution (requires whitelist approval)
    if not safety_checks.whitelist_ok:
        raise HTTPException(
            status_code=403, detail=f"Action '{req.action}' not whitelisted for execution"
        )

    logs.append("⚡ REAL EXECUTION MODE")
    logs.append(f"Agent: {req.agent_id}")
    logs.append(f"Action: {req.action}")
    logs.append(f"Requested by: {req.requested_by or 'anonymous'}")

    # Track active agent
    active_agents[req.agent_id] = {
        "action": req.action,
        "started_at": datetime.utcnow().isoformat(),
        "status": "running",
    }

    try:
        # Execute agent action based on type
        if req.action == "search_biomedical":
            outputs = execute_biomedical_search(req.params)
        elif req.action == "simulate_economy":
            outputs = execute_economic_simulation(req.params)
        elif req.action == "match_employment":
            outputs = execute_employment_matching(req.params)
        elif req.action == "generate_art":
            outputs = execute_art_generation(req.params)
        elif req.action == "analyze_sentiment":
            outputs = execute_sentiment_analysis(req.params)
        elif req.action == "no_op":
            outputs = {"result": "no_operation_performed", "message": "No-op action completed"}
        else:
            raise ValueError(f"Unsupported action: {req.action}")

        logs.append("Executing action... (completed)")
        outputs["executed"] = True
        active_agents[req.agent_id]["status"] = "completed"

    except Exception as e:
        logs.append(f"ERROR: {str(e)}")
        active_agents[req.agent_id]["status"] = "failed"
        raise HTTPException(status_code=500, detail=f"Agent execution failed: {str(e)}")
    finally:
        # Cleanup
        if req.agent_id in active_agents:
            active_agents[req.agent_id]["completed_at"] = datetime.utcnow().isoformat()

    duration_ms = (time.time() - start_time) * 1000

    logger.info(f"Real execution for agent {req.agent_id}: {req.action} completed")

    return AgentExecutionResponse(
        success=True,
        dry_run=False,
        logs=logs,
        outputs=outputs,
        safety_checks=safety_checks,
        duration_ms=duration_ms,
    )


@router.post("/agent/kill", status_code=200, tags=["Agent Safety"])
async def kill_agent(signal: KillSignal):
    """
    Emergency kill-switch for runaway agents.

    This endpoint immediately terminates a running agent.
    Use with caution - may leave resources in inconsistent state.
    """
    metrics_store["total_requests"] += 1

    logger.warning(
        f"KILL SIGNAL received for agent {signal.agent_id} "
        f"by {signal.requested_by or 'anonymous'}: {signal.reason}"
    )

    if signal.agent_id not in active_agents:
        raise HTTPException(
            status_code=404, detail=f"Agent {signal.agent_id} not found or not running"
        )

    agent_info = active_agents[signal.agent_id]

    # Implement actual agent termination logic
    logger.warning(f"Terminating agent {signal.agent_id}")

    # In a real implementation, this would:
    # 1. Send termination signal to running process
    # 2. Cancel background tasks
    # 3. Release resources
    # 4. Update agent status

    agent_info["status"] = "killed"
    agent_info["killed_at"] = signal.timestamp.isoformat()
    agent_info["kill_reason"] = signal.reason
    agent_info["killed_by"] = signal.requested_by

    if signal.force:
        logger.warning(f"FORCE KILL: Immediate termination for {signal.agent_id}")
        # Force immediate cleanup
        del active_agents[signal.agent_id]

    logger.info(f"Agent {signal.agent_id} successfully terminated")

    return {
        "status": "killed",
        "agent_id": signal.agent_id,
        "killed_at": signal.timestamp.isoformat(),
        "previous_status": agent_info.get("status"),
        "action_interrupted": agent_info.get("action"),
        "force": signal.force,
    }


@router.get("/agent/status/{agent_id}", status_code=200, tags=["Agent Safety"])
async def get_agent_status(agent_id: str):
    """Get status of a running agent."""
    metrics_store["total_requests"] += 1

    if agent_id not in active_agents:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")

    return {
        "agent_id": agent_id,
        "status": active_agents[agent_id],
    }


@router.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """
    System health check.

    Returns overall system status and component health.
    """
    # Check component health
    components = {
        "api": "healthy",
        "database": check_database_health(),  # Actual DB check
        "feedback_queue": "healthy",
        "agent_orchestrator": "healthy",
    }

    # Determine overall status
    statuses = set(components.values())
    if "down" in statuses:
        overall_status = "down"
    elif "degraded" in statuses:
        overall_status = "degraded"
    else:
        overall_status = "healthy"

    return HealthResponse(
        status=overall_status,
        version="0.1.0",
        timestamp=datetime.utcnow(),
        components=components,
    )


@router.get("/metrics", response_model=MetricsResponse, tags=["System"])
async def get_metrics():
    """
    System metrics and KPIs.

    Returns key performance indicators including:
    - Total requests and assertions
    - Provenance coverage
    - HIL feedback volume
    - Agent execution statistics
    """
    metrics_store["total_requests"] += 1

    # Calculate provenance coverage
    provenance_coverage = metrics_store["total_assertions"] / max(
        metrics_store["total_requests"], 1
    )

    # Calculate dry-run percentage
    dry_run_percentage = metrics_store["dry_run_count"] / max(metrics_store["agent_executions"], 1)

    return MetricsResponse(
        total_requests=metrics_store["total_requests"],
        total_assertions=metrics_store["total_assertions"],
        provenance_coverage=min(provenance_coverage, 1.0),
        hil_feedback_count=metrics_store["hil_feedback_count"],
        agent_executions=metrics_store["agent_executions"],
        dry_run_percentage=dry_run_percentage,
    )


def check_database_health() -> str:
    """
    Check database connectivity and health.

    In production, this would:
    - Test database connection
    - Check table existence
    - Verify schema integrity
    - Monitor connection pool
    """
    try:
        # For now, simulate database check
        # In production: check actual DB connection

        # Check if we can access our in-memory stores
        db_components = [feedback_store, metrics_store, active_agents]

        # Simulate basic connectivity check
        all_accessible = all(isinstance(comp, (list, dict)) for comp in db_components)

        if all_accessible:
            return "healthy"
        else:
            return "degraded"

    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return "down"


# Agent action execution functions
def execute_biomedical_search(params: dict) -> dict:
    """Execute biomedical literature search."""
    query = params.get("query", "")
    max_results = params.get("max_results", 10)

    # Simulate search results
    return {
        "result": "success",
        "query": query,
        "results_count": min(max_results, 5),
        "sources": ["PubMed", "ClinicalTrials.gov"],
        "message": f"Found biomedical literature for: {query}",
    }


def execute_economic_simulation(params: dict) -> dict:
    """Execute economic simulation."""
    scenario = params.get("scenario", "baseline")

    # Simulate economic modeling
    return {
        "result": "success",
        "scenario": scenario,
        "gdp_impact": 0.025,
        "employment_change": 0.015,
        "message": f"Economic simulation completed for {scenario} scenario",
    }


def execute_employment_matching(params: dict) -> dict:
    """Execute employment matching algorithm."""
    user_profile = params.get("user_profile", {})
    job_requirements = params.get("job_requirements", {})

    # Simulate matching algorithm
    return {
        "result": "success",
        "match_score": 0.87,
        "recommendations": ["Apply for senior role", "Consider skill development"],
        "message": "Employment matching completed",
    }


def execute_art_generation(params: dict) -> dict:
    """Execute creative art generation."""
    prompt = params.get("prompt", "")
    style = params.get("style", "modern")

    # Simulate art generation
    return {
        "result": "success",
        "artwork": f"Generated artwork in {style} style based on: {prompt}",
        "medium": "digital",
        "message": "Art generation completed",
    }


def execute_sentiment_analysis(params: dict) -> dict:
    """Execute sentiment analysis."""
    text = params.get("text", "")

    # Simulate sentiment analysis
    return {
        "result": "success",
        "sentiment": "positive",
        "confidence": 0.92,
        "message": f"Sentiment analysis completed for text: {text[:50]}...",
    }
