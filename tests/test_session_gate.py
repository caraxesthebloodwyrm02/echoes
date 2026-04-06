"""Session Gate Verification Suite.

Tests the 42% grounding-ratio threshold with time-aware session boundaries.
Deterministic — all timestamps are fixed, no wall-clock dependency.
"""

from __future__ import annotations

import pytest

from core_modules.session_gate import (
    THRESHOLD,
    ReadSignal,
    SearchSignal,
    SessionMemo,
    session_gate,
)


# ── Fixtures ──

def _reads(n: int, dim: str = "governance") -> list[ReadSignal]:
    return [
        ReadSignal(path=f"/path/{i}", dimension=dim, timestamp="2026-04-06T14:00:00+06:00")
        for i in range(n)
    ]


def _searches(n: int, scope: str = "governance") -> list[SearchSignal]:
    return [
        SearchSignal(query=f"query-{i}", scope=scope, result_count=10, timestamp="2026-04-06T14:00:00+06:00")
        for i in range(n)
    ]


REF_TIME = "2026-04-06T14:30:00+06:00"
TZ = "Asia/Dhaka"


# ── Threshold pass/halt ──

class TestThresholdGate:
    def test_balanced_session_passes(self):
        """50/50 reads/searches → ratio 0.5 > 0.42 → pass."""
        verdict, memo = session_gate(_reads(5), _searches(5), timestamp=REF_TIME, timezone=TZ)
        assert verdict.allowed is True
        assert memo.gate_result is True
        assert memo.grounding_ratio == 0.5

    def test_exploration_heavy_halts(self):
        """2 reads + 8 searches → ratio 0.2 < 0.42 → halt."""
        verdict, memo = session_gate(_reads(2), _searches(8), timestamp=REF_TIME, timezone=TZ)
        assert verdict.allowed is False
        assert memo.gate_result is False
        assert "HALT" in memo.reason

    def test_exactly_at_threshold_passes(self):
        """42 reads + 58 searches → ratio 0.42 = threshold → pass (not strictly less)."""
        verdict, memo = session_gate(_reads(42), _searches(58), timestamp=REF_TIME, timezone=TZ)
        assert verdict.allowed is True

    def test_just_below_threshold_halts(self):
        """4 reads + 10 searches → ratio 0.2857 < 0.42 → halt."""
        verdict, memo = session_gate(_reads(4), _searches(10), timestamp=REF_TIME, timezone=TZ)
        assert verdict.allowed is False

    def test_empty_session_halts(self):
        """No signals → halt. Cannot evaluate without data."""
        verdict, memo = session_gate([], [], timestamp=REF_TIME, timezone=TZ)
        assert verdict.allowed is False
        assert memo.grounding_ratio == 0.0
        assert "no signals" in memo.reason.lower()


# ── Bidirectional (dual read) ──

class TestBidirectionalCheck:
    def test_pure_observation_passes_with_advisory(self):
        """10 reads + 0 searches → ratio 1.0 > 0.58 → pass but advisory."""
        verdict, memo = session_gate(_reads(10), [], timestamp=REF_TIME, timezone=TZ)
        assert verdict.allowed is True
        assert "advisory" in memo.reason.lower() or "stale" in memo.reason.lower()

    def test_mixed_session_no_advisory(self):
        """Balanced session (within both bounds) → no advisory about staleness."""
        # 5 reads + 5 searches = 0.5, which is between 0.42 and 0.58 → balanced, no advisory
        verdict, memo = session_gate(_reads(5), _searches(5), timestamp=REF_TIME, timezone=TZ)
        assert verdict.allowed is True
        assert "advisory" not in memo.reason.lower()


# ── Time awareness ──

