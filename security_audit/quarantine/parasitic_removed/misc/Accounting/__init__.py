"""
Automated Auditor Experiment (AAE): Accounting & Accountability Framework

A comprehensive research framework designed to quantify and measure the capabilities
of AI systems in simulating both accounting (mechanical processes) and accountability
(human judgment and oversight) in financial audit contexts.

Research Question: To what extent can a code-based system (AI-driven) replicate
the accuracy, efficiency, and judgment of a human-led accounting and audit process?

Version: 1.0.0
Author: Echoes AI Platform
License: Consent-Based (see main LICENSE file)
"""

# Version information
__version__ = "1.0.0"
__author__ = "Echoes AI Platform"
__license__ = "Consent-Based"
__description__ = "Automated Auditor Experiment: Accounting & Accountability Framework"

# Core components (always available)
from .core.config import AAEConfig
from .core.experiment_orchestrator import ExperimentOrchestrator
from .core.models import (AccountabilityMetrics, AccountingMetrics,
                          DatasetConfig, ExperimentConfig, ExperimentGroup,
                          ExperimentResults)

# Dataset generation (placeholder until implemented)
try:
    from .dataset.document_generator import DocumentGenerator
    from .dataset.error_planting import ErrorPlanter
    from .dataset.innovate_inc_generator import InnovateIncGenerator
except ImportError:
    # Placeholder classes
    class InnovateIncGenerator:
        def generate_company_data(self, *args, **kwargs):
            print("InnovateIncGenerator not yet implemented.")
            return None

    class ErrorPlanter:
        pass

    class DocumentGenerator:
        pass


# AI Control platform (placeholder until implemented)
try:
    from .ai_platform.anomaly_detector import AnomalyDetector
    from .ai_platform.document_processor import DocumentProcessor
    from .ai_platform.process_miner import ProcessMiner
    from .ai_platform.rule_engine import RuleEngine
except ImportError:
    # Placeholder classes
    class RuleEngine:
        pass

    class AnomalyDetector:
        pass

    class DocumentProcessor:
        pass

    class ProcessMiner:
        pass


# OpenAI Integration (new Phase 1 prototype)
try:
    from .openai_prototype import AuditPolicy, OpenAIAuditOrchestrator
    from .openai_prototype.config import config
except ImportError:
    # Placeholder classes
    class OpenAIAuditOrchestrator:
        def __init__(self, *args, **kwargs):
            print(
                "OpenAIAuditOrchestrator not yet implemented. Install OpenAI dependencies."
            )

    class AuditPolicy:
        pass

    class config:
        pass


# Metrics and scoring (placeholder until implemented)
try:
    from .metrics.accountability_metrics import AccountabilityMetrics
    from .metrics.performance_tracker import PerformanceTracker
    from .metrics.scoring_engine import ScoringEngine
except ImportError:
    # Placeholder classes
    class ScoringEngine:
        pass

    class PerformanceTracker:
        pass


# Convenience functions (placeholder until implemented)
try:
    from .utils.helpers import create_experiment, validate_config
except ImportError:
    # Placeholder functions
    def create_experiment(*args, **kwargs):
        print("create_experiment helper not yet implemented.")
        return None

    def validate_config(*args, **kwargs):
        return True


# Supported configurations
SUPPORTED_GROUPS = ["human", "ai", "hybrid", "oracle"]
DATASET_SIZES = ["small", "medium", "large"]
COMPLEXITY_LEVELS = ["simple", "medium", "complex"]

# Default experiment configuration
DEFAULT_CONFIG = {
    "experiment_duration_hours": 8,
    "dataset_size": "medium",
    "complexity_level": "medium",
    "include_fraud_scheme": True,
    "enable_real_time_monitoring": True,
    "scoring_weights": {"simple_error": 1, "complex_error": 5, "fraud_scheme": 50},
    "groups": SUPPORTED_GROUPS,
}


def get_version():
    """Get the current AAE version."""
    return __version__


def create_default_experiment(name: str, **kwargs):
    """Create a default experiment with standard configuration.

    Args:
        name: Experiment name
        **kwargs: Override default configuration

    Returns:
        Configured ExperimentOrchestrator instance
    """
    orchestrator = ExperimentOrchestrator()
    return orchestrator.create_experiment(name, **kwargs)


def quick_start_demo():
    """Quick start demonstration of the AAE framework."""
    print("🔬 Automated Auditor Experiment (AAE) - Quick Start")
    print(f"Version: {get_version()}")
    print()

    # Generate synthetic dataset
    generator = InnovateIncGenerator()
    dataset = generator.generate_company_data(
        years=2, include_errors=True, complexity_level="medium"
    )

    print(f"📊 Generated dataset: {len(dataset.transactions)} transactions")
    print(f"📁 Documents: {len(dataset.documents)} files")
    print(f"⚠️  Planted errors: {len(dataset.planted_errors)} irregularities")

    # Create experiment
    experiment = create_default_experiment(
        name="AAE_Quick_Demo", dataset_size="pilot", groups=["ai", "hybrid"]
    )

    print(f"🧪 Experiment created: {experiment.name}")
    print(f"👥 Groups: {experiment.groups}")
    print(f"⏱️  Duration: {experiment.duration_hours} hours")

    return experiment


# Public API
__all__ = [
    # Core components
    "ExperimentConfig",
    "ExperimentGroup",
    "ExperimentResults",
    "DatasetConfig",
    "AccountingMetrics",
    "AccountabilityMetrics",
    "ExperimentOrchestrator",
    "AAEConfig",
    # Dataset generation
    "InnovateIncGenerator",
    "ErrorPlanter",
    "DocumentGenerator",
    # AI Control platform
    "RuleEngine",
    "AnomalyDetector",
    "DocumentProcessor",
    "ProcessMiner",
    # Metrics and scoring
    "ScoringEngine",
    "AccountabilityMetrics",
    "PerformanceTracker",
    # Utilities
    "create_experiment",
    "validate_config",
    "create_default_experiment",
    "quick_start_demo",
    "get_version",
    # Constants
    "SUPPORTED_GROUPS",
    "DATASET_SIZES",
    "COMPLEXITY_LEVELS",
    "DEFAULT_CONFIG",
]
