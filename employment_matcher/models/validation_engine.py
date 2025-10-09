"""
Semantic Match Validator: Ensure matches feel right, not just statistically strong
"""

from typing import Dict, List, NamedTuple

import numpy as np

from .context_filter import ContextFilter
from .relationship_matcher import MatchScore, RelationshipAwareMatcher
from .semantic_engine import ContextualEmbedding, SemanticVector


class ValidationCase(NamedTuple):
    """Test case for intuitive validation"""

    candidate_skills: List[str]
    job_skills: List[str]
    expected_score: float  # 0-1 scale
    description: str


class ValidationResult:
    """Result of a single validation test"""

    def __init__(
        self,
        test_case: ValidationCase,
        match_score: MatchScore,
        intuitive_alignment: float,
        passes_threshold: bool,
    ):
        self.test_case = test_case
        self.match_score = match_score
        self.intuitive_alignment = (
            intuitive_alignment  # How well score matches human intuition
        )
        self.passes_threshold = passes_threshold


class SemanticMatchValidator:
    """
    Ensure matches feel right, not just statistically strong.
    Core insight: Bridge statistical strength with human judgment.
    """

    def __init__(self):
        self.test_cases = self._load_validation_cases()
        self.feedback_loop = FeedbackCollector()

    def run_intuitive_validation(
        self, matcher: RelationshipAwareMatcher
    ) -> "ValidationReport":
        """Test against cases where human intuition matters"""

        results = []
        for test_case in self.test_cases:
            # Embed skills
            candidate_embedding = self._embed_skills(
                test_case.candidate_skills, "candidate"
            )
            job_embedding = self._embed_skills(test_case.job_skills, "job")

            # Run matching
            match_score = matcher.calculate_semantic_similarity(
                candidate_embedding, job_embedding
            )

            # Compare with human judgment
            intuitive_alignment = self._compare_with_human_judgment(
                match_score.score, test_case.expected_score
            )

            passes_threshold = intuitive_alignment >= 0.8

            results.append(
                ValidationResult(
                    test_case=test_case,
                    match_score=match_score,
                    intuitive_alignment=intuitive_alignment,
                    passes_threshold=passes_threshold,
                )
            )

        return self._generate_validation_report(results)

    def _embed_skills(self, skills: List[str], context: str) -> ContextualEmbedding:
        """Helper to embed a list of skills into a single contextual embedding"""
        # This is simplified - in practice, you'd use the full pipeline
        # For now, create mock embeddings
        mock_vector = np.random.rand(384)  # Mock embedding
        semantic_tags = set()

        for skill in skills:
            skill_lower = skill.lower()
            if "python" in skill_lower:
                semantic_tags.add("python")
                semantic_tags.add("programming")
            if "data" in skill_lower or "science" in skill_lower:
                semantic_tags.add("data_science")
            if "machine learning" in skill_lower:
                semantic_tags.add("machine_learning")
            if "javascript" in skill_lower:
                semantic_tags.add("javascript")
                semantic_tags.add("web_development")

        mock_semantic = SemanticVector(
            vector=mock_vector,
            confidence=0.8,
            semantic_tags=semantic_tags,
            original_text=", ".join(skills),
            context=context,
        )

        # Apply context filtering (simplified)
        context_filter = ContextFilter()
        return context_filter.apply_context(mock_semantic, "general")

    def _compare_with_human_judgment(
        self, actual_score: float, expected_score: float
    ) -> float:
        """
        Compare actual match score with human-expected score.
        Returns alignment score between 0 and 1.
        """
        difference = abs(actual_score - expected_score)

        # Perfect alignment
        if difference < 0.05:
            return 1.0
        # Good alignment
        elif difference < 0.15:
            return 0.8
        # Moderate alignment
        elif difference < 0.25:
            return 0.6
        # Poor alignment
        else:
            return 0.3

    def _generate_validation_report(
        self, results: List[ValidationResult]
    ) -> "ValidationReport":
        """Generate comprehensive validation report"""

        total_cases = len(results)
        passing_cases = sum(1 for r in results if r.passes_threshold)
        average_alignment = np.mean([r.intuitive_alignment for r in results])

        # Calculate score distribution
        score_distribution = {
            "excellent": len([r for r in results if r.intuitive_alignment >= 0.9]),
            "good": len([r for r in results if 0.8 <= r.intuitive_alignment < 0.9]),
            "moderate": len([r for r in results if 0.6 <= r.intuitive_alignment < 0.8]),
            "poor": len([r for r in results if r.intuitive_alignment < 0.6]),
        }

        # Detailed breakdown
        detailed_results = []
        for result in results:
            detailed_results.append(
                {
                    "description": result.test_case.description,
                    "expected_score": result.test_case.expected_score,
                    "actual_score": result.match_score.score,
                    "intuitive_alignment": result.intuitive_alignment,
                    "passes_threshold": result.passes_threshold,
                    "explanation": result.match_score.explanation,
                }
            )

        return ValidationReport(
            total_cases=total_cases,
            passing_cases=passing_cases,
            average_alignment=average_alignment,
            score_distribution=score_distribution,
            detailed_results=detailed_results,
        )

    def _load_validation_cases(self) -> List[ValidationCase]:
        """Real-world test cases that require semantic understanding"""
        return [
            ValidationCase(
                candidate_skills=["python", "data analysis", "statistics"],
                job_skills=["data science", "python programming", "analytics"],
                expected_score=0.85,  # Should be high - semantically very similar
                description="Data scientist with slightly different skill labels",
            ),
            ValidationCase(
                candidate_skills=["java", "spring framework", "backend"],
                job_skills=["python", "django", "web development"],
                expected_score=0.65,  # Moderate - different but related domains
                description="Backend developers with different tech stacks",
            ),
            ValidationCase(
                candidate_skills=["photoshop", "graphic design", "ui"],
                job_skills=["python", "data engineering", "etl"],
                expected_score=0.15,  # Low - completely different domains
                description="Completely unrelated skill sets",
            ),
            ValidationCase(
                candidate_skills=["python", "tensorflow", "machine learning"],
                job_skills=["python", "data science", "ai"],
                expected_score=0.90,  # Very high - direct skill matches with ML focus
                description="ML engineer applying for data science role",
            ),
            ValidationCase(
                candidate_skills=["javascript", "react", "frontend"],
                job_skills=["javascript", "node", "backend"],
                expected_score=0.75,  # Good - same language, different specializations
                description="Frontend dev for backend role",
            ),
            ValidationCase(
                candidate_skills=["sql", "excel", "reporting"],
                job_skills=["python", "pandas", "data science"],
                expected_score=0.55,  # Moderate - data skills but different tools
                description="Business analyst for data scientist role",
            ),
        ]


