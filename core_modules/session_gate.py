"""
Session Gate: grounding-ratio threshold with time-aware session boundaries.

Sibling to governance_gates.check() — this gate operates per-session, not per-operation.
governance_gates.check() authorizes individual actions (consent + values).
session_gate() evaluates session health (observation density + temporal freshness).

Three constraints encoded in the 0.42 threshold:
  1. Doesn't transport densely — lightweight signal counts, no payloads
  2. Restricts read from search — separates observation from exploration
  3. Time-aware — timezone-sensitive, tightens during off-hours

No async. No heavy deps. Synchronous, deterministic, reproducible.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import uuid4
from zoneinfo import ZoneInfo

from core_modules.governance_gates import GateVerdict

# ── Constants ──

THRESHOLD = 0.42
OFF_HOURS_TIGHTENING = 0.10
DAY_START = 8
DAY_END = 22


# ── Signal types ──

@dataclass(frozen=True)
class ReadSignal:
    """Observation event — passive data acquisition."""
    path: str
    dimension: str
    timestamp: str


@dataclass(frozen=True)
class SearchSignal:
    """Exploration event — active pattern scan."""
    query: str
    scope: str
    result_count: int
    timestamp: str


# ── Session memo ──

@dataclass
class SessionMemo:
    """Reproducible session boundary summary. Same shape for intro and exit."""
    gate_result: bool
    grounding_ratio: float
    struggle_count: int
    stalest_signal_age_hours: float
    local_hour: int
    timezone: str
    reason: str
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


# ── Gate function ──

def session_gate(
    reads: list[ReadSignal],
    searches: list[SearchSignal],
    timestamp: str | None = None,
    timezone: str = "Asia/Dhaka",
) -> tuple[GateVerdict, SessionMemo]:
    """Evaluate session grounding health.

    Returns (GateVerdict, SessionMemo). The verdict is pass/halt boolean.
    The memo is the reproducible summary for both intro and exit.

    Args:
        reads: Observation signals (file reads, directory listings).
        searches: Exploration signals (regex, glob, text search).
        timestamp: Reference time (ISO 8601). Defaults to now.
        timezone: IANA timezone for local hour computation.

    Returns:
        Tuple of (GateVerdict, SessionMemo).
    """
    now = datetime.fromisoformat(timestamp) if timestamp else datetime.now(UTC)
    if now.tzinfo is None:
        now = now.replace(tzinfo=UTC)

    tz = ZoneInfo(timezone)
    local_now = now.astimezone(tz)
    local_hour = local_now.hour

    # ── Grounding ratio: reads / total ──
    total = len(reads) + len(searches)
    if total == 0:
        return _empty_session(local_hour, timezone, now)

    grounding_ratio = len(reads) / total

    # ── Time-aware threshold ──
    effective_threshold = THRESHOLD
    off_hours = local_hour < DAY_START or local_hour >= DAY_END
    if off_hours:
        effective_threshold = THRESHOLD * (1 - OFF_HOURS_TIGHTENING)

    # ── Staleness ──
    all_timestamps = [_parse_ts(r.timestamp) for r in reads] + [_parse_ts(s.timestamp) for s in searches]
    oldest = min(all_timestamps)
    stalest_age_hours = (now - oldest).total_seconds() / 3600

    # ── Struggle count: signals near the threshold band ──
    struggle_count = sum(
        1 for r in reads
        if r.dimension != "general" and _is_near_threshold(r, reads, searches)
    )

    # ── Dual read: bidirectional check ──
    if grounding_ratio < effective_threshold:
        reason = (
            f"HALT: grounding ratio {grounding_ratio:.3f} < threshold {effective_threshold:.3f} "
            f"({len(reads)} reads / {len(searches)} searches). "
            f"Too much exploration without sufficient observation."
        )
        gate_result = False
    elif grounding_ratio > (1 - effective_threshold):
        reason = (
            f"PASS (advisory): grounding ratio {grounding_ratio:.3f} > {1 - effective_threshold:.3f}. "
            f"Pure observation — scope may be stale without active exploration."
        )
        gate_result = True
    else:
        reason = (
            f"PASS: grounding ratio {grounding_ratio:.3f} within "
            f"[{effective_threshold:.3f}, {1 - effective_threshold:.3f}]. "
            f"Balanced observation/exploration."
        )
        gate_result = True

    if off_hours:
        reason += f" [off-hours: threshold tightened to {effective_threshold:.3f}]"

    memo = SessionMemo(
        gate_result=gate_result,
        grounding_ratio=round(grounding_ratio, 4),
        struggle_count=struggle_count,
        stalest_signal_age_hours=round(stalest_age_hours, 2),
        local_hour=local_hour,
        timezone=timezone,
        reason=reason,
        timestamp=now.isoformat(),
    )

    verdict = GateVerdict(
        allowed=gate_result,
        reason=reason,
        confidence=grounding_ratio,
    )

    return verdict, memo


# ── Helpers ──

def _parse_ts(ts: str) -> datetime:
    dt = datetime.fromisoformat(ts)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt


def _is_near_threshold(
    signal: ReadSignal,
    reads: list[ReadSignal],
    searches: list[SearchSignal],
) -> bool:
    """Check if a signal's dimension is in the struggle band (near 0.42 ratio)."""
    dim_reads = sum(1 for r in reads if r.dimension == signal.dimension)
    dim_searches = sum(1 for s in searches if s.scope == signal.dimension)
    dim_total = dim_reads + dim_searches
    if dim_total == 0:
        return False
    dim_ratio = dim_reads / dim_total
    return abs(dim_ratio - THRESHOLD) < 0.1


def _empty_session(
    local_hour: int,
    timezone: str,
    now: datetime,
) -> tuple[GateVerdict, SessionMemo]:
    memo = SessionMemo(
        gate_result=False,
        grounding_ratio=0.0,
        struggle_count=0,
        stalest_signal_age_hours=0.0,
        local_hour=local_hour,
        timezone=timezone,
        reason="HALT: no signals. Cannot evaluate grounding without data.",
        timestamp=now.isoformat(),
    )
    verdict = GateVerdict(
        allowed=False,
        reason=memo.reason,
        confidence=0.0,
    )
    return verdict, memo
