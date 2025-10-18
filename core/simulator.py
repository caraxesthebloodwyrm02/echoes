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

import json
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List


class AlignmentFactor(Enum):
    TOOLCHAIN = "toolchain"
    COMPLEXITY = "complexity"
    TIME_ESTIMATE = "time_estimate"
    SOLO_FEASIBILITY = "solo_feasibility"
    VISION_ALIGNMENT = "vision_alignment"


@dataclass
class SimulationResult:
    phase_name: str
    alignment_score: float  # 0-1, higher better
    factors: Dict[str, float]
    recommendations: List[str]
    risks: List[str]


class PhaseSimulator:
    """
    Simulates development phases to evaluate alignment with user vision.
    User preferences: Python-only, no JS/TS/Node, single-operator workflow.
    """

    def __init__(self):
        self.vision_weights = {
            AlignmentFactor.TOOLCHAIN: 0.3,
            AlignmentFactor.COMPLEXITY: 0.2,
            AlignmentFactor.TIME_ESTIMATE: 0.1,
            AlignmentFactor.SOLO_FEASIBILITY: 0.2,
            AlignmentFactor.VISION_ALIGNMENT: 0.2,
        }

    def simulate_phase(self, phase_json: Dict[str, Any]) -> SimulationResult:
        """
        Simulate a phase plan and return alignment assessment.
        """
        phase_name = phase_json.get("phase", "Unknown Phase")

        # Evaluate factors
        factors = {}

        # Toolchain alignment (Python-only)
        components = phase_json.get("components", [])
        toolchain_score = self._evaluate_toolchain(components)
        factors[AlignmentFactor.TOOLCHAIN] = toolchain_score

        # Complexity (keep simple for solo operation)
        complexity_score = self._evaluate_complexity(phase_json)
        factors[AlignmentFactor.COMPLEXITY] = complexity_score

        # Time estimate (reasonable for single person)
        time_score = self._evaluate_time(phase_json.get("duration", ""))
        factors[AlignmentFactor.TIME_ESTIMATE] = time_score

        # Solo feasibility
        solo_score = self._evaluate_solo_feasibility(phase_json)
        factors[AlignmentFactor.SOLO_FEASIBILITY] = solo_score

        # Vision alignment (Python focus, automation)
        vision_score = self._evaluate_vision_alignment(phase_json)
        factors[AlignmentFactor.VISION_ALIGNMENT] = vision_score

        # Overall score
        alignment_score = sum(
            factors[factor] * self.vision_weights[factor] for factor in AlignmentFactor
        )

        # Generate recommendations and risks
        recommendations, risks = self._generate_feedback(phase_json, factors)

        return SimulationResult(
            phase_name=phase_name,
            alignment_score=alignment_score,
            factors={k.value: v for k, v in factors.items()},
            recommendations=recommendations,
            risks=risks,
        )

    def _evaluate_toolchain(self, components: List[Dict]) -> float:
        """Check if components use Python-only toolchain."""
        score = 1.0
        for comp in components:
            file_path = comp.get("file", "")
            if any(js in file_path.lower() for js in ["js", "ts", "node", "npm"]):
                score -= 0.5
        return max(0, score)

    def _evaluate_complexity(self, phase_json: Dict) -> float:
        """Assess complexity for solo operation."""
        components_count = len(phase_json.get("components", []))
        if components_count <= 3:
            return 1.0
        elif components_count <= 5:
            return 0.7
        else:
            return 0.4

    def _evaluate_time(self, duration: str) -> float:
        """Check if time estimate is reasonable for solo work."""
        if "1-2 weeks" in duration or "1 week" in duration:
            return 1.0
        elif "2-4 weeks" in duration:
            return 0.8
        elif "4-6 weeks" in duration:
            return 0.6
        else:
            return 0.5

    def _evaluate_solo_feasibility(self, phase_json: Dict) -> float:
        """Evaluate if phase can be done by one person."""
        milestones = phase_json.get("milestones", [])
        if len(milestones) <= 4:
            return 1.0
        elif len(milestones) <= 6:
            return 0.8
        else:
            return 0.5

    def _evaluate_vision_alignment(self, phase_json: Dict) -> float:
        """Check alignment with Python/automation vision."""
        objectives = phase_json.get("objectives", [])
        score = 0.5
        for obj in objectives:
            if "python" in obj.lower() or "automation" in obj.lower():
                score += 0.2
        return min(1.0, score)

    def _generate_feedback(
        self, phase_json: Dict, factors: Dict[AlignmentFactor, float]
    ) -> tuple[List[str], List[str]]:
        """Generate recommendations and risks based on factors."""
        recommendations = []
        risks = []

        if factors[AlignmentFactor.TOOLCHAIN] < 0.8:
            recommendations.append("Refactor to use Python-only components")
            risks.append("Toolchain mismatch may introduce maintenance overhead")

        if factors[AlignmentFactor.COMPLEXITY] < 0.7:
            recommendations.append("Break down into smaller, manageable components")
            risks.append("High complexity may overwhelm solo operation")

        if factors[AlignmentFactor.SOLO_FEASIBILITY] < 0.8:
            recommendations.append("Reduce milestones or parallelize simple tasks")
            risks.append("Timeline may slip due to single-operator constraints")

        if factors[AlignmentFactor.VISION_ALIGNMENT] < 0.8:
            recommendations.append(
                "Ensure deliverables align with Python/automation focus"
            )
            risks.append("Deviation from vision may lead to rework")

        return recommendations, risks


# Usage example
if __name__ == "__main__":
    simulator = PhaseSimulator()

    # Load phase plan
    with open("phase3_mcp_plan.json", "r") as f:
        phase_plan = json.load(f)

    result = simulator.simulate_phase(phase_plan)

    print(f"Phase: {result.phase_name}")
    print(f"Alignment Score: {result.alignment_score:.2f}")
    print("Factors:")
    for k, v in result.factors.items():
        print(f"  {k}: {v:.2f}")
    print("Recommendations:")
    for rec in result.recommendations:
        print(f"  - {rec}")
    print("Risks:")
    for risk in result.risks:
        print(f"  - {risk}")