class ValidationReport:
    """Comprehensive validation report"""

    def __init__(
        self,
        total_cases: int,
        passing_cases: int,
        average_alignment: float,
        score_distribution: Dict[str, int],
        detailed_results: List[Dict],
    ):
        self.total_cases = total_cases
        self.passing_cases = passing_cases
        self.average_alignment = average_alignment
        self.score_distribution = score_distribution
        self.detailed_results = detailed_results

    def __str__(self):
        return (
            f"Validation Report: {self.passing_cases}/{self.total_cases} passed "
            ".3f"
            f"Distribution: {self.score_distribution}"
        )


class FeedbackCollector:
    """Collect and learn from human feedback"""

    def __init__(self):
        self.feedback_data = []

    def add_feedback(
        self,
        candidate_skills: List[str],
        job_skills: List[str],
        human_score: float,
        system_score: float,
        comments: str = "",
    ):
        """Add human feedback for learning"""
        self.feedback_data.append(
            {
                "candidate_skills": candidate_skills,
                "job_skills": job_skills,
                "human_score": human_score,
                "system_score": system_score,
                "comments": comments,
                "timestamp": np.datetime64("now"),
            }
        )

    def get_feedback_insights(self) -> Dict:
        """Analyze feedback to identify improvement areas"""
        if not self.feedback_data:
            return {"message": "No feedback data available"}

        score_differences = [
            abs(f["human_score"] - f["system_score"]) for f in self.feedback_data
        ]

        avg_difference = np.mean(score_differences)
        max_difference = np.max(score_differences)

        return {
            "total_feedback": len(self.feedback_data),
            "average_score_difference": avg_difference,
            "max_score_difference": max_difference,
            "accuracy_trend": "improving" if avg_difference < 0.2 else "needs_work",
        }
