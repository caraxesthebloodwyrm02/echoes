"""
Endpoint smoke tests using FastAPI TestClient or live base_url.
Task name: "Smoke Test Endpoints" -> function: smoke_test_endpoints(context)
"""
from __future__ import annotations
from automation.core.logger import AutomationLogger
from typing import Optional


def _client_and_paths(base_url: Optional[str]):
    if base_url:
        import requests

        return ("live", base_url, requests)
    else:
        from fastapi.testclient import TestClient
        from app.main import app  # type: ignore

        return ("local", TestClient(app), None)


def smoke_test_endpoints(context):
    log = AutomationLogger()
    base_url = context.extra_data.get("base_url")
    mode, client_or_base, requests_mod = _client_and_paths(base_url)

    def _post(path: str, json_body: dict):
        if mode == "live":
            res = requests_mod.post(client_or_base + path, json=json_body, timeout=10)
            return res.status_code
        else:
            res = client_or_base.post(path, json=json_body)
            return res.status_code

    def _get(path: str):
        if mode == "live":
            res = requests_mod.get(client_or_base + path, timeout=10)
            return res.status_code
        else:
            res = client_or_base.get(path)
            return res.status_code

    checks = {
        "health": _get("/api/health"),
        "science": _post("/api/science/biomedical/search", {"query": "cancer", "max_results": 2}),
        "commerce": _post("/api/commerce/ubi/simulate", {}),
        "arts": _post(
            "/api/arts/create", {"prompt": "sunset", "medium": "text", "style": "modern"}
        ),
        "finance": _post(
            "/api/finance/personal/analyze",
            {"financial_data": {"income": 50000}, "goals": ["save"], "user_info": {"age": 30}},
        ),
    }

    failures = [k for k, v in checks.items() if v != 200]
    for k, v in checks.items():
        log.info(f"{k}: HTTP {v}")

    if failures:
        raise RuntimeError(f"Smoke test failed for: {', '.join(failures)}")
    log.info("✅ Smoke tests passed")
