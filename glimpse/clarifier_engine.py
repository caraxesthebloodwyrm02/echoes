"""
Clarifier Glimpse for Glimpse Preflight System
Provides various clarifier paths to resolve ambiguity and improve intent understanding

UPDATED: Now uses post-execution curiosity questions instead of pre-execution blocking questions
to improve user engagement and continuous learning.
"""
from dataclasses import dataclass
from enum import Enum
from typing import Any

# Import enhanced clarifier engine for new functionality
try:
    from .enhanced_clarifier_engine import (ClarifierType, CuriosityCategory,
                                            EnhancedClarifierEngine)

    ENHANCED_CLARIFIER_AVAILABLE = True
except ImportError:
    ENHANCED_CLARIFIER_AVAILABLE = False
    print("⚠️ Enhanced clarifier engine not available, using legacy mode")


class ClarifierType(Enum):
    """Types of clarifiers available"""

    AUDIENCE = "audience"
    TONE = "tone"
    LENGTH = "length"
    FORMAT = "format"
    SCOPE = "scope"
    LANGUAGE = "language"
    URGENCY = "urgency"
    DETAIL_LEVEL = "detail_level"


@dataclass
class Clarifier:
    """Represents a clarifier question and its options"""

    type: ClarifierType
    question: str
    options: list[str]
    default: str | None = None

    def format_question(self) -> str:
        """Format the clarifier as a user-facing question"""
        opts = " | ".join(self.options)
        if self.default:
            return f"Clarifier: {self.question} [{opts}] (default: {self.default})"
        return f"Clarifier: {self.question} [{opts}]"


