# app/harmony/swing_scheduler.py
"""
Swing Scheduler for LLM Sampling Controls
Translates rhythmic quantization (32-step loops, swing, odd-time) to per-token parameters.
"""

import math
from typing import Dict, Tuple
import yaml
from pathlib import Path

# Load configs
CONFIG_DIR = Path(__file__).parent.parent.parent / "configs" / "ai"
SWING_CONFIG = yaml.safe_load((CONFIG_DIR / "llm_swing_profiles.yaml").read_text())
USER_CONFIG = yaml.safe_load((CONFIG_DIR / "user_profiles.yaml").read_text())

GRID = "grid"
ODD = "odd"
PRECISION_LEVELS = ["Q4", "Q8", "Q16", "F16"]


class SamplerState:
    """Tracks current state for swing quantization sampling."""

    def __init__(
        self,
        profile: str = "swing_default",
        initial_precision: str = "Q8",
        initial_mode: str = GRID,
    ):
        self.profile = profile
        self.precision = initial_precision
        self.mode = initial_mode
        self.direction = "forward"  # or "backward"
        self.re_q_until = -1  # token index to stop re-quantizing
        self.downshift_until = -1  # token index to stop downshift
        self.config = SWING_CONFIG["profiles"][profile]

    def _get_base_params(self) -> Dict[str, float]:
        """Get base parameters from config."""
        base = self.config["base"]
        return {
            "temperature": base["temperature"],
            "top_p": base["top_p"],
            "repetition_penalty": base["repetition_penalty"],
            "frequency_penalty": base["frequency_penalty"],
        }

    def _get_mode_params(self) -> Dict[str, Tuple[float, float]]:
        """Get precision mode parameter ranges."""
        return self.config["precision_modes"][f"{self.precision}_{self.mode}"]

    def _apply_swing(self, params: Dict[str, float], t: int) -> Dict[str, float]:
        """Apply 4-beat swing jitter."""
        swing_config = self.config["swing"]
        cycle = swing_config["melody_cycle"]
        delta_t = swing_config["delta_temperature"]
        delta_p = swing_config["delta_top_p"]

        if (t % cycle) < (cycle // 2):  # First half: loosen
            params["temperature"] += delta_t
            params["top_p"] += delta_p
        else:  # Second half: tighten
            params["temperature"] -= delta_t
            params["top_p"] -= delta_p

        return params

    def _apply_variation(self, params: Dict[str, float], t: int) -> Dict[str, float]:
        """Apply 6-cycle variation for syncopation."""
        variation_config = self.config["variation"]
        cycle = variation_config["cycle"]
        delta_t = variation_config["delta_temperature"]

        params["temperature"] += delta_t * math.sin(2 * math.pi * ((t % cycle) / cycle))
        return params

    def _apply_downshift(self, params: Dict[str, float], t: int) -> Dict[str, float]:
        """Apply brief loosen/tighten after flip."""
        if t < self.downshift_until:
            if self.mode == ODD:
                params["temperature"] += 0.05
                params["top_p"] += 0.02
            else:
                params["temperature"] -= 0.05
                params["top_p"] -= 0.02
        return params

    def _apply_re_quantize(self, params: Dict[str, float], t: int) -> Dict[str, float]:
        """Re-quantize to 1/16 tightness after oddtime."""
        if t < self.re_q_until:
            tightness = self.config["flip_rules"]["re_quantize_tightness"]
            params["top_p"] = min(params["top_p"], tightness + 0.05)
            params["temperature"] = max(min(params["temperature"], 0.70), 0.60)
        return params

    def _clamp_params(self, params: Dict[str, float]) -> Dict[str, float]:
        """Clamp parameters to safe ranges."""
        params["temperature"] = max(0.2, min(params["temperature"], 1.2))
        params["top_p"] = max(0.5, min(params["top_p"], 0.98))
        params["repetition_penalty"] = max(1.0, min(params["repetition_penalty"], 1.5))
        params["frequency_penalty"] = max(0.0, min(params["frequency_penalty"], 0.5))
        return params

    def next_params(self, token_idx: int, event: bool = False) -> Dict[str, float]:
        """
        Compute sampling parameters for the next token.
        event: True if a boundary (e.g., ".") triggers a flip.
        """
        # Handle flip event
        if event:
            self.mode = GRID if self.mode == ODD else ODD
            idx = PRECISION_LEVELS.index(self.precision)
            if self.direction == "forward":
                idx = min(idx + 1, len(PRECISION_LEVELS) - 1)
            else:
                idx = max(idx - 1, 0)
            self.precision = PRECISION_LEVELS[idx]
            self.downshift_until = token_idx + self.config["flip_rules"]["downshift_duration"]
            if self.mode == GRID:
                self.re_q_until = token_idx + 12  # Re-quantize for ~12 tokens

        # Start with base or mode params
        params = self._get_base_params()
        mode_params = self._get_mode_params()
        # Use midpoints of ranges
        params["temperature"] = sum(mode_params["temperature"]) / 2
        params["top_p"] = sum(mode_params["top_p"]) / 2
        params["repetition_penalty"] = sum(mode_params["repetition_penalty"]) / 2
        params["frequency_penalty"] = sum(mode_params["frequency_penalty"]) / 2

        # Apply rhythmic modifiers
        params = self._apply_swing(params, token_idx)
        params = self._apply_variation(params, token_idx)
        params = self._apply_downshift(params, token_idx)
        params = self._apply_re_quantize(params, token_idx)
        params = self._clamp_params(params)

        return params
