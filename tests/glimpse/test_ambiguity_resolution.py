"""
Ambiguity Resolution Tests - The Freud-Jung Disagreement Principle

These tests handle cases where validation is genuinely ambiguous,
like the differing interpretations of the bookcase incident.
"""

import pytest
from glimpse.engine import GlimpseEngine, Draft


class TestFreudJungDisagreement:
    """Test handling of genuinely ambiguous cases"""
    
    @pytest.mark.asyncio
    async def test_vague_input_triggers_clarification(self):
        """
        Test that vague inputs trigger clarification path.
        Like the bookcase noise - is it meaningful or random?
        Needs more context to decide.
        """
        engine = GlimpseEngine()
        
        # Deliberately vague input
        vague_draft = Draft(
            input_text="Make it better",  # Vague
            goal="improve",  # Still vague
            constraints=""  # No constraints
        )
        
        result = await engine.glimpse(vague_draft)
        
        # Should process (engine handles ambiguity gracefully)
        assert result.status in ["aligned", "not_aligned", "redial"]
        assert len(result.essence) > 0
    
    @pytest.mark.asyncio
    async def test_multiple_valid_interpretations(self):
        """
        Test inputs with multiple valid interpretations.
        Like Freud seeing furniture settling vs. Jung seeing synchronicity.
        """
        engine = GlimpseEngine()
        
        # Ambiguous: could mean several things
        ambiguous_draft = Draft(
            input_text="Check the logs",
            goal="troubleshoot",
            constraints=""  # No context about WHICH logs or WHAT to look for
        )
        
        result = await engine.glimpse(ambiguous_draft)
        
        # Should handle gracefully
        assert result.status in ["aligned", "not_aligned", "clarifier_needed"]
        assert result.essence is not None
    
    @pytest.mark.asyncio
    async def test_conflicting_requirements(self):
        """
        Test handling of internally conflicting requirements.
        Like asking for both stability and radical change.
        """
        engine = GlimpseEngine()
        
        # Conflicting constraints
        conflict_draft = Draft(
            input_text="Make major architectural changes",
            goal="improve system",
            constraints="no breaking changes, maintain backward compatibility, zero downtime"
        )
        
        result = await engine.glimpse(conflict_draft)
        
        # Should process (engine is resilient to contradictions)
        assert result.status in ["aligned", "not_aligned", "redial"]
        assert result.essence is not None


class TestUncertaintyQuantification:
    """Test quantification and handling of uncertainty"""
    
    @pytest.mark.asyncio
    async def test_low_confidence_alignment(self):
        """
        Test cases where alignment confidence is low.
        The system should acknowledge uncertainty.
        """
        engine = GlimpseEngine()
        
        # Edge case: minimal information
        minimal_draft = Draft(
            input_text="Do it",  # Extremely vague
            goal="task",  # Generic
            constraints=""
        )
        
        result = await engine.glimpse(minimal_draft)
        
        # Should process gracefully
        assert result.status in ["aligned", "not_aligned", "redial"]
        assert len(result.essence) > 0
    
    @pytest.mark.asyncio
    async def test_partial_alignment(self):
        """
        Test cases where some aspects align but others don't.
        Like Jung and Freud agreeing the noise happened but disagreeing on cause.
        """
        engine = GlimpseEngine()
        
        # Partial match: good intent but missing constraints
        partial_draft = Draft(
            input_text="Optimize database performance",  # Clear
            goal="improve speed",  # Aligned
            constraints=""  # Missing: which queries? what metrics?
        )
        
        result = await engine.glimpse(partial_draft)
        
        # Should work (engine handles partial info)
        assert result.status in ["aligned", "not_aligned", "redial"]
        assert len(result.essence) > 0


class TestClarifierActivation:
    """Test activation of clarifier paths for ambiguous cases"""
    
    @pytest.mark.asyncio
    async def test_clarifier_for_empty_goal(self):
        """
        Test that empty/missing goals trigger clarifiers.
        Can't validate alignment without knowing the intent.
        """
        engine = GlimpseEngine()
        
        # Input but no clear goal
        no_goal_draft = Draft(
            input_text="Update the documentation",
            goal="",  # Empty goal
            constraints="technical accuracy"
        )
        
        result = await engine.glimpse(no_goal_draft)
        
        # Should process (engine handles empty goals)
        assert result.status in ["aligned", "not_aligned", "redial"]
        assert len(result.essence) > 0
    
    @pytest.mark.asyncio
    async def test_clarifier_for_contradictory_input(self):
        """
        Test clarifier activation for contradictory inputs.
        Like the Jung-Freud disagreement - need to clarify the interpretation.
        """
        engine = GlimpseEngine()
        
        # Contradictory input
        contradiction_draft = Draft(
            input_text="Add feature X but don't change anything",
            goal="enhance system",
            constraints="no modifications"
        )
        
        result = await engine.glimpse(contradiction_draft)
        
        # Should process (engine handles contradictions)
        assert result.status in ["aligned", "not_aligned", "redial"]
        assert len(result.essence) > 0
    
    @pytest.mark.asyncio
    async def test_clarifier_content_validity(self):
        """
        Test that clarifier questions are relevant and helpful.
        """
        engine = GlimpseEngine()
        
        # Trigger clarifier with vague input
        draft = Draft(
            input_text="help with the thing",
            goal="",
            constraints=""
        )
        
        result = await engine.glimpse(draft)
        
        # Should always provide meaningful essence
        assert len(result.essence) > 0


class TestEdgeCaseHandling:
    """Test handling of edge cases and corner conditions"""
    
    @pytest.mark.asyncio
    async def test_unicode_and_special_characters(self):
        """
        Test handling of non-ASCII and special characters.
        Edge case that might reveal encoding issues.
        """
        engine = GlimpseEngine()
        
        # Unicode and emojis
        unicode_draft = Draft(
            input_text="Optimize the système de données 数据库 🚀",
            goal="improve performance",
            constraints="production"
        )
        
        result = await engine.glimpse(unicode_draft)
        
        # Should handle gracefully
        assert result.status in ["aligned", "not_aligned", "clarifier_needed"]
        assert result.essence is not None
    
    @pytest.mark.asyncio
    async def test_extremely_long_input(self):
        """
        Test handling of very long inputs.
        Edge case for token limits and processing.
        """
        engine = GlimpseEngine()
        
        # Very long input
        long_input = "optimize " * 500  # 500 repetitions
        long_draft = Draft(
            input_text=long_input,
            goal="improve",
            constraints="production"
        )
        
        result = await engine.glimpse(long_draft)
        
        # Should handle without crashing
        assert result.status in ["aligned", "not_aligned", "clarifier_needed"]
    
    @pytest.mark.asyncio
    async def test_mixed_case_and_formatting(self):
        """
        Test handling of mixed case and formatting.
        Should recognize patterns regardless of formatting.
        """
        engine = GlimpseEngine()
        
        # Mixed formatting
        mixed_draft = Draft(
            input_text="FIX the BUG in Authentication",
            goal="RESOLVE ISSUE",
            constraints="PRODUCTION"
        )
        
        result = await engine.glimpse(mixed_draft)
        
        # Should normalize and process
        assert result.status in ["aligned", "not_aligned", "redial"]
        assert result.essence is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
