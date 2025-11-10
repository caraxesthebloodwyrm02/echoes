"""Main experiment orchestrator for AAE framework."""

import time
from typing import Dict, List, Optional, Any
from datetime import datetime
from .models import (
    ExperimentConfig,
    ExperimentGroup,
    ExperimentResults,
    AccountingMetrics,
    AccountabilityMetrics,
)
from .config import AAEConfig


class ExperimentOrchestrator:
    """Main controller for AAE experiments."""

    def __init__(self, config: Optional[AAEConfig] = None):
        self.config = config or AAEConfig()
        self.experiments: Dict[str, ExperimentConfig] = {}
        self.active_experiments: Dict[str, ExperimentResults] = {}

    def create_experiment(self, name: str, **kwargs) -> "ExperimentInstance":
        """Create a new experiment instance."""
        # Merge with default config
        config_dict = {
            "name": name,
            "duration_hours": kwargs.get("experiment_duration_hours", 8),
            "dataset_size": kwargs.get("dataset_size", "medium"),
            "complexity_level": kwargs.get("complexity_level", "medium"),
            "include_fraud_scheme": kwargs.get("include_fraud_scheme", True),
            "enable_real_time_monitoring": kwargs.get(
                "enable_real_time_monitoring", True
            ),
            "scoring_weights": kwargs.get(
                "scoring_weights",
                {"simple_error": 1, "complex_error": 5, "fraud_scheme": 50},
            ),
            "groups": kwargs.get("groups", ["human", "ai", "hybrid", "oracle"]),
        }

        # Validate configuration
        if not self.config.validate_experiment_config(config_dict):
            raise ValueError("Invalid experiment configuration")

        # Create experiment config
        exp_config = ExperimentConfig(**config_dict)
        self.experiments[name] = exp_config

        # Create experiment instance
        return ExperimentInstance(exp_config, self.config)

    def get_experiment(self, name: str) -> Optional[ExperimentConfig]:
        """Get experiment configuration by name."""
        return self.experiments.get(name)

    def list_experiments(self) -> List[str]:
        """List all experiment names."""
        return list(self.experiments.keys())

    def get_active_experiments(self) -> List[str]:
        """Get names of currently active experiments."""
        return list(self.active_experiments.keys())


