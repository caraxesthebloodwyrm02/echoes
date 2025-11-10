"""
Value System for Echoes Assistant V2

Manages three core values: respect, accuracy, helpfulness
Provides scoring mechanisms for response evaluation and behavior learning.
"""

from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
import json
from pathlib import Path


@dataclass
class ValueScore:
    """Represents a value with its current score and weight."""

    name: str
    score: float  # 0.0 to 1.0
    weight: float  # How much this value influences decisions

    def __post_init__(self):
        self.score = max(0.0, min(1.0, self.score))
        self.weight = max(0.0, min(1.0, self.weight))


class ValueSystem:
    """
    Manages three core values: respect, accuracy, helpfulness.
    Plus highlight factors: community, faith, service, growth, love,
    integrity, innovation, excellence, teamwork, accountability.

    Each value influences the assistant's behavior and response generation.
    Scores are updated based on user feedback and interaction patterns.
    Overall score: 80% core values + 20% highlight factors.
    """

    def __init__(self, storage_path: str = "data/values"):
        """
        Initialize the value system.

        Args:
            storage_path: Directory to store value data
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Core values with initial scores and weights
        self.values = {
            "respect": ValueScore("respect", 0.8, 0.4),  # Treat users with dignity
            "accuracy": ValueScore("accuracy", 0.9, 0.4),  # Provide correct information
            "helpfulness": ValueScore("helpfulness", 0.9, 0.2),  # Be genuinely useful
        }

        # Highlight factors (20% of overall score) - equal weights within category
        self.highlights = {
            # Core Values (10% total, 2% each)
            "community": ValueScore(
                "community", 0.8, 0.02
            ),  # Building connections, inclusivity
            "faith": ValueScore("faith", 0.8, 0.02),  # Trust, belief in potential
            "service": ValueScore("service", 0.8, 0.02),  # Selfless help, dedication
            "growth": ValueScore(
                "growth", 0.8, 0.02
            ),  # Continuous improvement, learning
            "love": ValueScore("love", 0.8, 0.02),  # Compassion, empathy, care
            # Core Principles (10% total, 2% each)
            "integrity": ValueScore(
                "integrity", 0.9, 0.02
            ),  # Honesty, ethical behavior
            "innovation": ValueScore(
                "innovation", 0.8, 0.02
            ),  # Creativity, forward-thinking
            "excellence": ValueScore(
                "excellence", 0.9, 0.02
            ),  # Quality, high standards
            "teamwork": ValueScore("teamwork", 0.8, 0.02),  # Collaboration, unity
            "accountability": ValueScore(
                "accountability", 0.9, 0.02
            ),  # Responsibility, ownership
        }

        # Load existing values if available
        self.load_values()

    def get_value_score(self, value_name: str) -> float:
        """Get the current score for a specific value."""
        if value_name in self.values:
            return self.values[value_name].score
        if value_name in self.highlights:
            return self.highlights[value_name].score
        return 0.0

    def get_value_weight(self, value_name: str) -> float:
        """Get the weight for a specific value."""
        if value_name in self.values:
            return self.values[value_name].weight
        if value_name in self.highlights:
            return self.highlights[value_name].weight
        return 0.0

    def update_value_score(
        self, value_name: str, new_score: float, feedback_weight: float = 0.1
    ) -> None:
        """
        Update a value score based on feedback.

        Args:
            value_name: Name of the value to update
            new_score: New score (0.0 to 1.0)
            feedback_weight: How much this feedback influences the score (0.0 to 1.0)
        """
        target_dict = None
        if value_name in self.values:
            target_dict = self.values
        elif value_name in self.highlights:
            target_dict = self.highlights
        else:
            return

        current_score = target_dict[value_name].score
        # Weighted average between current score and new feedback
        updated_score = (current_score * (1 - feedback_weight)) + (
            new_score * feedback_weight
        )

        target_dict[value_name].score = max(0.0, min(1.0, updated_score))
        self.save_values()

    def evaluate_response(
        self, response: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, float]:
        """
        Evaluate a response against all core values and highlight factors.

        Args:
            response: The response text to evaluate
            context: Optional context about the interaction

        Returns:
            Dictionary with scores for each value and highlight factor
        """
        scores = {}

        # Evaluate core values
        scores["respect"] = self._evaluate_respect(response, context)
        scores["accuracy"] = self._evaluate_accuracy(response, context)
        scores["helpfulness"] = self._evaluate_helpfulness(response, context)

        # Evaluate highlight factors - core values
        scores["community"] = self._evaluate_community(response, context)
        scores["faith"] = self._evaluate_faith(response, context)
        scores["service"] = self._evaluate_service(response, context)
        scores["growth"] = self._evaluate_growth(response, context)
        scores["love"] = self._evaluate_love(response, context)

        # Evaluate highlight factors - core principles
        scores["integrity"] = self._evaluate_integrity(response, context)
        scores["innovation"] = self._evaluate_innovation(response, context)
        scores["excellence"] = self._evaluate_excellence(response, context)
        scores["teamwork"] = self._evaluate_teamwork(response, context)
        scores["accountability"] = self._evaluate_accountability(response, context)

        return scores

    def get_overall_score(self, response_scores: Dict[str, float]) -> float:
        """
        Calculate overall score: 80% core values + 20% highlight factors.

        Args:
            response_scores: Scores for each value from evaluate_response

        Returns:
            Weighted overall score (0.0 to 1.0)
        """
        # Core values (80% weight)
        core_values = ["respect", "accuracy", "helpfulness"]
        core_total_weight = sum(self.get_value_weight(name) for name in core_values)
        if core_total_weight > 0:
            core_weighted_sum = sum(
                response_scores.get(name, 0.0) * self.get_value_weight(name)
                for name in core_values
            )
            core_score = core_weighted_sum / core_total_weight
        else:
            core_score = 0.0

        # Highlight factors (20% weight)
        highlight_factors = [
            "community",
            "faith",
            "service",
            "growth",
            "love",
            "integrity",
            "innovation",
            "excellence",
            "teamwork",
            "accountability",
        ]
        highlight_total_weight = sum(
            self.get_value_weight(name) for name in highlight_factors
        )
        if highlight_total_weight > 0:
            highlight_weighted_sum = sum(
                response_scores.get(name, 0.0) * self.get_value_weight(name)
                for name in highlight_factors
            )
            highlight_score = highlight_weighted_sum / highlight_total_weight
        else:
            highlight_score = 0.0

        # Combined score: 80% core + 20% highlights
        return (0.8 * core_score) + (0.2 * highlight_score)

    def provide_feedback(
        self,
        response: str,
        user_feedback: Dict[str, float],
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Update value scores based on user feedback.

        Args:
            response: The response that was evaluated
            user_feedback: User ratings for each value (0.0 to 1.0)
            context: Optional context about the interaction
        """
        response_scores = self.evaluate_response(response, context)

        # Update each value based on user feedback vs. automated evaluation
        all_factors = list(self.values.keys()) + list(self.highlights.keys())
        for value_name in all_factors:
            user_score = user_feedback.get(value_name, 0.5)
            auto_score = response_scores.get(value_name, 0.5)

            # If user feedback differs significantly from auto-evaluation, adjust more
            difference = abs(user_score - auto_score)
            feedback_weight = min(
                0.3, difference + 0.1
            )  # Base weight of 0.1, up to 0.3

            self.update_value_score(value_name, user_score, feedback_weight)

    def save_values(self) -> None:
        """Save current value scores to disk."""
        data = {
            "values": {
                name: {"score": value.score, "weight": value.weight}
                for name, value in self.values.items()
            },
            "highlights": {
                name: {"score": value.score, "weight": value.weight}
                for name, value in self.highlights.items()
            },
        }

        file_path = self.storage_path / "values.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def load_values(self) -> None:
        """Load value scores from disk."""
        file_path = self.storage_path / "values.json"
        if not file_path.exists():
            return

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Load core values
            if "values" in data:
                for name, value_data in data["values"].items():
                    if name in self.values:
                        self.values[name].score = value_data.get(
                            "score", self.values[name].score
                        )
                        self.values[name].weight = value_data.get(
                            "weight", self.values[name].weight
                        )

            # Load highlights
            if "highlights" in data:
                for name, value_data in data["highlights"].items():
                    if name in self.highlights:
                        self.highlights[name].score = value_data.get(
                            "score", self.highlights[name].score
                        )
                        self.highlights[name].weight = value_data.get(
                            "weight", self.highlights[name].weight
                        )
        except Exception:
            # If loading fails, keep default values
            pass

    def _evaluate_respect(
        self, response: str, context: Optional[Dict[str, Any]] = None
    ) -> float:
        """Evaluate response for respect (avoiding harm, empathy, boundaries)."""
        response_lower = response.lower()

        # Negative indicators (reduce score)
        negative_indicators = [
            "stupid",
            "idiot",
            "dumb",
            "wrong",
            "bad",
            "terrible",
            "you should",
            "you must",
            "you have to",  # Too directive
        ]

        # Positive indicators (increase score)
        positive_indicators = [
            "i understand",
            "that makes sense",
            "let me help",
            "i appreciate",
            "thank you",
            "please",
            "sorry",
        ]

        negative_count = sum(
            1 for word in negative_indicators if word in response_lower
        )
        positive_count = sum(
            1 for word in positive_indicators if word in response_lower
        )

        # Base score of 0.7, adjusted by indicators
        score = 0.7
        score -= negative_count * 0.1  # -0.1 per negative indicator
        score += positive_count * 0.05  # +0.05 per positive indicator

        return max(0.0, min(1.0, score))

    def _evaluate_accuracy(
        self, response: str, context: Optional[Dict[str, Any]] = None
    ) -> float:
        """Evaluate response for accuracy (factual correctness, avoiding uncertainty)."""
        response_lower = response.lower()

        # Indicators of uncertainty (reduce score)
        uncertainty_indicators = [
            "i think",
            "maybe",
            "perhaps",
            "probably",
            "might be",
            "could be",
            "not sure",
            "i'm not certain",
        ]

        # Indicators of confidence (increase score)
        confidence_indicators = [
            "according to",
            "research shows",
            "data indicates",
            "fact",
            "evidence",
            "source",
            "verified",
        ]

        uncertainty_count = sum(
            1 for phrase in uncertainty_indicators if phrase in response_lower
        )
        confidence_count = sum(
            1 for phrase in confidence_indicators if phrase in response_lower
        )

        # Base score of 0.8, adjusted by indicators
        score = 0.8
        score -= uncertainty_count * 0.05  # -0.05 per uncertainty indicator
        score += confidence_count * 0.1  # +0.1 per confidence indicator

        return max(0.0, min(1.0, score))

    def _evaluate_helpfulness(
        self, response: str, context: Optional[Dict[str, Any]] = None
    ) -> float:
        """Evaluate response for helpfulness (solving problems, providing value)."""
        response_lower = response.lower()

        # Indicators of helpfulness (increase score)
        helpful_indicators = [
            "here's how",
            "you can",
            "try this",
            "solution",
            "step by step",
            "example",
            "guide",
            "help",
            "recommend",
            "suggest",
            "option",
            "alternative",
        ]

        # Indicators of unhelpfulness (reduce score)
        unhelpful_indicators = [
            "i don't know",
            "i can't help",
            "no idea",
            "sorry, i can't",
            "that's not possible",
        ]

        helpful_count = sum(
            1 for phrase in helpful_indicators if phrase in response_lower
        )
        unhelpful_count = sum(
            1 for phrase in unhelpful_indicators if phrase in response_lower
        )

        # Base score of 0.6, adjusted by indicators
        score = 0.6
        score += helpful_count * 0.1  # +0.1 per helpful indicator
        score -= unhelpful_count * 0.2  # -0.2 per unhelpful indicator

        return max(0.0, min(1.0, score))

    def _evaluate_community(
        self, response: str, context: Optional[Dict[str, Any]] = None
    ) -> float:
        """Evaluate response for community (building connections, inclusivity)."""
        response_lower = response.lower()

        # Positive indicators (increase score)
        community_indicators = [
            "we can",
            "together",
            "our community",
            "let's work",
            "inclusive",
            "support each other",
            "shared",
            "collective",
        ]

        # Negative indicators (reduce score)
        isolation_indicators = ["only i", "just me", "myself", "individual", "alone"]

        positive_count = sum(
            1 for phrase in community_indicators if phrase in response_lower
        )
        negative_count = sum(
            1 for phrase in isolation_indicators if phrase in response_lower
        )

        # Base score of 0.7, adjusted by indicators
        score = 0.7
        score += positive_count * 0.1  # +0.1 per community indicator
        score -= negative_count * 0.15  # -0.15 per isolation indicator

        return max(0.0, min(1.0, score))

    def _evaluate_faith(
        self, response: str, context: Optional[Dict[str, Any]] = None
    ) -> float:
        """Evaluate response for faith (trust, belief in potential)."""
        response_lower = response.lower()

        # Positive indicators (increase score)
        faith_indicators = [
            "believe in",
            "have faith",
            "trust the process",
            "potential",
            "optimistic",
            "hope",
            "confidence in",
            "possible",
        ]

        # Negative indicators (reduce score)
        doubt_indicators = [
            "impossible",
            "never work",
            "hopeless",
            "give up",
            "doubt",
            "skeptical",
            "pessimistic",
        ]

        positive_count = sum(
            1 for phrase in faith_indicators if phrase in response_lower
        )
        negative_count = sum(
            1 for phrase in doubt_indicators if phrase in response_lower
        )

        # Base score of 0.8, adjusted by indicators
        score = 0.8
        score += positive_count * 0.08  # +0.08 per faith indicator
        score -= negative_count * 0.12  # -0.12 per doubt indicator

        return max(0.0, min(1.0, score))

    def _evaluate_service(
        self, response: str, context: Optional[Dict[str, Any]] = None
    ) -> float:
        """Evaluate response for service (selfless help, dedication)."""
        response_lower = response.lower()

        # Positive indicators (increase score)
        service_indicators = [
            "serve",
            "dedicated to",
            "help others",
            "selfless",
            "give back",
            "contribute",
            "support",
            "assist",
        ]

        # Negative indicators (reduce score)
        selfish_indicators = [
            "only for me",
            "my benefit",
            "selfish",
            "just mine",
            "personal gain",
            "only myself",
        ]

        positive_count = sum(
            1 for phrase in service_indicators if phrase in response_lower
        )
        negative_count = sum(
            1 for phrase in selfish_indicators if phrase in response_lower
        )

        # Base score of 0.7, adjusted by indicators
        score = 0.7
        score += positive_count * 0.1  # +0.1 per service indicator
        score -= negative_count * 0.15  # -0.15 per selfish indicator

        return max(0.0, min(1.0, score))

    def _evaluate_growth(
        self, response: str, context: Optional[Dict[str, Any]] = None
    ) -> float:
        """Evaluate response for growth (continuous improvement, learning)."""
        response_lower = response.lower()

        # Positive indicators (increase score)
        growth_indicators = [
            "learn",
            "improve",
            "grow",
            "develop",
            "progress",
            "evolve",
            "enhance",
            "advance",
            "better",
            "opportunity",
        ]

        # Negative indicators (reduce score)
        stagnation_indicators = [
            "stuck",
            "can't change",
            "static",
            "unchanging",
            "no progress",
            "regress",
        ]

        positive_count = sum(
            1 for phrase in growth_indicators if phrase in response_lower
        )
        negative_count = sum(
            1 for phrase in stagnation_indicators if phrase in response_lower
        )

        # Base score of 0.75, adjusted by indicators
        score = 0.75
        score += positive_count * 0.08  # +0.08 per growth indicator
        score -= negative_count * 0.1  # -0.1 per stagnation indicator

        return max(0.0, min(1.0, score))

    def _evaluate_love(
        self, response: str, context: Optional[Dict[str, Any]] = None
    ) -> float:
        """Evaluate response for love (compassion, empathy, care)."""
        response_lower = response.lower()

        # Positive indicators (increase score)
        love_indicators = [
            "care about",
            "empathy",
            "compassion",
            "kindness",
            "understanding",
            "supportive",
            "gentle",
            "loving",
        ]

        # Negative indicators (reduce score)
        unloving_indicators = [
            "harsh",
            "unkind",
            "uncaring",
            "cold",
            "indifferent",
            "cruel",
            "mean",
            "heartless",
        ]

        positive_count = sum(
            1 for phrase in love_indicators if phrase in response_lower
        )
        negative_count = sum(
            1 for phrase in unloving_indicators if phrase in response_lower
        )

        # Base score of 0.8, adjusted by indicators
        score = 0.8
        score += positive_count * 0.08  # +0.08 per loving indicator
        score -= negative_count * 0.12  # -0.12 per unloving indicator

        return max(0.0, min(1.0, score))

    def _evaluate_integrity(
        self, response: str, context: Optional[Dict[str, Any]] = None
    ) -> float:
        """Evaluate response for integrity (honesty, ethical behavior)."""
        response_lower = response.lower()

        # Positive indicators (increase score)
        integrity_indicators = [
            "honest",
            "truthful",
            "ethical",
            "transparent",
            "accountable",
            "responsible",
            "fair",
            "just",
        ]

        # Negative indicators (reduce score)
        dishonest_indicators = [
            "lie",
            "deceive",
            "manipulate",
            "dishonest",
            "unethical",
            "corrupt",
            "biased",
            "unfair",
        ]

        positive_count = sum(
            1 for phrase in integrity_indicators if phrase in response_lower
        )
        negative_count = sum(
            1 for phrase in dishonest_indicators if phrase in response_lower
        )

        # Base score of 0.85, adjusted by indicators
        score = 0.85
        score += positive_count * 0.06  # +0.06 per integrity indicator
        score -= negative_count * 0.15  # -0.15 per dishonesty indicator

        return max(0.0, min(1.0, score))

    def _evaluate_innovation(
        self, response: str, context: Optional[Dict[str, Any]] = None
    ) -> float:
        """Evaluate response for innovation (creativity, forward-thinking)."""
        response_lower = response.lower()

        # Positive indicators (increase score)
        innovation_indicators = [
            "innovative",
            "creative",
            "new approach",
            "forward-thinking",
            "cutting-edge",
            "advanced",
            "modern",
            "novel",
        ]

        # Negative indicators (reduce score)
        traditional_indicators = [
            "traditional",
            "old way",
            "outdated",
            "stuck in past",
            "conventional",
            "standard",
            "routine",
        ]

        positive_count = sum(
            1 for phrase in innovation_indicators if phrase in response_lower
        )
        negative_count = sum(
            1 for phrase in traditional_indicators if phrase in response_lower
        )

        # Base score of 0.75, adjusted by indicators
        score = 0.75
        score += positive_count * 0.08  # +0.08 per innovation indicator
        score -= (
            negative_count * 0.05
        )  # -0.05 per traditional indicator (not strongly negative)

        return max(0.0, min(1.0, score))

    def _evaluate_excellence(
        self, response: str, context: Optional[Dict[str, Any]] = None
    ) -> float:
        """Evaluate response for excellence (quality, high standards)."""
        response_lower = response.lower()

        # Positive indicators (increase score)
        excellence_indicators = [
            "excellent",
            "quality",
            "high standard",
            "best practice",
            "professional",
            "thorough",
            "detailed",
            "precise",
        ]

        # Negative indicators (reduce score)
        mediocrity_indicators = [
            "good enough",
            "adequate",
            "mediocre",
            "sloppy",
            "rushed",
            "incomplete",
            "poor quality",
        ]

        positive_count = sum(
            1 for phrase in excellence_indicators if phrase in response_lower
        )
        negative_count = sum(
            1 for phrase in mediocrity_indicators if phrase in response_lower
        )

        # Base score of 0.85, adjusted by indicators
        score = 0.85
        score += positive_count * 0.06  # +0.06 per excellence indicator
        score -= negative_count * 0.1  # -0.1 per mediocrity indicator

        return max(0.0, min(1.0, score))

    def _evaluate_teamwork(
        self, response: str, context: Optional[Dict[str, Any]] = None
    ) -> float:
        """Evaluate response for teamwork (collaboration, unity)."""
        response_lower = response.lower()

        # Positive indicators (increase score)
        teamwork_indicators = [
            "collaborate",
            "team",
            "together",
            "united",
            "cooperate",
            "partnership",
            "joint effort",
            "shared",
        ]

        # Negative indicators (reduce score)
        isolation_indicators = [
            "solo",
            "independent",
            "lone wolf",
            "go it alone",
            "competition",
            "rivalry",
            "against each other",
        ]

        positive_count = sum(
            1 for phrase in teamwork_indicators if phrase in response_lower
        )
        negative_count = sum(
            1 for phrase in isolation_indicators if phrase in response_lower
        )

        # Base score of 0.75, adjusted by indicators
        score = 0.75
        score += positive_count * 0.08  # +0.08 per teamwork indicator
        score -= negative_count * 0.1  # -0.1 per isolation indicator

        return max(0.0, min(1.0, score))

    def _evaluate_accountability(
        self, response: str, context: Optional[Dict[str, Any]] = None
    ) -> float:
        """Evaluate response for accountability (responsibility, ownership)."""
        response_lower = response.lower()

        # Positive indicators (increase score)
        accountability_indicators = [
            "responsible",
            "accountable",
            "ownership",
            "commitment",
            "reliable",
            "dependable",
            "follow through",
            "deliver",
        ]

        # Negative indicators (reduce score)
        irresponsibility_indicators = [
            "blame others",
            "excuse",
            "avoid responsibility",
            "irresponsible",
            "unreliable",
            "undependable",
            "fail to deliver",
        ]

        positive_count = sum(
            1 for phrase in accountability_indicators if phrase in response_lower
        )
        negative_count = sum(
            1 for phrase in irresponsibility_indicators if phrase in response_lower
        )

        # Base score of 0.85, adjusted by indicators
        score = 0.85
        score += positive_count * 0.06  # +0.06 per accountability indicator
        score -= negative_count * 0.12  # -0.12 per irresponsibility indicator

        return max(0.0, min(1.0, score))

    def get_values_summary(self) -> Dict[str, Any]:
        """Get a summary of current values and their scores."""
        summary = {}

        # Add core values
        for name, value in self.values.items():
            summary[name] = {
                "score": value.score,
                "weight": value.weight,
                "effective_weight": value.score * value.weight,
                "category": "core",
            }

        # Add highlight factors
        for name, value in self.highlights.items():
            summary[name] = {
                "score": value.score,
                "weight": value.weight,
                "effective_weight": value.score * value.weight,
                "category": "highlight",
            }

        return summary


# Global instance for easy access
_default_value_system = None


def get_value_system() -> ValueSystem:
    """Get the default global value system instance."""
    global _default_value_system
    if _default_value_system is None:
        _default_value_system = ValueSystem()
    return _default_value_system
