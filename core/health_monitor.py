#!/usr/bin/env python3
"""Automated health monitoring script for the unified platform."""

import time
from datetime import datetime
from typing import Tuple

import requests

BASE_URL = "http://127.0.0.1:8000"
SIMPLE_ENDPOINT = f"{BASE_URL}/api/health/simple"
DETAILED_ENDPOINT = f"{BASE_URL}/api/health"


def _run_check(endpoint: str, timeout: float) -> Tuple[int, float, str]:
    """Execute a health check request and return status, elapsed time, and body."""
    start = time.time()
    response = requests.get(endpoint, timeout=timeout)
    elapsed = time.time() - start
    try:
        body = response.json()
    except ValueError:
        body = response.text
    return response.status_code, elapsed, body


def monitor_health() -> bool:
    """Run both health checks and print a summarized report."""
    print(f"[{datetime.now()}] Starting unified platform health monitor\n")

    try:
        simple_status, simple_time, simple_body = _run_check(SIMPLE_ENDPOINT, timeout=5)
        detailed_status, detailed_time, detailed_body = _run_check(DETAILED_ENDPOINT, timeout=10)

        print("Simple Health Check")
        print(f"  Endpoint: {SIMPLE_ENDPOINT}")
        print(f"  Status : {simple_status}")
        print(f"  Time   : {simple_time:.2f}s")
        print(f"  Body   : {simple_body}\n")

        print("Detailed Health Check")
        print(f"  Endpoint: {DETAILED_ENDPOINT}")
        print(f"  Status : {detailed_status}")
        print(f"  Time   : {detailed_time:.2f}s")
        print(f"  Body   : {detailed_body}\n")

        all_healthy = simple_status == 200 and detailed_status == 200
        print("Overall Result")
        if all_healthy:
            print("  [OK] SYSTEM HEALTHY")
        else:
            print("  [FAIL] SYSTEM UNHEALTHY")

        return all_healthy

    except requests.RequestException as exc:
        print(f"  [FAIL] Health monitoring request failed: {exc}")
        return False


if __name__ == "__main__":
    monitor_health()
