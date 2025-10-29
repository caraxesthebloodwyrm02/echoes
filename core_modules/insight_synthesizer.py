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
InsightSynthesizer - Summarizes validated learnings back into prompt memory
"""

import json
from datetime import datetime
from typing import Any, Dict, List


class InsightSynthesizer:
    """Synthesizes insights from feedback loops and integrates them into memory"""

    def __init__(self):
        self.insights_cache: List[Dict[str, Any]] = []
        self.synthesis_history: List[Dict[str, Any]] = []
        self.patterns_learned: Dict[str, Any] = {}

    def synthesize_from_loop(self, loop_result: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Synthesize insights from a feedback loop result

        Args:
            loop_result: Result from LoopController
            context: Execution context

        Returns:
            Synthesized insights
        """
        synthesis = {
            "synthesis_id": f"synth_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "source_loop_id": loop_result.get("loop_id"),
            "insights": [],
            "patterns": [],
            "recommendations": [],
        }

        # Extract insights from loop iterations
        for iteration in loop_result.get("history", []):
            iteration_insights = self._extract_iteration_insights(iteration, context)
            synthesis["insights"].extend(iteration_insights)

        # Identify patterns
        patterns = self._identify_patterns(loop_result, context)
        synthesis["patterns"] = patterns

        # Generate recommendations
        recommendations = self._generate_recommendations(loop_result, synthesis["insights"], patterns, context)
        synthesis["recommendations"] = recommendations

        # Cache insights
        self._cache_insights(synthesis)

        # Update learned patterns
        self._update_learned_patterns(patterns)

        # Store in history
        self.synthesis_history.append(synthesis)

        return synthesis

    def _extract_iteration_insights(self, iteration: Dict[str, Any], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract insights from a single iteration"""
        insights = []

        quality_score = iteration.get("quality_score", 0.0)
        issues = iteration.get("issues", [])

        # Insight: Quality progression
        if quality_score > 0:
            insights.append(
                {
                    "type": "quality_metric",
                    "category": "performance",
                    "content": f"Achieved quality score of {quality_score:.2f}",
                    "confidence": quality_score,
                    "iteration": iteration.get("iteration"),
                    "timestamp": iteration.get("timestamp"),
                }
            )

        # Insights from issues
        for issue in issues:
            insight = {
                "type": "identified_issue",
                "category": issue.get("type", "general"),
                "content": issue.get("description", "Unspecified issue"),
                "confidence": issue.get("severity", 0.5),
                "iteration": iteration.get("iteration"),
                "timestamp": iteration.get("timestamp"),
            }
            insights.append(insight)

        # Insight: Refinements applied
        if "refinements_applied" in iteration:
            for refinement in iteration["refinements_applied"]:
                insights.append(
                    {
                        "type": "refinement_strategy",
                        "category": "improvement",
                        "content": refinement,
                        "confidence": 0.7,
                        "iteration": iteration.get("iteration"),
                        "timestamp": iteration.get("timestamp"),
                    }
                )

        return insights

    def _identify_patterns(self, loop_result: Dict[str, Any], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify patterns in the loop execution"""
        patterns = []

        metadata = loop_result.get("metadata", {})
        history = loop_result.get("history", [])

        # Pattern: Convergence behavior
        if metadata.get("converged"):
            patterns.append(
                {
                    "pattern_type": "convergence",
                    "description": f"Converged in {metadata['iterations']} iterations",
                    "confidence": 0.9,
                    "data": {
                        "iterations": metadata["iterations"],
                        "final_quality": metadata["final_quality"],
                    },
                }
            )
        else:
            patterns.append(
                {
                    "pattern_type": "non_convergence",
                    "description": f"Did not converge after {metadata['iterations']} iterations",
                    "confidence": 0.8,
                    "data": {
                        "iterations": metadata["iterations"],
                        "final_quality": metadata["final_quality"],
                    },
                }
            )

        # Pattern: Quality trajectory
        if len(history) > 1:
            quality_scores = [iter_data.get("quality_score", 0) for iter_data in history]

            # Check if quality is improving
            if quality_scores[-1] > quality_scores[0]:
                improvement = quality_scores[-1] - quality_scores[0]
                patterns.append(
                    {
                        "pattern_type": "quality_improvement",
                        "description": f"Quality improved by {improvement:.2f}",
                        "confidence": 0.85,
                        "data": {
                            "initial": quality_scores[0],
                            "final": quality_scores[-1],
                            "trajectory": quality_scores,
                        },
                    }
                )
            elif quality_scores[-1] < quality_scores[0]:
                patterns.append(
                    {
                        "pattern_type": "quality_degradation",
                        "description": "Quality degraded over iterations",
                        "confidence": 0.7,
                        "data": {"trajectory": quality_scores},
                    }
                )

        # Pattern: Common issue types
        all_issues = []
        for iteration in history:
            all_issues.extend(iteration.get("issues", []))

        if all_issues:
            issue_types = {}
            for issue in all_issues:
                issue_type = issue.get("type", "unknown")
                issue_types[issue_type] = issue_types.get(issue_type, 0) + 1

            most_common = max(issue_types.items(), key=lambda x: x[1])
            patterns.append(
                {
                    "pattern_type": "recurring_issue",
                    "description": f"Most common issue: {most_common[0]} ({most_common[1]} occurrences)",
                    "confidence": 0.75,
                    "data": {
                        "issue_distribution": issue_types,
                        "most_common": most_common[0],
                    },
                }
            )

        return patterns

    def _generate_recommendations(
        self,
        loop_result: Dict[str, Any],
        insights: List[Dict[str, Any]],
        patterns: List[Dict[str, Any]],
        context: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Generate actionable recommendations"""
        recommendations = []

        metadata = loop_result.get("metadata", {})

        # Recommendation based on convergence
        if not metadata.get("converged"):
            recommendations.append(
                {
                    "priority": "high",
                    "category": "convergence",
                    "action": "Increase max iterations or adjust convergence threshold",
                    "reasoning": "Loop did not converge within iteration limit",
                    "expected_impact": "Improved convergence rate",
                }
            )

        # Recommendation based on quality
        if metadata.get("final_quality", 0) < 0.7:
            recommendations.append(
                {
                    "priority": "high",
                    "category": "quality",
                    "action": "Review data sources and validation criteria",
                    "reasoning": f"Final quality score ({metadata['final_quality']:.2f}) below target",
                    "expected_impact": "Higher quality outputs",
                }
            )

        # Recommendations based on patterns
        for pattern in patterns:
            if pattern["pattern_type"] == "recurring_issue":
                recommendations.append(
                    {
                        "priority": "medium",
                        "category": "issue_resolution",
                        "action": f"Address recurring issue: {pattern['data']['most_common']}",
                        "reasoning": "Issue appears frequently across iterations",
                        "expected_impact": "Reduced iteration count, faster convergence",
                    }
                )

            elif pattern["pattern_type"] == "quality_degradation":
                recommendations.append(
                    {
                        "priority": "high",
                        "category": "quality",
                        "action": "Review refinement strategy - quality is degrading",
                        "reasoning": "Refinements are reducing quality instead of improving it",
                        "expected_impact": "Positive quality trajectory",
                    }
                )

        # Recommendation based on duration
        if metadata.get("duration", 0) > 60:  # More than 1 minute
            recommendations.append(
                {
                    "priority": "medium",
                    "category": "performance",
                    "action": "Optimize validation and refinement functions",
                    "reasoning": f"Loop took {metadata['duration']:.1f} seconds",
                    "expected_impact": "Faster iteration cycles",
                }
            )

        return recommendations

    def _cache_insights(self, synthesis: Dict[str, Any]):
        """Cache insights for future reference"""
        for insight in synthesis["insights"]:
            self.insights_cache.append(
                {
                    "synthesis_id": synthesis["synthesis_id"],
                    "insight": insight,
                    "cached_at": datetime.now().isoformat(),
                }
            )

        # Keep cache size manageable
        if len(self.insights_cache) > 1000:
            self.insights_cache = self.insights_cache[-1000:]

    def _update_learned_patterns(self, patterns: List[Dict[str, Any]]):
        """Update learned patterns database"""
        for pattern in patterns:
            pattern_type = pattern["pattern_type"]

            if pattern_type not in self.patterns_learned:
                self.patterns_learned[pattern_type] = {
                    "occurrences": 0,
                    "examples": [],
                    "confidence_scores": [],
                }

            self.patterns_learned[pattern_type]["occurrences"] += 1
            self.patterns_learned[pattern_type]["confidence_scores"].append(pattern["confidence"])

            # Keep limited examples
            if len(self.patterns_learned[pattern_type]["examples"]) < 10:
                self.patterns_learned[pattern_type]["examples"].append(pattern["data"])

    def get_relevant_insights(self, query: str, category: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve relevant cached insights"""
        relevant = []
        query_lower = query.lower()

        for cached in self.insights_cache:
            insight = cached["insight"]

            # Filter by category if specified
            if category and insight.get("category") != category:
                continue

            # Simple relevance check
            content = insight.get("content", "").lower()
            if any(word in content for word in query_lower.split()):
                relevant.append(cached)

        # Sort by confidence and recency
        relevant.sort(key=lambda x: (x["insight"]["confidence"], x["cached_at"]), reverse=True)

        return relevant[:limit]

    def get_learned_patterns_summary(self) -> Dict[str, Any]:
        """Get summary of learned patterns"""
        summary = {"total_pattern_types": len(self.patterns_learned), "patterns": {}}

        for pattern_type, data in self.patterns_learned.items():
            avg_confidence = (
                sum(data["confidence_scores"]) / len(data["confidence_scores"]) if data["confidence_scores"] else 0.0
            )

            summary["patterns"][pattern_type] = {
                "occurrences": data["occurrences"],
                "average_confidence": avg_confidence,
                "example_count": len(data["examples"]),
            }

        return summary

    def synthesize_cross_loop_insights(self, loop_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Synthesize insights across multiple loops"""
        cross_synthesis = {
            "synthesis_id": f"cross_synth_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "loops_analyzed": len(loop_results),
            "meta_patterns": [],
            "aggregate_insights": [],
        }

        # Aggregate quality metrics
        quality_scores = [lr.get("metadata", {}).get("final_quality", 0) for lr in loop_results]

        if quality_scores:
            cross_synthesis["aggregate_insights"].append(
                {
                    "type": "quality_statistics",
                    "average_quality": sum(quality_scores) / len(quality_scores),
                    "min_quality": min(quality_scores),
                    "max_quality": max(quality_scores),
                    "quality_variance": self._calculate_variance(quality_scores),
                }
            )

        # Meta-pattern: Overall convergence rate
        converged_count = sum(1 for lr in loop_results if lr.get("metadata", {}).get("converged", False))
        convergence_rate = converged_count / len(loop_results) if loop_results else 0

        cross_synthesis["meta_patterns"].append(
            {
                "pattern_type": "convergence_rate",
                "description": f"Overall convergence rate: {convergence_rate:.1%}",
                "data": {
                    "total_loops": len(loop_results),
                    "converged": converged_count,
                    "rate": convergence_rate,
                },
            }
        )

        return cross_synthesis

    def _calculate_variance(self, values: List[float]) -> float:
        """Calculate variance of values"""
        if not values:
            return 0.0

        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance

    def export_insights(self, filepath: str):
        """Export insights to file"""
        export_data = {
            "timestamp": datetime.now().isoformat(),
            "insights_cache": self.insights_cache,
            "learned_patterns": self.patterns_learned,
            "synthesis_history": self.synthesis_history,
        }

        with open(filepath, "w") as f:
            json.dump(export_data, f, indent=2)

    def import_insights(self, filepath: str):
        """Import insights from file"""
        with open(filepath, "r") as f:
            import_data = json.load(f)

        self.insights_cache.extend(import_data.get("insights_cache", []))

        # Merge learned patterns
        for pattern_type, data in import_data.get("learned_patterns", {}).items():
            if pattern_type not in self.patterns_learned:
                self.patterns_learned[pattern_type] = data
            else:
                # Merge existing with imported
                self.patterns_learned[pattern_type]["occurrences"] += data["occurrences"]
                self.patterns_learned[pattern_type]["confidence_scores"].extend(data["confidence_scores"])
                self.patterns_learned[pattern_type]["examples"].extend(data["examples"])
