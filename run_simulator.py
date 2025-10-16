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

"""
Phase Simulator Runner
Run simulations on phase plans to assess alignment with user vision.
"""

import json
import sys

from automation.simulator import PhaseSimulator


def main():
    if len(sys.argv) != 2:
        print("Usage: python run_simulator.py <phase_plan.json>")
        sys.exit(1)

    plan_file = sys.argv[1]

    try:
        with open(plan_file, "r") as f:
            phase_plan = json.load(f)
    except FileNotFoundError:
        print(f"Error: File {plan_file} not found")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        sys.exit(1)

    simulator = PhaseSimulator()
    result = simulator.simulate_phase(phase_plan)

    print(f"Phase: {result.phase_name}")
    print(f"Alignment Score: {result.alignment_score:.2f}")
    print("Factors:")
    for k, v in result.factors.items():
        print(f"  {k}: {v:.2f}")
    print("Recommendations:")
    for rec in result.recommendations:
        print(f"  - {rec}")
    print("Risks:")
    for risk in result.risks:
        print(f"  - {risk}")


if __name__ == "__main__":
    main()
