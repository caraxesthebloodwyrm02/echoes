import importlib
import json
import os
import sys
import tempfile
from unittest.mock import patch

import pytest


@pytest.fixture(autouse=True)
def clear_policy_cache(monkeypatch):
    # Ensure fresh env for each test
    for k in [
        "EGRESS_ENFORCE",
        "EGRESS_ALLOWLIST",
        "EGRESS_LOG",
        "EGRESS_LOG_FORMAT",
        "EGRESS_AUTOPATCH",
        "OPENAI_BASE_URL",
        "OPENAI_API_BASE",
        "EGRESS_OTEL_ENABLE",
        "EGRESS_PROM_ENABLE",
        "EGRESS_CI_FAIL_ON_BLOCKED",
        "EGRESS_CI_ALLOW_DISABLE",
        "EGRESS_CI_FAIL_ON_DRIFT",
        "CI",
    ]:
        monkeypatch.delenv(k, raising=False)

    # Reload module to reset cache state
    if "core_modules.network.policy" in globals():
        pass
    import core_modules.network.policy as policy

    importlib.reload(policy)
    # Reset metrics
    policy.reset_metrics()
    yield


def test_default_config_enforces_and_allows_openai(monkeypatch):
    import core_modules.network.policy as policy

    cfg = policy.get_config()
    assert cfg.enforce is True
    assert "openai" in cfg.allowlist
    assert policy.is_allowed("api.openai.com") is True
    assert policy.is_allowed("example.com") is False


def test_env_parsing_allowlist_and_disable_enforcement(monkeypatch):
    monkeypatch.setenv("EGRESS_ENFORCE", "0")
    monkeypatch.setenv("EGRESS_ALLOWLIST", "example.com, internal.local")

    import core_modules.network.policy as policy

    policy.refresh_config()

    cfg = policy.get_config()
    assert cfg.enforce is False
    assert cfg.allowlist == ("example.com", "internal.local")

    # When not enforced, all hosts are allowed
    assert policy.is_allowed("anything.invalid") is True


def test_require_allowed_raises_when_blocked(monkeypatch):
    import core_modules.network.policy as policy

    # Default: enforce on, only allow openai
    with pytest.raises(policy.EgressDenied):
        policy.require_allowed("example.com")


def test_host_only_parsing():
    import core_modules.network.policy as policy

    cases = {
        "https://api.openai.com/v1/models": "api.openai.com",
        "http://example.com:8080/path": "example.com",
        "internal.local": "internal.local",
        "https://example.com": "example.com",
        "example.com/path": "example.com",
    }
    for s, expected in cases.items():
        assert policy._host_only(s) == expected


def test_require_openai_allowed_respects_env_base(monkeypatch):
    monkeypatch.setenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    import core_modules.network.policy as policy

    # Should not raise because allowlist includes 'openai'
    policy.require_openai_allowed()


def test_patch_requests_blocks_unlisted_hosts(monkeypatch):
    import core_modules.network.policy as policy

    # Ensure enforcement is on and allowlist is default ('openai')
    policy.refresh_config()

    # Patch requests and ensure deny path triggers before any socket usage
    import requests

    policy.patch_requests()
    with pytest.raises(policy.EgressDenied):
        # This should be blocked immediately by our patched request()
        requests.get("https://example.com")


@pytest.mark.parametrize(
    "env_value,expected",
    [
        ("", True),
        ("1", True),
        ("true", True),
        ("0", False),
        ("false", False),
        ("garbage", True),  # defaults to True when unrecognized
    ],
)
def test_enforce_bool_parsing(monkeypatch, env_value, expected):
    if env_value != "":
        monkeypatch.setenv("EGRESS_ENFORCE", env_value)
    else:
        monkeypatch.delenv("EGRESS_ENFORCE", raising=False)

    import core_modules.network.policy as policy

    policy.refresh_config()
    assert policy.get_config().enforce is expected


