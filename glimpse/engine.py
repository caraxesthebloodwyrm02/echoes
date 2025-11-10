"""Glimpse Engine - Core orchestration for the two-try glimpse flow.

This module provides the core GlimpseEngine class that orchestrates the glimpse workflow,
including latency monitoring, privacy guards, and status management for AI-assisted coding.
"""

from __future__ import annotations

import asyncio
import os
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import Literal

# Import optional performance and clarifier modules
try:
    from .performance_optimizer import PerformanceOptimizer

    PERFORMANCE_AVAILABLE = True
except ImportError:
    PERFORMANCE_AVAILABLE = False

try:
    from .clarifier_engine import ClarifierEngine, enhanced_sampler_with_clarifiers

    CLARIFIER_AVAILABLE = True
except ImportError:
    CLARIFIER_AVAILABLE = False

# Status strings per UX contract
STATUS_TRYING_1 = "Glimpse 1…"
STATUS_TRYING_2 = "Glimpse 2…"
STATUS_ALIGNED = "Aligned. Ready to commit."
STATUS_NOT_ALIGNED = "Not aligned yet. One adjustment suggested."
STATUS_REDIAL = "Clean reset. Same channel. Let's try again."
STATUS_STALE = "Stale result (won't count). Re‑glimpse?"
STATUS_DEGRADED = "Still trying… network appears slow."


@dataclass
class Draft:
    """Draft input Glimpse: input text plus 1–2 anchors (goal, constraints)."""

    input_text: str
    goal: str
    constraints: str = ""


@dataclass
class GlimpseResult:
    """Minimal structured result for a glimpse."""

    sample: str
    essence: str
    delta: str | None = None
    status: Literal["aligned", "not_aligned", "redial", "stale", "error"] = "aligned"
    attempt: int = 1
    status_history: list[str] = field(default_factory=list)
    stale: bool = False


# Sampler type alias
Sampler = Callable[[Draft], Awaitable[tuple[str, str, str | None, bool]]]

# Default sampler: use OpenAI if available and enabled; otherwise fall back to local default
USE_OPENAI_DEFAULT = os.getenv("GLIMPSE_USE_OPENAI", "true").lower() in {
    "true",
    "1",
    "yes",
}
# Gate legacy pre-execution clarifier (default: off)
PREEXEC_CLARIFIER_ENABLED = os.getenv("GLIMPSE_PREEXEC_CLARIFIER", "false").lower() in {
    "true",
    "1",
    "yes",
}


async def default_sampler(draft: Draft) -> tuple[str, str, str | None, bool]:
    """A simple, dependency-free sampler.

    Returns (sample, essence, delta, aligned)
    """
    await asyncio.sleep(0.15)
    text = draft.input_text.strip().replace("\n", " ")
    sample = (text[:90] + ("…" if len(text) > 90 else "")) or "(no content)"
    intent_text = draft.goal.strip()
    constraints_text = draft.constraints.strip() or "none"
    essence = f"Intent: {intent_text or '(unspecified)'}; constraints: {constraints_text}; tone: neutral."
    delta: str | None = None

    lower = (draft.input_text + " " + draft.goal + " " + draft.constraints).lower()
    if "refactor" in lower and any(x in lower for x in ["no change", "don't change"]):
        delta = "Potential conflict: mentions refactor while requesting no change."

    # Check PREEXEC_CLARIFIER_ENABLED at runtime (not module import time)
    # to support tests that set the env var after import
    preexec_enabled = os.getenv("GLIMPSE_PREEXEC_CLARIFIER", "false").lower() in {
        "true",
        "1",
        "yes",
    }
    if preexec_enabled and not intent_text:
        delta = delta or "Clarifier: Is the audience external (customers)? (Yes/No)"

    aligned = delta is None
    return sample, essence, delta, aligned


# Use OpenAI sampler if available, otherwise use default
if USE_OPENAI_DEFAULT:
    try:
        from .sampler_openai import openai_sampler as default_sampler
    except ImportError:
        pass


