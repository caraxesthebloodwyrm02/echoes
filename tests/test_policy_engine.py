from core_modules.network.policy_engine import decide
from core_modules.network.policy import PolicyConfig


def make_cfg(**overrides):
    base = dict(
        enforce=True,
        allowlist=("openai",),
        log_level=1,
        log_format="text",
        otel_enable=False,
        otel_exporter="http",
        otel_endpoint="http://localhost:4318",
        prom_enable=False,
        ci_fail_on_blocked=False,
        ci_allow_disable=False,
        ci_fail_on_drift=False,
    )
    base.update(overrides)
    return PolicyConfig(**base)


def test_decide_enforcement_disabled_allows():
    cfg = make_cfg(enforce=False)
    d = decide("api.example.com", cfg)
    assert d.allowed is True
    assert d.reason == "enforcement disabled"
    assert d.matched_token is None


def test_decide_allowlist_match_allows():
    cfg = make_cfg(allowlist=("example",))
    d = decide("api.example.com", cfg)
    assert d.allowed is True
    assert d.reason == "allowlist match"
    assert d.matched_token == "example"


def test_decide_not_in_allowlist_denies():
    cfg = make_cfg(allowlist=("openai",))
    d = decide("api.example.com", cfg)
    assert d.allowed is False
    assert d.reason == "not in allowlist"
    assert d.matched_token is None
