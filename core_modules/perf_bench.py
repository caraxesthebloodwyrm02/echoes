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
Simple performance benchmark for key endpoints.
Task name: "Performance Benchmark" -> function: performance_benchmark(context)
"""

from __future__ import annotations

import time
from statistics import mean

from fastapi.testclient import TestClient

from automation.core.logger import AutomationLogger


def _load_app():
    try:
        from app.main import app

        return app
    except Exception:
        import importlib

        mod = importlib.import_module("main")
        return getattr(mod, "app")  # noqa: B009


def _bench(client, method: str, path: str, payload=None, n=10):
    times = []
    for _ in range(n):
        t0 = time.perf_counter()
        if method == "GET":
            client.get(path)
        else:
            client.post(path, json=payload or {})
        times.append(time.perf_counter() - t0)
    return mean(times)


def performance_benchmark(context):
    log = AutomationLogger()
    client = TestClient(_load_app())
    n = int(context.extra_data.get("iterations", 10))
    results = {}
    results["health_get"] = _bench(client, "GET", "/api/health", n=n)
    results["science_search"] = _bench(client, "POST", "/api/science/biomedical/search", {"query": "test"}, n)
    results["finance_personal"] = _bench(
        client,
        "POST",
        "/api/finance/personal/analyze",
        {"financial_data": {"income": 1}, "goals": ["g"], "user_info": {"age": 1}},
        n,
    )

    for k, v in results.items():
        log.info(f"{k}: {v * 1000:.2f} ms (avg over {n})")
    log.info("✅ Performance benchmark complete")
