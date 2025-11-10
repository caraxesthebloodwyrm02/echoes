"""
Enhanced Clarifier Glimpse with Post-Execution Curiosity System
Transforms clarifiers from interrogators to learning companions
"""

import random
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any


class ClarifierType(Enum):
    """Types of clarifiers available"""

    PRE_EXECUTION = "pre_execution"  # Blocking, rare, critical only
    POST_EXECUTION = "post_execution"  # Curiosity-driven, frequent


class CuriosityCategory(Enum):
    """Categories of curiosity questions"""

    SATISFACTION = "satisfaction"
    PREFERENCE = "preference"
    CONTEXT = "context"
    FREQUENCY = "frequency"
    IMPROVEMENT = "improvement"


@dataclass
class Clarifier:
    """Represents a clarifier question and its options"""

    type: ClarifierType
    category: CuriosityCategory | None
    question: str
    options: list[str]
    default: str | None = None

    def format_question(self) -> str:
        """Format the clarifier as a user-facing question"""
        opts = " | ".join(self.options)
        if self.default:
            return f"Curiosity: {self.question} [{opts}] (default: {self.default})"
        return f"Curiosity: {self.question} [{opts}]"


class UserEngagementTracker:
    """Tracks user engagement to determine when to ask curiosity questions"""

    def __init__(self):
        self.interaction_count = 0
        self.last_curiosity_time = 0
        self.curiosity_response_rate = 0.0
        self.engagement_score = 0.5
        self.user_profile = {}

    def track_interaction(self, user_responded: bool = True):
        """Track an interaction and update engagement metrics"""
        self.interaction_count += 1
        if user_responded:
            self.curiosity_response_rate = (self.curiosity_response_rate * 0.8) + (
                1.0 * 0.2
            )
        else:
            self.curiosity_response_rate = (self.curiosity_response_rate * 0.8) + (
                0.0 * 0.2
            )

        # Update engagement score
        self.engagement_score = min(
            1.0,
            (
                self.engagement_score + 0.05
                if user_responded
                else self.engagement_score - 0.02
            ),
        )

    def should_ask_curiosity(self) -> bool:
        """Determine if it's a good time to ask a curiosity question"""
        time_since_last = time.time() - self.last_curiosity_time

        # Only ask if:
        # - Engagement is good (>0.3)
        # - Not asked recently (>5 minutes)
        # - Response rate is decent (>0.2)
        return (
            self.engagement_score > 0.3
            and time_since_last > 300
            and self.curiosity_response_rate > 0.2
            and self.interaction_count > 2
        )

    def update_user_preference(self, key: str, value: str):
        """Update user preferences based on responses"""
        if key not in self.user_profile:
            self.user_profile[key] = {}

        # Track frequency of preferences
        if value in self.user_profile[key]:
            self.user_profile[key][value] += 1
        else:
            self.user_profile[key][value] = 1


