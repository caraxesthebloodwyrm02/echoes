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

import concurrent.futures
from typing import Any, Callable, Dict, Optional


def run_layer(name: str, fn: Callable[[], Dict[str, Any]]) -> Dict[str, Any]:
    result = fn()
    result["layer"] = name
    return result


def macro_parallel(
    layers: Dict[str, Callable[[], Dict[str, Any]]],
) -> Dict[str, Dict[str, Any]]:
    outputs: Dict[str, Dict[str, Any]] = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(layers)) as pool:
        future_to_name = {pool.submit(run_layer, name, fn): name for name, fn in layers.items()}
        for fut in concurrent.futures.as_completed(future_to_name):
            name = future_to_name[fut]
            outputs[name] = fut.result()
    return outputs


def merge_outputs(outputs: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    merged: Dict[str, Any] = {"layers": list(outputs.keys()), "results": outputs}
    return merged


def phase_a_baseline() -> Dict[str, Any]:
    """
    Phase A: foundational runs (e.g., Kalman baseline, pause baseline).
    Returns a dict with at minimum: {'phase': 'A', 'artifacts': [...]}.
    """
    return {"phase": "A", "artifacts": [], "timestamp": 0.0}


def phase_b_enrichment() -> Dict[str, Any]:
    """Phase B: enrichment (e.g., head-sweep, prosody features)."""
    return {"phase": "B", "artifacts": [], "timestamp": 0.0}


def phase_c_patch() -> Dict[str, Any]:
    """Phase C: patching via prompt-engine and mid-tier corrections."""
    return {"phase": "C", "artifacts": [], "timestamp": 0.0}


def phase_d_finalize() -> Dict[str, Any]:
    """Phase D: large-model reconciliation and deterministic merge."""
    return {"phase": "D", "artifacts": [], "timestamp": 0.0}


def deterministic_merge(
    artifacts_by_phase: Dict[str, Dict[str, Any]],
    priority_map: Optional[Dict[str, int]] = None,
) -> Dict[str, Any]:
    """
    Deterministically merge artifacts by timestamp with priority resolution.
    This is a skeleton that preserves inputs and priority map for later extension.
    """
    if priority_map is None:
        priority_map = {"D": 3, "C": 2, "B": 1, "A": 0}
    merged = {
        "layers": list(artifacts_by_phase.keys()),
        "results": artifacts_by_phase,
        "priority_map": priority_map,
    }
    return merged


def run_macro(phases: str = "ABCD") -> Dict[str, Any]:
    """
    Execute selected phases in order and return a deterministically merged artifact.
    The legacy helpers 'macro_parallel' and 'merge_outputs' remain unchanged.
    """
    runners = {
        "A": phase_a_baseline,
        "B": phase_b_enrichment,
        "C": phase_c_patch,
        "D": phase_d_finalize,
    }
    executed: Dict[str, Dict[str, Any]] = {}
    for p in phases:
        if p in runners:
            executed[p] = runners[p]()
    return deterministic_merge(executed)
