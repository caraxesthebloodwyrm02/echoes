"""Data models for AAE entities."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class ExperimentConfig:
    """Configuration for an AAE experiment."""

    name: str
    duration_hours: int = 8
    dataset_size: str = "medium"
    complexity_level: str = "medium"
    include_fraud_scheme: bool = True
    enable_real_time_monitoring: bool = True
    scoring_weights: dict[str, int] = field(
        default_factory=lambda: {
            "simple_error": 1,
            "complex_error": 5,
            "fraud_scheme": 50,
        }
    )
    groups: list[str] = field(
        default_factory=lambda: ["human", "ai", "hybrid", "oracle"]
    )


@dataclass
class ExperimentGroup:
    """Represents an experimental group (Human, AI, Hybrid, Oracle)."""

    name: str
    type: str  # 'human', 'ai', 'hybrid', 'oracle'
    participants: list[str] = field(default_factory=list)
    start_time: datetime | None = None
    end_time: datetime | None = None
    status: str = "pending"  # 'pending', 'running', 'completed', 'failed'


@dataclass
class ExperimentResults:
    """Results from an AAE experiment."""

    experiment_name: str
    start_time: datetime
    end_time: datetime
    duration_minutes: float

    # Scores by group
    human_score: float = 0.0
    ai_score: float = 0.0
    hybrid_score: float = 0.0
    oracle_score: float = 0.0

    # Detailed metrics
    accounting_metrics: dict[str, Any] = field(default_factory=dict)
    accountability_metrics: dict[str, Any] = field(default_factory=dict)

    # Performance data
    group_performance: dict[str, dict[str, Any]] = field(default_factory=dict)
    error_analysis: dict[str, Any] = field(default_factory=dict)

    # Findings
    key_findings: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)


@dataclass
class DatasetConfig:
    """Configuration for dataset generation."""

    years: int = 2
    include_errors: bool = True
    complexity_level: str = "medium"
    include_fraud_scheme: bool = True
    transaction_volume: str = "medium"  # 'small', 'medium', 'large'
    document_types: list[str] = field(
        default_factory=lambda: [
            "invoices",
            "receipts",
            "contracts",
            "payroll",
            "ledgers",
        ]
    )


@dataclass
class AccountingMetrics:
    """Metrics for accounting system performance."""

    time_to_complete_hours: float = 0.0
    accuracy_percentage: float = 0.0
    processing_efficiency: float = 0.0
    rule_application_score: float = 0.0
    transaction_processing_rate: float = 0.0  # transactions per hour

    # Error types
    simple_errors_found: int = 0
    complex_errors_found: int = 0
    fraud_indicators_found: int = 0

    # False positives
    false_positives: int = 0
    false_positive_rate: float = 0.0


@dataclass
class AccountabilityMetrics:
    """Metrics for accountability and judgment performance."""

    true_positive_rate: float = 0.0  # Recall
    false_positive_rate: float = 0.0  # Precision
    materiality_judgment_score: float = 0.0
    depth_of_investigation: float = 0.0
    narrative_quality: float = 0.0

    # Judgment calls
    correct_materiality_calls: int = 0
    incorrect_materiality_calls: int = 0
    root_cause_analysis_quality: float = 0.0

    # Investigative depth
    additional_findings: int = 0
    false_leads: int = 0