class ClarifierEngine:
    """Glimpse for generating and processing clarifiers"""

    def __init__(self, use_enhanced_mode: bool = True):
        """Initialize the clarifier Glimpse with default configurations"""
        # Try to use enhanced mode if available
        self.enhanced_mode = use_enhanced_mode and ENHANCED_CLARIFIER_AVAILABLE
        if self.enhanced_mode:
            self.enhanced_engine = EnhancedClarifierEngine()
            print("✅ Using enhanced clarifier engine with post-execution curiosity")
        else:
            print("📋 Using legacy clarifier engine")
            # Legacy clarifier rules (kept for compatibility)
            self.clarifier_rules = {
                # Audience clarifiers
                "customer": Clarifier(
                    type=ClarifierType.AUDIENCE,
                    question="Is this for customers or internal team?",
                    options=["customers", "internal"],
                    default="internal",
                ),
                "external": Clarifier(
                    type=ClarifierType.AUDIENCE,
                    question="Is this for external stakeholders?",
                    options=["external", "internal"],
                    default="internal",
                ),
                "public": Clarifier(
                    type=ClarifierType.AUDIENCE,
                    question="Is this for public consumption?",
                    options=["public", "private"],
                    default="private",
                ),
                # Tone clarifiers
                "formal": Clarifier(
                    type=ClarifierType.TONE,
                    question="Should this be formal or informal?",
                    options=["formal", "informal"],
                    default="informal",
                ),
                # Length clarifiers
                "brief": Clarifier(
                    type=ClarifierType.LENGTH,
                    question="How detailed should this be?",
                    options=["brief", "detailed", "comprehensive"],
                    default="brief",
                ),
                # Format clarifiers
                "list": Clarifier(
                    type=ClarifierType.FORMAT,
                    question="What format would you prefer?",
                    options=["bullet points", "paragraphs", "numbered list"],
                    default="bullet points",
                ),
            }

    def detect_ambiguity(
        self, input_text: str, goal: str, constraints: str
    ) -> list[Clarifier]:
        """
        Detect ambiguities in the input and suggest clarifiers

        Args:
            input_text: The user's input text
            goal: The stated goal (may be empty)
            constraints: Current constraints

        Returns:
            List of suggested clarifiers
        """
        if self.enhanced_mode:
            # Use enhanced engine - only detect critical pre-execution issues
            return self.enhanced_engine.detect_critical_ambiguity(
                input_text, goal, constraints
            )
        else:
            # Legacy mode - detect all ambiguities (blocking)
            return self._legacy_detect_ambiguity(input_text, goal, constraints)

    def _legacy_detect_ambiguity(
        self, input_text: str, goal: str, constraints: str
    ) -> list[Clarifier]:
        """Legacy ambiguity detection (blocking questions)"""
        clarifiers = []
        text_lower = input_text.lower()
        constraints_lower = constraints.lower()

        # Check for audience ambiguity
        if (
            any(word in text_lower for word in ["customer", "client", "user"])
            and "audience" not in constraints_lower
        ):
            clarifiers.append(self.clarifier_rules["customer"])

        # Check for tone ambiguity
        if (
            any(
                word in text_lower
                for word in ["email", "report", "presentation", "document"]
            )
            and "tone" not in constraints_lower
        ):
            clarifiers.append(self.clarifier_rules["formal"])

        # Check for length ambiguity
        if (
            any(
                word in text_lower
                for word in ["explain", "describe", "detail", "overview"]
            )
            and "length" not in constraints_lower
        ):
            clarifiers.append(self.clarifier_rules["brief"])

        # Check for format ambiguity
        if (
            any(
                word in text_lower
                for word in ["list", "organize", "structure", "format"]
            )
            and "format" not in constraints_lower
        ):
            clarifiers.append(self.clarifier_rules["list"])

        # Limit to maximum 3 clarifiers
        return clarifiers[:3]

    def generate_post_execution_curiosity(self, context: dict[str, Any]) -> str | None:
        """
        Generate a post-execution curiosity question

        Args:
            context: Context about the recent interaction

        Returns:
            Curiosity question string or None
        """
        if self.enhanced_mode:
            curiosity = self.enhanced_engine.generate_curiosity_question(context)
            return curiosity.format_question() if curiosity else None
        else:
            # Legacy mode - no post-execution curiosity
            return None

    def apply_curiosity_response(
        self, response: str, context: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Apply a curiosity response to update user profile

        Args:
            response: The user's response
            context: Context about the interaction

        Returns:
            Updated preferences
        """
        if self.enhanced_mode:
            # Find the last asked curiosity question
            curiosity = self.enhanced_engine.generate_curiosity_question(context)
            if curiosity:
                return self.enhanced_engine.apply_curiosity_response(
                    curiosity, response
                )
        return {"preference_updated": False}

    def get_learned_preferences(self) -> dict[str, Any]:
        """Get learned user preferences"""
        if self.enhanced_mode:
            return self.enhanced_engine.get_user_preferences()
        return {"profile": {}, "engagement_score": 0.5}

    def apply_clarifier_response(
        self, clarifier: Clarifier, response: str, constraints: str
    ) -> str:
        """
        Apply a clarifier response to the constraints

        Args:
            clarifier: The clarifier that was asked
            response: The user's response
            constraints: Current constraints

        Returns:
            Updated constraints string
        """
        # Normalize response
        response = response.lower().strip()

        # Map response to standard value
        if response in ["y", "yes", "true", "1"]:
            if clarifier.type == ClarifierType.AUDIENCE:
                response = (
                    "customers"
                    if "customer" in clarifier.question.lower()
                    else "external"
                )
            elif clarifier.type == ClarifierType.TONE:
                response = "formal"
            elif clarifier.type == ClarifierType.LENGTH:
                response = "detailed"
            elif clarifier.type == ClarifierType.FORMAT:
                response = "structured"
            elif clarifier.type == ClarifierType.SCOPE:
                response = "broad"
            elif clarifier.type == ClarifierType.LANGUAGE:
                response = "simple"
            elif clarifier.type == ClarifierType.URGENCY:
                response = "urgent"
            elif clarifier.type == ClarifierType.DETAIL_LEVEL:
                response = "deep-dive"
        elif response in ["n", "no", "false", "0"]:
            if clarifier.type == ClarifierType.AUDIENCE:
                response = "internal"
            elif clarifier.type == ClarifierType.TONE:
                response = "informal"
            elif clarifier.type == ClarifierType.LENGTH:
                response = "brief"
            elif clarifier.type == ClarifierType.FORMAT:
                response = "freeform"
            elif clarifier.type == ClarifierType.SCOPE:
                response = "narrow"
            elif clarifier.type == ClarifierType.LANGUAGE:
                response = "technical"
            elif clarifier.type == ClarifierType.URGENCY:
                response = "normal"
            elif clarifier.type == ClarifierType.DETAIL_LEVEL:
                response = "high-level"

        # Validate response is in options
        if response not in [opt.lower() for opt in clarifier.options]:
            response = clarifier.default or clarifier.options[0].lower()

        # Add to constraints
        constraint_key = clarifier.type.value
        new_constraint = f"{constraint_key}: {response}"

        if constraints.strip():
            return f"{constraints} | {new_constraint}"
        else:
            return new_constraint

    def generate_clarifier_delta(self, clarifiers: list[Clarifier]) -> str:
        """
        Generate a delta string for multiple clarifiers

        Args:
            clarifiers: List of clarifiers to include

        Returns:
            Formatted delta string
        """
        if not clarifiers:
            return ""

        if len(clarifiers) == 1:
            return clarifiers[0].format_question()

        # Multiple clarifiers - format as a list
        lines = ["Clarifier: Please specify:"]
        for i, clarifier in enumerate(clarifiers, 1):
            lines.append(f"  {i}. {clarifier.format_question()}")

        return "\n".join(lines)


# Enhanced sampler with clarifier integration
async def enhanced_sampler_with_clarifiers(
    draft, clarifier_engine: ClarifierEngine = None
):
    """
    Enhanced sampler that includes clarifier logic

    Args:
        draft: The input draft
        clarifier_engine: Optional clarifier Glimpse instance

    Returns:
        Tuple of (sample, essence, delta, aligned)
    """
    if clarifier_engine is None:
        clarifier_engine = ClarifierEngine()

    # Detect ambiguities
    clarifiers = clarifier_engine.detect_ambiguity(
        draft.input_text, draft.goal, draft.constraints
    )

    if clarifiers:
        # Return clarifier question
        delta = clarifier_engine.generate_clarifier_delta(clarifiers)
        return ("", "", delta, False)

    # No clarifiers needed - proceed with normal sampling
    # This would integrate with your actual sampling logic
    sample = f"Sample response for: {draft.input_text[:50]}..."
    essence = f"Essence: Process request about {draft.goal or 'general topic'}"

    return (sample, essence, None, True)


# Example usage and testing
if __name__ == "__main__":
    engine = ClarifierEngine()

    # Test ambiguity detection
    test_cases = [
        ("Write an email to customers about the new feature", "inform users", ""),
        ("Create a detailed report for the board", "present findings", ""),
        ("Explain the technical concept", "help user understand", ""),
        ("List the main benefits", "organize information", ""),
        (" urgent fix needed", "resolve issue", ""),
    ]

    for text, goal, constraints in test_cases:
        clarifiers = Glimpse.detect_ambiguity(text, goal, constraints)
        print(f"\nInput: {text}")
        print(f"Detected clarifiers: {len(clarifiers)}")
        for c in clarifiers:
            print(f"  - {c.format_question()}")
