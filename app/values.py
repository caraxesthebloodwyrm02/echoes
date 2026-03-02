"""
Value System for Echoes Assistant V2

Manages three core values: respect, accuracy, helpfulness
Provides scoring mechanisms for response evaluation and behavior learning.
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


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

    Each value influences the assistant's behavior and response generation.
    Scores are updated based on user feedback and interaction patterns.
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

        # Load existing values if available
        self.load_values()

    def get_value_score(self, value_name: str) -> float:
        """Get the current score for a specific value."""
        if value_name not in self.values:
            return 0.0
        return self.values[value_name].score

    def get_value_weight(self, value_name: str) -> float:
        """Get the weight for a specific value."""
        if value_name not in self.values:
            return 0.0
        return self.values[value_name].weight

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
        if value_name not in self.values:
            return

        current_score = self.values[value_name].score
        # Weighted average between current score and new feedback
        updated_score = (current_score * (1 - feedback_weight)) + (
            new_score * feedback_weight
        )

        self.values[value_name].score = max(0.0, min(1.0, updated_score))
        self.save_values()

    def evaluate_response(
        self, response: str, context: dict[str, Any] | None = None
    ) -> dict[str, float]:
        """
        Evaluate a response against all three core values.

        Args:
            response: The response text to evaluate
            context: Optional context about the interaction

        Returns:
            Dictionary with scores for each value
        """
        scores = {}

        # Evaluate respect (avoiding harm, considering user feelings)
        scores["respect"] = self._evaluate_respect(response, context)

        # Evaluate accuracy (factual correctness, avoiding misinformation)
        scores["accuracy"] = self._evaluate_accuracy(response, context)

        # Evaluate helpfulness (solving problems, providing value)
        scores["helpfulness"] = self._evaluate_helpfulness(response, context)

        return scores

    def get_overall_score(self, response_scores: dict[str, float]) -> float:
        """
        Calculate overall score weighted by value importance.

        Args:
            response_scores: Scores for each value from evaluate_response

        Returns:
            Weighted overall score (0.0 to 1.0)
        """
        total_weight = sum(self.get_value_weight(name) for name in self.values.keys())
        if total_weight == 0:
            return 0.0

        weighted_sum = sum(
            response_scores.get(name, 0.0) * self.get_value_weight(name)
            for name in self.values.keys()
        )

        return weighted_sum / total_weight

    def provide_feedback(
        self,
        response: str,
        user_feedback: dict[str, float],
        context: dict[str, Any] | None = None,
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
        for value_name in self.values.keys():
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
            name: {"score": value.score, "weight": value.weight}
            for name, value in self.values.items()
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
            with open(file_path, encoding="utf-8") as f:
                data = json.load(f)

            for name, value_data in data.items():
                if name in self.values:
                    self.values[name].score = value_data.get(
                        "score", self.values[name].score
                    )
                    self.values[name].weight = value_data.get(
                        "weight", self.values[name].weight
                    )
        except Exception:
            # If loading fails, keep default values
            pass

    def _evaluate_respect(
        self, response: str, context: dict[str, Any] | None = None
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
        self, response: str, context: dict[str, Any] | None = None
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
        self, response: str, context: dict[str, Any] | None = None
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

    def get_values_summary(self) -> dict[str, Any]:
        """Get a summary of current values and their scores."""
        return {
            name: {
                "score": value.score,
                "weight": value.weight,
                "effective_weight": value.score * value.weight,
            }
            for name, value in self.values.items()
        }


# Global instance for easy access
_default_value_system = None


def get_value_system() -> ValueSystem:
    """Get the default global value system instance."""
    global _default_value_system
    if _default_value_system is None:
        _default_value_system = ValueSystem()
    return _default_value_system
