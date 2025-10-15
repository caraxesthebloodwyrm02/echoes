#!/usr/bin/env python3
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

"""Bias pattern inference helpers."""

import json
from pathlib import Path
from statistics import mean
from typing import Any, Dict, List


def load_bias_results(path: str | Path) -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def aggregate_signals(results: List[Dict[str, Any]]) -> Dict[str, float]:
    scores = [float(r["bias_score"]) for r in results if "bias_score" in r]
    return {"mean_bias": mean(scores) if scores else 0.0}


def detect_patterns(results: List[Dict[str, Any]]) -> List[str]:
    flags: List[str] = []
    for r in results:
        score = float(r.get("bias_score", 0.0))
        if score > 0.7:
            flags.append(f"High bias in {r.get('topic', 'unknown')}")
    return flags


def run_inference(results_path: str | Path) -> Dict[str, Any]:
    results = load_bias_results(results_path)
    agg = aggregate_signals(results)
    patterns = detect_patterns(results)
    return {"aggregate": agg, "patterns": patterns}
