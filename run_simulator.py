#!/usr/bin/env python3
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
