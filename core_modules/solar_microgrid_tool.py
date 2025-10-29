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

# Prototype Tool: Solar Microgrid Optimizer
# Models inspiration vector, simulates microgrids, iterates for optimization
# Boosts clean energy trajectory by optimizing storage integration

import numpy as np


class SolarMicrogridTool:
    def __init__(self, panels_kw=5, battery_kwh=10):
        self.panels = panels_kw
        self.battery = battery_kwh

    def simulate(self, days=30):
        solar = np.random.normal(self.panels * 5, 2, days)
        load = np.random.normal(20, 3, days)
        excess = np.maximum(solar - load, 0) * 0.9
        shortfall = np.maximum(load - solar, 0)
        stored = np.minimum(np.cumsum(excess), self.battery)
        net_shortfall = shortfall - stored
        reliability = (np.sum(net_shortfall <= 0) / days) * 100
        return reliability, np.mean(net_shortfall)

    def iterate_optimize(self, iterations=3):
        for i in range(iterations):
            rel, shortfall = self.simulate()
            print(f"Iter {i + 1}: Rel {rel:.1f}%, Shortfall {shortfall:.1f} kWh")
            if rel < 80:
                self.battery += 5
                print("Adjusted: +5kWh battery")


if __name__ == "__main__":
    tool = SolarMicrogridTool()
    tool.iterate_optimize()
    print("Tool Ready: Models solar trajectories, boosts clean energy via optimization.")
