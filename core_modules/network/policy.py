"""
Centralized outbound network policy.

Default: deny all outbound egress unless explicitly allowed via environment.

Environment variables:
- EGRESS_ENFORCE: '1'/'true' to enforce, '0'/'false' to disable (default: '1')
- EGRESS_ALLOWLIST: comma-separated list of allowed host keywords (default: 'openai')
- EGRESS_LOG: '0' to silence, '1' basic, '2' verbose (default: '1')
- EGRESS_LOG_FORMAT: 'text' or 'json' for structured logging (default: 'text')
- EGRESS_AUTOPATCH: '1'/'true' to auto-patch the `requests` library at startup (default: '1')
- EGRESS_OTEL_ENABLE: '1' to enable OpenTelemetry metrics (default: '0')
- EGRESS_OTEL_EXPORTER: 'http' or 'grpc' for OpenTelemetry (default: 'http')
- EGRESS_OTEL_ENDPOINT: OpenTelemetry endpoint URL (default: 'http://localhost:4318')
- EGRESS_PROM_ENABLE: '1' to enable Prometheus metrics (default: '0')
- EGRESS_CI_FAIL_ON_BLOCKED: '1' to fail CI on blocked events (default: '0')
- EGRESS_CI_ALLOW_DISABLE: '1' to allow EGRESS_ENFORCE=0 in CI (default: '0')
- EGRESS_CI_FAIL_ON_DRIFT: '1' to fail CI on allowlist drift (default: '0')

Usage:
- Call `is_allowed(host)` before making a network call.
- Optionally call `patch_requests()` to automatically enforce policy on `requests` library.
- Use `require_openai_allowed()` prior to constructing OpenAI clients.
- Set `EGRESS_ALLOWLIST=openai` (default) to permit OpenAI hosts, or add more via commas.
- Use CLI: `python -m core_modules.network.policy --print --json --verify`

This module avoids importing heavy deps and can be used very early in program startup.
"""
from __future__ import annotations

import os
import argparse
import json
import sys
import threading
import time
from collections import deque
from typing import Optional

from .policy_engine import decide
from .policy_types import PolicyConfig, PolicyEvent, load_config

try:
    import requests  # type: ignore
except Exception:  # pragma: no cover - requests may not be installed in minimal envs
    requests = None  # type: ignore


def _now_ms() -> int:
    return int(time.time() * 1000)


_cfg_lock = threading.Lock()
_cfg_cache: Optional[PolicyConfig] = None


def get_config() -> PolicyConfig:
    global _cfg_cache
    with _cfg_lock:
        if _cfg_cache is None:
            _cfg_cache = load_config()
        return _cfg_cache


def refresh_config() -> PolicyConfig:
    global _cfg_cache
    with _cfg_lock:
        _cfg_cache = load_config()
        return _cfg_cache


# Metrics tracking
_metrics_lock = threading.Lock()
_allowed_total = 0
_blocked_total = 0
_recent_events = deque(maxlen=100)  # Configurable ring buffer

# Optional telemetry exporters (lazy import)
_otel_counter_allowed = None
_otel_counter_blocked = None
_prom_counter_allowed = None
_prom_counter_blocked = None


def _init_otel():
    """Initialize OpenTelemetry if enabled and available."""
    global _otel_counter_allowed, _otel_counter_blocked
    if _otel_counter_allowed is not None:
        return

    try:
        from opentelemetry import metrics as otel_metrics
        from opentelemetry.sdk.metrics import MeterProvider
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
        from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader

        cfg = get_config()
        resource = Resource.create({"service.name": "egress-policy"})
        exporter = OTLPMetricExporter(endpoint=cfg.otel_endpoint)
        reader = PeriodicExportingMetricReader(exporter, export_interval_millis=30000)
        provider = MeterProvider(resource=resource, metric_readers=[reader])
        otel_metrics.set_meter_provider(provider)

        meter = otel_metrics.get_meter(__name__)
        _otel_counter_allowed = meter.create_counter("egress_allowed_total")
        _otel_counter_blocked = meter.create_counter("egress_blocked_total")

        _log(2, "OpenTelemetry initialized")
    except ImportError:
        _log(2, "OpenTelemetry packages not available; install opentelemetry-api and opentelemetry-sdk")
    except Exception as e:
        _log(1, f"Failed to initialize OpenTelemetry: {e}")


