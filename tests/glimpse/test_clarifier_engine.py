"""
Comprehensive tests for ClarifierEngine
"""
import pytest

from glimpse.clarifier_engine import (Clarifier, ClarifierEngine,
                                      ClarifierType,
                                      enhanced_sampler_with_clarifiers)
from glimpse.Glimpse import Draft


class TestClarifier:
    """Test the Clarifier dataclass"""

    def test_clarifier_creation(self):
        clarifier = Clarifier(
            type=ClarifierType.AUDIENCE,
            question="Is this for customers?",
            options=["customers", "internal"],
            default="internal",
        )
        assert clarifier.type == ClarifierType.AUDIENCE
        assert clarifier.question == "Is this for customers?"
        assert clarifier.options == ["customers", "internal"]
        assert clarifier.default == "internal"

    def test_format_question_with_default(self):
        clarifier = Clarifier(
            type=ClarifierType.AUDIENCE,
            question="Is this for customers?",
            options=["customers", "internal"],
            default="internal",
        )
        formatted = clarifier.format_question()
        assert "Clarifier: Is this for customers?" in formatted
        assert "[customers | internal]" in formatted
        assert "(default: internal)" in formatted

    def test_format_question_without_default(self):
        clarifier = Clarifier(
            type=ClarifierType.TONE,
            question="What tone?",
            options=["formal", "informal"],
        )
        formatted = clarifier.format_question()
        assert "Clarifier: What tone?" in formatted
        assert "[formal | informal]" in formatted
        assert "(default:" not in formatted


