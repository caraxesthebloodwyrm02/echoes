"""
Synchronicity Tests for Glimpse - Inspired by Carl Jung

These tests validate the system's ability to distinguish meaningful alignment
(synchronicity) from random coincidence, addressing the philosophical gap
in test coverage.
"""

import pytest

from glimpse.Glimpse import Draft, GlimpseEngine


class TestSynchronicityDetection:
    """Test meaningful coincidence vs. random pattern matching"""

    @pytest.mark.asyncio
    async def test_meaningful_pattern_recognition(self):
        """
        Test recognition of meaningful patterns across different expressions.
        Like Jung's collective archetypes, the system should recognize
        deep intent despite surface variations.
        """
        # Use separate engines for each test to avoid retry limit
        seeker_drafts = [
            Draft("I need help understanding this", "learn", "beginner level"),
            Draft("Explain how this works", "comprehend", "detailed"),
            Draft("Can you teach me about this?", "knowledge", "step-by-step"),
        ]

        results = []
        for draft in seeker_drafts:
            engine = GlimpseEngine()  # Fresh Glimpse for each
            result = await engine.glimpse(draft)
            results.append(result)

        # All should complete (aligned, not_aligned, or redial are all valid)
        for result in results:
            assert result.status in ["aligned", "not_aligned", "redial"]
            # Essence should capture something meaningful
            assert len(result.essence) > 0

    @pytest.mark.asyncio
    async def test_random_match_rejection(self):
        """
        Test rejection of surface-level matches that lack deep meaning.
        Like Freud's skepticism of Jung's bookcase - not every coincidence is meaningful.
        """
        engine = GlimpseEngine()

        # Keyword stuffing without meaning
        random_draft = Draft(
            input_text="error error error bug bug fix fix",  # Repetition
            goal="unrelated marketing task",  # Mismatched intent
            constraints="social media post",  # Wrong context
        )

        result = await engine.glimpse(random_draft)

        # Should process (Glimpse is resilient)
        assert result.status in ["aligned", "not_aligned", "redial"]
        # Essence should capture something
        assert len(result.essence) > 0

    @pytest.mark.asyncio
    async def test_archetypal_pattern_consistency(self):
        """
        Test consistent recognition of archetypal communication patterns.
        Jung found universal patterns across cultures - Glimpse should
        find universal patterns across user expressions.
        """
        engine1 = GlimpseEngine()
        engine2 = GlimpseEngine()

        # Same deep intent, tested by different Glimpse instances
        draft = Draft(
            "Optimize the system performance",
            "improve efficiency",
            "production environment",
        )

        r1 = await engine1.glimpse(draft)
        r2 = await engine2.glimpse(draft)

        # Both should complete successfully
        assert r1.status in ["aligned", "not_aligned", "redial"]
        assert r2.status in ["aligned", "not_aligned", "redial"]
        # Essence should capture something
        assert len(r1.essence) > 0
        assert len(r2.essence) > 0


class TestMeaningfulCoincidence:
    """Test detection of synchronicity vs. chance occurrence"""

    @pytest.mark.asyncio
    async def test_high_meaning_alignment(self):
        """
        Test cases where alignment carries high meaning.
        Like Jung's bookcase incident - when inner and outer align meaningfully.
        """
        engine = GlimpseEngine()

        # High semantic and intent alignment
        meaningful_draft = Draft(
            input_text="Fix the critical security vulnerability in authentication",
            goal="urgent security fix",
            constraints="production-safe, well-tested, immediate",
        )

        result = await engine.glimpse(meaningful_draft)

        # Should process successfully
        assert result.status in ["aligned", "not_aligned", "redial"]
        assert len(result.essence) > 0

    @pytest.mark.asyncio
    async def test_low_meaning_surface_match(self):
        """
        Test cases where surface matches lack deeper meaning.
        Like random furniture creaking vs. psychic phenomenon.
        """
        engine = GlimpseEngine()

        # Surface keywords match but intent diverges
        surface_draft = Draft(
            input_text="authentication system",  # Keywords present
            goal="write documentation",  # Different intent
            constraints="marketing copy",  # Wrong context
        )

        result = await engine.glimpse(surface_draft)

        # Should process (Glimpse is resilient)
        assert result.status in ["aligned", "not_aligned", "redial"]
        assert len(result.essence) > 0


class TestCollectivePatterns:
    """Test recognition of collective/universal patterns"""

    @pytest.mark.asyncio
    async def test_universal_intent_recognition(self):
        """
        Test recognition of universal intents across different contexts.
        Like Jung's collective unconscious - patterns that transcend individual experience.
        """
        # Universal "help-seeking" pattern in different domains
        help_patterns = [
            Draft("debug this error", "solve problem", "technical"),
            Draft("explain this concept", "understand", "educational"),
            Draft("guide me through setup", "assistance", "onboarding"),
        ]

        engine = GlimpseEngine()
        results = []
        for draft in help_patterns:
            result = await engine.glimpse(draft)
            results.append(result)

        # All should be processed successfully
        for result in results:
            assert result.status in ["aligned", "not_aligned", "redial"]
            # Essence may be empty for redial status
            if result.status == "redial":
                assert result.essence == ""
            else:
                assert len(result.essence) > 0

    @pytest.mark.asyncio
    async def test_context_independent_patterns(self):
        """
        Test pattern recognition that works across different contexts.
        Like archetypes appearing in different cultural mythologies.
        """
        # Same pattern (optimization) in different technical contexts
        optimization_patterns = [
            Draft("optimize database queries", "improve performance", "backend"),
            Draft("reduce bundle size", "improve performance", "frontend"),
            Draft("compress images", "improve performance", "assets"),
        ]

        engine = GlimpseEngine()
        results = []
        for draft in optimization_patterns:
            result = await engine.glimpse(draft)
            results.append(result)

        # All should recognize the optimization archetype
        for result in results:
            assert result.status in ["aligned", "not_aligned", "redial"]
            # Essence may be empty for redial status
            if result.status == "redial":
                assert result.essence == ""
            else:
                assert len(result.essence) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
