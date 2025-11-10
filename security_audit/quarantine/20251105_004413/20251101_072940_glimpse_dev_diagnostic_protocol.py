#!/usr/bin/env python3
"""
glimpse Dev Diagnostic Protocol - Unified Software Metrics Analysis
Enhanced framework translating chaotic telemetry into structured diagnostic clarity.

Author: Core Systems Mentor
Version: 2.0.0
Purpose: Transform high-density process noise into clear diagnostic visibility across
development dimensions: Impact Analysis, Atmospheric Processing, Throughput Dynamics,
Observability Streams, Validation Intelligence, and AI Anomaly Detection.
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import matplotlib.pyplot as plt
import numpy as np
import yaml

# Configure logging for diagnostic reproducibility
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("sandstorm_dev_diagnostic.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


@dataclass
class DiagnosticSignature:
    """Represents diagnostic signature across development dimensions"""

    source_name: str
    duration: float
    impact_analysis: Dict[str, float] = field(
        default_factory=dict
    )  # Static Analysis → Impact Analysis
    atmospheric_metrics: Dict[str, float] = field(
        default_factory=dict
    )  # Runtime → Atmospheric Metrics
    throughput_dynamics: Dict[str, float] = field(
        default_factory=dict
    )  # Throughput → Throughput Dynamics
    observability_streams: Dict[str, float] = field(
        default_factory=dict
    )  # Logs → Observability Streams
    validation_intelligence: Dict[str, float] = field(
        default_factory=dict
    )  # Tests → Validation Intelligence
    ai_anomaly_signature: Dict[str, float] = field(default_factory=dict)
    unified_quality: float = 0.0
    coherence_score: float = 0.0


class SandstormDevDiagnostic:
    """
    Enhanced diagnostic Glimpse processing codebase signals across development metrics.
    Implements unified alert to align metrics and enable AI anomaly detection.
    Transforms chaos into comprehension through systematic spectral analysis.
    """

    def __init__(self, config_path: str = "glimpse_dev_config.yaml"):
        self.config = self._load_config(config_path)
        self.impact_signature = None  # raw_signature → impact_signature
        self.atmospheric_signature = None  # pipeline_signature → atmospheric_signature
        self.analysis = {}
        self.unified_alert_active = False

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.warning(f"Config file {config_path} not found, using defaults")
            return self._get_default_sandstorm_config()

    def _get_default_sandstorm_config(self) -> Dict[str, Any]:
        return {
            "impact_modes": {  # static_modes → impact_modes
                "issues_weight": 1.0,
                "coverage_weight": 0.9,
                "complexity_weight": 0.7,
                "duplication_threshold": 0.5,
                "diagnostic_clarity": 0.8,
            },
            "atmospheric_modes": {  # runtime_modes → atmospheric_modes
                "error_rate_threshold": 0.8,
                "cpu_spike_sensitivity": 0.7,
                "memory_leak_sensitivity": 0.8,
                "response_time_target": 0.6,
                "harmonic_balance": 0.75,
            },
            "throughput_dynamics": {  # throughput_modes → throughput_dynamics
                "requests_per_second_target": 0.8,
                "queue_backpressure_tolerance": 0.6,
                "throughput_stability": 0.7,
                "flow_resonance": 0.8,
            },
            "observability_streams": {  # logs_modes → observability_streams
                "error_density_tolerance": 0.6,
                "warning_noise_threshold": 0.7,
                "observability_coverage": 0.8,
                "signal_clarity": 0.7,
            },
            "validation_intelligence": {  # test_modes → validation_intelligence
                "glimpse_coverage": 0.8,
                "integration_stability": 0.7,
                "flaky_test_rate_tolerance": 0.6,
                "validation_confidence": 0.85,
            },
            "ai_detection_modes": {  # ai_modes → ai_detection_modes
                "anomaly_sensitivity": 0.7,
                "root_cause_confidence": 0.6,
                "pattern_recognition": 0.8,
                "diagnostic_confidence": 0.75,
            },
            "unified_alert": {
                "activation_threshold": 0.75,
                "quality_requirement": 0.65,
                "incident_window_seconds": 300,
                "coherence_stability": 0.8,
            },
        }

    # --- Analysis entry points ---
    def analyze_impact_layer(
        self, source_name: str, raw_data: Any
    ) -> DiagnosticSignature:
        """Analyze impact layer signals from codebase or incident window"""
        logger.info(f"Analyzing impact layer: {source_name}")
        sig = DiagnosticSignature(
            source_name=source_name, duration=raw_data.get("duration", 60.0)
        )

        sig.impact_analysis = self._analyze_impact_raw(raw_data)
        sig.atmospheric_metrics = self._analyze_atmospheric_raw(raw_data)
        sig.throughput_dynamics = self._analyze_throughput_raw(raw_data)
        sig.observability_streams = self._analyze_observability_raw(raw_data)
        sig.validation_intelligence = self._analyze_validation_raw(raw_data)

        sig.unified_quality = self._calculate_unified_quality(sig)
        sig.coherence_score = self._calculate_coherence_score(sig)

        self.impact_signature = sig
        logger.info("Impact layer analysis complete")
        return sig

    def analyze_atmospheric_extension(
        self, source_name: str, processed_data: Any
    ) -> DiagnosticSignature:
        """Analyze atmospheric extension signals from CI/CD, staging and observability"""
        logger.info(f"Analyzing atmospheric extension: {source_name}")
        sig = DiagnosticSignature(
            source_name=source_name, duration=processed_data.get("duration", 120.0)
        )

        sig.impact_analysis = self._analyze_impact_atmospheric(processed_data)
        sig.atmospheric_metrics = self._analyze_atmospheric_processed(processed_data)
        sig.throughput_dynamics = self._analyze_throughput_atmospheric(processed_data)
        sig.observability_streams = self._analyze_observability_atmospheric(
            processed_data
        )
        sig.validation_intelligence = self._analyze_validation_atmospheric(
            processed_data
        )

        # Atmospheric extension improves quality through architectural refinement
        sig.unified_quality = self._calculate_unified_quality(sig) * 1.2
        sig.coherence_score = self._calculate_coherence_score(sig) * 1.3

        self.atmospheric_signature = sig
        logger.info("Atmospheric extension analysis complete")
        return sig

    # --- Impact Layer analyzers ---
    def _analyze_impact_raw(self, data: Any) -> Dict[str, float]:
        """Analyze impact layer static metrics"""
        return {
            "issues_density": min(data.get("issues", 0.9), 1.0),
            "coverage": max(0.0, 1.0 - data.get("coverage_gap", 0.6)),
            "complexity": min(data.get("avg_cyclomatic_complexity", 0.8), 1.0),
            "duplication_ratio": min(data.get("duplication", 0.7), 1.0),
            "diagnostic_clarity": max(0.0, 1.0 - data.get("complexity", 0.8)),
        }

    def _analyze_atmospheric_raw(self, data: Any) -> Dict[str, float]:
        """Analyze atmospheric runtime metrics"""
        return {
            "error_rate": min(data.get("error_rate", 0.9), 1.0),
            "cpu_spikes": min(data.get("cpu_spike_prob", 0.8), 1.0),
            "memory_leak_risk": min(data.get("memory_leak_risk", 0.7), 1.0),
            "p99_latency": min(data.get("p99_latency_score", 0.85), 1.0),
            "harmonic_balance": max(0.0, 1.0 - data.get("error_rate", 0.9)),
        }

    def _analyze_throughput_raw(self, data: Any) -> Dict[str, float]:
        """Analyze throughput dynamics raw metrics"""
        return {
            "rps_observed": min(data.get("rps_normalized", 0.5), 1.0),
            "queue_backpressure": min(data.get("backpressure", 0.8), 1.0),
            "throughput_stability": min(data.get("throughput_stability", 0.4), 1.0),
            "flow_resonance": max(0.0, data.get("throughput_stability", 0.4)),
        }

    def _analyze_observability_raw(self, data: Any) -> Dict[str, float]:
        """Analyze observability streams raw metrics"""
        return {
            "error_density": min(data.get("error_density", 0.9), 1.0),
            "warning_noise": min(data.get("warning_noise", 0.8), 1.0),
            "observability_gaps": min(data.get("obs_gap", 0.7), 1.0),
            "signal_clarity": max(0.0, 1.0 - data.get("warning_noise", 0.8)),
        }

    def _analyze_validation_raw(self, data: Any) -> Dict[str, float]:
        """Analyze validation intelligence raw metrics"""
        return {
            "glimpse_coverage": max(0.0, data.get("glimpse_coverage", 0.5)),
            "integration_stability": max(0.0, data.get("integration_stability", 0.4)),
            "flaky_test_rate": min(data.get("flaky_rate", 0.8), 1.0),
            "validation_confidence": max(0.0, data.get("glimpse_coverage", 0.5)),
        }

    # --- Atmospheric Extension analyzers ---
    def _analyze_impact_atmospheric(self, data: Any) -> Dict[str, float]:
        """Analyze impact layer atmospheric metrics"""
        return {
            "issues_density": max(0.0, data.get("issues", 0.3)),
            "coverage": min(data.get("coverage", 0.9), 1.0),
            "complexity": max(0.0, 1.0 - data.get("complexity_reduction", 0.4)),
            "duplication_ratio": max(0.0, data.get("duplication", 0.2)),
            "diagnostic_clarity": min(data.get("coverage", 0.9), 1.0),
        }

    def _analyze_atmospheric_processed(self, data: Any) -> Dict[str, float]:
        """Analyze atmospheric processed metrics"""
        return {
            "error_rate": max(0.0, data.get("error_rate", 0.2)),
            "cpu_spikes": max(0.0, data.get("cpu_spike_prob", 0.2)),
            "memory_leak_risk": max(0.0, data.get("memory_leak_risk", 0.2)),
            "p99_latency": max(0.0, data.get("p99_latency_score", 0.3)),
            "harmonic_balance": min(data.get("coverage", 0.9), 1.0),
        }

    def _analyze_throughput_atmospheric(self, data: Any) -> Dict[str, float]:
        """Analyze throughput atmospheric metrics"""
        return {
            "rps_observed": min(data.get("rps_normalized", 0.9), 1.0),
            "queue_backpressure": max(0.0, data.get("backpressure", 0.2)),
            "throughput_stability": min(data.get("throughput_stability", 0.8), 1.0),
            "flow_resonance": min(data.get("throughput_stability", 0.8), 1.0),
        }

    def _analyze_observability_atmospheric(self, data: Any) -> Dict[str, float]:
        """Analyze observability atmospheric metrics"""
        return {
            "error_density": max(0.0, data.get("error_density", 0.2)),
            "warning_noise": max(0.0, data.get("warning_noise", 0.3)),
            "observability_gaps": max(0.0, data.get("obs_gap", 0.1)),
            "signal_clarity": min(data.get("coverage", 0.9), 1.0),
        }

    def _analyze_validation_atmospheric(self, data: Any) -> Dict[str, float]:
        """Analyze validation atmospheric metrics"""
        return {
            "glimpse_coverage": min(data.get("glimpse_coverage", 0.9), 1.0),
            "integration_stability": min(data.get("integration_stability", 0.85), 1.0),
            "flaky_test_rate": max(0.0, data.get("flaky_rate", 0.1)),
            "validation_confidence": min(data.get("integration_stability", 0.85), 1.0),
        }

    # --- Coherence calculations and unified alert ---
    def activate_sandstorm_alert(self) -> bool:
        """Activate glimpse unified alert when metrics align for diagnostic clarity"""
        logger.info("Activating glimpse unified alert")

        if not self.impact_signature or not self.atmospheric_signature:
            logger.error(
                "Cannot activate glimpse alert without analyzing both impact and atmospheric signatures"
            )
            return False

        impact_coh = self._analyze_impact_coherence()
        atmospheric_coh = self._analyze_atmospheric_coherence()
        throughput_coh = self._analyze_throughput_coherence()
        observability_coh = self._analyze_observability_coherence()
        validation_coh = self._analyze_validation_coherence()

        total_coh = (
            impact_coh
            + atmospheric_coh
            + throughput_coh
            + observability_coh
            + validation_coh
        ) / 5.0

        threshold = self.config["unified_alert"]["activation_threshold"]

        if total_coh >= threshold:
            self.unified_alert_active = True
            logger.info(f"glimpse Alert Activated. Coherence: {total_coh:.3f}")

            ai_signature = self._extract_ai_anomaly_signature(total_coh)

            self.analysis = {
                "impact_coherence": impact_coh,  # static_coherence → impact_coherence
                "atmospheric_coherence": atmospheric_coh,  # runtime_coherence → atmospheric_coherence
                "throughput_coherence": throughput_coh,
                "observability_coherence": observability_coh,  # logs_coherence → observability_coherence
                "validation_coherence": validation_coh,  # tests_coherence → validation_coherence
                "ai_anomaly_signature": ai_signature,
                "unified_coherence": total_coh,
                "quality_state_achieved": total_coh
                >= self.config["unified_alert"]["quality_requirement"],
            }
            return True
        else:
            logger.warning(
                f"glimpse Alert not activated. Coherence: {total_coh:.3f} < {threshold}"
            )
            return False

    def _analyze_impact_coherence(self) -> float:
        """Analyze impact layer coherence"""
        if not self.impact_signature or not self.atmospheric_signature:
            return 0.0
        raw_issues = self.impact_signature.impact_analysis.get("issues_density", 1.0)
        atmospheric_coverage = self.atmospheric_signature.impact_analysis.get(
            "coverage", 0.5
        )
        coherence = atmospheric_coverage / max(raw_issues, 0.1)
        return min(coherence, 1.0)

    def _analyze_atmospheric_coherence(self) -> float:
        """Analyze atmospheric coherence"""
        if not self.impact_signature or not self.atmospheric_signature:
            return 0.0
        raw_errors = self.impact_signature.atmospheric_metrics.get("error_rate", 1.0)
        atmospheric_errors = self.atmospheric_signature.atmospheric_metrics.get(
            "error_rate", 0.2
        )
        coherence = (1.0 - raw_errors) * (1.0 - atmospheric_errors)
        return min(max(coherence, 0.0), 1.0)

    def _analyze_throughput_coherence(self) -> float:
        """Analyze throughput coherence"""
        if not self.impact_signature or not self.atmospheric_signature:
            return 0.0
        raw_rps = self.impact_signature.throughput_dynamics.get("rps_observed", 0.5)
        atmospheric_rps = self.atmospheric_signature.throughput_dynamics.get(
            "rps_observed", 0.9
        )
        coherence = atmospheric_rps / max(raw_rps, 0.1)
        return min(coherence, 1.0)

    def _analyze_observability_coherence(self) -> float:
        """Analyze observability coherence"""
        if not self.impact_signature or not self.atmospheric_signature:
            return 0.0
        raw_error_density = self.impact_signature.observability_streams.get(
            "error_density", 1.0
        )
        atmospheric_obs_gaps = self.atmospheric_signature.observability_streams.get(
            "observability_gaps", 0.1
        )
        coherence = (1.0 - raw_error_density) + (1.0 - atmospheric_obs_gaps)
        return min(coherence / 2.0, 1.0)

    def _analyze_validation_coherence(self) -> float:
        """Analyze validation coherence"""
        if not self.impact_signature or not self.atmospheric_signature:
            return 0.0
        raw_unit = self.impact_signature.validation_intelligence.get(
            "glimpse_coverage", 0.5
        )
        atmospheric_unit = self.atmospheric_signature.validation_intelligence.get(
            "glimpse_coverage", 0.9
        )
        coherence = atmospheric_unit / max(raw_unit, 0.1)
        return min(coherence, 1.0)

    def _extract_ai_anomaly_signature(self, total_coherence: float) -> Dict[str, float]:
        """Extract AI anomaly detection signature"""
        return {
            "anomaly_confidence": total_coherence * 0.9,
            "root_cause_score": total_coherence * 0.7,
            "autofix_suggestion_strength": total_coherence * 0.5,
            "pattern_recognition_confidence": total_coherence * 0.8,
        }

    # --- Quality and coherence summaries ---
    def _calculate_unified_quality(self, signature: DiagnosticSignature) -> float:
        """Calculate unified quality score across all dimensions"""
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
                    )
                    or "coverage" in k
                    or "stability" in k
                    or "clarity" in k
                    or "confidence" in k
                    or "resonance" in k
                ]
                positive_indicators.extend(vals)
        return float(np.mean(positive_indicators)) if positive_indicators else 0.0

    def _calculate_coherence_score(self, signature: DiagnosticSignature) -> float:
        """Calculate coherence score across dimensions"""
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
                    )
                ):
                    positives.append(v)
        return float(np.mean(positives)) if positives else 0.0

    # --- Visualizations and reporting ---
    def generate_sandstorm_visualization(
        self, output_dir: str = "sandstorm_dev_outputs"
    ):
        """Generate glimpse diagnostic visualizations"""
        logger.info("Generating glimpse diagnostic visualizations")
        out = Path(output_dir)
        out.mkdir(exist_ok=True)
        self._create_sandstorm_radar(out)
        self._create_unified_alert_viz(out)
        self._create_coherence_flow(out)
        logger.info(f"glimpse outputs saved to {out}")

    def _create_sandstorm_radar(self, output_path: Path):
        """Create glimpse radar chart for metrics comparison"""
        fig, axes = plt.subplots(
            2, 3, figsize=(18, 12), subplot_kw=dict(projection="polar")
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
                    atmospheric_vals = ai_vals if ai_vals else [0.1] * 4
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
                ax.set_title(f"{dim}", size=12, weight="bold")
                ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.0))
                ax.grid(True)

        plt.tight_layout()
        plt.savefig(
            output_path / "sandstorm_radar_chart.png", dpi=300, bbox_inches="tight"
        )
        plt.close()

    def _create_unified_alert_viz(self, output_path: Path):
        """Create unified alert visualization"""
        fig, ax = plt.subplots(1, 1, figsize=(12, 8))
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
            colors = ["red", "green", "blue", "purple", "orange", "gray"]
            ax.bar(dims, values, color=colors, alpha=0.8)
            threshold = self.config["unified_alert"]["activation_threshold"]
            ax.axhline(
                y=threshold,
                color="black",
                linestyle="--",
                linewidth=2,
                label=f"Threshold ({threshold})",
            )
            ax.set_ylabel("Coherence")
            ax.set_title("glimpse Unified Alert - Multi-Metric Alignment")
            ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
            ax.set_ylim(0, 1)
            if self.unified_alert_active:
                ax.text(
                    0.02,
                    0.98,
                    "glimpse ALERT ACTIVE",
                    transform=ax.transAxes,
                    fontsize=12,
                    weight="bold",
                    verticalalignment="top",
                    bbox=dict(boxstyle="round", facecolor="red", alpha=0.2),
                )
            else:
                ax.text(
                    0.02,
                    0.98,
                    "AWAITING ALERT",
                    transform=ax.transAxes,
                    fontsize=12,
                    weight="bold",
                    verticalalignment="top",
                    bbox=dict(boxstyle="round", facecolor="lightgray", alpha=0.2),
                )
        plt.tight_layout()
        plt.savefig(
            output_path / "sandstorm_unified_alert.png", dpi=300, bbox_inches="tight"
        )
        plt.close()

    def _create_coherence_flow(self, output_path: Path):
        """Create coherence flow diagram"""
        fig, ax = plt.subplots(1, 1, figsize=(14, 8))
        if self.impact_signature and self.atmospheric_signature:
            stages = [
                "Impact\nSignals",
                "Analysis\nPhase",
                "Stabilization",
                "glimpse\nAlert",
                "AI\nDetection",
            ]
            flow = [
                self.impact_signature.coherence_score,
                0.3,
                0.5,
                0.8 if self.unified_alert_active else 0.6,
                0.9 if self.unified_alert_active else 0.2,
            ]
            x_pos = range(len(stages))
            ax.plot(
                x_pos, flow, "o-", linewidth=3, markersize=8, alpha=0.8, color="purple"
            )
            for i, (s, v) in enumerate(zip(stages, flow)):
                ax.annotate(
                    f"{v:.2f}",
                    (i, v),
                    textcoords="offset points",
                    xytext=(0, 10),
                    ha="center",
                    bbox=dict(
                        boxstyle="round,pad=0.3", facecolor="lightblue", alpha=0.7
                    ),
                )
                ax.text(i, -0.1, s, ha="center", va="top", fontsize=10, weight="bold")
            if self.unified_alert_active:
                ax.scatter([3], [flow[3]], s=200, color="red", marker="*", zorder=5)
                ax.annotate(
                    "ALERT",
                    (3, flow[3]),
                    textcoords="offset points",
                    xytext=(20, 20),
                    ha="center",
                    fontsize=12,
                    weight="bold",
                    color="red",
                )
            ax.set_ylabel("Coherence Level")
            ax.set_title("glimpse Dev Diagnostic - Coherence Flow")
            ax.set_xlim(-0.5, len(stages) - 0.5)
            ax.set_ylim(-0.2, 1.0)
            ax.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(
            output_path / "sandstorm_coherence_flow.png", dpi=300, bbox_inches="tight"
        )
        plt.close()

    def export_sandstorm_report(
        self, output_path: str = "sandstorm_dev_outputs"
    ) -> Dict[str, Any]:
        """Export glimpse diagnostic report"""
        logger.info("Exporting glimpse diagnostic report")
        out = Path(output_path)
        out.mkdir(exist_ok=True)

        report = {
            "protocol_info": {
                "name": "SANDSTORM_DEV_DIAGNOSTIC_PROTOCOL",
                "version": "2.0.0",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "unified_alert_active": self.unified_alert_active,
                "intent": "Transform high-density process noise into clear diagnostic visibility",
            },
            "impact_signature": {  # raw_signature → impact_signature
                "source": self.impact_signature.source_name
                if self.impact_signature
                else None,
                "impact_analysis": self.impact_signature.impact_analysis
                if self.impact_signature
                else {},  # static → impact_analysis
                "atmospheric_metrics": self.impact_signature.atmospheric_metrics
                if self.impact_signature
                else {},  # runtime → atmospheric_metrics
                "throughput_dynamics": self.impact_signature.throughput_dynamics
                if self.impact_signature
                else {},
                "observability_streams": self.impact_signature.observability_streams
                if self.impact_signature
                else {},  # logs → observability_streams
                "validation_intelligence": self.impact_signature.validation_intelligence
                if self.impact_signature
                else {},  # tests → validation_intelligence
                "unified_quality": self.impact_signature.unified_quality
                if self.impact_signature
                else 0.0,
                "coherence_score": self.impact_signature.coherence_score
                if self.impact_signature
                else 0.0,
            },
            "atmospheric_signature": {  # pipeline_signature → atmospheric_signature
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
            "sandstorm_analysis": self.analysis
            if self.analysis
            else {},  # unified_analysis → sandstorm_analysis
            "diagnostic_summary": {  # summary → diagnostic_summary
                "dimensions_analyzed": 6,
                "sandstorm_alert_status": "ACTIVE"
                if self.unified_alert_active
                else "INACTIVE",  # unified_alert_status → sandstorm_alert_status
                "quality_state": self.analysis.get("quality_state_achieved", False)
                if self.analysis
                else False,
                "quality_improvement_pct": f"{((self.atmospheric_signature.unified_quality - self.impact_signature.unified_quality) / max(self.impact_signature.unified_quality, 0.1) * 100):.1f}%"
                if self.impact_signature and self.atmospheric_signature
                else "0%",
                "chaos_to_clarity_transformation": self.unified_alert_active,
            },
        }

        # Save JSON and YAML with UTF-8 encoding
        json_file = out / "glimpse_dev_report.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, default=str)
        yaml_file = out / "glimpse_dev_report.yaml"
        with open(yaml_file, "w", encoding="utf-8") as f:
            yaml.dump(report, f, default_flow_style=False)

        logger.info(f"glimpse report exported to {json_file}")
        return report


def main():
    """Main execution function for glimpse Dev Diagnostic Protocol"""
    print("🏁 glimpse DEV DIAGNOSTIC PROTOCOL - CHAOS TO CLARITY")
    print("=" * 70)
    print("Version: 2.0.0")
    print("Author: Core Systems Mentor")
    print(
        "Intent: Transform high-density process noise into clear diagnostic visibility"
    )
    print("=" * 70)

    protocol = SandstormDevDiagnostic()

    # Simulated impact layer data (raw chaotic signals)
    impact_data = {
        "duration": 60,
        "issues": 0.85,
        "coverage_gap": 0.6,
        "avg_cyclomatic_complexity": 0.8,
        "duplication": 0.7,
        "error_rate": 0.9,
        "cpu_spike_prob": 0.8,
        "memory_leak_risk": 0.7,
        "p99_latency_score": 0.8,
        "rps_normalized": 0.5,
        "backpressure": 0.7,
        "throughput_stability": 0.4,
        "error_density": 0.9,
        "warning_noise": 0.8,
        "obs_gap": 0.7,
        "glimpse_coverage": 0.5,
        "integration_stability": 0.4,
        "flaky_rate": 0.8,
    }

    # Simulated atmospheric extension data (processed architectural clarity)
    atmospheric_data = {
        "duration": 120,
        "issues": 0.25,
        "coverage": 0.92,
        "complexity_reduction": 0.45,
        "duplication": 0.18,
        "error_rate": 0.15,
        "cpu_spike_prob": 0.2,
        "memory_leak_risk": 0.1,
        "p99_latency_score": 0.3,
        "rps_normalized": 0.9,
        "backpressure": 0.15,
        "throughput_stability": 0.8,
        "error_density": 0.2,
        "warning_noise": 0.25,
        "obs_gap": 0.1,
        "glimpse_coverage": 0.93,
        "integration_stability": 0.86,
        "flaky_rate": 0.08,
    }

    # Analyze impact layer (raw chaos)
    impact_sig = protocol.analyze_impact_layer("repository_impact", impact_data)

    # Analyze atmospheric extension (architectural order)
    atmospheric_sig = protocol.analyze_atmospheric_extension(
        "ci_atmospheric", atmospheric_data
    )

    logger.info(f"Impact unified quality: {impact_sig.unified_quality:.3f}")
    logger.info(f"Atmospheric unified quality: {atmospheric_sig.unified_quality:.3f}")

    # Activate glimpse unified alert
    activated = protocol.activate_sandstorm_alert()
    if activated:
        logger.info("glimpse alert active. AI anomaly signature:")
        logger.info(protocol.analysis.get("ai_anomaly_signature"))
        print("\n🎯 glimpse ALERT ACTIVE - Diagnostic Clarity Achieved")
    else:
        logger.info(
            "glimpse alert not triggered. Improve atmospheric extension or reduce impact issues."
        )
        print("\n⚠️  glimpse ALERT INACTIVE - Further Processing Required")

    # Generate visualizations and reports
    protocol.generate_sandstorm_visualization()
    report = protocol.export_sandstorm_report()

    print("\n📁 glimpse outputs saved to sandstorm_dev_outputs/")
    print("\n🎭 Transformation Summary:")
    print(f"   Impact Layer Quality: {impact_sig.unified_quality:.3f}")
    print(f"   Atmospheric Quality: {atmospheric_sig.unified_quality:.3f}")
    print(
        f"   Quality Improvement: {((atmospheric_sig.unified_quality - impact_sig.unified_quality) / max(impact_sig.unified_quality, 0.1) * 100):.1f}%"
    )
    print(f"   Alert Status: {'ACTIVE' if activated else 'INACTIVE'}")

    print("\n🌊 Chaos transformed into comprehension.")
    print("   Impact layer captured raw system truth.")
    print("   Atmospheric extension defined architectural order.")
    print("   glimpse alert created clarity from collision.")
    print("   Maintenance becomes music.")


if __name__ == "__main__":
    main()