def _init_prometheus():
    """Initialize Prometheus metrics if enabled and available."""
    global _prom_counter_allowed, _prom_counter_blocked
    if _prom_counter_allowed is not None:
        return

    try:
        from prometheus_client import Counter

        _prom_counter_allowed = Counter("egress_allowed_total", "Total allowed egress requests")
        _prom_counter_blocked = Counter("egress_blocked_total", "Total blocked egress requests")

        _log(2, "Prometheus metrics initialized")
    except ImportError:
        _log(2, "prometheus_client not available; install prometheus_client")
    except Exception as e:
        _log(1, f"Failed to initialize Prometheus: {e}")


def _record_event(action: str, host: str, reason: str) -> None:
    """Record a policy event and update metrics."""
    global _allowed_total, _blocked_total

    cfg = get_config()
    event = PolicyEvent(ts=_now_ms(), action=action, host=host, reason=reason)

    with _metrics_lock:
        _recent_events.append(event)
        if action == "ALLOW":
            _allowed_total += 1
        else:
            _blocked_total += 1

    # Optional telemetry exporters
    if cfg.otel_enable:
        _init_otel()
        if action == "ALLOW" and _otel_counter_allowed:
            _otel_counter_allowed.add(1, {"host": host})
        elif action == "DENY" and _otel_counter_blocked:
            _otel_counter_blocked.add(1, {"host": host})

    if cfg.prom_enable:
        _init_prometheus()
        if action == "ALLOW" and _prom_counter_allowed:
            _prom_counter_allowed.inc()
        elif action == "DENY" and _prom_counter_blocked:
            _prom_counter_blocked.inc()


def get_metrics() -> dict:
    """Get current metrics."""
    with _metrics_lock:
        return {
            "allowed_total": _allowed_total,
            "blocked_total": _blocked_total,
            "total": _allowed_total + _blocked_total,
        }


def get_recent_events() -> list[dict]:
    """Get recent events from the ring buffer."""
    with _metrics_lock:
        return [{
            "ts": e.ts,
            "action": e.action,
            "host": e.host,
            "reason": e.reason,
        } for e in _recent_events]


def reset_metrics() -> None:
    """Reset all metrics and clear the event buffer."""
    global _allowed_total, _blocked_total
    with _metrics_lock:
        _allowed_total = 0
        _blocked_total = 0
        _recent_events.clear()


class EgressDenied(Exception):
    pass


def _log(level: int, msg: str, host: str = "", action: str = "") -> None:
    cfg = get_config()
    if cfg.log_level < level:
        return

    if cfg.log_format == "json":
        log_entry = {
            "ts": _now_ms(),
            "pid": os.getpid(),
            "thread": threading.current_thread().name,
            "action": action,
            "host": host,
            "allowed": action == "ALLOW",
            "reason": msg,
        }
        print(json.dumps(log_entry))
    else:
        # Simple text format
        print(f"[egress-policy][{_now_ms()}] {msg}")


def is_allowed(host: str) -> bool:
    cfg = get_config()
    decision = decide(host, cfg)
    if decision.allowed:
        _log(2, f"ALLOW host={host}", host, "ALLOW")
        _record_event("ALLOW", host, decision.reason)
        return True
    else:
        _log(2, f"DENY host={host} ({decision.reason})", host, "DENY")
        _record_event("DENY", host, decision.reason)
        return False


def require_allowed(host: str) -> None:
    if not is_allowed(host):
        _log(1, f"DENY host={host}", host, "DENY")
        raise EgressDenied(
            f"Outbound network to '{host}' blocked by policy. Set EGRESS_ALLOWLIST or disable via EGRESS_ENFORCE=0 (not recommended)."
        )


def require_openai_allowed() -> None:
    # Convenience for common path
    # Try to resolve default OpenAI API base host if env sets custom base
    api_base = os.environ.get("OPENAI_BASE_URL") or os.environ.get("OPENAI_API_BASE") or "api.openai.com"
    require_allowed(_host_only(api_base))


def _host_only(url_or_host: str) -> str:
    # Extract host if a URL is provided
    s = url_or_host.strip()
    if "://" in s:
        # naive parse to avoid deps
        s = s.split("://", 1)[1]
    # strip path
    s = s.split("/", 1)[0]
    # strip port
    s = s.split(":", 1)[0]
    return s