class LatencyMonitor:
    """Soft-threshold latency monitor with transparent status updates."""

    def __init__(
        self, t1: int = 1500, t2: int = 2500, t3: int = 4000, t4: int = 6000
    ) -> None:
        # Default thresholds are milliseconds and tuned for OpenAI API performance
        # Based on observed p50~1.4s, p75~2.5s, p95~4s, p99+~6s
        self.t1, self.t2, self.t3, self.t4 = t1, t2, t3, t4
        self._start_ms: int | None = None

    def start(self) -> None:
        """Start the latency timer."""
        self._start_ms = self._now_ms()

    def elapsed_ms(self) -> int:
        """Return elapsed time in milliseconds since start() was called."""
        if self._start_ms is None:
            return 0
        return self._now_ms() - self._start_ms

    def statuses_for_elapsed(self, attempt: int) -> list[str]:
        """Return the list of statuses appropriate for the current elapsed time."""
        e = self.elapsed_ms()
        out: list[str] = []
        if e >= self.t1:
            out.append(STATUS_TRYING_2 if attempt == 2 else STATUS_TRYING_1)
        if e >= self.t2:
            out.append("Making sure it matches your intent…")
        if e >= self.t3:
            out.append(
                "Options: Keep waiting • Redial (no try) • Essence‑only • Commit (confirm)"
            )
        if e >= self.t4:
            out.append(STATUS_DEGRADED)
        return out

    def mark_stale(self) -> bool:
        """Whether a result arriving now should be marked stale."""
        return self.elapsed_ms() >= self.t4

    @staticmethod
    def _now_ms() -> int:
        return int(time.time() * 1000)


class PrivacyGuard:
    """Ensures ephemeral behavior: no logging or side effects until commit."""

    def __init__(self, on_commit: Callable[[Draft], None] | None = None) -> None:
        # Store the provided handler (or None) and track commit state
        self._on_commit = on_commit if callable(on_commit) else None
        self.committed = False

    def commit(self, draft: Draft) -> None:
        """Execute the commit callback with the given draft."""
        try:
            if self._on_commit:
                self._on_commit(draft)
        except Exception:
            # Do not allow commit handler exceptions to propagate
            pass
        finally:
            # Mark as committed in all cases
            self.committed = True


