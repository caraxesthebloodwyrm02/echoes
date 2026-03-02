"""
Tests for glimpse.__init__ module
"""

import pytest

from glimpse import (
    Draft,
    GlimpseEngine,
    GlimpseResult,
    LatencyMonitor,
    PrivacyGuard,
    default_sampler,
)


class TestGlimpseInit:
    """Test the glimpse module imports and initialization"""

    def test_import_main_classes(self):
        """Test that main classes can be imported"""
        from glimpse import (
            Draft,
            GlimpseResult,
            LatencyMonitor,
            PrivacyGuard,
            default_sampler,
        )

        assert GlimpseEngine is not None
        assert Draft is not None
        assert GlimpseResult is not None
        assert LatencyMonitor is not None
        assert PrivacyGuard is not None
        assert default_sampler is not None

    def test_create_draft(self):
        """Test Draft creation"""
        draft = Draft(
            input_text="test input", goal="test goal", constraints="test constraints"
        )

        assert draft.input_text == "test input"
        assert draft.goal == "test goal"
        assert draft.constraints == "test constraints"

    def test_create_draft_empty(self):
        """Test Draft creation with empty values"""
        draft = Draft("", "", "")

        assert draft.input_text == ""
        assert draft.goal == ""
        assert draft.constraints == ""

    def test_create_glimpse_result(self):
        """Test GlimpseResult creation"""
        result = GlimpseResult(
            attempt=1,
            status="aligned",
            sample="test sample",
            essence="test essence",
            delta=None,
            stale=False,
            status_history=["test"],
        )

        assert result.attempt == 1
        assert result.status == "aligned"
        assert result.sample == "test sample"
        assert result.essence == "test essence"
        assert result.delta is None
        assert result.stale == False
        assert result.status_history == ["test"]

    def test_create_latency_monitor(self):
        """Test LatencyMonitor creation with implementation defaults (ms)"""
        monitor = LatencyMonitor()

        assert monitor.t1 == 1500
        assert monitor.t2 == 2500
        assert monitor.t3 == 4000
        assert monitor.t4 == 6000
        assert monitor._start_ms is None

    def test_create_latency_monitor_custom_thresholds(self):
        """Test LatencyMonitor with custom thresholds"""
        monitor = LatencyMonitor(t1=50, t2=150, t3=400, t4=1000)

        assert monitor.t1 == 50
        assert monitor.t2 == 150
        assert monitor.t3 == 400
        assert monitor.t4 == 1000

    def test_create_privacy_guard(self):
        """Test PrivacyGuard creation"""
        guard = PrivacyGuard()

        assert guard.committed == False
        # Uses no-op lambda by default, not None
        assert guard._on_commit is not None

    def test_create_privacy_guard_with_commit_handler(self):
        """Test PrivacyGuard with custom commit handler"""
        committed_drafts = []

        def test_handler(draft):
            committed_drafts.append(draft)

        guard = PrivacyGuard(on_commit=test_handler)

        assert guard.committed == False
        assert guard._on_commit == test_handler

    def test_privacy_guard_commit(self):
        """Test PrivacyGuard commit functionality"""
        committed_drafts = []

        def test_handler(draft):
            committed_drafts.append(draft)

        guard = PrivacyGuard(on_commit=test_handler)
        draft = Draft("test", "goal", "constraints")

        guard.commit(draft)

        assert guard.committed == True
        assert len(committed_drafts) == 1
        assert committed_drafts[0] == draft

    def test_privacy_guard_commit_without_handler(self):
        """Test PrivacyGuard commit without handler"""
        guard = PrivacyGuard()
        draft = Draft("test", "goal", "constraints")

        # Should not raise error (no-op lambda is used)
        guard.commit(draft)

        assert guard.committed == True

    def test_privacy_guard_commit_handler_exception(self):
        """Test PrivacyGuard commit when handler raises exception"""

        def failing_handler(draft):
            raise ValueError("Commit failed")

        guard = PrivacyGuard(on_commit=failing_handler)
        draft = Draft("test", "goal", "constraints")

        # Exception propagates (PrivacyGuard does not catch exceptions)
        # committed is set to True before callback is called
        with pytest.raises(ValueError, match="Commit failed"):
            guard.commit(draft)
        # committed was set before the exception
        assert guard.committed == True


@pytest.mark.asyncio
class TestDefaultSampler:
    """Test the default sampler function"""

    async def test_default_sampler_basic(self):
        """Test default sampler with basic input"""
        draft = Draft(
            input_text="test input", goal="test goal", constraints="test constraints"
        )

        sample, essence, delta, aligned = await default_sampler(draft)

        assert isinstance(sample, str)
        assert isinstance(essence, str)
        assert isinstance(delta, (str, type(None)))
        assert isinstance(aligned, bool)
        assert len(sample) > 0
        assert len(essence) > 0

    async def test_default_sampler_empty_input(self):
        """Test default sampler with empty input"""
        draft = Draft("", "", "")

        sample, essence, delta, aligned = await default_sampler(draft)

        assert sample == "(no content)"
        assert "Intent: (unspecified)" in essence
        assert "constraints: none" in essence

    async def test_default_sampler_long_input(self):
        """Test default sampler with long input"""
        long_text = "x" * 200
        draft = Draft(long_text, "goal", "constraints")

        sample, essence, delta, aligned = await default_sampler(draft)

        assert "…" in sample  # Should truncate long text
        assert len(sample) <= 93  # 90 chars + "..."

    async def test_default_sampler_refactor_conflict(self):
        """Test default sampler detects refactor conflict"""
        draft = Draft(
            input_text="refactor the code",
            goal="improve structure",
            constraints="no change needed",
        )

        sample, essence, delta, aligned = await default_sampler(draft)

        assert delta is not None
        assert "conflict" in delta.lower()
        assert aligned == False

    async def test_default_sampler_clarifier_for_empty_goal(self):
        """Test default sampler adds clarifier for empty goal when env enabled"""
        from unittest.mock import patch

        draft = Draft(input_text="some input", goal="", constraints="")
        # Clarifier for empty goal is gated by PREEXEC_CLARIFIER_ENABLED
        with patch("glimpse.engine.PREEXEC_CLARIFIER_ENABLED", True):
            from glimpse.engine import default_sampler as patched_sampler

            sample, essence, delta, aligned = await patched_sampler(draft)

        assert delta is not None
        assert "Clarifier:" in delta
        assert "audience" in delta.lower()
        assert aligned == False

    async def test_default_sampler_no_conflict(self):
        """Test default sampler with no conflicts"""
        draft = Draft(
            input_text="simple task",
            goal="complete work",
            constraints="normal approach",
        )

        sample, essence, delta, aligned = await default_sampler(draft)

        assert delta is None
        assert aligned == True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