class EnhancedClarifierEngine:
    """Enhanced clarifier Glimpse with post-execution curiosity system"""

    def __init__(self):
        """Initialize with engagement tracking and curiosity rules"""
        self.engagement_tracker = UserEngagementTracker()

        # Critical pre-execution clarifiers (rare, blocking)
        self.critical_clarifiers = {
            "critical_audience": Clarifier(
                type=ClarifierType.PRE_EXECUTION,
                category=None,
                question="This request affects external people. Should I proceed?",
                options=["proceed", "cancel"],
                default="proceed",
            )
        }

        # Post-execution curiosity questions (frequent, non-blocking)
        self.curiosity_questions = {
            # Satisfaction questions
            "tone_satisfaction": Clarifier(
                type=ClarifierType.POST_EXECUTION,
                category=CuriosityCategory.SATISFACTION,
                question="How was the tone of that response?",
                options=["perfect", "too formal", "too casual", "just right"],
                default="perfect",
            ),
            "length_satisfaction": Clarifier(
                type=ClarifierType.POST_EXECUTION,
                category=CuriosityCategory.SATISFACTION,
                question="Was the length appropriate?",
                options=["too short", "just right", "too long"],
                default="just right",
            ),
            # Preference questions
            "audience_preference": Clarifier(
                type=ClarifierType.POST_EXECUTION,
                category=CuriosityCategory.PREFERENCE,
                question="For future requests like this, who's your audience?",
                options=["customers", "internal team", "mixed", "just me"],
                default="internal team",
            ),
            "format_preference": Clarifier(
                type=ClarifierType.POST_EXECUTION,
                category=CuriosityCategory.PREFERENCE,
                question="What format works best for you?",
                options=["bullet points", "paragraphs", "numbered list", "outline"],
                default="bullet points",
            ),
            # Context questions
            "goal_context": Clarifier(
                type=ClarifierType.POST_EXECUTION,
                category=CuriosityCategory.CONTEXT,
                question="What was the main goal of that request?",
                options=["inform", "persuade", "analyze", "create", "organize"],
                default="inform",
            ),
            # Frequency questions
            "task_frequency": Clarifier(
                type=ClarifierType.POST_EXECUTION,
                category=CuriosityCategory.FREQUENCY,
                question="How often do you do this type of task?",
                options=["daily", "weekly", "monthly", "rarely"],
                default="weekly",
            ),
            # Improvement questions
            "improvement_feedback": Clarifier(
                type=ClarifierType.POST_EXECUTION,
                category=CuriosityCategory.IMPROVEMENT,
                question="What could make responses like this better?",
                options=["more examples", "simpler language", "more detail", "nothing"],
                default="nothing",
            ),
        }

    def detect_critical_ambiguity(
        self, input_text: str, goal: str, constraints: str
    ) -> list[Clarifier]:
        """
        Detect critical ambiguities that require pre-execution clarification
        Only used for high-stakes or potentially harmful scenarios

        Args:
            input_text: The user's input text
            goal: The stated goal (may be empty)
            constraints: Current constraints

        Returns:
            List of critical clarifiers (usually 0 or 1)
        """
        clarifiers = []
        text_lower = (input_text or "").lower()

        # Only detect critical issues that could cause harm
        if (
            any(
                word in text_lower
                for word in ["delete", "remove", "cancel", "terminate"]
            )
            and "critical_action" not in (constraints or "").lower()
        ):
            clarifiers.append(self.critical_clarifiers["critical_audience"])

        # Maximum 1 critical clarifier to avoid blocking
        return clarifiers[:1]

    def generate_curiosity_question(self, context: dict[str, Any]) -> Clarifier | None:
        """
        Generate a curiosity question based on context and engagement

        Args:
            context: Context about the recent interaction

        Returns:
            A curiosity question or None if not appropriate
        """
        if not self.engagement_tracker.should_ask_curiosity():
            return None

        # Select question category based on context
        if "task_type" in context:
            task_type = context["task_type"]

            if task_type == "communication":
                # Ask about communication preferences
                questions = [
                    self.curiosity_questions["tone_satisfaction"],
                    self.curiosity_questions["audience_preference"],
                    self.curiosity_questions["format_preference"],
                ]
            elif task_type == "analysis":
                # Ask about analysis preferences
                questions = [
                    self.curiosity_questions["length_satisfaction"],
                    self.curiosity_questions["goal_context"],
                    self.curiosity_questions["improvement_feedback"],
                ]
            else:
                # General questions
                questions = [
                    self.curiosity_questions["task_frequency"],
                    self.curiosity_questions["improvement_feedback"],
                ]
        else:
            # Random selection from all curiosity questions
            questions = list(self.curiosity_questions.values())

        # Select a question (weighted by user response history)
        selected = random.choice(questions)

        # Update last curiosity time
        self.engagement_tracker.last_curiosity_time = time.time()

        return selected

    def apply_curiosity_response(
        self, clarifier: Clarifier, response: str
    ) -> dict[str, Any]:
        """
        Apply a curiosity response to update user profile

        Args:
            clarifier: The curiosity question asked
            response: The user's response

        Returns:
            Updated user preferences
        """
        # Normalize response
        response = response.lower().strip()

        # Track engagement
        self.engagement_tracker.track_interaction(user_responded=True)

        # Update user profile
        if clarifier.category == CuriosityCategory.PREFERENCE:
            key = clarifier.category.value
            self.engagement_tracker.update_user_preference(key, response)

        return {
            "preference_updated": True,
            "category": clarifier.category.value if clarifier.category else None,
            "response": response,
            "engagement_score": self.engagement_tracker.engagement_score,
        }

    def get_user_preferences(self) -> dict[str, Any]:
        """Get learned user preferences"""
        return {
            "profile": self.engagement_tracker.user_profile,
            "engagement_score": self.engagement_tracker.engagement_score,
            "interaction_count": self.engagement_tracker.interaction_count,
            "response_rate": self.engagement_tracker.curiosity_response_rate,
        }

    def generate_preferred_constraints(self, context: dict[str, Any]) -> str:
        """
        Generate constraints based on learned user preferences

        Args:
            context: Current request context

        Returns:
            Constraint string based on user preferences
        """
        constraints = []
        profile = self.engagement_tracker.user_profile

        # Apply learned preferences
        if "audience" in profile and profile["audience"]:
            top_audience = max(profile["audience"].items(), key=lambda x: x[1])[0]
            constraints.append(f"audience: {top_audience}")

        if "format" in profile and profile["format"]:
            top_format = max(profile["format"].items(), key=lambda x: x[1])[0]
            constraints.append(f"format: {top_format}")

        # Add context-based defaults
        if "task_type" in context:
            task_type = context["task_type"]
            if task_type == "communication" and "tone" not in constraints:
                constraints.append("tone: professional")
            elif task_type == "analysis" and "length" not in constraints:
                constraints.append("length: detailed")

        return " | ".join(constraints)


