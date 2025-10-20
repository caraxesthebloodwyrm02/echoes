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

# Solar AI Improvements Script
# Goal: Build a robust solar microgrid simulation tool that leverages AI for reasoned improvements, integrates real data, and boosts clean energy trajectory.
# Structure: Modular class with AI reasoning, tool selection, data integration, and iterative optimization.

import sys

sys.path.append("e:/Projects/Development")
import json

import numpy as np
import requests

from ai_modules.minicon.config import Config


class SolarAITool:
    def __init__(self):
        self.config = Config.from_env()
        self.client = self.config.openai_client
        self.assets = {
            "gaps": ["intermittency", "storage", "cost", "grid integration"],
            "breakthroughs": [
                "perovskite tandems",
                "AI forecasting",
                "battery advances",
            ],
            "contributors": ["LONGi", "NREL", "OpenAI"],
            "trajectory": "2024-2025 CAGR 6%, AI-driven",
            "mock_data": {
                "Paris, France": 150,
                "New York, USA": 140,
                "Staten Island, New York": 145,
            },
        }

    def get_solar_data(self, location):
        try:
            locations = {
                "Paris, France": (48.8566, 2.3522),
                "New York, USA": (40.7128, -74.0060),
                "Staten Island, New York": (40.5795, -74.1502),
            }
            lat, lon = locations.get(location, (48.8566, 2.3522))
            url = (
                f"https://re.jrc.ec.europa.eu/api/v5_2/PVcalc?lat={lat}&lon={lon}&peakpower=1&loss=14&outputformat=json"
            )
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                monthly = data.get("outputs", {}).get("monthly", {})
                avg_output = sum(monthly.values()) / len(monthly) if monthly else 0
                return f"Solar data in {location}: Avg monthly PV output {avg_output:.2f} kWh"
        except:
            pass
        mock = self.assets["mock_data"].get(location, 150)
        return f"Solar irradiance in {location}: {mock} W/m² (robust mock)"

    def simulate_microgrid(self, location, days=30):
        irradiance = float(self.get_solar_data(location).split(": ")[-1].split(" ")[0])
        solar_gen = np.random.normal(irradiance * 0.01, 2, days)  # Proxy
        load = np.random.normal(20, 3, days)
        excess = np.maximum(solar_gen - load, 0) * 0.9
        shortfall = np.maximum(load - solar_gen, 0)
        stored = np.minimum(np.cumsum(excess), 10)
        net_shortfall = shortfall - stored
        reliability = (np.sum(net_shortfall <= 0) / days) * 100
        return f"Sim for {location}: Reliability {reliability:.1f}%, Avg Shortfall {net_shortfall.mean():.1f} kWh"

    def intelligent_tool_selection(self, query):
        if "suggest" in query.lower() or "improvements" in query.lower():
            return "reason_improvements"
        elif "solar" in query.lower() or "irradiance" in query.lower():
            return "get_solar_data"
        elif "simulate" in query.lower() or "microgrid" in query.lower():
            return "simulate_microgrid"
        else:
            return "reason_improvements"

    def reason_improvements(self, query):
        # Use AI to reason
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_solar_data",
                    "description": "Fetch solar data for improvements.",
                    "parameters": {
                        "type": "object",
                        "properties": {"location": {"type": "string"}},
                        "required": ["location"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "simulate_microgrid",
                    "description": "Run simulation for robustness.",
                    "parameters": {
                        "type": "object",
                        "properties": {"location": {"type": "string"}},
                        "required": ["location"],
                    },
                },
            },
        ]
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": query}],
            tools=tools,
        )
        content = response.choices[0].message.content or ""
        if response.choices[0].message.tool_calls:
            for call in response.choices[0].message.tool_calls:
                func_name = call.function.name
                args = json.loads(call.function.arguments)
                if func_name == "get_solar_data":
                    result = self.get_solar_data(args["location"])
                elif func_name == "simulate_microgrid":
                    result = self.simulate_microgrid(args["location"])
                content += f"\nTool Result ({func_name}): {result}"
        return content

    def run(self, query):
        selected_tool = self.intelligent_tool_selection(query)
        if selected_tool == "get_solar_data":
            location = query.split("in ")[-1] if "in " in query else "Paris, France"
            return self.get_solar_data(location)
        elif selected_tool == "simulate_microgrid":
            location = query.split("for ")[-1] if "for " in query else "Paris, France"
            return self.simulate_microgrid(location)
        else:
            return self.reason_improvements(query)


# Usage
if __name__ == "__main__":
    tool = SolarAITool()
    query = "Suggest improvements for microgrid simulation tools and fetch data for Staten Island, New York."
    result = tool.run(query)
    print("Intelligent Response:")
    print(result)
