"""
Simple performance benchmark for key endpoints.
Task name: "Performance Benchmark" -> function: performance_benchmark(context)
"""
from __future__ import annotations
import time
from statistics import mean
from automation.core.logger import AutomationLogger
from fastapi.testclient import TestClient


def _load_app():
    try:
        from app.main import app

        return app
    except Exception:
        import importlib

        mod = importlib.import_module("main")
        return getattr(mod, "app")


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
    results["science_search"] = _bench(
        client, "POST", "/api/science/biomedical/search", {"query": "test"}, n
    )
    results["finance_personal"] = _bench(
        client,
        "POST",
        "/api/finance/personal/analyze",
        {"financial_data": {"income": 1}, "goals": ["g"], "user_info": {"age": 1}},
        n,
    )

    for k, v in results.items():
        log.info(f"{k}: {v*1000:.2f} ms (avg over {n})")
    log.info("✅ Performance benchmark complete")
