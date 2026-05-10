"""Shared CLI helpers used by core_modules mixins and assistant_v2_core.

Extracted to break the circular import between directory_analysis_mixin
and assistant_v2_core.  Both modules now import from here instead.
"""

from __future__ import annotations

import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

try:
    import yaml

    _YAML_AVAILABLE = True
except ImportError:
    yaml = None  # type: ignore[assignment]
    _YAML_AVAILABLE = False


# ---------------------------------------------------------------------------
# Status constants
# ---------------------------------------------------------------------------
STATUS_SPINNER = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
STATUS_COMPLETE = "✅"
STATUS_ERROR = "❌"
STATUS_WORKING = "⚙️"
STATUS_SEARCH = "🔍"
STATUS_TOOL = "🔧"
STATUS_RETRY = "↻"


def utc_now_iso_ms() -> str:
    """UTC timestamp with millisecond precision (ISO 8601)."""
    return datetime.now(UTC).isoformat(timespec="milliseconds")


# ---------------------------------------------------------------------------
# EnhancedStatusIndicator
# ---------------------------------------------------------------------------
class EnhancedStatusIndicator:
    def __init__(self, enabled: bool = True) -> None:
        self.enabled = enabled
        self.current_phase: str | None = None
        self.current_step = 0
        self.total_steps = 0
        self.spinner_index = 0
        self.phase_start_time: float | None = None

    def start_phase(self, phase_name: str, total_steps: int = 0) -> None:
        if not self.enabled:
            return
        self.current_phase = phase_name
        self.total_steps = total_steps
        self.current_step = 0
        self.phase_start_time = time.time()
        if total_steps > 0:
            print(f"\n{STATUS_WORKING} {phase_name}")
        else:
            print(f"\n{STATUS_WORKING} {phase_name}...", end="", flush=True)

    def update_step(self, message: str, completed: bool = False) -> None:
        if not self.enabled:
            return

        if completed:
            self.current_step += 1
            icon = STATUS_COMPLETE
            elapsed = f"({(time.time() - self.phase_start_time) * 1000:.0f}ms)" if self.phase_start_time else ""
            if self.total_steps > 0:
                progress = f"[{self.current_step}/{self.total_steps}]"
                print(f"\r{icon} {progress} {message} {elapsed}")
            else:
                print(f"\r{icon} {message} {elapsed}")
        else:
            icon = STATUS_SPINNER[self.spinner_index % len(STATUS_SPINNER)]
            self.spinner_index += 1
            if self.total_steps > 0:
                progress = f"[{self.current_step}/{self.total_steps}]"
                print(f"\r{icon} {progress} {message}", end="", flush=True)
            else:
                print(f"\r{icon} {message}...", end="", flush=True)

    def complete_phase(self, message: str = "Done") -> None:
        if not self.enabled:
            return
        elapsed = f"({(time.time() - self.phase_start_time) * 1000:.0f}ms)" if self.phase_start_time else ""
        print(f"\r{STATUS_COMPLETE} {message} {elapsed}")

    def error(self, message: str) -> None:
        if not self.enabled:
            return
        print(f"\r{STATUS_ERROR} Error: {message}")


# ---------------------------------------------------------------------------
# Prompt loader
# ---------------------------------------------------------------------------
def load_prompt(prompt_name: str) -> str:
    """Load a YAML prompt file from the ``prompts/`` directory."""
    if not _YAML_AVAILABLE:
        print(f"Warning: YAML not available, cannot load prompt {prompt_name}")
        return ""

    prompt_path = Path("prompts") / f"{prompt_name}.yaml"
    try:
        with open(prompt_path, encoding="utf-8") as f:
            data: Any = yaml.safe_load(f)
            if isinstance(data, str):
                return data
            elif isinstance(data, dict) and "prompt" in data:
                return data["prompt"]
            elif isinstance(data, dict) and "directive" in data:
                return data["directive"]
            return str(data)
    except Exception as e:
        print(f"Warning: Could not load prompt {prompt_name}: {e}")
        return ""