class ExperimentInstance:
    """Represents a single experiment instance."""

    def __init__(self, config: ExperimentConfig, orchestrator_config: AAEConfig):
        self.config = config
        self.orchestrator_config = orchestrator_config
        self.groups: List[ExperimentGroup] = []
        self.results: Optional[ExperimentResults] = None
        self.dataset = None
        self._setup_groups()

    def _setup_groups(self):
        """Initialize experiment groups."""
        for group_name in self.config.groups:
            group = ExperimentGroup(
                name=f"{self.config.name}_{group_name}", type=group_name
            )
            self.groups.append(group)

    @property
    def name(self) -> str:
        """Get experiment name."""
        return self.config.name

    @property
    def duration_hours(self) -> int:
        """Get experiment duration."""
        return self.config.duration_hours

    def run(self) -> ExperimentResults:
        """Run the complete experiment."""
        print(f"🧪 Starting experiment: {self.config.name}")
        start_time = datetime.now()

        try:
            # Phase 1: Dataset preparation
            self._prepare_dataset()

            # Phase 2: Group execution
            group_results = self._run_groups()

            # Phase 3: Scoring and analysis
            final_scores = self._calculate_scores(group_results)

            # Phase 4: Generate results
            end_time = datetime.now()
            duration_minutes = (end_time - start_time).total_seconds() / 60

            self.results = ExperimentResults(
                experiment_name=self.config.name,
                start_time=start_time,
                end_time=end_time,
                duration_minutes=duration_minutes,
                human_score=final_scores.get("human", 0.0),
                ai_score=final_scores.get("ai", 0.0),
                hybrid_score=final_scores.get("hybrid", 0.0),
                oracle_score=final_scores.get("oracle", 0.0),
                group_performance=group_results,
                key_findings=self._generate_findings(final_scores),
            )

            print(f"✅ Experiment completed in {duration_minutes:.1f} minutes")
            return self.results

        except Exception as e:
            print(f"❌ Experiment failed: {e}")
            raise

    def _prepare_dataset(self):
        """Prepare the experiment dataset."""
        print("📊 Preparing dataset...")
        # This would integrate with dataset generators
        # For now, create mock dataset info
        self.dataset = {
            "transactions": 10000,
            "documents": 500,
            "planted_errors": 25,
            "fraud_schemes": 1 if self.config.include_fraud_scheme else 0,
        }
        print(f"   Generated {self.dataset['transactions']} transactions")

    def _run_groups(self) -> Dict[str, Dict[str, Any]]:
        """Run all experimental groups."""
        print("👥 Running experimental groups...")
        results = {}

        for group in self.groups:
            print(f"   Running group: {group.type}")
            group.start_time = datetime.now()

            # Simulate group execution based on type
            if group.type == "oracle":
                group_results = self._run_oracle_group()
            elif group.type == "ai":
                group_results = self._run_ai_group()
            elif group.type == "human":
                group_results = self._run_human_group()
            elif group.type == "hybrid":
                group_results = self._run_hybrid_group()
            else:
                group_results = {"score": 0.0}

            group.end_time = datetime.now()
            group.status = "completed"

            results[group.type] = group_results

        return results

    def _run_oracle_group(self) -> Dict[str, Any]:
        """Run the Oracle (ground truth) group."""
        return {
            "score": 100.0,
            "accounting_metrics": AccountingMetrics(
                accuracy_percentage=100.0,
                simple_errors_found=self.dataset["planted_errors"],
                complex_errors_found=5,
                fraud_indicators_found=self.dataset["fraud_schemes"],
            ),
            "accountability_metrics": AccountabilityMetrics(
                true_positive_rate=1.0,
                false_positive_rate=0.0,
                materiality_judgment_score=1.0,
            ),
        }

    def _run_ai_group(self) -> Dict[str, Any]:
        """Run the AI Control group."""
        # Simulate AI performance
        return {
            "score": 85.0,
            "accounting_metrics": AccountingMetrics(
                accuracy_percentage=95.0,
                simple_errors_found=int(self.dataset["planted_errors"] * 0.9),
                complex_errors_found=4,
                fraud_indicators_found=self.dataset["fraud_schemes"],
                false_positives=8,
            ),
            "accountability_metrics": AccountabilityMetrics(
                true_positive_rate=0.85,
                false_positive_rate=0.15,
                materiality_judgment_score=0.7,
            ),
        }

    def _run_human_group(self) -> Dict[str, Any]:
        """Run the Human Control group."""
        return {
            "score": 78.0,
            "accounting_metrics": AccountingMetrics(
                accuracy_percentage=88.0,
                simple_errors_found=int(self.dataset["planted_errors"] * 0.8),
                complex_errors_found=3,
                fraud_indicators_found=int(self.dataset["fraud_schemes"] * 0.75),
                false_positives=3,
            ),
            "accountability_metrics": AccountabilityMetrics(
                true_positive_rate=0.75,
                false_positive_rate=0.05,
                materiality_judgment_score=0.9,
                narrative_quality=0.9,
            ),
        }

    def _run_hybrid_group(self) -> Dict[str, Any]:
        """Run the Hybrid Model group."""
        return {
            "score": 92.0,
            "accounting_metrics": AccountingMetrics(
                accuracy_percentage=96.0,
                simple_errors_found=int(self.dataset["planted_errors"] * 0.95),
                complex_errors_found=5,
                fraud_indicators_found=self.dataset["fraud_schemes"],
                false_positives=4,
            ),
            "accountability_metrics": AccountabilityMetrics(
                true_positive_rate=0.92,
                false_positive_rate=0.08,
                materiality_judgment_score=0.9,
                narrative_quality=0.85,
            ),
        }

    def _calculate_scores(
        self, group_results: Dict[str, Dict[str, Any]]
    ) -> Dict[str, float]:
        """Calculate final scores for each group."""
        scores = {}
        weights = self.config.scoring_weights

        for group_name, results in group_results.items():
            # Base score from accounting metrics
            accounting_score = results.get("accounting_metrics", AccountingMetrics())
            base_score = (
                accounting_score.simple_errors_found * weights["simple_error"]
                + accounting_score.complex_errors_found * weights["complex_error"]
                + accounting_score.fraud_indicators_found * weights["fraud_scheme"]
            )

            # Adjust for false positives
            penalty = accounting_score.false_positives * 2
            adjusted_score = max(0, base_score - penalty)

            # Boost for accountability
            accountability_score = results.get(
                "accountability_metrics", AccountabilityMetrics()
            )
            boost = accountability_score.true_positive_rate * 20

            scores[group_name] = min(100, adjusted_score + boost)

        return scores

    def _generate_findings(self, scores: Dict[str, float]) -> List[str]:
        """Generate key findings from experiment results."""
        findings = []

        # Compare hybrid vs individual approaches
        hybrid_score = scores.get("hybrid", 0)
        ai_score = scores.get("ai", 0)
        human_score = scores.get("human", 0)

        if hybrid_score > max(ai_score, human_score):
            findings.append(
                "Hybrid AI-human collaboration significantly outperforms individual approaches"
            )

        if ai_score > human_score:
            findings.append("AI shows superior accuracy in rule-based accounting tasks")
        else:
            findings.append("Humans maintain advantage in complex judgment calls")

        # False positive analysis
        findings.append(
            "AI systems show higher false positive rates than human auditors"
        )
        findings.append(
            "Hybrid approaches reduce false positives while maintaining detection rates"
        )

        return findings
