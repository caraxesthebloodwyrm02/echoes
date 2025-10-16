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
LoopController - Controls iterative feedback loops between insights, codebase, and web
"""

from datetime import datetime
from typing import Any, Callable, Dict, List, Optional


class LoopController:
    """Manages iterative feedback loops for continuous improvement"""

    def __init__(self, max_iterations: int = 5, convergence_threshold: float = 0.95):
        self.max_iterations = max_iterations
        self.convergence_threshold = convergence_threshold
        self.loop_history: List[Dict[str, Any]] = []
        self.metrics = {
            "total_loops": 0,
            "successful_loops": 0,
            "average_iterations": 0.0,
            "convergence_rate": 0.0,
        }

    async def run_feedback_loop(
        self,
        initial_data: Dict[str, Any],
        validation_fn: Callable,
        refinement_fn: Callable,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Run iterative feedback loop

        Args:
            initial_data: Starting data
            validation_fn: Function to validate data quality
            refinement_fn: Function to refine data based on feedback
            context: Execution context

        Returns:
            Final refined data with loop metadata
        """
        loop_id = f"loop_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        loop_state = {
            "loop_id": loop_id,
            "start_time": datetime.now(),
            "iterations": [],
            "current_data": initial_data,
            "converged": False,
            "final_quality": 0.0,
        }

        for iteration in range(self.max_iterations):
            iteration_start = datetime.now()

            # Validate current data
            validation_result = await validation_fn(loop_state["current_data"], context)

            quality_score = validation_result.get("quality_score", 0.0)
            issues = validation_result.get("issues", [])

            iteration_data = {
                "iteration": iteration,
                "timestamp": iteration_start.isoformat(),
                "quality_score": quality_score,
                "issues_found": len(issues),
                "issues": issues,
            }

            # Check for convergence
            if quality_score >= self.convergence_threshold:
                iteration_data["converged"] = True
                loop_state["converged"] = True
                loop_state["iterations"].append(iteration_data)
                break

            # Refine data based on validation feedback
            if iteration < self.max_iterations - 1:
                refinement_result = await refinement_fn(
                    loop_state["current_data"], validation_result, context
                )

                loop_state["current_data"] = refinement_result.get(
                    "refined_data", loop_state["current_data"]
                )
                iteration_data["refinements_applied"] = refinement_result.get(
                    "refinements", []
                )

            loop_state["iterations"].append(iteration_data)

        # Finalize loop
        loop_state["end_time"] = datetime.now()
        loop_state["duration"] = (
            loop_state["end_time"] - loop_state["start_time"]
        ).total_seconds()
        loop_state["final_quality"] = loop_state["iterations"][-1]["quality_score"]
        loop_state["total_iterations"] = len(loop_state["iterations"])

        # Update metrics
        self._update_metrics(loop_state)

        # Store in history
        self.loop_history.append(loop_state)

        return {
            "loop_id": loop_id,
            "data": loop_state["current_data"],
            "metadata": {
                "converged": loop_state["converged"],
                "iterations": loop_state["total_iterations"],
                "final_quality": loop_state["final_quality"],
                "duration": loop_state["duration"],
            },
            "history": loop_state["iterations"],
        }

    async def run_multi_phase_loop(
        self, phases: List[Dict[str, Any]], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Run multi-phase feedback loop

        Args:
            phases: List of phase configurations
            context: Execution context

        Returns:
            Results from all phases
        """
        multi_loop_id = f"multi_loop_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        results = {
            "multi_loop_id": multi_loop_id,
            "start_time": datetime.now(),
            "phases": [],
            "overall_success": True,
        }

        current_data = context.get("initial_data", {})

        for phase_idx, phase in enumerate(phases):
            phase_name = phase.get("name", f"phase_{phase_idx}")

            phase_result = await self.run_feedback_loop(
                initial_data=current_data,
                validation_fn=phase["validation_fn"],
                refinement_fn=phase["refinement_fn"],
                context={**context, "phase": phase_name},
            )

            results["phases"].append(
                {
                    "phase_name": phase_name,
                    "phase_index": phase_idx,
                    "result": phase_result,
                }
            )

            # Use output of this phase as input to next
            current_data = phase_result["data"]

            # Check if phase failed to converge
            if not phase_result["metadata"]["converged"]:
                results["overall_success"] = False

        results["end_time"] = datetime.now()
        results["final_data"] = current_data

        return results

    def _update_metrics(self, loop_state: Dict[str, Any]):
        """Update loop metrics"""
        self.metrics["total_loops"] += 1

        if loop_state["converged"]:
            self.metrics["successful_loops"] += 1

        # Update average iterations with safe division
        if self.loop_history:
            total_iterations = sum(
                len(loop["iterations"]) for loop in self.loop_history
            )
            self.metrics["average_iterations"] = total_iterations / len(
                self.loop_history
            )
        else:
            self.metrics["average_iterations"] = 0.0

        # Update convergence rate
        self.metrics["convergence_rate"] = (
            self.metrics["successful_loops"] / self.metrics["total_loops"]
        )

    def get_loop_metrics(self) -> Dict[str, Any]:
        """Get loop performance metrics"""
        return {
            **self.metrics,
            "total_history_entries": len(self.loop_history),
            "recent_loops": self.loop_history[-5:] if self.loop_history else [],
        }

    def get_loop_by_id(self, loop_id: str) -> Optional[Dict[str, Any]]:
        """Get loop details by ID"""
        for loop in self.loop_history:
            if loop["loop_id"] == loop_id:
                return loop
        return None

    def analyze_convergence_patterns(self) -> Dict[str, Any]:
        """Analyze convergence patterns across loops"""
        if not self.loop_history:
            return {"status": "no_data"}

        analysis = {
            "total_loops": len(self.loop_history),
            "converged_loops": sum(
                1 for loop in self.loop_history if loop["converged"]
            ),
            "average_quality_improvement": 0.0,
            "common_issues": {},
            "iteration_distribution": {},
        }

        quality_improvements = []

        for loop in self.loop_history:
            if len(loop["iterations"]) > 1:
                initial_quality = loop["iterations"][0]["quality_score"]
                final_quality = loop["iterations"][-1]["quality_score"]
                improvement = final_quality - initial_quality
                quality_improvements.append(improvement)

            # Track iteration counts
            iter_count = len(loop["iterations"])
            analysis["iteration_distribution"][iter_count] = (
                analysis["iteration_distribution"].get(iter_count, 0) + 1
            )

            # Collect common issues
            for iteration in loop["iterations"]:
                for issue in iteration.get("issues", []):
                    issue_type = issue.get("type", "unknown")
                    analysis["common_issues"][issue_type] = (
                        analysis["common_issues"].get(issue_type, 0) + 1
                    )

        if quality_improvements:
            analysis["average_quality_improvement"] = sum(quality_improvements) / len(
                quality_improvements
            )

        return analysis

    # ------------------------------------------------------------------
    # Phase 2: Adaptive Loop Feedback
    # ------------------------------------------------------------------

    def assess_prompt_complexity(self, prompt: str) -> str:
        """Assess prompt complexity for adaptive iteration control (Phase 2 prototype)"""
        prompt_lower = prompt.lower()

        # Simple heuristic-based complexity assessment
        complexity_indicators = {
            "high": [
                "architecture",
                "system",
                "integration",
                "scalable",
                "enterprise",
                "complex",
            ],
            "medium": [
                "implement",
                "create",
                "build",
                "design",
                "optimize",
                "multiple",
            ],
            "low": ["explain", "help", "simple", "basic", "quick", "what"],
        }

        scores = {}
        for level, indicators in complexity_indicators.items():
            score = sum(1 for indicator in indicators if indicator in prompt_lower)
            scores[level] = score

        # Return the level with highest score, default to medium
        return max(scores, key=scores.get) if any(scores.values()) else "medium"

    def get_adaptive_max_iterations(self, complexity: str) -> int:
        """Return dynamic max iterations based on prompt complexity (Phase 2 prototype)"""
        # Adaptive iteration caps based on complexity
        caps = {
            "low": 2,  # Simple prompts need minimal refinement
            "medium": 5,  # Medium complexity allows moderate iterations
            "high": 10,  # Complex prompts get maximum iteration allowance
        }
        return caps.get(complexity, 5)  # Default to medium