# Enhanced sampler with post-execution curiosity
async def enhanced_sampler_with_curiosity(
    draft, clarifier_engine: EnhancedClarifierEngine = None
):
    """
    Enhanced sampler that includes critical pre-execution and post-execution curiosity

    Args:
        draft: The input draft
        clarifier_engine: Optional enhanced clarifier Glimpse instance

    Returns:
        Tuple of (sample, essence, delta, aligned, post_execution_curiosity)
    """
    if clarifier_engine is None:
        clarifier_engine = EnhancedClarifierEngine()

    # Check for critical pre-execution ambiguities (rare)
    critical_clarifiers = clarifier_engine.detect_critical_ambiguity(
        draft.input_text, draft.goal, draft.constraints
    )

    if critical_clarifiers:
        # Return critical clarifier (blocking)
        delta = critical_clarifiers[0].format_question()
        return ("", "", delta, False, None)

    # Generate preferred constraints from learned profile
    context = {
        "task_type": (
            "communication" if "email" in draft.input_text.lower() else "general"
        )
    }
    preferred_constraints = clarifier_engine.generate_preferred_constraints(context)

    # Combine with existing constraints
    if preferred_constraints and draft.constraints:
        full_constraints = f"{draft.constraints} | {preferred_constraints}"
    elif preferred_constraints:
        full_constraints = preferred_constraints
    else:
        full_constraints = draft.constraints

    # Generate response using learned preferences
    sample = f"Sample response with learned preferences: {full_constraints}"
    essence = "Essence: Tailored response based on user profile"

    # Generate post-execution curiosity question
    curiosity = clarifier_engine.generate_curiosity_question(context)
    curiosity_delta = curiosity.format_question() if curiosity else None

    return (sample, essence, None, True, curiosity_delta)


# Example usage and testing
if __name__ == "__main__":
    engine = EnhancedClarifierEngine()

    # Test critical ambiguity detection (should return empty for normal requests)
    test_cases = [
        ("Write an email to customers", "inform users", ""),
        ("Delete all user data", "cleanup", ""),
        ("Create a report", "analyze data", ""),
    ]

    for text, goal, constraints in test_cases:
        clarifiers = engine.detect_critical_ambiguity(text, goal, constraints)
        print(f"\nInput: {text}")
        print(f"Critical clarifiers: {len(clarifiers)}")
        for c in clarifiers:
            print(f"  - {c.format_question()}")

    # Test curiosity question generation
    context = {"task_type": "communication"}
    curiosity = engine.generate_curiosity_question(context)
    if curiosity:
        print(f"\nCuriosity question: {curiosity.format_question()}")

    # Test preference learning
    response = engine.apply_curiosity_response(curiosity, "customers")
    print(f"\nPreferences updated: {response}")
    print(f"User profile: {engine.get_user_preferences()}")
