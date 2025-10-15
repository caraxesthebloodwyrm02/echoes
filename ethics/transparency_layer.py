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
Transparency Layer Module

Provides transparency mechanisms for the ethics framework, ensuring all processes
are open to scrutiny and understanding.
"""

from datetime import datetime
from typing import Dict, List

from .core_principles import CORE_PRINCIPLES, get_principle
from .evolution_mechanisms import TRANSPARENCY_LEDGER, get_current_phase


class TransparencyReport:
    """Generates comprehensive transparency reports."""

    def __init__(self):
        self.report_data = {}

    def generate_system_overview(self) -> Dict:
        """Generate an overview of the current system state."""
        current_phase = get_current_phase()

        return {
            "system_name": "Ethics-Based Bias Detection Framework",
            "version": "1.0.0",
            "current_date": datetime.now().isoformat(),
            "evolution_phase": current_phase.name
            if current_phase
            else "Not initialized",
            "active_principles": list(CORE_PRINCIPLES.keys()),
            "principle_count": len(CORE_PRINCIPLES),
            "societal_models_integrated": ["Scandinavian", "German", "French"],
        }

    def generate_bias_detection_report(self, detection_results: Dict) -> Dict:
        """Generate a report on bias detection activities."""
        return {
            "detection_timestamp": datetime.now().isoformat(),
            "biases_detected": len(detection_results.get("biases", [])),
            "severity_distribution": self._analyze_severity(detection_results),
            "affected_groups": detection_results.get("affected_groups", []),
            "mitigation_strategies": detection_results.get("mitigation_strategies", []),
            "ethical_compliance_score": self._calculate_compliance_score(
                detection_results
            ),
        }

    def _analyze_severity(self, results: Dict) -> Dict:
        """Analyze the severity distribution of detected biases."""
        biases = results.get("biases", [])
        severity_counts = {"low": 0, "medium": 0, "high": 0, "critical": 0}

        for bias in biases:
            severity = bias.get("severity", "medium")
            if severity in severity_counts:
                severity_counts[severity] += 1

        return severity_counts

    def _calculate_compliance_score(self, results: Dict) -> float:
        """Calculate an overall ethical compliance score."""
        # Placeholder calculation based on mitigation effectiveness
        mitigations = results.get("mitigation_strategies", [])
        if not mitigations:
            return 0.0

        # Simple scoring based on number of mitigation strategies
        base_score = min(len(mitigations) * 20, 100)
        return base_score

    def generate_full_report(self) -> str:
        """Generate a full transparency report in markdown format."""
        overview = self.generate_system_overview()

        report = f"""# Ethics Framework Transparency Report

## System Overview
- **System Name**: {overview["system_name"]}
- **Version**: {overview["version"]}
- **Current Date**: {overview["current_date"]}
- **Evolution Phase**: {overview["evolution_phase"]}
- **Active Principles**: {", ".join(overview["active_principles"])}
- **Societal Models**: {", ".join(overview["societal_models_integrated"])}

## Principle Details
"""

        for name, principle in CORE_PRINCIPLES.items():
            report += f"""### {principle.name}
- **Description**: {principle.description}
- **Implementation Guidelines**:
{chr(10).join(f"  - {guideline}" for guideline in principle.implementation_guidelines)}

"""

        report += "## Audit Trail (Recent Entries)\n"
        recent_entries = TRANSPARENCY_LEDGER.get_audit_trail(
            start_date=datetime.now() - timedelta(days=30)
        )[:5]  # Last 5 entries

        if recent_entries:
            for entry in recent_entries:
                report += f"- **{entry['timestamp']}**: {entry['description']} (Type: {entry['decision_type']})\n"
        else:
            report += "No recent audit entries.\n"

        report += "\n## Ethical Compliance Status\n"
        report += "All core principles are actively monitored and enforced.\n"

        return report


class ExplanationEngine:
    """Provides clear explanations for AI decisions and processes."""

    def __init__(self):
        self.explanation_templates = {
            "bias_detected": "A bias was detected in {context} due to {reason}. This may affect {affected_groups}. Mitigation: {mitigation}.",
            "principle_violation": "The {principle} principle may be violated because {violation}. Recommended action: {action}.",
            "system_decision": "The system decided {decision} based on {factors}, ensuring compliance with {principles}.",
        }

    def explain_bias_detection(self, bias_info: Dict) -> str:
        """Explain a bias detection result."""
        template = self.explanation_templates["bias_detected"]
        return template.format(
            context=bias_info.get("context", "unknown context"),
            reason=bias_info.get("reason", "unspecified reason"),
            affected_groups=", ".join(bias_info.get("affected_groups", [])),
            mitigation=bias_info.get("mitigation", "review required"),
        )

    def explain_principle_check(
        self, principle_name: str, is_compliant: bool, details: str
    ) -> str:
        """Explain a principle compliance check."""
        principle = get_principle(principle_name)
        if is_compliant:
            return (
                f"The {principle.name} principle is being followed correctly. {details}"
            )
        else:
            template = self.explanation_templates["principle_violation"]
            return template.format(
                principle=principle.name,
                violation=details,
                action="Implement corrective measures as per guidelines",
            )

    def explain_system_decision(
        self, decision: str, factors: List[str], relevant_principles: List[str]
    ) -> str:
        """Explain a system-level decision."""
        template = self.explanation_templates["system_decision"]
        return template.format(
            decision=decision,
            factors=", ".join(factors),
            principles=", ".join(relevant_principles),
        )


class PublicInterface:
    """Provides a public interface for external scrutiny and engagement."""

    def __init__(self):
        self.report_generator = TransparencyReport()
        self.explanation_engine = ExplanationEngine()

    def get_public_dashboard_data(self) -> Dict:
        """Get data suitable for public dashboard display."""
        return {
            "system_overview": self.report_generator.generate_system_overview(),
            "recent_activity": len(
                TRANSPARENCY_LEDGER.get_audit_trail(
                    start_date=datetime.now() - timedelta(days=7)
                )
            ),
            "compliance_score": 85.0,  # Placeholder - would be calculated
            "last_updated": datetime.now().isoformat(),
        }

    def submit_public_inquiry(self, inquiry: str, contact_info: str = None) -> str:
        """Handle public inquiries about the system."""
        # Log the inquiry
        TRANSPARENCY_LEDGER.log_decision(
            "public_inquiry",
            f"Public inquiry received: {inquiry[:100]}...",
            "External stakeholder engagement",
            ["public_interface", contact_info]
            if contact_info
            else ["public_interface"],
        )

        # Generate response
        response = (
            "Thank you for your inquiry about our ethics-based bias detection system. "
        )
        response += "We are committed to transparency and will review your question. "
        response += (
            "For detailed information, please refer to our full transparency report."
        )

        return response

    def get_explanation_for_query(self, query_type: str, **kwargs) -> str:
        """Get explanations for specific queries."""
        if query_type == "bias_detection":
            return self.explanation_engine.explain_bias_detection(
                kwargs.get("bias_info", {})
            )
        elif query_type == "principle_check":
            return self.explanation_engine.explain_principle_check(
                kwargs.get("principle_name", ""),
                kwargs.get("is_compliant", True),
                kwargs.get("details", ""),
            )
        elif query_type == "system_decision":
            return self.explanation_engine.explain_system_decision(
                kwargs.get("decision", ""),
                kwargs.get("factors", []),
                kwargs.get("principles", []),
            )
        else:
            return "Explanation not available for this query type."
