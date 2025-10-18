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
Mode Performance Profiler
Profiles execution time for each mode to identify optimization opportunities
"""

import asyncio
import cProfile
import json
import os
import pstats
import sys
import time
from io import StringIO
from typing import Any, Dict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from prompting.system import PromptingSystem


class ModeProfiler:
    """Profile performance of all modes"""

    def __init__(self):
        self.system = PromptingSystem()
        self.results = {}
        self.test_prompts = [
            "Explain machine learning",
            "Create a data processing pipeline",
            "How does recursion work?",
            "Design a scalable system",
            "Optimize database queries",
        ]

    async def profile_mode(self, mode: str, iterations: int = 10) -> Dict[str, Any]:
        """Profile a single mode with multiple iterations"""
        print(f"📊 Profiling {mode} mode ({iterations} iterations)...")

        execution_times = []
        profiler = cProfile.Profile()

        for i, prompt in enumerate(self.test_prompts[:iterations]):
            profiler.enable()
            start = time.perf_counter()

            try:
                await self.system.process_prompt(
                    prompt=prompt, mode=mode, enable_data_loop=False
                )
                duration = time.perf_counter() - start
                execution_times.append(duration)

                print(f"  Iteration {i + 1}: {duration * 1000:.2f}ms")

            except Exception as e:
                print(f"  ❌ Iteration {i + 1} failed: {e}")
                execution_times.append(-1)

            finally:
                profiler.disable()

        # Analyze profiler stats
        s = StringIO()
        stats = pstats.Stats(profiler, stream=s).sort_stats("cumulative")
        stats.print_stats(20)  # Top 20 functions

        # Calculate statistics
        valid_times = [t for t in execution_times if t > 0]
        if valid_times:
            avg_time = sum(valid_times) / len(valid_times)
            min_time = min(valid_times)
            max_time = max(valid_times)
            std_dev = (
                sum((t - avg_time) ** 2 for t in valid_times) / len(valid_times)
            ) ** 0.5
        else:
            avg_time = min_time = max_time = std_dev = 0

        profile_data = {
            "mode": mode,
            "iterations": iterations,
            "execution_times": execution_times,
            "statistics": {
                "average_ms": avg_time * 1000,
                "min_ms": min_time * 1000,
                "max_ms": max_time * 1000,
                "std_dev_ms": std_dev * 1000,
            },
            "hotspots": s.getvalue().split("\n")[:25],  # Top 25 lines
        }

        print(
            f"  ✅ Average: {avg_time * 1000:.2f}ms (min: {min_time * 1000:.2f}ms, max: {max_time * 1000:.2f}ms)"
        )
        return profile_data

    async def profile_all_modes(self) -> Dict[str, Any]:
        """Profile all 5 modes"""
        print("=" * 70)
        print("MODE PERFORMANCE PROFILER")
        print("=" * 70)

        modes = ["concise", "ide", "conversational", "star_stuff", "business"]

        for mode in modes:
            self.results[mode] = await self.profile_mode(mode, iterations=5)
            print()

        return self.results

    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive profiling report"""
        report = {
            "timestamp": time.time(),
            "phase": "Phase 1 Baseline",
            "modes": self.results,
            "summary": {
                "total_modes": len(self.results),
                "average_execution_time_ms": 0,
                "fastest_mode": None,
                "slowest_mode": None,
            },
            "optimization_targets": [],
        }

        # Calculate summary statistics
        mode_averages = {
            mode: data["statistics"]["average_ms"]
            for mode, data in self.results.items()
        }

        if mode_averages:
            report["summary"]["average_execution_time_ms"] = sum(
                mode_averages.values()
            ) / len(mode_averages)
            report["summary"]["fastest_mode"] = min(
                mode_averages, key=mode_averages.get
            )
            report["summary"]["slowest_mode"] = max(
                mode_averages, key=mode_averages.get
            )

        # Identify optimization targets (modes >1000ms average)
        for mode, avg_time in mode_averages.items():
            if avg_time > 1000:
                report["optimization_targets"].append(
                    {
                        "mode": mode,
                        "current_ms": avg_time,
                        "target_ms": avg_time / 2,  # 50% reduction target
                        "priority": "HIGH",
                    }
                )
            elif avg_time > 500:
                report["optimization_targets"].append(
                    {
                        "mode": mode,
                        "current_ms": avg_time,
                        "target_ms": 500,
                        "priority": "MEDIUM",
                    }
                )

        return report

    def save_report(
        self, report: Dict[str, Any], filename: str = "mode_profile_baseline.json"
    ):
        """Save profiling report to file"""
        report_path = os.path.join(
            os.path.dirname(__file__), "..", "automation", "reports", filename
        )

        with open(report_path, "w") as f:
            json.dump(report, f, indent=2, default=str)

        print(f"📄 Report saved to: {report_path}")


async def main():
    """Run profiler and generate report"""
    profiler = ModeProfiler()

    # Profile all modes
    await profiler.profile_all_modes()

    # Generate report
    report = profiler.generate_report()

    print("=" * 70)
    print("PROFILING SUMMARY")
    print("=" * 70)
    print(
        f"Average Execution Time: {report['summary']['average_execution_time_ms']:.2f}ms"
    )
    print(f"Fastest Mode: {report['summary']['fastest_mode']}")
    print(f"Slowest Mode: {report['summary']['slowest_mode']}")

    if report["optimization_targets"]:
        print(f"\n🎯 Optimization Targets: {len(report['optimization_targets'])} modes")
        for target in report["optimization_targets"]:
            print(
                f"  - {target['mode']}: {target['current_ms']:.0f}ms → {target['target_ms']:.0f}ms ({target['priority']})"
            )
    else:
        print("\n✅ All modes performing within targets!")

    # Save report
    profiler.save_report(report)

    print("\n🚀 Profiling complete! Use this baseline to measure Phase 2 improvements.")


if __name__ == "__main__":
    asyncio.run(main())
