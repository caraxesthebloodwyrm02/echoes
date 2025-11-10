import json
from pathlib import Path


import core_modules.network.policy as policy


def set_env(monkeypatch, **envs):
    for k, v in envs.items():
        monkeypatch.setenv(k, str(v))


def test_verify_categories_validation_and_drift(monkeypatch, tmp_path):
    # Simulate CI env
    set_env(monkeypatch, CI="1")

    # Start with empty allowlist to trigger validation error
    set_env(monkeypatch, EGRESS_ALLOWLIST="")
    # Enforcement disabled without allow-disable should also trigger validation
    set_env(monkeypatch, EGRESS_ENFORCE="0", EGRESS_CI_ALLOW_DISABLE="0")

    # Refresh cached config
    policy.refresh_config()

    ok, errors, categories = policy.verify_policy()
    assert ok is False
    assert "validation" in categories
    assert any("Allowlist cannot be empty" in e for e in errors)

    # Create a lock file with a different token to trigger drift
    lock_path = Path(policy.__file__).with_name("policy_allowlist.lock")
    lock_path.write_text("openai\n", encoding="utf-8")

    # Set a different allowlist to cause drift vs lock
    set_env(monkeypatch, EGRESS_ALLOWLIST="example")
    set_env(monkeypatch, EGRESS_ENFORCE="1")
    policy.refresh_config()

    ok, errors, categories = policy.verify_policy()
    assert ok is False
    assert "drift" in categories
    assert any("Allowlist missing tokens" in e or "extra tokens" in e for e in errors)

    # Cleanup
    lock_path.unlink(missing_ok=True)


def test_summary_includes_unique_blocked_hosts(monkeypatch, tmp_path):
    # Ensure deterministic environment
    set_env(monkeypatch, EGRESS_ENFORCE="1", EGRESS_ALLOWLIST="openai")
    policy.refresh_config()
    policy.reset_metrics()

    # Generate two denied events for the same host and one for a different host
    assert policy.is_allowed("api.example.com") is False
    assert policy.is_allowed("data.example.com") is False
    assert policy.is_allowed("api.example.com") is False

    out = tmp_path / "egress-summary.json"
    policy.write_summary(str(out))

    data = json.loads(out.read_text("utf-8"))
    uniq = data["unique_blocked_hosts"]
    assert uniq["count"] == 2
    hosts = {h["host"]: h["occurrences"] for h in uniq["hosts"]}
    assert hosts["api.example.com"] == 2
    assert hosts["data.example.com"] == 1

    # Check some config fields are present
    cfg = data["config"]
    assert "enforce" in cfg and "allowlist" in cfg and "log_format" in cfg