def test_metrics_tracking(monkeypatch):
    import core_modules.network.policy as policy

    # Initially no metrics
    metrics = policy.get_metrics()
    assert metrics["allowed_total"] == 0
    assert metrics["blocked_total"] == 0
    assert metrics["total"] == 0

    # Test allowed host
    assert policy.is_allowed("api.openai.com") is True
    metrics = policy.get_metrics()
    assert metrics["allowed_total"] == 1
    assert metrics["blocked_total"] == 0

    # Test blocked host
    assert policy.is_allowed("example.com") is False
    metrics = policy.get_metrics()
    assert metrics["allowed_total"] == 1
    assert metrics["blocked_total"] == 1

    # Test recent events
    events = policy.get_recent_events()
    assert len(events) == 2
    assert events[0]["action"] == "ALLOW"
    assert events[1]["action"] == "DENY"

    # Test reset
    policy.reset_metrics()
    metrics = policy.get_metrics()
    assert metrics["allowed_total"] == 0
    assert metrics["blocked_total"] == 0
    assert len(policy.get_recent_events()) == 0


def test_structured_logging_json(monkeypatch, capsys):
    monkeypatch.setenv("EGRESS_LOG_FORMAT", "json")
    monkeypatch.setenv("EGRESS_LOG", "2")

    import core_modules.network.policy as policy

    policy.refresh_config()

    # Trigger an allow event
    policy.is_allowed("api.openai.com")

    captured = capsys.readouterr()
    assert captured.out

    # Parse JSON log
    log_entry = json.loads(captured.out.strip())
    assert log_entry["action"] == "ALLOW"
    assert log_entry["host"] == "api.openai.com"
    assert log_entry["allowed"] is True
    assert "ts" in log_entry
    assert "pid" in log_entry
    assert "thread" in log_entry


def test_structured_logging_text(monkeypatch, capsys):
    monkeypatch.setenv("EGRESS_LOG_FORMAT", "text")
    monkeypatch.setenv("EGRESS_LOG", "2")

    import core_modules.network.policy as policy

    policy.refresh_config()

    # Trigger an allow event
    policy.is_allowed("api.openai.com")

    captured = capsys.readouterr()
    assert "[egress-policy][" in captured.out
    assert "ALLOW host=api.openai.com" in captured.out


def test_cli_print_config(monkeypatch, capsys):
    import core_modules.network.policy as policy

    # Test text output
    with patch.object(sys, "argv", ["policy.py", "--print"]):
        policy._cli()

    captured = capsys.readouterr()
    assert "=== Egress Policy Configuration ===" in captured.out
    assert "Enforcement: ENABLED" in captured.out
    assert "Allowlist: openai" in captured.out


def test_cli_print_json(monkeypatch, capsys):
    import core_modules.network.policy as policy

    # Test JSON output
    with patch.object(sys, "argv", ["policy.py", "--print", "--json"]):
        policy._cli()

    captured = capsys.readouterr()
    output = json.loads(captured.out)
    assert "config" in output
    assert "metrics" in output
    assert "recent_events" in output
    assert output["config"]["enforce"] is True
    assert "openai" in output["config"]["allowlist"]


def test_cli_verify_success(monkeypatch, capsys):
    import core_modules.network.policy as policy

    # Test successful verification
    with patch.object(sys, "argv", ["policy.py", "--verify"]):
        policy._cli()

    captured = capsys.readouterr()
    assert "Policy verification PASSED" in captured.out


def test_cli_verify_ci_enforcement_failure(monkeypatch, capsys):
    monkeypatch.setenv("CI", "1")
    monkeypatch.setenv("EGRESS_ENFORCE", "0")

    import core_modules.network.policy as policy

    policy.refresh_config()

    # Test CI enforcement failure
    with patch.object(sys, "argv", ["policy.py", "--verify"]):
        with pytest.raises(SystemExit) as exc_info:
            policy._cli()

    assert exc_info.value.code == 2
    captured = capsys.readouterr()
    assert "Policy verification FAILED" in captured.out
    assert "EGRESS_ENFORCE must be '1'" in captured.out


