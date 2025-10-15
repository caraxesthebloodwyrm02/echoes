# MIT License
#
# Copyright (c) 2024 Echoes Project
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
Integration Module

Integrates the ethics framework with the existing bias detection system.
"""

from .core_principles import validate_all_principles
from .evolution_mechanisms import (
    TRANSPARENCY_LEDGER,
    get_current_phase,
)
from .societal_inspirations import apply_all_models
from .transparency_layer import ExplanationEngine, PublicInterface, TransparencyReport


class EthicsIntegratedBiasDetector:
    """Bias detector enhanced with ethical framework."""

    def __init__(self):
        self.transparency_report = TransparencyReport()
        self.explanation_engine = ExplanationEngine()
        self.public_interface = PublicInterface()
        self.ethics_enabled = True

    def detect_bias_with_ethics(self, data: dict, context: str = "general") -> dict:
        """Perform bias detection with ethical oversight."""
        # Standard bias detection (placeholder)
        detection_results = self._perform_bias_detection(data)

        if not self.ethics_enabled:
            return detection_results

        # Apply ethical principles
        principle_compliance = validate_all_principles(detection_results)

        # Apply societal models
        societal_applications = apply_all_models("bias_detection")

        # Log for transparency
        TRANSPARENCY_LEDGER.log_decision(
            "bias_detection",
            f"Bias detection performed in {context}",
            f"Detected {len(detection_results.get('biases', []))} biases",
            ["bias_detector", "ethical_framework"],
        )

        # Enhance results with ethical insights
        detection_results["ethical_compliance"] = principle_compliance
        detection_results["societal_inspirations"] = societal_applications
        detection_results["evolution_phase"] = (
            get_current_phase().name if get_current_phase() else "Unknown"
        )
        detection_results["transparency_report"] = (
            self.transparency_report.generate_bias_detection_report(detection_results)
        )

        return detection_results

    def _perform_bias_detection(self, data: dict) -> dict:
        """Placeholder for actual bias detection logic."""
        # This would integrate with the existing bias_detection modules
        return {
            "biases": [],
            "confidence": 0.95,
            "affected_groups": [],
            "mitigation_strategies": [
                "Review data sources",
                "Implement fairness constraints",
            ],
        }

    def generate_ethical_report(self) -> str:
        """Generate a comprehensive ethical report."""
        return self.transparency_report.generate_full_report()

    def explain_ethical_decision(self, decision_type: str, **kwargs) -> str:
        """Provide explanations for ethical decisions."""
        return self.public_interface.get_explanation_for_query(decision_type, **kwargs)


# Global instance for easy access
ethics_detector = EthicsIntegratedBiasDetector()


def enable_ethics_integration():
    """Enable ethics integration across the system."""
    global ethics_detector
    ethics_detector.ethics_enabled = True


def disable_ethics_integration():
    """Disable ethics integration (for testing or fallback)."""
    global ethics_detector
    ethics_detector.ethics_enabled = False


# Convenience functions
def detect_bias_ethically(data: dict, context: str = "general") -> dict:
    """Convenience function for ethical bias detection."""
    return ethics_detector.detect_bias_with_ethics(data, context)


def get_ethical_explanation(query_type: str, **kwargs) -> str:
    """Get ethical explanations."""
    return ethics_detector.explain_ethical_decision(query_type, **kwargs)


def generate_transparency_report() -> str:
    """Generate full transparency report."""
    return ethics_detector.generate_ethical_report()
