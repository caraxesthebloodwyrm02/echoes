# MIT License
#
# Copyright (c) 2024 Echoes Project
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Resonance Governor - patched prototype (macro → middleware → micro)
# Focus: scope risks, gap closure, and robust simulation with logs and validation.

import json
import math
import random
from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class MacroConfig:
    cadence: float = 50.0
    variance: float = 30.0
    smoothing_strength: float = 0.3
    feedback_sensitivity: float = 0.5
    min_smoothing: float = 0.1
    max_smoothing: float = 0.9

    def validate(self) -> List[str]:
        errors = []
        if not (0 <= self.cadence <= 100):
            errors.append(f"cadence {self.cadence} out of range (0–100)")
        if not (0 <= self.variance <= 100):
            errors.append(f"variance {self.variance} out of range (0–100)")
        if not (0.0 < self.smoothing_strength <= 1.0):
            errors.append(f"invalid smoothing_strength {self.smoothing_strength}")
        if not (0.0 <= self.feedback_sensitivity <= 2.0):
            errors.append(f"invalid feedback_sensitivity {self.feedback_sensitivity}")
        return errors


@dataclass
class GovernorState:
    raw_input: float = 50.0
    smoothed_output: float = 50.0
    governor_angle: float = 0.0
    damping_force: float = 0.0


def cadence_to_rate_limit(cadence: float) -> float:
    cadence = max(1e-6, cadence)
    return 1.0 / (cadence / 100.0)


def variance_to_filter_strength(variance: float) -> float:
    s = 1.0 - (variance / 100.0)
    return max(0.1, min(0.9, s))


def apply_ema(new_value: float, old_value: float, alpha: float) -> float:
    return alpha * new_value + (1.0 - alpha) * old_value


def generate_noisy_input(base: float, variance: float, timestep: int, rng: random.Random) -> float:
    noise = (rng.random() - 0.5) * variance * 2.0
    sine = math.sin(timestep * 0.1) * 15.0
    raw = base + noise + sine
    return max(0.0, min(100.0, raw))


def calculate_feedback(error: float, macro: MacroConfig) -> float:
    return error * macro.feedback_sensitivity * 0.01


class ResonanceGovernor:
    def __init__(self, macro: MacroConfig, seed: int = 0):
        errs = macro.validate()
        if errs:
            raise ValueError(f"Invalid MacroConfig: {errs}")
        self.macro = macro
        self.state = GovernorState()
        self.t = 0
        self.history: List[Dict[str, Any]] = []
        self.rng = random.Random(seed)

    def step(self):
        self.t += 1
        raw = generate_noisy_input(self.macro.cadence, self.macro.variance, self.t, self.rng)
        alpha = variance_to_filter_strength(self.macro.variance) * self.macro.smoothing_strength
        alpha = max(1e-6, min(0.999999, alpha))
        smoothed = apply_ema(raw, self.state.smoothed_output, alpha)
        error = raw - self.macro.cadence
        damping = -error * 0.3
        angle = max(-60.0, min(60.0, error))
        if abs(error) > self.macro.variance * 0.7:
            adj = calculate_feedback(error, self.macro)
            new_strength = self.macro.smoothing_strength + adj
            self.macro.smoothing_strength = max(self.macro.min_smoothing, min(self.macro.max_smoothing, new_strength))
        self.state.raw_input = raw
        self.state.smoothed_output = smoothed
        self.state.governor_angle = angle
        self.state.damping_force = damping
        rec = {
            "t": self.t,
            "raw": round(raw, 4),
            "smooth": round(smoothed, 4),
            "alpha": round(alpha, 5),
            "err": round(error, 4),
            "strength": round(self.macro.smoothing_strength, 4),
        }
        self.history.append(rec)
        if len(self.history) > 100:
            self.history = self.history[-100:]
        return rec

    def run(self, steps=200):
        for _ in range(steps):
            self.step()

    def metrics(self) -> Dict[str, float]:
        errors = [abs(r["err"]) for r in self.history[-50:]]
        avg_err = sum(errors) / len(errors)
        # Normalize error by a scale derived from macro variance so the
        # stability index is comparable across parameterizations.
        # Scale accounts for operating cadence: at higher cadence, the same absolute
        # error should count as proportionally larger (harder to stabilize).
        # Using a quadratic cadence factor creates separation between moderate and high cadence.
        cadence_factor = max(1e-6, (self.macro.cadence / 50.0))
        scale = max(1.0, self.macro.variance / (cadence_factor**2))
        norm_err = avg_err / scale
        stability_index = 1.0 / (1.0 + norm_err)
        return {"avg_error": avg_err, "stability_index": round(stability_index, 4)}

    def dump_json(self, path="sketches/output/governor_history.json"):
        with open(path, "w") as f:
            json.dump(self.history, f, indent=2)


if __name__ == "__main__":
    macro = MacroConfig(cadence=50, variance=25, smoothing_strength=0.35, feedback_sensitivity=0.6)
    gov = ResonanceGovernor(macro, seed=42)
    gov.run(250)
    m = gov.metrics()
    gov.dump_json("governor_output.json")
    print("Final stability metrics:", m)