def test_cli_verify_wildcard_failure(monkeypatch, capsys):
    monkeypatch.setenv("CI", "1")
    monkeypatch.setenv("EGRESS_ALLOWLIST", "openai,*,example.com")

    import core_modules.network.policy as policy

    policy.refresh_config()

    # Test wildcard failure
    with patch.object(sys, "argv", ["policy.py", "--verify"]):
        with pytest.raises(SystemExit) as exc_info:
            policy._cli()

    assert exc_info.value.code == 3  # drift error (has higher priority than validation)
    captured = capsys.readouterr()
    assert "Wildcard '*' not allowed" in captured.out


def test_cli_summary_output(monkeypatch):
    import core_modules.network.policy as policy

    # Generate some activity
    policy.is_allowed("api.openai.com")
    policy.is_allowed("example.com")

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
        summary_path = f.name

    try:
        with patch.object(sys, "argv", ["policy.py", "--summary-out", summary_path]):
            policy._cli()

        # Verify summary file
        with open(summary_path, "r") as f:
            summary = json.load(f)

        assert "timestamp" in summary
        assert "config" in summary
        assert "metrics" in summary
        assert "recent_events" in summary
        assert summary["metrics"]["allowed_total"] == 1
        assert summary["metrics"]["blocked_total"] == 1
    finally:
        os.unlink(summary_path)


def test_allowlist_lock_drift_detection(monkeypatch, capsys):
    import core_modules.network.policy as policy
    import shutil

    # Create a temporary lock file
    lock_path = os.path.join(os.path.dirname(policy.__file__), "policy_allowlist.lock")

    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        f.write("# Test lock file\nopenai\nexample.com\n")
        temp_lock_path = f.name

    try:
        # Replace the real lock file temporarily
        if os.path.exists(lock_path):
            shutil.copy2(lock_path, lock_path + ".backup")
            os.remove(lock_path)
        shutil.copy2(temp_lock_path, lock_path)

        # Set CI and test drift
        monkeypatch.setenv("CI", "1")
        monkeypatch.setenv("EGRESS_ALLOWLIST", "openai")  # Missing example.com

        policy.refresh_config()

        with patch.object(sys, "argv", ["policy.py", "--verify"]):
            with pytest.raises(SystemExit) as exc_info:
                policy._cli()

        assert exc_info.value.code == 3  # drift error
        captured = capsys.readouterr()
        assert "Allowlist missing tokens: example.com" in captured.out

    finally:
        # Restore original state
        if os.path.exists(lock_path):
            os.remove(lock_path)
        if os.path.exists(lock_path + ".backup"):
            shutil.copy2(lock_path + ".backup", lock_path)
            os.remove(lock_path + ".backup")
        os.unlink(temp_lock_path)


def test_opentelemetry_optional_exporter(monkeypatch):
    monkeypatch.setenv("EGRESS_OTEL_ENABLE", "1")

    import core_modules.network.policy as policy

    policy.refresh_config()

    # Should not fail even without OpenTelemetry packages
    policy.is_allowed("api.openai.com")
    metrics = policy.get_metrics()
    assert metrics["allowed_total"] == 1


def test_prometheus_optional_exporter(monkeypatch):
    monkeypatch.setenv("EGRESS_PROM_ENABLE", "1")

    import core_modules.network.policy as policy

    policy.refresh_config()

    # Should not fail even without prometheus_client
    policy.is_allowed("api.openai.com")
    metrics = policy.get_metrics()
    assert metrics["allowed_total"] == 1


def test_ci_fail_on_blocked(monkeypatch, capsys):
    monkeypatch.setenv("CI", "1")
    monkeypatch.setenv("EGRESS_CI_FAIL_ON_BLOCKED", "1")

    import core_modules.network.policy as policy

    policy.refresh_config()

    # Generate a blocked event
    policy.is_allowed("example.com")

    with patch.object(sys, "argv", ["policy.py", "--verify"]):
        with pytest.raises(SystemExit) as exc_info:
            policy._cli()

    assert exc_info.value.code == 4  # blocked error (highest priority)
    captured = capsys.readouterr()
    assert "blocked events detected" in captured.out
