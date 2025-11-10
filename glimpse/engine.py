from __future__ import annotations

import asyncio
import os
import time
from dataclasses import dataclass, field
from typing import Callable, Optional, Literal, Awaitable, List, Any
from enum import Enum

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
STATUS_REDIAL = "Clean reset. Same channel. Let’s try again."
STATUS_STALE = "Stale result (won’t count). Re‑glimpse?"
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
    delta: Optional[str] = None
    status: Literal["aligned", "not_aligned", "redial", "stale", "error"] = "aligned"
    attempt: int = 1
    status_history: List[str] = field(default_factory=list)
    stale: bool = False


# Sampler type alias
Sampler = Callable[[Draft], Awaitable[tuple[str, str, Optional[str], bool]]]

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
if USE_OPENAI_DEFAULT:
    try:
        from .sampler_openai import openai_sampler as default_sampler
    except Exception:
        # If OpenAI sampler fails to import, fall back to the built-in default
        async def default_sampler(draft: Draft) -> tuple[str, str, Optional[str], bool]:
            """A simple, dependency-free sampler.

            Returns (sample, essence, delta, aligned)
            """
            # Simulate lightweight processing latency (~120–250 ms)
            await asyncio.sleep(0.15)
            text = draft.input_text.strip().replace("\n", " ")
            sample = (text[:90] + ("…" if len(text) > 90 else "")) or "(no content)"
            intent_text = draft.goal.strip()
            constraints_text = draft.constraints.strip() or "none"
            essence = f"Intent: {intent_text or '(unspecified)'}; constraints: {constraints_text}; tone: neutral."
            delta: Optional[str] = None

            # Naive mismatch heuristic: if constraints mention 'no change' but input suggests 'refactor'
            lower = (
                draft.input_text + " " + draft.goal + " " + draft.constraints
            ).lower()
            if "refactor" in lower and (
                "no change" in lower
                or "don’t change" in lower
                or "don't change" in lower
            ):
                delta = (
                    "Potential conflict: mentions refactor while requesting no change."
                )

            # Clarifier path (legacy): only if explicitly enabled via env flag
            if PREEXEC_CLARIFIER_ENABLED and not intent_text:
                delta = (
                    delta or "Clarifier: Is the audience external (customers)? (Yes/No)"
                )

            aligned = delta is None
            return sample, essence, delta, aligned

else:

    async def default_sampler(draft: Draft) -> tuple[str, str, Optional[str], bool]:
        """A simple, dependency-free sampler.

        Returns (sample, essence, delta, aligned)
        """
        # Simulate lightweight processing latency (~120–250 ms)
        await asyncio.sleep(0.15)
        text = draft.input_text.strip().replace("\n", " ")
        sample = (text[:90] + ("…" if len(text) > 90 else "")) or "(no content)"
        intent_text = draft.goal.strip()
        constraints_text = draft.constraints.strip() or "none"
        essence = f"Intent: {intent_text or '(unspecified)'}; constraints: {constraints_text}; tone: neutral."
        delta: Optional[str] = None

        # Naive mismatch heuristic: if constraints mention 'no change' but input suggests 'refactor'
        lower = (draft.input_text + " " + draft.goal + " " + draft.constraints).lower()
        if "refactor" in lower and (
            "no change" in lower or "don’t change" in lower or "don't change" in lower
        ):
            delta = "Potential conflict: mentions refactor while requesting no change."

        # Clarifier path (legacy): only if explicitly enabled via env flag
        if PREEXEC_CLARIFIER_ENABLED and not intent_text:
            delta = delta or "Clarifier: Is the audience external (customers)? (Yes/No)"

        aligned = delta is None
        return sample, essence, delta, aligned


# Status strings per UX contract
STATUS_TRYING_1 = "Glimpse 1…"
STATUS_TRYING_2 = "Glimpse 2…"
STATUS_ALIGNED = "Aligned. Ready to commit."
STATUS_NOT_ALIGNED = "Not aligned yet. One adjustment suggested."
STATUS_REDIAL = "Clean reset. Same channel. Let’s try again."
STATUS_STALE = "Stale result (won’t count). Re‑glimpse?"
STATUS_DEGRADED = "Still trying… network appears slow."