def patch_requests() -> None:
    """Monkeypatch requests.Session.request to enforce policy.

    Safe to call multiple times. No-op if `requests` is not available.
    """
    if requests is None:
        _log(2, "requests not available; patch skipped")
        return

    Session = requests.Session  # type: ignore[attr-defined]
    # If already patched, do nothing
    if getattr(Session.request, "__egress_patched__", False):  # type: ignore[attr-defined]
        return

    orig_request = Session.request

    def guarded(self, method, url, *args, **kwargs):  # type: ignore[no-redef]
        host = _host_only(str(url))
        require_allowed(host)
        return orig_request(self, method, url, *args, **kwargs)

    # Mark as patched and assign directly to the class method
    setattr(guarded, "__egress_patched__", True)
    Session.request = guarded  # type: ignore[assignment]
    _log(1, "requests.Session.request patched with egress policy")


def resolve_host(host_or_hostname: str) -> list[str]:
    """Best-effort DNS resolution to IPs; used for logging or future checks.
    Does not affect allow/deny decisions (we keep it simple by host keyword).
    """
    try:
        return list({ai[4][0] for ai in socket.getaddrinfo(host_or_hostname, None)})
    except Exception:
        return []


def _load_allowlist_lock() -> set[str]:
    """Load the allowlist lock file for drift detection."""
    lock_path = os.path.join(os.path.dirname(__file__), "policy_allowlist.lock")
    if not os.path.exists(lock_path):
        return set()

    try:
        with open(lock_path, "r", encoding="utf-8") as f:
            tokens = set()
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    tokens.add(line.lower().strip())
            return tokens
    except Exception as e:
        _log(1, f"Failed to load allowlist lock: {e}")
        return set()


def verify_policy() -> tuple[bool, list[str], set[str]]:
    """Verify policy configuration and return (is_valid, errors, categories).

    Categories (subset may be returned):
    - 'validation': generic configuration issues (empty allowlist, wildcards, enforcement requirement)
    - 'drift': allowlist drift vs. lock file
    - 'blocked': blocked events occurred with CI fail-on-blocked enabled
    """
    cfg = get_config()
    errors: list[str] = []
    categories: set[str] = set()

    # Check CI enforcement requirements
    if os.getenv("CI"):
        if not cfg.enforce and not cfg.ci_allow_disable:
            errors.append("CI: EGRESS_ENFORCE must be '1' unless EGRESS_CI_ALLOW_DISABLE=1")
            categories.add('validation')

        if not cfg.allowlist:
            errors.append("CI: Allowlist cannot be empty")
            categories.add('validation')

        # Check for wildcards
        wildcards = {"*", "all", "any"}
        for token in cfg.allowlist:
            if token in wildcards:
                errors.append(f"CI: Wildcard '{token}' not allowed in allowlist")
                categories.add('validation')

        # Check allowlist drift
        lock_tokens = _load_allowlist_lock()
        if lock_tokens:
            allowlist_set = set(cfg.allowlist)
            if lock_tokens != allowlist_set:
                missing = lock_tokens - allowlist_set
                extra = allowlist_set - lock_tokens
                if missing:
                    errors.append(f"CI: Allowlist missing tokens: {', '.join(sorted(missing))}")
                if extra:
                    errors.append(f"CI: Allowlist has extra tokens: {', '.join(sorted(extra))}")
                categories.add('drift')
                if cfg.ci_fail_on_drift:
                    errors.append("CI: Allowlist drift detected and EGRESS_CI_FAIL_ON_DRIFT=1")

    # Check for blocked events in CI
    if os.getenv("CI") and cfg.ci_fail_on_blocked:
        metrics = get_metrics()
        if metrics["blocked_total"] > 0:
            errors.append(f"CI: {metrics['blocked_total']} blocked events detected and EGRESS_CI_FAIL_ON_BLOCKED=1")
            categories.add('blocked')

    return len(errors) == 0, errors, categories


