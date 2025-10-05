"""
API Schemas for AI Advisor

Pydantic models for request/response validation with emphasis on:
- Provenance tracking for all assertions
- Human-in-the-loop feedback capture
- Agent safety and execution controls
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, HttpUrl, validator


class ProvenanceSource(str, Enum):
    """Verified data source types"""

    PUBMED = "PubMed"
    ARXIV = "arXiv"
    CLINICAL_TRIALS = "ClinicalTrials.gov"
    BLS = "BLS"  # Bureau of Labor Statistics
    WORLD_BANK = "WorldBank"
    CUSTOM = "custom"


class Provenance(BaseModel):
    """
    Provenance object - MANDATORY for all assertions

    Tracks source, verification, and licensing for generated claims.
    """

    source: str = Field(..., description="Canonical source name or id (e.g., PubMed, arXiv)")
    url: Optional[HttpUrl] = Field(None, description="Permalink to the source")
    snippet: Optional[str] = Field(
        None, description="Quoted snippet used to justify the assertion", max_length=500
    )
    timestamp: datetime = Field(..., description="When the source was fetched or published")
    license: Optional[str] = Field(
        None, description="License string for reuse (e.g., CC-BY, public-domain)"
    )
    confidence: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Confidence score for this source (0-1)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "source": "PubMed",
                "url": "https://pubmed.ncbi.nlm.nih.gov/12345678/",
                "snippet": "Study demonstrates significant reduction in...",
                "timestamp": "2025-10-05T00:00:00Z",
                "license": "CC-BY-4.0",
                "confidence": 0.92,
            }
        }


class Assertion(BaseModel):
    """
    Assertion with provenance - base unit of knowledge

    All generated claims MUST include provenance.
    """

    claim: str = Field(
        ..., description="The assertion or claim being made", min_length=1, max_length=1000
    )
    provenance: List[Provenance] = Field(
        ..., min_length=1, description="List of provenance sources (minimum 1 required)"
    )
    domain: Optional[str] = Field(
        None, description="Domain this assertion belongs to (science, commerce, arts)"
    )
    confidence: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Overall confidence in the claim"
    )

    @validator("provenance")
    def validate_provenance_not_empty(cls, v):
        if not v or len(v) == 0:
            raise ValueError("At least one provenance source is required")
        return v


class FeedbackLabel(str, Enum):
    """Standardized feedback labels for HIL"""

    INCORRECT = "incorrect"
    BIASED = "biased"
    HELPFUL = "helpful"
    MISLEADING = "misleading"
    INCOMPLETE = "incomplete"
    ACCURATE = "accurate"


class HILFeedback(BaseModel):
    """
    Human-in-the-Loop Feedback

    Captures user corrections and labels for continuous improvement.
    """

    assertion_id: str = Field(..., description="Unique ID of the assertion being reviewed")
    user_id: Optional[str] = Field(None, description="Anonymous or authenticated user identifier")
    correction: Optional[str] = Field(
        None, description="User-provided correction text", max_length=2000
    )
    label: Optional[FeedbackLabel] = Field(None, description="Standardized label for the feedback")
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Additional context (severity, domain, etc.)"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="When feedback was submitted"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "assertion_id": "assert-12345",
                "user_id": "user-anon-678",
                "correction": "The study actually showed no significant effect",
                "label": "incorrect",
                "metadata": {"severity": "high", "domain": "science"},
                "timestamp": "2025-10-05T01:00:00Z",
            }
        }


class AgentAction(str, Enum):
    """Whitelisted agent actions"""

    SEARCH_BIOMEDICAL = "search_biomedical"
    SIMULATE_ECONOMY = "simulate_economy"
    MATCH_EMPLOYMENT = "match_employment"
    GENERATE_ART = "generate_art"
    ANALYZE_SENTIMENT = "analyze_sentiment"
    NO_OP = "no_op"


class AgentExecutionRequest(BaseModel):
    """
    Request for agent execution with safety controls

    Defaults to dry-run mode for safety.
    """

    agent_id: str = Field(..., description="Unique identifier for the agent instance")
    action: str = Field(..., description="Action to execute (must be whitelisted)")
    params: Dict[str, Any] = Field(default_factory=dict, description="Parameters for the action")
    dry_run: bool = Field(
        default=True, description="If true, no side-effects executed (SAFETY DEFAULT)"
    )
    requested_by: Optional[str] = Field(None, description="User or system requesting execution")
    timeout_seconds: Optional[int] = Field(
        default=30, ge=1, le=300, description="Maximum execution time (1-300 seconds)"
    )


class SafetyCheck(BaseModel):
    """Results of safety pre-checks"""

    whitelist_ok: bool = Field(..., description="Action is whitelisted")
    dry_run_allowed: bool = Field(..., description="Dry-run mode allowed")
    side_effects_detected: Optional[List[str]] = Field(
        None, description="List of potential side effects"
    )
    warnings: Optional[List[str]] = Field(None, description="Safety warnings")


class AgentExecutionResponse(BaseModel):
    """Response from agent execution"""

    success: bool = Field(..., description="Whether execution succeeded")
    dry_run: bool = Field(..., description="Was this a dry-run?")
    logs: List[str] = Field(default_factory=list, description="Execution logs")
    outputs: Optional[Dict[str, Any]] = Field(None, description="Results from the execution")
    safety_checks: Optional[SafetyCheck] = Field(None, description="Safety check results")
    duration_ms: Optional[float] = Field(None, description="Execution duration in milliseconds")


class KillSignal(BaseModel):
    """Emergency stop signal for runaway agents"""

    agent_id: str = Field(..., description="ID of the agent to terminate")
    reason: Optional[str] = Field(None, description="Reason for termination")
    requested_by: Optional[str] = Field(None, description="Who requested the kill")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="When kill was requested"
    )
    force: bool = Field(default=False, description="Force immediate termination without cleanup")


# Domain-specific schemas


class BiomedicalQuery(BaseModel):
    """Query for biomedical research"""

    query: str = Field(..., min_length=3, max_length=500)
    max_results: int = Field(default=10, ge=1, le=100)
    include_preprints: bool = Field(default=False)
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None


class BiomedicalResult(BaseModel):
    """Biomedical search result with provenance"""

    title: str
    abstract: Optional[str] = None
    authors: List[str] = Field(default_factory=list)
    publication_date: Optional[datetime] = None
    provenance: Provenance
    peer_reviewed: bool = Field(default=False)


class UBISimulationParams(BaseModel):
    """Parameters for Universal Basic Income simulation"""

    population_size: int = Field(..., ge=1000)
    monthly_amount: float = Field(..., ge=0)
    duration_months: int = Field(..., ge=1, le=120)
    inflation_rate: float = Field(default=0.02, ge=0, le=1)
    economic_model: str = Field(default="baseline")


class UBISimulationResult(BaseModel):
    """Results from UBI simulation"""

    total_cost: float
    gdp_impact: float
    employment_impact: float
    poverty_reduction: float
    confidence_interval: Dict[str, float]
    provenance: List[Provenance]


class EmploymentMatch(BaseModel):
    """Employment opportunity match result"""

    job_title: str
    company: Optional[str] = None
    match_score: float = Field(..., ge=0, le=1)
    skills_matched: List[str]
    skills_missing: List[str]
    bias_score: Optional[float] = Field(
        None, ge=0, le=1, description="Bias detection score (lower is better)"
    )
    explanation: str


class CreativeWork(BaseModel):
    """Generated creative content with attribution"""

    work_type: str = Field(..., description="music, art, story, etc.")
    content: str = Field(..., description="The creative work itself")
    attribution: List[str] = Field(
        ..., description="Sources/inspirations that influenced this work"
    )
    license: str = Field(default="CC-BY-SA-4.0")
    originality_score: Optional[float] = Field(
        None, ge=0, le=1, description="Estimated originality (1 = highly original)"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Health check and system schemas


class HealthResponse(BaseModel):
    """System health status"""

    status: str = Field(..., description="healthy, degraded, or down")
    version: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    components: Dict[str, str] = Field(
        default_factory=dict, description="Status of individual components"
    )


class MetricsResponse(BaseModel):
    """System metrics"""

    total_requests: int
    total_assertions: int
    provenance_coverage: float = Field(
        ..., ge=0, le=1, description="Percentage of assertions with provenance"
    )
    hil_feedback_count: int
    agent_executions: int
    dry_run_percentage: float