class TestClarifierEngine:
    """Test the ClarifierEngine class"""

    def test_glimpse_initialization(self):
        ClarifierEngine()
        assert len(Glimpse.clarifier_rules) > 0
        assert "customer" in Glimpse.clarifier_rules
        assert "formal" in Glimpse.clarifier_rules
        assert "brief" in Glimpse.clarifier_rules

    def test_detect_audience_ambiguity(self):
        ClarifierEngine()

        # Test customer mention
        clarifiers = Glimpse.detect_ambiguity(
            "Write an email to customers", "inform users", ""
        )
        assert len(clarifiers) > 0
        assert any(c.type == ClarifierType.AUDIENCE for c in clarifiers)

    def test_detect_tone_ambiguity(self):
        ClarifierEngine()

        # Test email/presentation triggers tone clarifier
        clarifiers = Glimpse.detect_ambiguity(
            "Create a presentation", "explain concept", ""
        )
        assert len(clarifiers) > 0
        assert any(c.type == ClarifierType.TONE for c in clarifiers)

    def test_detect_length_ambiguity(self):
        ClarifierEngine()

        # Test explain/describe triggers length clarifier
        clarifiers = Glimpse.detect_ambiguity(
            "Explain the process", "help user understand", ""
        )
        assert len(clarifiers) > 0
        assert any(c.type == ClarifierType.LENGTH for c in clarifiers)

    def test_detect_format_ambiguity(self):
        ClarifierEngine()

        # Test list/organize triggers format clarifier
        clarifiers = Glimpse.detect_ambiguity(
            "List the benefits", "organize information", ""
        )
        assert len(clarifiers) > 0
        assert any(c.type == ClarifierType.FORMAT for c in clarifiers)

    def test_detect_scope_ambiguity(self):
        ClarifierEngine()

        # Test focus/scope triggers scope clarifier
        clarifiers = Glimpse.detect_ambiguity(
            "Focus on technical aspects", "provide overview", ""
        )
        assert len(clarifiers) > 0
        assert any(c.type == ClarifierType.SCOPE for c in clarifiers)

    def test_detect_language_ambiguity(self):
        ClarifierEngine()

        # Test simplify/explain triggers language clarifier
        clarifiers = Glimpse.detect_ambiguity(
            "Simplify the technical details", "make it understandable", ""
        )
        assert len(clarifiers) > 0
        assert any(c.type == ClarifierType.LANGUAGE for c in clarifiers)

    def test_detect_urgency_ambiguity(self):
        ClarifierEngine()

        # Test urgent/asap triggers urgency clarifier
        clarifiers = Glimpse.detect_ambiguity(
            "urgent fix needed", "resolve immediately", ""
        )
        assert len(clarifiers) > 0
        assert any(c.type == ClarifierType.URGENCY for c in clarifiers)

    def test_detect_detail_level_ambiguity(self):
        ClarifierEngine()

        # Test detail/comprehensive triggers detail level clarifier
        clarifiers = Glimpse.detect_ambiguity(
            "Provide comprehensive details", "thorough analysis", ""
        )
        assert len(clarifiers) > 0
        assert any(c.type == ClarifierType.DETAIL_LEVEL for c in clarifiers)

    def test_empty_goal_triggers_audience_clarifier(self):
        ClarifierEngine()

        # Empty goal should always trigger audience clarifier
        clarifiers = Glimpse.detect_ambiguity("Some input text", "", "")
        assert len(clarifiers) > 0
        assert any(c.type == ClarifierType.AUDIENCE for c in clarifiers)

    def test_no_ambiguity_detected(self):
        ClarifierEngine()

        # Clear input with goal should not trigger clarifiers
        clarifiers = Glimpse.detect_ambiguity(
            "Simple task", "clear goal provided", "audience: internal"
        )
        assert len(clarifiers) == 0

    def test_max_three_clarifiers(self):
        ClarifierEngine()

        # Even with multiple triggers, should limit to 3
        clarifiers = Glimpse.detect_ambiguity(
            "urgent email to customers explaining technical details comprehensively",
            "",
            "",
        )
        assert len(clarifiers) <= 3

    def test_apply_clarifier_response_yes_no(self):
        ClarifierEngine()
        clarifier = Glimpse.clarifier_rules["customer"]

        # Test yes response
        result = Glimpse.apply_clarifier_response(clarifier, "y", "")
        assert "audience: customers" in result

        # Test no response
        result = Glimpse.apply_clarifier_response(clarifier, "n", "")
        assert "audience: internal" in result

    def test_apply_clarifier_response_explicit_options(self):
        ClarifierEngine()
        clarifier = Glimpse.clarifier_rules["formal"]

        # Test explicit option
        result = Glimpse.apply_clarifier_response(clarifier, "formal", "")
        assert "tone: formal" in result

    def test_apply_clarifier_response_invalid_uses_default(self):
        ClarifierEngine()
        clarifier = Glimpse.clarifier_rules["customer"]

        # Test invalid response uses default
        result = Glimpse.apply_clarifier_response(clarifier, "invalid", "")
        assert "audience: internal" in result  # default value

    def test_apply_clarifier_response_appends_to_existing(self):
        ClarifierEngine()
        clarifier = Glimpse.clarifier_rules["customer"]

        # Test appending to existing constraints
        result = Glimpse.apply_clarifier_response(
            clarifier, "y", "existing: constraint"
        )
        assert "existing: constraint" in result
        assert "audience: customers" in result
        assert "|" in result  # separator added

    def test_generate_clarifier_delta_single(self):
        ClarifierEngine()
        clarifiers = [Glimpse.clarifier_rules["customer"]]

        delta = Glimpse.generate_clarifier_delta(clarifiers)
        assert "Clarifier: Is this for customers or internal team?" in delta
        assert "[customers | internal]" in delta
        assert "(default: internal)" in delta

    def test_generate_clarifier_delta_multiple(self):
        ClarifierEngine()
        clarifiers = [
            Glimpse.clarifier_rules["customer"],
            Glimpse.clarifier_rules["formal"],
        ]

        delta = Glimpse.generate_clarifier_delta(clarifiers)
        assert "Clarifier: Please specify:" in delta
        assert "1. Clarifier:" in delta
        assert "2. Clarifier:" in delta

    def test_generate_clarifier_delta_empty(self):
        ClarifierEngine()

        delta = Glimpse.generate_clarifier_delta([])
        assert delta == ""


@pytest.mark.asyncio
class TestEnhancedSampler:
    """Test the enhanced sampler with clarifiers"""

    async def test_enhanced_sampler_detects_ambiguity(self):
        draft = Draft(input_text="Write an email to customers", goal="", constraints="")

        result = await enhanced_sampler_with_clarifiers(draft)
        sample, essence, delta, aligned = result

        # Should detect ambiguity and return clarifier
        assert delta is not None
        assert "Clarifier:" in delta
        assert not aligned
        assert sample == ""
        assert essence == ""

    async def test_enhanced_sampler_no_ambiguity(self):
        draft = Draft(
            input_text="Simple task",
            goal="clear goal",
            constraints="audience: internal",
        )

        result = await enhanced_sampler_with_clarifiers(draft)
        sample, essence, delta, aligned = result

        # Should not detect ambiguity
        assert delta is None
        assert aligned
        assert sample != ""
        assert essence != ""

    async def test_enhanced_sampler_with_custom_clarifier_engine(self):
        from glimpse.clarifier_engine import ClarifierEngine

        custom_engine = ClarifierEngine()
        draft = Draft(input_text="urgent request", goal="", constraints="")

        result = await enhanced_sampler_with_clarifiers(draft, custom_engine)
        sample, essence, delta, aligned = result

        # Should use custom Glimpse to detect ambiguity
        assert delta is not None
        assert "Clarifier:" in delta


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
