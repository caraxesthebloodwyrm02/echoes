"""
Ethics Framework for Echoes AI System
Implements ethical AI principles, impact assessment, and Kardashev-scale considerations.
"""

import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import threading

# Configure ethics logger
ethics_logger = logging.getLogger("echoes.ethics")
ethics_logger.setLevel(logging.INFO)


class EthicalPrinciple(Enum):
    """Core ethical principles for AI systems."""

    TRANSPARENCY = "transparency"
    FAIRNESS = "fairness"
    ACCOUNTABILITY = "accountability"
    PRIVACY = "privacy"
    BENEFICENCE = "beneficence"
    NON_MALEFICENCE = "non_maleficence"
    AUTONOMY = "autonomy"
    JUSTICE = "justice"
    SUSTAINABILITY = "sustainability"


class ImpactCategory(Enum):
    """Categories for impact assessment."""

    ENVIRONMENTAL = "environmental"
    SOCIAL = "social"
    ECONOMIC = "economic"
    PRIVACY = "privacy"
    BIAS = "bias"
    AUTONOMY = "autonomy"
    SECURITY = "security"
    GLOBAL_COORDINATION = "global_coordination"


@dataclass
class EthicalDecision:
    """Represents an ethical decision point."""

    timestamp: str
    user_id: str
    action: str
    context: Dict[str, Any]
    ethical_analysis: Dict[str, Any]
    decision_made: str
    rationale: str
    alternatives_considered: List[str]
    monitoring_required: bool

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ImpactAssessment:
    """Assessment of potential impacts."""

    category: ImpactCategory
    severity: float  # 0.0 to 1.0
    probability: float  # 0.0 to 1.0
    description: str
    mitigation_strategies: List[str]
    stakeholders_affected: List[str]

    def risk_score(self) -> float:
        """Calculate risk score as severity × probability."""
        return self.severity * self.probability

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class EthicsFramework:
    """Core ethics framework implementation."""

    def __init__(self):
        self.principles = self._load_principles()
        self.impact_assessors: Dict[ImpactCategory, Callable] = {}
        self.decision_log: List[EthicalDecision] = []
        self._lock = threading.RLock()

        # Register default impact assessors
        self._register_default_assessors()

    def _load_principles(self) -> Dict[EthicalPrinciple, Dict[str, Any]]:
        """Load ethical principles definitions."""
        return {
            EthicalPrinciple.TRANSPARENCY: {
                "description": "AI systems should be transparent in their operations and decision-making",
                "requirements": [
                    "explainable_decisions",
                    "open_source_when_possible",
                    "clear_documentation",
                ],
                "weight": 1.0,
            },
            EthicalPrinciple.FAIRNESS: {
                "description": "AI should not discriminate and should treat all users equitably",
                "requirements": [
                    "bias_auditing",
                    "diverse_training_data",
                    "fairness_metrics",
                ],
                "weight": 1.0,
            },
            EthicalPrinciple.ACCOUNTABILITY: {
                "description": "Clear responsibility chains for AI actions and decisions",
                "requirements": [
                    "audit_trails",
                    "human_oversight",
                    "liability_frameworks",
                ],
                "weight": 0.9,
            },
            EthicalPrinciple.PRIVACY: {
                "description": "Protection of user data and privacy rights",
                "requirements": [
                    "data_minimization",
                    "consent_management",
                    "anonymization",
                ],
                "weight": 1.0,
            },
            EthicalPrinciple.BENEFICENCE: {
                "description": "AI should maximize positive impact and human well-being",
                "requirements": [
                    "benefit_assessment",
                    "impact_measurement",
                    "positive_outcomes",
                ],
                "weight": 0.95,
            },
            EthicalPrinciple.NON_MALEFICENCE: {
                "description": "AI should avoid causing harm",
                "requirements": [
                    "risk_assessment",
                    "harm_prevention",
                    "safety_measures",
                ],
                "weight": 1.0,
            },
            EthicalPrinciple.AUTONOMY: {
                "description": "Respect for human agency and decision-making",
                "requirements": [
                    "human_override",
                    "informed_consent",
                    "agency_preservation",
                ],
                "weight": 0.9,
            },
            EthicalPrinciple.JUSTICE: {
                "description": "Fair distribution of benefits and burdens",
                "requirements": [
                    "equitable_access",
                    "resource_distribution",
                    "justice_metrics",
                ],
                "weight": 0.85,
            },
            EthicalPrinciple.SUSTAINABILITY: {
                "description": "Long-term environmental and social sustainability",
                "requirements": [
                    "carbon_footprint",
                    "resource_efficiency",
                    "future_generations",
                ],
                "weight": 0.8,
            },
        }

    def _register_default_assessors(self):
        """Register default impact assessment functions."""
        self.impact_assessors = {
            ImpactCategory.ENVIRONMENTAL: self._assess_environmental,
            ImpactCategory.SOCIAL: self._assess_social,
            ImpactCategory.ECONOMIC: self._assess_economic,
            ImpactCategory.PRIVACY: self._assess_privacy,
            ImpactCategory.BIAS: self._assess_bias,
            ImpactCategory.AUTONOMY: self._assess_autonomy,
            ImpactCategory.SECURITY: self._assess_security,
            ImpactCategory.GLOBAL_COORDINATION: self._assess_global_coordination,
        }

    def assess_impact(self, action: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive impact assessment."""
        assessments = {}

        for category, assessor in self.impact_assessors.items():
            try:
                assessment = assessor(action, context)
                assessments[category.value] = assessment.to_dict()
            except Exception as e:
                ethics_logger.error(
                    f"Impact assessment failed for {category.value}: {e}"
                )
                assessments[category.value] = {
                    "category": category.value,
                    "severity": 0.5,
                    "probability": 0.5,
                    "description": f"Assessment failed: {e}",
                    "mitigation_strategies": ["manual_review_required"],
                    "stakeholders_affected": ["system_admin"],
                }

        # Calculate overall risk score
        total_risk = sum(
            ImpactAssessment(**data).risk_score() for data in assessments.values()
        ) / len(assessments)

        return {
            "action": action,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "assessments": assessments,
            "overall_risk_score": total_risk,
            "recommendations": self._generate_recommendations(assessments, total_risk),
        }

    def _assess_environmental(
        self, action: str, context: Dict[str, Any]
    ) -> ImpactAssessment:
        """Assess environmental impact."""
        # Analyze action for environmental implications
        high_impact_actions = [
            "large_scale_computation",
            "mass_data_processing",
            "global_model_training",
            "resource_intensive_operation",
        ]

        severity = (
            0.8 if any(term in action.lower() for term in high_impact_actions) else 0.3
        )
        probability = 0.9  # Most AI operations have environmental impact

        return ImpactAssessment(
            category=ImpactCategory.ENVIRONMENTAL,
            severity=severity,
            probability=probability,
            description="Energy consumption and carbon footprint of AI operations",
            mitigation_strategies=[
                "Use energy-efficient hardware",
                "Optimize model architectures",
                "Implement carbon-aware scheduling",
                "Offset carbon emissions",
            ],
            stakeholders_affected=[
                "environment",
                "future_generations",
                "local_communities",
            ],
        )

    def _assess_social(self, action: str, context: Dict[str, Any]) -> ImpactAssessment:
        """Assess social impact."""
        social_indicators = [
            "bias_detection",
            "fairness_analysis",
            "community_impact",
            "social_recommendation",
            "group_dynamics",
        ]

        severity = (
            0.6 if any(term in action.lower() for term in social_indicators) else 0.2
        )
        probability = 0.7

        return ImpactAssessment(
            category=ImpactCategory.SOCIAL,
            severity=severity,
            probability=probability,
            description="Impact on social structures, relationships, and community well-being",
            mitigation_strategies=[
                "Conduct social impact studies",
                "Engage community stakeholders",
                "Monitor social metrics",
                "Implement feedback loops",
            ],
            stakeholders_affected=["users", "communities", "social_groups"],
        )

    def _assess_economic(
        self, action: str, context: Dict[str, Any]
    ) -> ImpactAssessment:
        """Assess economic impact."""
        economic_indicators = [
            "cost_optimization",
            "resource_allocation",
            "market_analysis",
            "financial_prediction",
            "economic_impact",
        ]

        severity = (
            0.7 if any(term in action.lower() for term in economic_indicators) else 0.4
        )
        probability = 0.8

        return ImpactAssessment(
            category=ImpactCategory.ECONOMIC,
            severity=severity,
            probability=probability,
            description="Economic implications for stakeholders and markets",
            mitigation_strategies=[
                "Economic impact modeling",
                "Stakeholder compensation",
                "Gradual implementation",
                "Economic monitoring",
            ],
            stakeholders_affected=["workers", "businesses", "consumers", "markets"],
        )

    def _assess_privacy(self, action: str, context: Dict[str, Any]) -> ImpactAssessment:
        """Assess privacy impact."""
        privacy_sensitive_actions = [
            "data_processing",
            "user_analysis",
            "personalization",
            "tracking",
            "profiling",
            "surveillance",
        ]

        severity = (
            0.9
            if any(term in action.lower() for term in privacy_sensitive_actions)
            else 0.3
        )
        probability = 0.85

        return ImpactAssessment(
            category=ImpactCategory.PRIVACY,
            severity=severity,
            probability=probability,
            description="Privacy implications and data protection concerns",
            mitigation_strategies=[
                "Data anonymization",
                "Privacy-preserving techniques",
                "User consent management",
                "Data minimization",
            ],
            stakeholders_affected=["users", "data_subjects", "privacy_regulators"],
        )

    def _assess_bias(self, action: str, context: Dict[str, Any]) -> ImpactAssessment:
        """Assess bias impact."""
        bias_indicators = [
            "classification",
            "prediction",
            "recommendation",
            "decision_making",
            "ranking",
            "scoring",
        ]

        severity = (
            0.8 if any(term in action.lower() for term in bias_indicators) else 0.2
        )
        probability = 0.9  # Most ML operations have bias potential

        return ImpactAssessment(
            category=ImpactCategory.BIAS,
            severity=severity,
            probability=probability,
            description="Potential for algorithmic bias and discrimination",
            mitigation_strategies=[
                "Bias audits and testing",
                "Diverse training data",
                "Bias detection algorithms",
                "Human oversight",
            ],
            stakeholders_affected=["marginalized_groups", "users", "society"],
        )

    def _assess_autonomy(
        self, action: str, context: Dict[str, Any]
    ) -> ImpactAssessment:
        """Assess autonomy impact."""
        autonomy_impacting_actions = [
            "automation",
            "decision_override",
            "autonomous_operation",
            "workflow_optimization",
            "process_automation",
        ]

        severity = (
            0.7
            if any(term in action.lower() for term in autonomy_impacting_actions)
            else 0.3
        )
        probability = 0.8

        return ImpactAssessment(
            category=ImpactCategory.AUTONOMY,
            severity=severity,
            probability=probability,
            description="Impact on human agency and decision-making autonomy",
            mitigation_strategies=[
                "Human-in-the-loop systems",
                "Right to human override",
                "Transparency in automation",
                "Skill development programs",
            ],
            stakeholders_affected=["workers", "users", "decision_makers"],
        )

    def _assess_security(
        self, action: str, context: Dict[str, Any]
    ) -> ImpactAssessment:
        """Assess security impact."""
        security_critical_actions = [
            "authentication",
            "authorization",
            "encryption",
            "access_control",
            "security_audit",
            "threat_detection",
        ]

        severity = (
            0.6
            if any(term in action.lower() for term in security_critical_actions)
            else 0.4
        )
        probability = 0.7

        return ImpactAssessment(
            category=ImpactCategory.SECURITY,
            severity=severity,
            probability=probability,
            description="Security implications and potential vulnerabilities",
            mitigation_strategies=[
                "Security hardening",
                "Regular security audits",
                "Vulnerability assessments",
                "Incident response planning",
            ],
            stakeholders_affected=["users", "organizations", "security_community"],
        )

    def _assess_global_coordination(
        self, action: str, context: Dict[str, Any]
    ) -> ImpactAssessment:
        """Assess global coordination impact."""
        global_actions = [
            "international_cooperation",
            "global_impact",
            "planetary_scale",
            "kardashev",
            "space_exploration",
            "scientific_discovery",
        ]

        severity = (
            0.9 if any(term in action.lower() for term in global_actions) else 0.1
        )
        probability = 0.6

        return ImpactAssessment(
            category=ImpactCategory.GLOBAL_COORDINATION,
            severity=severity,
            probability=probability,
            description="Impact on global coordination and Kardashev-scale advancement",
            mitigation_strategies=[
                "International collaboration",
                "Global governance frameworks",
                "Cross-cultural communication",
                "Long-term planning",
            ],
            stakeholders_affected=[
                "global_community",
                "future_generations",
                "planetary_system",
            ],
        )

    def _generate_recommendations(
        self, assessments: Dict[str, Any], overall_risk: float
    ) -> List[str]:
        """Generate ethical recommendations based on assessments."""
        recommendations = []

        # High-risk recommendations
        if overall_risk > 0.7:
            recommendations.extend(
                [
                    "Implement human oversight for this operation",
                    "Conduct detailed ethical review",
                    "Prepare mitigation strategies",
                    "Consider delaying implementation",
                ]
            )

        # Category-specific recommendations
        for category_data in assessments.values():
            assessment = ImpactAssessment(**category_data)
            if assessment.risk_score() > 0.6:
                recommendations.extend(assessment.mitigation_strategies[:2])

        # Kardashev-scale considerations
        if any(
            "kardashev" in str(data).lower() or "global" in str(data).lower()
            for data in assessments.values()
        ):
            recommendations.extend(
                [
                    "Consult international stakeholders",
                    "Evaluate long-term planetary impact",
                    "Consider multi-generational implications",
                ]
            )

        return list(set(recommendations))  # Remove duplicates

    def log_ethical_decision(self, decision: EthicalDecision):
        """Log an ethical decision for audit purposes."""
        with self._lock:
            self.decision_log.append(decision)
            ethics_logger.info(f"Ethical decision logged: {decision.action}")

    def get_decision_history(
        self, user_id: Optional[str] = None, action_filter: Optional[str] = None
    ) -> List[EthicalDecision]:
        """Retrieve ethical decision history."""
        decisions = self.decision_log

        if user_id:
            decisions = [d for d in decisions if d.user_id == user_id]

        if action_filter:
            decisions = [
                d for d in decisions if action_filter.lower() in d.action.lower()
            ]

        return decisions

    def kardashev_ethics_check(
        self, action: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Special ethics check for Kardashev-scale operations."""
        base_assessment = self.assess_impact(action, context)

        # Enhanced Kardashev considerations
        kardashev_factors = {
            "planetary_impact": 0.95,
            "generational_responsibility": 0.90,
            "existential_risk": 0.85,
            "global_coordination": 0.80,
            "technological_leap": 0.75,
        }

        # Adjust overall risk with Kardashev factors
        kardashev_multiplier = sum(kardashev_factors.values()) / len(kardashev_factors)
        base_assessment["kardashev_adjusted_risk"] = (
            base_assessment["overall_risk_score"] * kardashev_multiplier
        )

        # Add Kardashev-specific recommendations
        base_assessment["kardashev_recommendations"] = [
            "Form international expert review board",
            "Conduct planetary impact assessment",
            "Establish multi-generational oversight committee",
            "Create Kardashev advancement protocols",
            "Implement global coordination frameworks",
        ]

        return base_assessment


class EthicalImpactAssessor:
    """High-level interface for ethical impact assessment."""

    def __init__(self):
        self.framework = EthicsFramework()

    def assess_operation(
        self, operation_name: str, user_id: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Assess the ethical impact of an operation."""
        return self.framework.assess_impact(operation_name, context)

    def kardashev_assessment(
        self, operation_name: str, user_id: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Special assessment for Kardashev-scale operations."""
        return self.framework.kardashev_ethics_check(operation_name, context)

    def requires_human_review(self, assessment: Dict[str, Any]) -> bool:
        """Determine if operation requires human ethical review."""
        risk_score = assessment.get("overall_risk_score", 0)
        kardashev_risk = assessment.get("kardashev_adjusted_risk", risk_score)

        # High-risk thresholds
        return kardashev_risk > 0.7 or risk_score > 0.8

    def generate_ethical_report(self, assessment: Dict[str, Any]) -> str:
        """Generate a human-readable ethical assessment report."""
        lines = [
            "# Ethical Impact Assessment Report",
            f"**Action:** {assessment['action']}",
            f"**Timestamp:** {assessment['timestamp']}",
            f"**Overall Risk Score:** {assessment['overall_risk_score']:.2f}/1.0",
        ]

        if "kardashev_adjusted_risk" in assessment:
            lines.append(
                f"**Kardashev-Adjusted Risk:** {assessment['kardashev_adjusted_risk']:.2f}/1.0"
            )

        lines.append("\n## Impact Assessments:")
        for category, data in assessment["assessments"].items():
            impact = ImpactAssessment(**data)
            lines.extend(
                [
                    f"### {category.title()}",
                    f"- **Risk Score:** {impact.risk_score():.2f}",
                    f"- **Severity:** {impact.severity:.2f}",
                    f"- **Probability:** {impact.probability:.2f}",
                    f"- **Description:** {impact.description}",
                    f"- **Affected Stakeholders:** {', '.join(impact.stakeholders_affected)}",
                ]
            )

        lines.extend(
            [
                "\n## Recommendations:",
                *[f"- {rec}" for rec in assessment["recommendations"]],
            ]
        )

        if "kardashev_recommendations" in assessment:
            lines.extend(
                [
                    "\n## Kardashev-Scale Considerations:",
                    *[f"- {rec}" for rec in assessment["kardashev_recommendations"]],
                ]
            )

        return "\n".join(lines)


# Global ethics assessor instance
ethics_assessor = EthicalImpactAssessor()