def print_config(json_format: bool = False) -> None:
    """Print current configuration."""
    cfg = get_config()
    metrics = get_metrics()

    if json_format:
        output = {
            "config": {
                "enforce": cfg.enforce,
                "allowlist": list(cfg.allowlist),
                "log_level": cfg.log_level,
                "log_format": cfg.log_format,
                "otel_enable": cfg.otel_enable,
                "otel_exporter": cfg.otel_exporter,
                "otel_endpoint": cfg.otel_endpoint,
                "prom_enable": cfg.prom_enable,
                "ci_fail_on_blocked": cfg.ci_fail_on_blocked,
                "ci_allow_disable": cfg.ci_allow_disable,
                "ci_fail_on_drift": cfg.ci_fail_on_drift,
            },
            "metrics": metrics,
            "recent_events": get_recent_events(),
        }
        print(json.dumps(output, indent=2))
    else:
        print("=== Egress Policy Configuration ===")
        print(f"Enforcement: {'ENABLED' if cfg.enforce else 'DISABLED'}")
        print(f"Allowlist: {', '.join(cfg.allowlist) if cfg.allowlist else '(empty)'}")
        print(f"Log Level: {cfg.log_level}")
        print(f"Log Format: {cfg.log_format}")
        print(f"OpenTelemetry: {'ENABLED' if cfg.otel_enable else 'DISABLED'}")
        if cfg.otel_enable:
            print(f"  Exporter: {cfg.otel_exporter}")
            print(f"  Endpoint: {cfg.otel_endpoint}")
        print(f"Prometheus: {'ENABLED' if cfg.prom_enable else 'DISABLED'}")
        print("\n=== Metrics ===")
        print(f"Allowed: {metrics['allowed_total']}")
        print(f"Blocked: {metrics['blocked_total']}")
        print(f"Total: {metrics['total']}")

        recent = get_recent_events()
        if recent:
            print(f"\n=== Recent Events (last {len(recent)}) ===")
            for event in recent[-10:]:  # Show last 10
                print(f"[{event['ts']}] {event['action']} {event['host']} - {event['reason']}")


def write_summary(output_path: str) -> None:
    """Write egress summary to JSON file."""
    cfg = get_config()
    metrics = get_metrics()
    events = get_recent_events()

    # Derive unique blocked hosts and counts
    blocked_hosts = {}
    for e in events:
        if e.get("action") == "DENY":
            h = e.get("host", "")
            if h:
                blocked_hosts[h] = blocked_hosts.get(h, 0) + 1

    summary = {
        "timestamp": _now_ms(),
        "config": {
            "enforce": cfg.enforce,
            "allowlist": list(cfg.allowlist),
            "log_level": cfg.log_level,
            "log_format": cfg.log_format,
            "otel_enable": cfg.otel_enable,
            "otel_exporter": cfg.otel_exporter,
            "otel_endpoint": cfg.otel_endpoint,
            "prom_enable": cfg.prom_enable,
            "ci_fail_on_blocked": cfg.ci_fail_on_blocked,
            "ci_allow_disable": cfg.ci_allow_disable,
            "ci_fail_on_drift": cfg.ci_fail_on_drift,
        },
        "metrics": metrics,
        "recent_events": events,
        "unique_blocked_hosts": {
            "count": len(blocked_hosts),
            "hosts": [
                {"host": h, "occurrences": c} for h, c in sorted(blocked_hosts.items(), key=lambda x: (-x[1], x[0]))
            ],
        },
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)


def _cli() -> None:
    """Command line interface."""

    parser = argparse.ArgumentParser(description="Egress Policy Management")
    parser.add_argument("--print", action="store_true", help="Print current configuration")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    parser.add_argument("--verify", action="store_true", help="Verify policy configuration")
    parser.add_argument("--summary-out", help="Write summary to file")

    args = parser.parse_args()

    exit_code = 0

    if args.verify:
        is_valid, errors, categories = verify_policy()
        if not is_valid:
            print("Policy verification FAILED:")
            for error in errors:
                print(f"  - {error}")
            # Map categories to exit codes with priority: blocked(4) > drift(3) > validation(2)
            if 'blocked' in categories:
                exit_code = max(exit_code, 4)
            if 'drift' in categories:
                exit_code = max(exit_code, 3)
            if 'validation' in categories:
                exit_code = max(exit_code, 2)
        else:
            print("Policy verification PASSED")

    if args.print:
        print_config(json_format=args.json)

    if args.summary_out:
        write_summary(args.summary_out)
        print(f"Summary written to {args.summary_out}")

    if args.verify and exit_code != 0:
        sys.exit(exit_code)


if __name__ == "__main__":
    _cli()