class LatencyMonitor:
    """Soft-threshold latency monitor with transparent status updates.

    Thresholds (ms) – calibrated for real OpenAI API latency:
      - 1500: show trying message
      - 2500: add intent-matching message
      - 4000: patience hinge (user choices in UI layer)
      - 6000: degraded notice
    """

    def __init__(
        self, t1: int = 1500, t2: int = 2500, t3: int = 4000, t4: int = 6000
    ) -> None:
        self.t1, self.t2, self.t3, self.t4 = t1, t2, t3, t4
        self._start_ms: Optional[int] = None

    def start(self) -> None:
        self._start_ms = self._now_ms()

    def elapsed_ms(self) -> int:
        if self._start_ms is None:
            return 0
        return self._now_ms() - self._start_ms

    def statuses_for_elapsed(self, attempt: int) -> List[str]:
        """Return the list of statuses appropriate for the current elapsed time."""
        e = self.elapsed_ms()
        out: List[str] = []
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

    def __init__(
        self, on_commit: Optional[Callable[[GlimpseResult], None]] = None
    ) -> None:
        # Use no-op if caller does not supply a callable
        self._on_commit = on_commit if callable(on_commit) else lambda _draft: None

    def commit(self, result: GlimpseResult) -> None:
        """Execute commit callback (if any) when a result is finalized."""
        self._on_commit(result)


class GlimpseEngine:
    """Orchestrates the two-try glimpse flow with latency transparency."""

    def __init__(
        self,
        sampler: Sampler = None,
        latency_monitor: Optional[LatencyMonitor] = None,
        privacy_guard: Optional[PrivacyGuard] = None,
        debounce_ms: int = 300,
        essence_only: bool = False,
        enable_performance: bool = True,
        enable_clarifiers: bool = True,
    ) -> None:
        self._latency = latency_monitor or LatencyMonitor()
        self._privacy = privacy_guard or PrivacyGuard()
        self._debounce_ms = debounce_ms
        self._tries = 0
        self._cancel_requested = False
        self._essence_only = essence_only

        # Initialize performance optimizer if available and enabled
        self._performance_optimizer = None
        if enable_performance and PERFORMANCE_AVAILABLE:
            self._performance_optimizer = PerformanceOptimizer()

        # Initialize clarifier Glimpse if available and enabled
        self._clarifier_engine = None
        if enable_clarifiers and CLARIFIER_AVAILABLE:
            self._clarifier_engine = ClarifierEngine()

        # Use enhanced sampler if clarifiers are enabled, otherwise use default
        if sampler is None:
            if enable_clarifiers and CLARIFIER_AVAILABLE:
                # Create a wrapper that uses this instance's clarifier engine
                async def _wrapped_sampler(draft):
                    return await enhanced_sampler_with_clarifiers(
                        draft, self._clarifier_engine
                    )

                self._sampler = _wrapped_sampler
            else:
                self._sampler = default_sampler
        else:
            self._sampler = sampler

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
        status_history: List[str] = []

        # Kick off sampler concurrently
        sampler_task = asyncio.create_task(self._sampler(draft))

        # Poll for latency-based statuses until sampler finishes or canceled
        try:
            while not sampler_task.done():
                if self._cancel_requested:
                    sampler_task.cancel()
                    # Debounce before allowing a new glimpse start
                    await asyncio.sleep(self._debounce_ms / 1000.0)
                    # Do not count this as a try
                    self._tries -= 1
                    return GlimpseResult(
                        sample="",
                        essence="",
                        status="not_aligned",
                        attempt=attempt,
                        status_history=status_history,
                    )

                # Update status history idempotently
                for s in self._latency.statuses_for_elapsed(attempt):
                    if not status_history or status_history[-1] != s:
                        status_history.append(s)

                await asyncio.sleep(0.05)  # 50 ms tick

            # Gather result
            sample, essence, delta, aligned = await sampler_task
            # Apply essence-only mode (user-chosen; never auto-applied)
            if self._essence_only:
                sample = ""
            is_stale = self._latency.mark_stale()
            final_status = "aligned" if aligned else "not_aligned"

            # Map to user-facing summary message in status history
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
            # Surface as a benign cancellation (no try consumed)
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

    # Public toggle for essence-only mode
    def set_essence_only(self, enabled: bool) -> None:
        self._essence_only = enabled


# Tiny demo for local testing (run: python -m glimpse.Glimpse)
async def _demo() -> None:
    engine = GlimpseEngine()
    draft = Draft(
        input_text="Refactor parse_event to handle None safely while keeping response shape unchanged.",
        goal="Safe None handling; preserve return schema.",
        constraints="Don’t change the schema; no test updates in this commit.",
    )

    r1 = await Glimpse.glimpse(draft)
    print("Attempt:", r1.attempt)
    print("Status:", r1.status)
    print("History:", r1.status_history)
    print("Sample:", r1.sample)
    print("Essence:", r1.essence)
    print("Delta:", r1.delta)

    if r1.status != "aligned":
        # Adjust once (example)
        draft.goal += " (function only)"
        r2 = await Glimpse.glimpse(draft)
        print("Attempt:", r2.attempt)
        print("Status:", r2.status)
        print("History:", r2.status_history)

    # Commit (for demo)
    Glimpse.commit(draft)


if __name__ == "__main__":
    try:
        asyncio.run(_demo())
    except KeyboardInterrupt:
        pass