class GlimpseEngine:
    """Orchestrates the two-try glimpse flow with latency transparency."""

    def __init__(
        self,
        sampler: Sampler = None,
        latency_monitor: LatencyMonitor | None = None,
        privacy_guard: PrivacyGuard | None = None,
        debounce_ms: int = 300,
        essence_only: bool = False,
        enable_performance: bool = True,
        enable_clarifiers: bool = True,
    ) -> None:
        """Initialize the GlimpseEngine with optional components.

        Args:
            sampler: Custom sampler function, uses default if None
            latency_monitor: Custom latency monitor, creates default if None
            privacy_guard: Custom privacy guard, creates default if None
            debounce_ms: Milliseconds to wait after cancellation
            essence_only: Whether to return only essence, no sample
            enable_performance: Whether to enable performance optimizer
            enable_clarifiers: Whether to enable clarifier engine
        """
        self._latency = latency_monitor or LatencyMonitor()
        self._privacy = privacy_guard or PrivacyGuard()
        self._debounce_ms = debounce_ms
        self._tries = 0
        self._cancel_requested = False
        self._essence_only = essence_only

        self._performance_optimizer = (
            PerformanceOptimizer()
            if enable_performance and PERFORMANCE_AVAILABLE
            else None
        )
        self._clarifier_engine = (
            ClarifierEngine() if enable_clarifiers and CLARIFIER_AVAILABLE else None
        )

        if sampler is not None:
            self._sampler = sampler
        else:
            # Check PREEXEC_CLARIFIER_ENABLED at runtime (not module import time)
            # to support tests that set the env var after import
            preexec_enabled = os.getenv("GLIMPSE_PREEXEC_CLARIFIER", "false").lower() in {
                "true",
                "1",
                "yes",
            }
            if preexec_enabled:
                # When pre-execution clarifier is enabled via env var, use default_sampler
                # which checks for empty goals and returns clarifiers
                self._sampler = default_sampler
            elif enable_clarifiers and CLARIFIER_AVAILABLE:
                self._sampler = lambda draft: enhanced_sampler_with_clarifiers(
                    draft, self._clarifier_engine
                )
            else:
                self._sampler = default_sampler

    def reset(self) -> None:
        self._tries = 0
        self._cancel_requested = False

    def cancel(self) -> None:
        """Cancel the in-flight glimpse (e.g., user edits). Does not consume a try."""
        self._cancel_requested = True

    async def glimpse(self, draft: Draft) -> GlimpseResult:
        if self._tries >= 2:
            return GlimpseResult(
                sample="",
                essence="",
                status="redial",
                attempt=2,
                status_history=[STATUS_REDIAL],
            )

        self._tries += 1
        attempt = self._tries
        self._cancel_requested = False

        self._latency.start()
        status_history: list[str] = []

        try:
            sampler_task = asyncio.create_task(self._sampler(draft))

            while not sampler_task.done():
                if self._cancel_requested:
                    sampler_task.cancel()
                    await asyncio.sleep(self._debounce_ms / 1000.0)
                    self._tries -= 1
                    return GlimpseResult(
                        sample="",
                        essence="",
                        status="not_aligned",
                        attempt=attempt,
                        status_history=status_history,
                    )

                for s in self._latency.statuses_for_elapsed(attempt):
                    if not status_history or status_history[-1] != s:
                        status_history.append(s)

                await asyncio.sleep(0.05)

            sample, essence, delta, aligned = await sampler_task

            if self._essence_only:
                sample = ""

            is_stale = self._latency.mark_stale()
            final_status = "aligned" if aligned else "not_aligned"

            status_history.append(STATUS_ALIGNED if aligned else STATUS_NOT_ALIGNED)
            if is_stale:
                status_history.append(STATUS_STALE)

            return GlimpseResult(
                sample=sample,
                essence=essence,
                delta=delta,
                status=final_status if not is_stale else "stale",
                attempt=attempt,
                status_history=status_history,
                stale=is_stale,
            )
        except asyncio.CancelledError:
            self._tries -= 1
            return GlimpseResult(
                sample="",
                essence="",
                status="not_aligned",
                attempt=attempt,
                status_history=status_history,
            )

    def commit(self, draft: Draft) -> None:
        """Commit the draft (logging/applying begins here). Resets tries."""
        self._privacy.commit(draft)
        self.reset()

    def set_essence_only(self, enabled: bool) -> None:
        """Set whether to return essence-only results."""
        self._essence_only = enabled


async def _demo() -> None:
    engine = GlimpseEngine()
    draft = Draft(
        input_text="Refactor parse_event to handle None safely while keeping response shape unchanged.",
        goal="Safe None handling; preserve return schema.",
        constraints="Don't change the schema; no test updates in this commit.",
    )

    r1 = await engine.glimpse(draft)
    print("Attempt:", r1.attempt)
    print("Status:", r1.status)
    print("History:", r1.status_history)
    print("Sample:", r1.sample)
    print("Essence:", r1.essence)
    print("Delta:", r1.delta)

    if r1.status != "aligned":
        draft.goal += " (function only)"
        r2 = await engine.glimpse(draft)
        print("Attempt:", r2.attempt)
        print("Status:", r2.status)
        print("History:", r2.status_history)
        print("Sample:", r2.sample)
        print("Essence:", r2.essence)
        print("Delta:", r2.delta)

    engine.commit(draft)


if __name__ == "__main__":
    try:
        asyncio.run(_demo())
    except KeyboardInterrupt:
        pass
