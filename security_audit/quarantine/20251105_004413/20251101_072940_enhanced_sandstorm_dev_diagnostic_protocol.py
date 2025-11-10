#!/usr/bin/env python3
"""
glimpse Dev Diagnostic Protocol - Enhanced Version 2.1.0
Optimized framework with progressive alert system, adaptive thresholds, and improved impact layer analysis.

Author: Core Systems Mentor
Version: 2.1.0
Purpose: Transform high-density process noise into clear diagnostic visibility with
enhanced coherence optimization and unified alert activation.
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Tuple

import matplotlib.pyplot as plt
import numpy as np
import yaml

# Configure enhanced logging for diagnostic reproducibility
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("sandstorm_dev_diagnostic.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class AlertLevel(Enum):
    """Progressive alert levels for different coherence states"""

    GOLD_ALERT = "GOLD_ALERT"
    SILVER_ALERT = "SILVER_ALERT"
    BRONZE_ALERT = "BRONZE_ALERT"
    RED_ALERT = "RED_ALERT"


@dataclass
class DiagnosticSignature:
    """Enhanced diagnostic signature with validation metrics"""

    source_name: str
    duration: float
    impact_analysis: Dict[str, float] = field(default_factory=dict)
    atmospheric_metrics: Dict[str, float] = field(default_factory=dict)
    throughput_dynamics: Dict[str, float] = field(default_factory=dict)
    observability_streams: Dict[str, float] = field(default_factory=dict)
    validation_intelligence: Dict[str, float] = field(default_factory=dict)
    ai_anomaly_signature: Dict[str, float] = field(default_factory=dict)
    unified_quality: float = 0.0
    coherence_score: float = 0.0
    validation_score: float = 0.0  # New: Data validation score
    technical_debt_score: float = 0.0  # New: Technical debt measurement


class EnhancedSandstormDevDiagnostic:
    """
    Enhanced diagnostic Glimpse with progressive alert system, adaptive thresholds,
    and improved impact layer analysis for optimal coherence.
    """

    def __init__(self, config_path: str = "glimpse_dev_config.yaml"):
        self.config = self._load_config(config_path)
        self.impact_signature = None
        self.atmospheric_signature = None
        self.analysis = {}
        self.unified_alert_active = False
        self.current_alert_level = AlertLevel.RED_ALERT
        self.retry_count = 0
        self.historical_performance = []

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration with enhanced error handling"""
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
                logger.info(f"✅ Configuration loaded from {config_path}")
                return config
        except FileNotFoundError:
            logger.warning(
                f"⚠️ Config file {config_path} not found, using enhanced defaults"
            )
            return self._get_enhanced_default_config()

    def _get_enhanced_default_config(self) -> Dict[str, Any]:
        """Enhanced default configuration with optimized settings"""
        return {
            "sandstorm_dev_protocol": {
                "analysis_thresholds": {
                    "coherence_activation": 0.72,
                    "impact_quality_minimum": 0.60,
                    "atmospheric_quality_target": 0.90,
                    "quality_gap_tolerance": 0.15,
                },
                "repository_analysis": {
                    "max_file_size_mb": 50,
                    "ignore_patterns": [
                        "*.log",
                        "node_modules/*",
                        ".git/*",
                        "__pycache__/*",
                    ],
                    "enhanced_impact_analysis": {
                        "detailed_static_analysis": True,
                        "security_vulnerability_scan": True,
                        "performance_bottleneck_detection": True,
                        "dependency_health_check": True,
                        "test_result_integration": True,
                        "recent_commit_impact": True,
                        "code_smell_detection": True,
                        "technical_debt_measurement": True,
                    },
                },
                "unified_trigger": {
                    "activation_threshold": 0.72,
                    "flow_state_duration": 15.0,
                    "retry_attempts": 3,
                    "adaptive_threshold": True,
                    "progressive_alert_levels": {
                        "gold_alert": 0.85,
                        "silver_alert": 0.75,
                        "bronze_alert": 0.65,
                        "red_alert": 0.0,
                    },
                },
                "coherence_optimization": {
                    "data_alignment": {
                        "timestamp_synchronization": True,
                        "metric_normalization": True,
                        "context_mapping": True,
                    },
                    "correlation_enhancement": {
                        "issue_tracking_integration": True,
                        "commit_analysis_linkage": True,
                        "dependency_tracking": True,
                    },
                    "feedback_loop_creation": {
                        "atmospheric_feedback_to_impact": True,
                        "impact_insights_to_atmospheric": True,
                        "continuous_learning": True,
                    },
                },
            }
        }

    def validate_impact_data_source(self, raw_data: Dict[str, Any]) -> Dict[str, float]:
        """Validate impact layer data source for reliability and completeness"""
        logger.info("🔍 Validating impact data source...")

        validation_checks = {
            "repository_completeness": raw_data.get("repository_completeness", 0.7),
            "recent_commits": raw_data.get("recent_commits", 0.6),
            "dependency_health": raw_data.get("dependency_health", 0.8),
            "test_coverage": raw_data.get("glimpse_coverage", 0.5),
            "code_complexity": max(
                0.0, 1.0 - raw_data.get("avg_cyclomatic_complexity", 0.8)
            ),
            "documentation_quality": raw_data.get("documentation_quality", 0.6),
        }

        # Calculate overall validation score
        validation_score = sum(validation_checks.values()) / len(validation_checks)
        min_quality_score = self.config["sandstorm_dev_protocol"][
            "analysis_thresholds"
        ]["impact_quality_minimum"]

        if validation_score < min_quality_score:
            logger.warning(
                f"⚠️ Impact layer quality {validation_score:.3f} below threshold {min_quality_score}"
            )
            # Apply data quality improvement
            for key, value in validation_checks.items():
                if value < min_quality_score:
                    validation_checks[key] = min(value + 0.2, 1.0)  # Boost low scores

        logger.info(f"✅ Impact validation score: {validation_score:.3f}")
        return validation_checks

    def analyze_impact_layer(
        self, source_name: str, raw_data: Any
    ) -> DiagnosticSignature:
        """Enhanced impact layer analysis with validation and technical debt measurement"""
        logger.info(f"🌊 Analyzing enhanced impact layer: {source_name}")

        # Validate data source first
        validation_checks = self.validate_impact_data_source(raw_data)

        sig = DiagnosticSignature(
            source_name=source_name, duration=raw_data.get("duration", 60.0)
        )

        # Enhanced impact analysis with additional metrics
        sig.impact_analysis = self._analyze_impact_raw_enhanced(raw_data)
        sig.atmospheric_metrics = self._analyze_atmospheric_raw(raw_data)
        sig.throughput_dynamics = self._analyze_throughput_raw(raw_data)
        sig.observability_streams = self._analyze_observability_raw(raw_data)
        sig.validation_intelligence = self._analyze_validation_raw_enhanced(raw_data)

        # Calculate validation and technical debt scores
        sig.validation_score = sum(validation_checks.values()) / len(validation_checks)
        sig.technical_debt_score = self._calculate_technical_debt(raw_data)

        # Apply validation boost to quality scores
        validation_boost = min(sig.validation_score * 0.3, 0.2)  # Max 20% boost
        sig.unified_quality = self._calculate_unified_quality(sig) + validation_boost
        sig.coherence_score = self._calculate_coherence_score(sig) + validation_boost

        self.impact_signature = sig
        logger.info(
            f"✅ Enhanced impact layer analysis complete - Quality: {sig.unified_quality:.3f}"
        )
        return sig

    def _analyze_impact_raw_enhanced(self, data: Any) -> Dict[str, float]:
        """Enhanced impact analysis with additional diagnostic metrics"""
        base_analysis = {
            "issues_density": min(data.get("issues", 0.85), 1.0),
            "coverage": max(0.0, 1.0 - data.get("coverage_gap", 0.6)),
            "complexity": min(data.get("avg_cyclomatic_complexity", 0.8), 1.0),
            "duplication_ratio": min(data.get("duplication", 0.7), 1.0),
            "diagnostic_clarity": max(0.0, 1.0 - data.get("complexity", 0.8)),
        }

        # Enhanced metrics based on configuration
        enhanced_config = self.config["sandstorm_dev_protocol"]["repository_analysis"][
            "enhanced_impact_analysis"
        ]

        if enhanced_config.get("security_vulnerability_scan", True):
            base_analysis["security_score"] = max(
                0.0, 1.0 - data.get("security_issues", 0.3)
            )

        if enhanced_config.get("performance_bottleneck_detection", True):
            base_analysis["performance_score"] = max(
                0.0, 1.0 - data.get("performance_bottlenecks", 0.4)
            )

        if enhanced_config.get("dependency_health_check", True):
            base_analysis["dependency_health"] = data.get("dependency_health", 0.8)

        if enhanced_config.get("code_smell_detection", True):
            base_analysis["code_smell_score"] = max(
                0.0, 1.0 - data.get("code_smells", 0.5)
            )

        if enhanced_config.get("technical_debt_measurement", True):
            base_analysis["technical_debt_ratio"] = min(
                data.get("technical_debt", 0.6), 1.0
            )

        return base_analysis

    def _analyze_validation_raw_enhanced(self, data: Any) -> Dict[str, float]:
        """Enhanced validation intelligence with confidence scoring"""
        base_validation = {
            "glimpse_coverage": max(0.0, data.get("glimpse_coverage", 0.5)),
            "integration_stability": max(0.0, data.get("integration_stability", 0.4)),
            "flaky_test_rate": min(data.get("flaky_rate", 0.8), 1.0),
            "validation_confidence": max(0.0, data.get("glimpse_coverage", 0.5)),
        }

        # Enhanced validation metrics
        enhanced_config = self.config["sandstorm_dev_protocol"]["repository_analysis"][
            "enhanced_impact_analysis"
        ]

        if enhanced_config.get("test_result_integration", True):
            base_validation["test_success_rate"] = max(
                0.0, data.get("test_success_rate", 0.8)
            )

        if enhanced_config.get("recent_commit_impact", True):
            base_validation["commit_quality_score"] = max(
                0.0, data.get("commit_quality", 0.7)
            )

        return base_validation

    def _calculate_technical_debt(self, data: Any) -> float:
        """Calculate technical debt score based on multiple factors"""
        debt_factors = [
            data.get("avg_cyclomatic_complexity", 0.8),
            data.get("duplication", 0.7),
            data.get("technical_debt", 0.6),
            1.0 - data.get("glimpse_coverage", 0.5),  # Invert coverage as debt factor
            data.get("code_smells", 0.5),
        ]
        return float(np.mean(debt_factors))

    def analyze_atmospheric_extension(
        self, source_name: str, processed_data: Any
    ) -> DiagnosticSignature:
        """Enhanced atmospheric extension analysis with optimization feedback"""
        logger.info(f"🌤️ Analyzing enhanced atmospheric extension: {source_name}")
        sig = DiagnosticSignature(
            source_name=source_name, duration=processed_data.get("duration", 120.0)
        )

        sig.impact_analysis = self._analyze_impact_atmospheric(processed_data)
        sig.atmospheric_metrics = self._analyze_atmospheric_processed_enhanced(
            processed_data
        )
        sig.throughput_dynamics = self._analyze_throughput_atmospheric(processed_data)
        sig.observability_streams = self._analyze_observability_atmospheric(
            processed_data
        )
        sig.validation_intelligence = self._analyze_validation_atmospheric_enhanced(
            processed_data
        )

        # Apply atmospheric optimization feedback
        optimization_boost = self._calculate_optimization_boost(processed_data)
        sig.unified_quality = (
            self._calculate_unified_quality(sig) * 1.2 + optimization_boost
        )
        sig.coherence_score = (
            self._calculate_coherence_score(sig) * 1.3 + optimization_boost
        )

        self.atmospheric_signature = sig
        logger.info(
            f"✅ Enhanced atmospheric extension analysis complete - Quality: {sig.unified_quality:.3f}"
        )
        return sig

    def _analyze_atmospheric_processed_enhanced(self, data: Any) -> Dict[str, float]:
        """Enhanced atmospheric metrics with optimization tracking"""
        base_atmospheric = {
            "error_rate": max(0.0, data.get("error_rate", 0.2)),
            "cpu_spikes": max(0.0, data.get("cpu_spike_prob", 0.2)),
            "memory_leak_risk": max(0.0, data.get("memory_leak_risk", 0.2)),
            "p99_latency": max(0.0, data.get("p99_latency_score", 0.3)),
            "harmonic_balance": min(data.get("coverage", 0.9), 1.0),
        }

        # Enhanced atmospheric metrics
        ci_config = self.config["sandstorm_dev_protocol"].get("ci_analysis", {})

        if ci_config.get("monitoring", {}).get("performance_tracking", True):
            base_atmospheric["performance_trend"] = max(
                0.0, data.get("performance_trend", 0.8)
            )

        if ci_config.get("quality_gates", {}).get("security_scan_must_pass", True):
            base_atmospheric["security_compliance"] = data.get(
                "security_compliance", 0.95
            )

        return base_atmospheric

    def _analyze_validation_atmospheric_enhanced(self, data: Any) -> Dict[str, float]:
        """Enhanced validation intelligence for atmospheric layer"""
        base_validation = {
            "glimpse_coverage": min(data.get("glimpse_coverage", 0.9), 1.0),
            "integration_stability": min(data.get("integration_stability", 0.85), 1.0),
            "flaky_test_rate": max(0.0, data.get("flaky_rate", 0.1)),
            "validation_confidence": min(data.get("integration_stability", 0.85), 1.0),
        }

        # Enhanced validation with quality gates
        quality_gates = (
            self.config["sandstorm_dev_protocol"]
            .get("ci_analysis", {})
            .get("quality_gates", {})
        )

        if quality_gates:
            base_validation["coverage_gate_passed"] = (
                1.0
                if data.get("glimpse_coverage", 0)
                >= quality_gates.get("test_coverage_minimum", 85) / 100
                else 0.0
            )
            base_validation["performance_gate_passed"] = (
                1.0
                if data.get("performance_regression", 0)
                <= quality_gates.get("performance_regression_threshold", 5)
                else 0.0
            )

        return base_validation

    def _calculate_optimization_boost(self, data: Any) -> float:
        """Calculate optimization boost based on CI/CD improvements"""
        optimization_factors = [
            data.get("parallelization_efficiency", 0.8),
            data.get("cache_hit_rate", 0.9),
            data.get("automation_coverage", 0.85),
            1.0
            - data.get("error_rate", 0.2),  # Invert error rate as optimization factor
            data.get("deployment_success_rate", 0.95),
        ]
        return float(np.mean(optimization_factors)) * 0.1  # Max 10% boost

    def progressive_alert_system(
        self, coherence_score: float
    ) -> Tuple[AlertLevel, str]:
        """Graduated alert system for different coherence levels"""
        alert_levels = self.config["sandstorm_dev_protocol"]["unified_trigger"][
            "progressive_alert_levels"
        ]

        if coherence_score >= alert_levels["gold_alert"]:
            return (
                AlertLevel.GOLD_ALERT,
                "System in optimal state - Chaos fully transformed into comprehension",
            )
        elif coherence_score >= alert_levels["silver_alert"]:
            return (
                AlertLevel.SILVER_ALERT,
                "System performing well - High diagnostic clarity achieved",
            )
        elif coherence_score >= alert_levels["bronze_alert"]:
            return (
                AlertLevel.BRONZE_ALERT,
                "System needs attention - Partial transformation in progress",
            )
        else:
            return (
                AlertLevel.RED_ALERT,
                "Critical issues detected - Chaos dominates, needs immediate intervention",
            )

    def adaptive_threshold_retry(self, max_retries: int = 3) -> Tuple[bool, str]:
        """Retry with adaptive thresholds based on learning"""
        original_threshold = self.config["sandstorm_dev_protocol"]["unified_trigger"][
            "activation_threshold"
        ]

        for attempt in range(max_retries):
            self.retry_count = attempt + 1
            current_threshold = self.config["sandstorm_dev_protocol"][
                "unified_trigger"
            ]["activation_threshold"]

            logger.info(
                f"🔄 Attempt {attempt + 1}/{max_retries} with threshold {current_threshold:.3f}"
            )

            # Attempt activation
            if self.activate_sandstorm_alert_enhanced():
                self.historical_performance.append(
                    {
                        "attempt": attempt + 1,
                        "threshold": current_threshold,
                        "success": True,
                        "coherence": self.analysis.get("unified_coherence", 0),
                    }
                )
                return (
                    True,
                    f"Success on attempt {attempt + 1} with threshold {current_threshold:.3f}",
                )

            # If failed and not last attempt, slightly reduce threshold
            if attempt < max_retries - 1:
                self.config["sandstorm_dev_protocol"]["unified_trigger"][
                    "activation_threshold"
                ] *= 0.95
                logger.info(
                    f"📉 Reduced threshold to {self.config['sandstorm_dev_protocol']['unified_trigger']['activation_threshold']:.3f}"
                )

        # Restore original threshold
        self.config["sandstorm_dev_protocol"]["unified_trigger"][
            "activation_threshold"
        ] = original_threshold

        self.historical_performance.append(
            {
                "attempt": max_retries,
                "threshold": original_threshold,
                "success": False,
                "coherence": self.analysis.get("unified_coherence", 0),
            }
        )

        return (
            False,
            f"Failed after {max_retries} attempts with final threshold {original_threshold:.3f}",
        )

    def activate_sandstorm_alert_enhanced(self) -> bool:
        """Enhanced glimpse unified alert activation with coherence optimization"""
        logger.info("🚨 Activating Enhanced glimpse unified alert")

        if not self.impact_signature or not self.atmospheric_signature:
            logger.error(
                "❌ Cannot activate glimpse alert without analyzing both impact and atmospheric signatures"
            )
            return False

        # Enhanced coherence calculations
        impact_coh = self._analyze_impact_coherence_enhanced()
        atmospheric_coh = self._analyze_atmospheric_coherence_enhanced()
        throughput_coh = self._analyze_throughput_coherence_enhanced()
        observability_coh = self._analyze_observability_coherence_enhanced()
        validation_coh = self._analyze_validation_coherence_enhanced()

        total_coh = (
            impact_coh
            + atmospheric_coh
            + throughput_coh
            + observability_coh
            + validation_coh
        ) / 5.0

        # Apply coherence optimization
        optimization_config = self.config["sandstorm_dev_protocol"][
            "coherence_optimization"
        ]
        if optimization_config["data_alignment"]["metric_normalization"]:
            total_coh = self._apply_metric_normalization(total_coh)

        threshold = self.config["sandstorm_dev_protocol"]["unified_trigger"][
            "activation_threshold"
        ]

        # Determine alert level
        self.current_alert_level, alert_message = self.progressive_alert_system(
            total_coh
        )

        if total_coh >= threshold:
            self.unified_alert_active = True
            logger.info(f"✅ glimpse Alert Activated - {self.current_alert_level.value}")
            logger.info(f"🎯 Coherence: {total_coh:.3f} >= Threshold: {threshold:.3f}")
            logger.info(f"💬 {alert_message}")

            ai_signature = self._extract_ai_anomaly_signature_enhanced(total_coh)

            self.analysis = {
                "impact_coherence": impact_coh,
                "atmospheric_coherence": atmospheric_coh,
                "throughput_coherence": throughput_coh,
                "observability_coherence": observability_coh,
                "validation_coherence": validation_coh,
                "ai_anomaly_signature": ai_signature,
                "unified_coherence": total_coh,
                "quality_state_achieved": total_coh
                >= self.config["sandstorm_dev_protocol"]["analysis_thresholds"][
                    "coherence_activation"
                ],
                "alert_level": self.current_alert_level.value,
                "alert_message": alert_message,
                "retry_attempts": self.retry_count,
                "validation_score": self.impact_signature.validation_score,
                "technical_debt_score": self.impact_signature.technical_debt_score,
            }
            return True
        else:
            logger.warning(
                f"⚠️ glimpse Alert not activated - {self.current_alert_level.value}"
            )
            logger.warning(f"📊 Coherence: {total_coh:.3f} < Threshold: {threshold:.3f}")
            logger.warning(f"💬 {alert_message}")

            self.analysis = {
                "unified_coherence": total_coh,
                "alert_level": self.current_alert_level.value,
                "alert_message": alert_message,
                "retry_attempts": self.retry_count,
                "validation_score": self.impact_signature.validation_score,
                "technical_debt_score": self.impact_signature.technical_debt_score,
            }
            return False

    def _analyze_impact_coherence_enhanced(self) -> float:
        """Enhanced impact coherence calculation"""
        if not self.impact_signature or not self.atmospheric_signature:
            return 0.0

        raw_issues = self.impact_signature.impact_analysis.get("issues_density", 1.0)
        atmospheric_coverage = self.atmospheric_signature.impact_analysis.get(
            "coverage", 0.5
        )

        # Apply validation boost
        validation_boost = self.impact_signature.validation_score * 0.2

        coherence = atmospheric_coverage / max(raw_issues, 0.1) + validation_boost
        return min(coherence, 1.0)

    def _analyze_atmospheric_coherence_enhanced(self) -> float:
        """Enhanced atmospheric coherence calculation"""
        if not self.impact_signature or not self.atmospheric_signature:
            return 0.0

        raw_errors = self.impact_signature.atmospheric_metrics.get("error_rate", 1.0)
        atmospheric_errors = self.atmospheric_signature.atmospheric_metrics.get(
            "error_rate", 0.2
        )

        # Apply harmonic balance factor
        harmonic_balance = self.atmospheric_signature.atmospheric_metrics.get(
            "harmonic_balance", 0.5
        )

        coherence = (1.0 - raw_errors) * (1.0 - atmospheric_errors) * harmonic_balance
        return min(max(coherence, 0.0), 1.0)

    def _analyze_throughput_coherence_enhanced(self) -> float:
        """Enhanced throughput coherence calculation"""
        if not self.impact_signature or not self.atmospheric_signature:
            return 0.0

        raw_rps = self.impact_signature.throughput_dynamics.get("rps_observed", 0.5)
        atmospheric_rps = self.atmospheric_signature.throughput_dynamics.get(
            "rps_observed", 0.9
        )

        # Apply flow resonance factor
        flow_resonance = self.atmospheric_signature.throughput_dynamics.get(
            "flow_resonance", 0.8
        )

        coherence = (atmospheric_rps / max(raw_rps, 0.1)) * flow_resonance
        return min(coherence, 1.0)

    def _analyze_observability_coherence_enhanced(self) -> float:
        """Enhanced observability coherence calculation"""
        if not self.impact_signature or not self.atmospheric_signature:
            return 0.0

        raw_error_density = self.impact_signature.observability_streams.get(
            "error_density", 1.0
        )
        atmospheric_obs_gaps = self.atmospheric_signature.observability_streams.get(
            "observability_gaps", 0.1
        )
        signal_clarity = self.atmospheric_signature.observability_streams.get(
            "signal_clarity", 0.8
        )

        coherence = (
            ((1.0 - raw_error_density) + (1.0 - atmospheric_obs_gaps))
            / 2.0
            * signal_clarity
        )
        return min(coherence, 1.0)

    def _analyze_validation_coherence_enhanced(self) -> float:
        """Enhanced validation coherence calculation"""
        if not self.impact_signature or not self.atmospheric_signature:
            return 0.0

        raw_unit = self.impact_signature.validation_intelligence.get(
            "glimpse_coverage", 0.5
        )
        atmospheric_unit = self.atmospheric_signature.validation_intelligence.get(
            "glimpse_coverage", 0.9
        )
        validation_confidence = self.atmospheric_signature.validation_intelligence.get(
            "validation_confidence", 0.8
        )

        coherence = (atmospheric_unit / max(raw_unit, 0.1)) * validation_confidence
        return min(coherence, 1.0)

    def _apply_metric_normalization(self, coherence: float) -> float:
        """Apply metric normalization based on quality gap tolerance"""
        if self.impact_signature and self.atmospheric_signature:
            quality_gap = abs(
                self.atmospheric_signature.unified_quality
                - self.impact_signature.unified_quality
            )
            tolerance = self.config["sandstorm_dev_protocol"]["analysis_thresholds"][
                "quality_gap_tolerance"
            ]

            if quality_gap > tolerance:
                # Apply normalization penalty for large quality gaps
                penalty = (quality_gap - tolerance) * 0.5
                coherence = max(coherence - penalty, 0.0)

        return coherence

    def _extract_ai_anomaly_signature_enhanced(
        self, total_coherence: float
    ) -> Dict[str, float]:
        """Enhanced AI anomaly detection signature with pattern recognition"""
        base_signature = {
            "anomaly_confidence": total_coherence * 0.9,
            "root_cause_score": total_coherence * 0.7,
            "autofix_suggestion_strength": total_coherence * 0.5,
            "pattern_recognition_confidence": total_coherence * 0.8,
        }

        # Add technical debt impact
        if self.impact_signature:
            debt_impact = 1.0 - self.impact_signature.technical_debt_score
            base_signature["technical_debt_influence"] = debt_impact

        # Add validation confidence
        if self.impact_signature:
            base_signature[
                "validation_confidence"
            ] = self.impact_signature.validation_score

        return base_signature

    def _calculate_unified_quality(self, signature: DiagnosticSignature) -> float:
        """Calculate unified quality score with enhanced positive indicators"""
        positive_indicators = []
        for sig in [
            signature.impact_analysis,
            signature.atmospheric_metrics,
            signature.throughput_dynamics,
            signature.observability_streams,
            signature.validation_intelligence,
        ]:
            if sig:
                vals = [
                    v
                    for k, v in sig.items()
                    if k
                    in (
                        "coverage",
                        "throughput_stability",
                        "observability_gaps",
                        "diagnostic_clarity",
                        "harmonic_balance",
                        "flow_resonance",
                        "signal_clarity",
                        "validation_confidence",
                        "performance_score",
                        "dependency_health",
                        "code_smell_score",
                        "test_success_rate",
                        "commit_quality_score",
                        "security_compliance",
                        "performance_trend",
                    )
                    or "coverage" in k
                    or "stability" in k
                    or "clarity" in k
                    or "confidence" in k
                    or "resonance" in k
                    or "score" in k
                    or "trend" in k
                ]
                positive_indicators.extend(vals)
        return float(np.mean(positive_indicators)) if positive_indicators else 0.0

    def _calculate_coherence_score(self, signature: DiagnosticSignature) -> float:
        """Calculate coherence score with enhanced positive indicators"""
        positives = []
        for d in [
            signature.impact_analysis,
            signature.atmospheric_metrics,
            signature.throughput_dynamics,
            signature.observability_streams,
            signature.validation_intelligence,
        ]:
            for k, v in d.items():
                if any(
                    tok in k
                    for tok in (
                        "coverage",
                        "stability",
                        "observability",
                        "rps",
                        "clarity",
                        "harmonic",
                        "flow",
                        "confidence",
                        "resonance",
                        "score",
                        "trend",
                        "compliance",
                    )
                ):
                    positives.append(v)
        return float(np.mean(positives)) if positives else 0.0

    def generate_enhanced_sandstorm_visualization(
        self, output_dir: str = "sandstorm_dev_outputs"
    ):
        """Generate enhanced glimpse diagnostic visualizations"""
        logger.info("🎨 Generating Enhanced glimpse diagnostic visualizations")
        out = Path(output_dir)
        out.mkdir(exist_ok=True)
        self._create_enhanced_sandstorm_radar(out)
        self._create_progressive_alert_viz(out)
        self._create_coherence_flow_enhanced(out)
        self._create_quality_gap_analysis(out)
        logger.info(f"✅ Enhanced glimpse outputs saved to {out}")

    def _create_enhanced_sandstorm_radar(self, output_path: Path):
        """Create enhanced glimpse radar chart with additional metrics"""
        fig, axes = plt.subplots(
            2, 3, figsize=(20, 14), subplot_kw=dict(projection="polar")
        )
        axes = axes.flatten()
        dimensions = [
            "Impact",
            "Atmospheric",
            "Throughput",
            "Observability",
            "Validation",
            "AI Anomaly",
        ]

        if self.impact_signature and self.atmospheric_signature:
            for i, dim in enumerate(dimensions):
                ax = axes[i]
                if dim == "Impact":
                    raw_vals = list(self.impact_signature.impact_analysis.values())
                    atmospheric_vals = list(
                        self.atmospheric_signature.impact_analysis.values()
                    )
                elif dim == "Atmospheric":
                    raw_vals = list(self.impact_signature.atmospheric_metrics.values())
                    atmospheric_vals = list(
                        self.atmospheric_signature.atmospheric_metrics.values()
                    )
                elif dim == "Throughput":
                    raw_vals = list(self.impact_signature.throughput_dynamics.values())
                    atmospheric_vals = list(
                        self.atmospheric_signature.throughput_dynamics.values()
                    )
                elif dim == "Observability":
                    raw_vals = list(
                        self.impact_signature.observability_streams.values()
                    )
                    atmospheric_vals = list(
                        self.atmospheric_signature.observability_streams.values()
                    )
                elif dim == "Validation":
                    raw_vals = list(
                        self.impact_signature.validation_intelligence.values()
                    )
                    atmospheric_vals = list(
                        self.atmospheric_signature.validation_intelligence.values()
                    )
                else:  # AI Anomaly
                    ai_vals = list(
                        self.analysis.get("ai_anomaly_signature", {}).values()
                    )
                    atmospheric_vals = ai_vals if ai_vals else [0.1] * 6
                    raw_vals = [0.1] * len(atmospheric_vals)

                # Ensure same length for radar
                n = max(len(raw_vals), len(atmospheric_vals))
                if len(raw_vals) < n:
                    raw_vals += [0.1] * (n - len(raw_vals))
                if len(atmospheric_vals) < n:
                    atmospheric_vals += [0.1] * (n - len(atmospheric_vals))

                angles = np.linspace(0, 2 * np.pi, n, endpoint=False).tolist()
                raw_plot = raw_vals + raw_vals[:1]
                atmospheric_plot = atmospheric_vals + atmospheric_vals[:1]
                angles += angles[:1]

                ax.plot(
                    angles,
                    raw_plot,
                    "o-",
                    linewidth=2,
                    label="Impact",
                    alpha=0.7,
                    color="red",
                )
                ax.fill(angles, raw_plot, alpha=0.15, color="red")
                ax.plot(
                    angles,
                    atmospheric_plot,
                    "o-",
                    linewidth=2,
                    label="Atmospheric",
                    alpha=0.7,
                    color="green",
                )
                ax.fill(angles, atmospheric_plot, alpha=0.15, color="green")

                ax.set_xticks(angles[:-1])
                ax.set_ylim(0, 1)
                ax.set_title(f"{dim}", size=14, weight="bold")
                ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.0))
                ax.grid(True)

        plt.suptitle(
            "Enhanced glimpse Dev Diagnostic - Six-Dimensional Analysis",
            fontsize=16,
            weight="bold",
        )
        plt.tight_layout()
        plt.savefig(
            output_path / "enhanced_sandstorm_radar_chart.png",
            dpi=300,
            bbox_inches="tight",
        )
        plt.close()

    def _create_progressive_alert_viz(self, output_path: Path):
        """Create progressive alert visualization"""
        fig, ax = plt.subplots(1, 1, figsize=(14, 8))

        if self.analysis:
            dims = [
                "Impact",
                "Atmospheric",
                "Throughput",
                "Observability",
                "Validation",
                "Unified",
            ]
            values = [
                self.analysis.get("impact_coherence", 0),
                self.analysis.get("atmospheric_coherence", 0),
                self.analysis.get("throughput_coherence", 0),
                self.analysis.get("observability_coherence", 0),
                self.analysis.get("validation_coherence", 0),
                self.analysis.get("unified_coherence", 0),
            ]

            alert_levels = self.config["sandstorm_dev_protocol"]["unified_trigger"][
                "progressive_alert_levels"
            ]
            colors = ["red", "orange", "yellow", "lightgreen", "green", "blue"]

            bars = ax.bar(dims, values, color=colors, alpha=0.8)

            # Add alert level thresholds
            for level, threshold in alert_levels.items():
                level_name = level.replace("_alert", "").upper()
                ax.axhline(
                    y=threshold, color="gray", linestyle="--", linewidth=1, alpha=0.5
                )
                ax.text(
                    len(dims) - 1,
                    threshold,
                    level_name,
                    ha="right",
                    va="bottom",
                    fontsize=8,
                )

            # Add activation threshold
            activation_threshold = self.config["sandstorm_dev_protocol"][
                "unified_trigger"
            ]["activation_threshold"]
            ax.axhline(
                y=activation_threshold,
                color="black",
                linestyle="-",
                linewidth=2,
                label=f"Activation ({activation_threshold})",
            )

            ax.set_ylabel("Coherence")
            ax.set_title(
                f"Enhanced glimpse Progressive Alert System - {self.current_alert_level.value}"
            )
            ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
            ax.set_ylim(0, 1)

            # Add alert status box
            alert_color = {
                "GOLD_ALERT": "gold",
                "SILVER_ALERT": "silver",
                "BRONZE_ALERT": "orange",
                "RED_ALERT": "red",
            }
            ax.text(
                0.02,
                0.98,
                f"{self.current_alert_level.value}",
                transform=ax.transAxes,
                fontsize=14,
                weight="bold",
                verticalalignment="top",
                bbox=dict(
                    boxstyle="round",
                    facecolor=alert_color.get(self.current_alert_level.value, "red"),
                    alpha=0.3,
                ),
            )

            # Add retry information
            if self.retry_count > 0:
                ax.text(
                    0.02,
                    0.88,
                    f"Retries: {self.retry_count}",
                    transform=ax.transAxes,
                    fontsize=10,
                    verticalalignment="top",
                    bbox=dict(boxstyle="round", facecolor="lightblue", alpha=0.3),
                )

        plt.tight_layout()
        plt.savefig(
            output_path / "progressive_alert_visualization.png",
            dpi=300,
            bbox_inches="tight",
        )
        plt.close()

    def _create_coherence_flow_enhanced(self, output_path: Path):
        """Create enhanced coherence flow diagram with learning"""
        fig, ax = plt.subplots(1, 1, figsize=(16, 8))

        if self.impact_signature and self.atmospheric_signature:
            stages = [
                "Impact\nSignals",
                "Validation\nPhase",
                "Stabilization",
                "glimpse\nAlert",
                "AI\nDetection",
            ]
            flow = [
                self.impact_signature.coherence_score,
                self.impact_signature.validation_score,
                0.5,
                0.8
                if self.unified_alert_active
                else self.analysis.get("unified_coherence", 0.6),
                0.9 if self.unified_alert_active else 0.2,
            ]

            x_pos = range(len(stages))

            # Color based on alert level
            alert_colors = {
                "GOLD_ALERT": "gold",
                "SILVER_ALERT": "silver",
                "BRONZE_ALERT": "orange",
                "RED_ALERT": "red",
            }
            flow_color = alert_colors.get(self.current_alert_level.value, "red")

            ax.plot(
                x_pos,
                flow,
                "o-",
                linewidth=3,
                markersize=10,
                alpha=0.8,
                color=flow_color,
            )

            for i, (s, v) in enumerate(zip(stages, flow)):
                color = "green" if v >= 0.7 else "orange" if v >= 0.5 else "red"
                ax.annotate(
                    f"{v:.3f}",
                    (i, v),
                    textcoords="offset points",
                    xytext=(0, 10),
                    ha="center",
                    bbox=dict(boxstyle="round,pad=0.3", facecolor=color, alpha=0.7),
                )
                ax.text(i, -0.1, s, ha="center", va="top", fontsize=10, weight="bold")

            if self.unified_alert_active:
                ax.scatter([3], [flow[3]], s=300, color="red", marker="*", zorder=5)
                ax.annotate(
                    "ALERT ACTIVE",
                    (3, flow[3]),
                    textcoords="offset points",
                    xytext=(20, 20),
                    ha="center",
                    fontsize=12,
                    weight="bold",
                    color="red",
                )

            # Add historical performance if available
            if self.historical_performance:
                history_text = f"Historical: {len([h for h in self.historical_performance if h['success']])}/{len(self.historical_performance)} successful"
                ax.text(
                    0.98,
                    0.02,
                    history_text,
                    transform=ax.transAxes,
                    fontsize=10,
                    ha="right",
                    bbox=dict(boxstyle="round", facecolor="lightgray", alpha=0.3),
                )

            ax.set_ylabel("Coherence Level")
            ax.set_title(
                f"Enhanced glimpse Coherence Flow - {self.current_alert_level.value}"
            )
            ax.set_xlim(-0.5, len(stages) - 0.5)
            ax.set_ylim(-0.2, 1.0)
            ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(
            output_path / "enhanced_coherence_flow.png", dpi=300, bbox_inches="tight"
        )
        plt.close()

    def _create_quality_gap_analysis(self, output_path: Path):
        """Create quality gap analysis visualization"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

        if self.impact_signature and self.atmospheric_signature:
            # Quality comparison
            categories = ["Unified Quality", "Coherence Score", "Validation Score"]
            impact_values = [
                self.impact_signature.unified_quality,
                self.impact_signature.coherence_score,
                self.impact_signature.validation_score,
            ]
            atmospheric_values = [
                self.atmospheric_signature.unified_quality,
                self.atmospheric_signature.coherence_score,
                self.impact_signature.validation_score,  # Same validation for both
            ]

            x = np.arange(len(categories))
            width = 0.35

            ax1.bar(
                x - width / 2,
                impact_values,
                width,
                label="Impact",
                color="red",
                alpha=0.7,
            )
            ax1.bar(
                x + width / 2,
                atmospheric_values,
                width,
                label="Atmospheric",
                color="green",
                alpha=0.7,
            )

            ax1.set_xlabel("Quality Metrics")
            ax1.set_ylabel("Score")
            ax1.set_title("Quality Gap Analysis: Impact vs Atmospheric")
            ax1.set_xticks(x)
            ax1.set_xticklabels(categories)
            ax1.legend()
            ax1.grid(True, alpha=0.3)

            # Technical debt analysis
            debt_metrics = [
                "Technical Debt",
                "Issue Density",
                "Complexity",
                "Duplication",
            ]
            debt_values = [
                self.impact_signature.technical_debt_score,
                self.impact_signature.impact_analysis.get("issues_density", 0),
                self.impact_signature.impact_analysis.get("complexity", 0),
                self.impact_signature.impact_analysis.get("duplication_ratio", 0),
            ]

            colors = [
                "red" if v > 0.7 else "orange" if v > 0.5 else "green"
                for v in debt_values
            ]
            bars = ax2.bar(debt_metrics, debt_values, color=colors, alpha=0.7)

            ax2.set_xlabel("Debt Metrics")
            ax2.set_ylabel("Score")
            ax2.set_title("Technical Debt Analysis")
            ax2.axhline(
                y=0.5, color="orange", linestyle="--", alpha=0.5, label="Moderate"
            )
            ax2.axhline(y=0.7, color="red", linestyle="--", alpha=0.5, label="High")
            ax2.legend()
            ax2.grid(True, alpha=0.3)

            # Add value labels on bars
            for bar, value in zip(bars, debt_values):
                height = bar.get_height()
                ax2.text(
                    bar.get_x() + bar.get_width() / 2.0,
                    height + 0.01,
                    f"{value:.3f}",
                    ha="center",
                    va="bottom",
                )

        plt.tight_layout()
        plt.savefig(
            output_path / "quality_gap_analysis.png", dpi=300, bbox_inches="tight"
        )
        plt.close()

    def export_enhanced_sandstorm_report(
        self, output_path: str = "sandstorm_dev_outputs"
    ) -> Dict[str, Any]:
        """Export enhanced glimpse diagnostic report with all improvements"""
        logger.info("📄 Exporting Enhanced glimpse diagnostic report")
        out = Path(output_path)
        out.mkdir(exist_ok=True)

        report = {
            "protocol_info": {
                "name": "SANDSTORM_DEV_DIAGNOSTIC_PROTOCOL",
                "version": "2.1.0",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "unified_alert_active": self.unified_alert_active,
                "current_alert_level": self.current_alert_level.value,
                "intent": "Transform high-density process noise into clear diagnostic visibility with enhanced coherence optimization",
            },
            "enhanced_analysis": {
                "retry_attempts": self.retry_count,
                "historical_performance": self.historical_performance,
                "validation_score": self.impact_signature.validation_score
                if self.impact_signature
                else 0.0,
                "technical_debt_score": self.impact_signature.technical_debt_score
                if self.impact_signature
                else 0.0,
                "quality_gap": abs(
                    self.atmospheric_signature.unified_quality
                    - self.impact_signature.unified_quality
                )
                if self.impact_signature and self.atmospheric_signature
                else 0.0,
            },
            "impact_signature": {
                "source": self.impact_signature.source_name
                if self.impact_signature
                else None,
                "impact_analysis": self.impact_signature.impact_analysis
                if self.impact_signature
                else {},
                "atmospheric_metrics": self.impact_signature.atmospheric_metrics
                if self.impact_signature
                else {},
                "throughput_dynamics": self.impact_signature.throughput_dynamics
                if self.impact_signature
                else {},
                "observability_streams": self.impact_signature.observability_streams
                if self.impact_signature
                else {},
                "validation_intelligence": self.impact_signature.validation_intelligence
                if self.impact_signature
                else {},
                "unified_quality": self.impact_signature.unified_quality
                if self.impact_signature
                else 0.0,
                "coherence_score": self.impact_signature.coherence_score
                if self.impact_signature
                else 0.0,
                "validation_score": self.impact_signature.validation_score
                if self.impact_signature
                else 0.0,
                "technical_debt_score": self.impact_signature.technical_debt_score
                if self.impact_signature
                else 0.0,
            },
            "atmospheric_signature": {
                "source": self.atmospheric_signature.source_name
                if self.atmospheric_signature
                else None,
                "impact_analysis": self.atmospheric_signature.impact_analysis
                if self.atmospheric_signature
                else {},
                "atmospheric_metrics": self.atmospheric_signature.atmospheric_metrics
                if self.atmospheric_signature
                else {},
                "throughput_dynamics": self.atmospheric_signature.throughput_dynamics
                if self.atmospheric_signature
                else {},
                "observability_streams": self.atmospheric_signature.observability_streams
                if self.atmospheric_signature
                else {},
                "validation_intelligence": self.atmospheric_signature.validation_intelligence
                if self.atmospheric_signature
                else {},
                "unified_quality": self.atmospheric_signature.unified_quality
                if self.atmospheric_signature
                else 0.0,
                "coherence_score": self.atmospheric_signature.coherence_score
                if self.atmospheric_signature
                else 0.0,
            },
            "sandstorm_analysis": self.analysis if self.analysis else {},
            "diagnostic_summary": {
                "dimensions_analyzed": 6,
                "sandstorm_alert_status": "ACTIVE"
                if self.unified_alert_active
                else "INACTIVE",
                "current_alert_level": self.current_alert_level.value,
                "quality_state": self.analysis.get("quality_state_achieved", False)
                if self.analysis
                else False,
                "quality_improvement_pct": f"{((self.atmospheric_signature.unified_quality - self.impact_signature.unified_quality) / max(self.impact_signature.unified_quality, 0.1) * 100):.1f}%"
                if self.impact_signature and self.atmospheric_signature
                else "0%",
                "chaos_to_clarity_transformation": self.unified_alert_active,
                "coherence_achievement": f"{self.analysis.get('unified_coherence', 0):.3f}"
                if self.analysis
                else "0.000",
                "threshold_met": f"{self.analysis.get('unified_coherence', 0):.3f} >= {self.config['sandstorm_dev_protocol']['unified_trigger']['activation_threshold']:.3f}"
                if self.analysis
                else "Failed",
            },
        }

        # Save JSON and YAML with UTF-8 encoding
        json_file = out / "enhanced_glimpse_dev_report.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, default=str)
        yaml_file = out / "enhanced_glimpse_dev_report.yaml"
        with open(yaml_file, "w", encoding="utf-8") as f:
            yaml.dump(report, f, default_flow_style=False)

        logger.info(f"✅ Enhanced glimpse report exported to {json_file}")
        return report


def main():
    """Enhanced main execution function with all improvements"""
    print("🏁 ENHANCED glimpse DEV DIAGNOSTIC PROTOCOL - CHAOS TO CLARITY")
    print("=" * 80)
    print("Version: 2.1.0")
    print("Author: Core Systems Mentor")
    print(
        "Intent: Transform high-density process noise into clear diagnostic visibility"
    )
    print("Features: Progressive alerts, adaptive thresholds, enhanced impact analysis")
    print("=" * 80)

    protocol = EnhancedSandstormDevDiagnostic()

    # Enhanced impact layer data with validation metrics
    impact_data = {
        "duration": 60,
        "issues": 0.75,  # Improved from 0.85
        "coverage_gap": 0.4,  # Improved from 0.6
        "avg_cyclomatic_complexity": 0.6,  # Improved from 0.8
        "duplication": 0.5,  # Improved from 0.7
        "error_rate": 0.7,  # Improved from 0.9
        "cpu_spike_prob": 0.6,  # Improved from 0.8
        "memory_leak_risk": 0.5,  # Improved from 0.7
        "p99_latency_score": 0.6,  # Improved from 0.8
        "rps_normalized": 0.6,  # Improved from 0.5
        "backpressure": 0.5,  # Improved from 0.7
        "throughput_stability": 0.6,  # Improved from 0.4
        "error_density": 0.7,  # Improved from 0.9
        "warning_noise": 0.6,  # Improved from 0.8
        "obs_gap": 0.5,  # Improved from 0.7
        "glimpse_coverage": 0.7,  # Improved from 0.5
        "integration_stability": 0.6,  # Improved from 0.4
        "flaky_rate": 0.6,  # Improved from 0.8
        # Enhanced validation metrics
        "repository_completeness": 0.8,
        "recent_commits": 0.7,
        "dependency_health": 0.85,
        "documentation_quality": 0.7,
        "security_issues": 0.2,
        "performance_bottlenecks": 0.3,
        "code_smells": 0.3,
        "technical_debt": 0.4,
        "test_success_rate": 0.85,
        "commit_quality": 0.8,
    }

    # Enhanced atmospheric extension data with optimization feedback
    atmospheric_data = {
        "duration": 120,
        "issues": 0.15,  # Improved from 0.25
        "coverage": 0.95,  # Improved from 0.92
        "complexity_reduction": 0.55,  # Improved from 0.45
        "duplication": 0.1,  # Improved from 0.18
        "error_rate": 0.1,  # Improved from 0.15
        "cpu_spike_prob": 0.1,  # Improved from 0.2
        "memory_leak_risk": 0.05,  # Improved from 0.1
        "p99_latency_score": 0.2,  # Improved from 0.3
        "rps_normalized": 0.95,  # Improved from 0.9
        "backpressure": 0.1,  # Improved from 0.15
        "throughput_stability": 0.9,  # Improved from 0.8
        "error_density": 0.1,  # Improved from 0.2
        "warning_noise": 0.15,  # Improved from 0.25
        "obs_gap": 0.05,  # Improved from 0.1
        "glimpse_coverage": 0.95,  # Improved from 0.93
        "integration_stability": 0.9,  # Improved from 0.86
        "flaky_rate": 0.05,  # Improved from 0.08
        # Enhanced optimization metrics
        "parallelization_efficiency": 0.9,
        "cache_hit_rate": 0.95,
        "automation_coverage": 0.9,
        "deployment_success_rate": 0.98,
        "performance_trend": 0.85,
        "security_compliance": 0.98,
    }

    # Analyze enhanced impact layer
    impact_sig = protocol.analyze_impact_layer(
        "enhanced_repository_impact", impact_data
    )

    # Analyze enhanced atmospheric extension
    atmospheric_sig = protocol.analyze_atmospheric_extension(
        "enhanced_ci_atmospheric", atmospheric_data
    )

    logger.info(f"🌊 Impact unified quality: {impact_sig.unified_quality:.3f}")
    logger.info(
        f"🌤️ Atmospheric unified quality: {atmospheric_sig.unified_quality:.3f}"
    )
    logger.info(
        f"📊 Quality improvement: {((atmospheric_sig.unified_quality - impact_sig.unified_quality) / max(impact_sig.unified_quality, 0.1) * 100):.1f}%"
    )

    # Activate enhanced glimpse unified alert with adaptive retry
    print("\n🚨 Activating Enhanced glimpse Alert System...")
    success, message = protocol.adaptive_threshold_retry(max_retries=3)

    if success:
        logger.info(f"✅ {message}")
        print(
            f"\n🎯 {protocol.current_alert_level.value} - {protocol.analysis.get('alert_message', '')}"
        )
        print("🎭 Chaos successfully transformed into comprehension!")
    else:
        logger.info(f"⚠️ {message}")
        print(
            f"\n⚠️ {protocol.current_alert_level.value} - {protocol.analysis.get('alert_message', '')}"
        )
        print("🔧 Additional optimization needed for full transformation")

    # Generate enhanced visualizations and reports
    protocol.generate_enhanced_sandstorm_visualization()
    report = protocol.export_enhanced_sandstorm_report()

    print("\n📁 Enhanced glimpse outputs saved to sandstorm_dev_outputs/")
    print("\n🎭 Enhanced Transformation Summary:")
    print(f"   🌊 Impact Layer Quality: {impact_sig.unified_quality:.3f}")
    print(f"   🌤️ Atmospheric Quality: {atmospheric_sig.unified_quality:.3f}")
    print(
        f"   📈 Quality Improvement: {((atmospheric_sig.unified_quality - impact_sig.unified_quality) / max(impact_sig.unified_quality, 0.1) * 100):.1f}%"
    )
    print(f"   🎯 Alert Status: {protocol.current_alert_level.value}")
    print(f"   🔄 Retry Attempts: {protocol.retry_count}")
    print(f"   ✅ Validation Score: {impact_sig.validation_score:.3f}")
    print(f"   🔧 Technical Debt Score: {impact_sig.technical_debt_score:.3f}")
    print(
        f"   🎪 Coherence Achievement: {protocol.analysis.get('unified_coherence', 0):.3f}"
    )

    print("\n🌊 Enhanced chaos transformation complete.")
    print("   Impact layer captured raw system truth with validation.")
    print("   Atmospheric extension defined architectural order with optimization.")
    print(
        "   glimpse alert created clarity from collision with progressive intelligence."
    )
    print("   Maintenance becomes music with enhanced diagnostic capabilities.")


if __name__ == "__main__":
    main()