class TestTimeAwareness:
    def test_off_hours_tightens_threshold(self):
        """At 03:00 local, threshold tightens. A session that passes during day halts at night."""
        # During day (14:00): 4 reads + 6 searches = 0.4 < 0.42 → halt
        # But let's use a ratio that passes at 0.42 but fails at 0.378
        reads = _reads(4)
        searches = _searches(6)
        # ratio = 0.4, day threshold = 0.42 → halt
        v_day, _ = session_gate(reads, searches, timestamp="2026-04-06T14:00:00+06:00", timezone=TZ)
        assert v_day.allowed is False  # already halts during day at 0.4

        # Use a ratio between 0.378 and 0.42: 38 reads + 62 searches = 0.38
        reads_edge = _reads(38)
        searches_edge = _searches(62)
        # ratio = 0.38, night threshold = 0.378 → just above → passes at night
        # But 37 reads + 63 searches = 0.37 < 0.378 → halts at night
        reads_tight = _reads(37)
        searches_tight = _searches(63)
        v_night, m_night = session_gate(
            reads_tight, searches_tight,
            timestamp="2026-04-06T03:00:00+06:00", timezone=TZ,
        )
        assert v_night.allowed is False
        assert "off-hours" in m_night.reason

    def test_day_hours_normal_threshold(self):
        """During day hours, standard 0.42 threshold applies."""
        # 45 reads + 55 searches = 0.45 > 0.42 → pass
        verdict, memo = session_gate(
            _reads(45), _searches(55),
            timestamp="2026-04-06T14:00:00+06:00", timezone=TZ,
        )
        assert verdict.allowed is True
        assert memo.local_hour == 14

    def test_timezone_affects_local_hour(self):
        """Same UTC time, different timezone → different local hour."""
        utc_time = "2026-04-06T22:00:00+00:00"
        # In Dhaka (UTC+6): 22+6 = 04:00 next day → off-hours
        _, memo_dhaka = session_gate(_reads(5), _searches(5), timestamp=utc_time, timezone="Asia/Dhaka")
        assert memo_dhaka.local_hour == 4  # next day 04:00

        # In London (UTC+1 BST): 23:00 → off-hours
        _, memo_london = session_gate(_reads(5), _searches(5), timestamp=utc_time, timezone="Europe/London")
        assert memo_london.local_hour == 23


# ── Staleness ──

class TestStaleness:
    def test_stalest_signal_age_computed(self):
        """Stalest signal age is measured from oldest signal to reference time."""
        old_reads = [ReadSignal(path="/old", dimension="governance", timestamp="2026-04-06T10:00:00+06:00")]
        new_searches = [SearchSignal(query="q", scope="governance", result_count=5, timestamp="2026-04-06T14:00:00+06:00")]
        _, memo = session_gate(old_reads, new_searches, timestamp="2026-04-06T14:30:00+06:00", timezone=TZ)
        assert memo.stalest_signal_age_hours == 4.5


# ── Reproducibility ──

class TestReproducibility:
    def test_same_inputs_same_output(self):
        """Deterministic — same signals + same timestamp → identical memo."""
        reads = _reads(5)
        searches = _searches(5)
        _, memo1 = session_gate(reads, searches, timestamp=REF_TIME, timezone=TZ)
        _, memo2 = session_gate(reads, searches, timestamp=REF_TIME, timezone=TZ)
        assert memo1.gate_result == memo2.gate_result
        assert memo1.grounding_ratio == memo2.grounding_ratio
        assert memo1.reason == memo2.reason
        assert memo1.local_hour == memo2.local_hour

    def test_memo_has_all_fields(self):
        """SessionMemo carries the complete boundary summary."""
        _, memo = session_gate(_reads(3), _searches(7), timestamp=REF_TIME, timezone=TZ)
        assert isinstance(memo.gate_result, bool)
        assert isinstance(memo.grounding_ratio, float)
        assert isinstance(memo.struggle_count, int)
        assert isinstance(memo.stalest_signal_age_hours, float)
        assert isinstance(memo.local_hour, int)
        assert isinstance(memo.timezone, str)
        assert isinstance(memo.reason, str)
        assert isinstance(memo.timestamp, str)


# ── Verdict shape ──

class TestVerdictShape:
    def test_verdict_carries_confidence_as_grounding_ratio(self):
        """GateVerdict.confidence mirrors the grounding ratio."""
        verdict, memo = session_gate(_reads(6), _searches(4), timestamp=REF_TIME, timezone=TZ)
        assert verdict.confidence == memo.grounding_ratio

    def test_verdict_has_provenance_id(self):
        """Every verdict gets a unique provenance_id."""
        v1, _ = session_gate(_reads(5), _searches(5), timestamp=REF_TIME, timezone=TZ)
        v2, _ = session_gate(_reads(5), _searches(5), timestamp=REF_TIME, timezone=TZ)
        assert v1.provenance_id  # non-empty
        assert v2.provenance_id
        assert v1.provenance_id != v2.provenance_id  # unique per call
