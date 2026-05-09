"""Tests for tools.security.advanced_routine (secret + PII masking)."""

from __future__ import annotations

from api.logging_structured import redact_telemetry_processor
from tools.security.advanced_routine import (
    RoutineMode,
    detect_findings,
    redact_text,
    sanitize_mapping,
)


def test_redacts_openai_key() -> None:
    s = "key is sk-abcdefghijklmnopqrstuvwxyz12345678 here"
    out = redact_text(s, RoutineMode.ADVANCED)
    assert "sk-abc" not in out
    assert "[REDACTED:openai_key]" in out


def test_redacts_bearer() -> None:
    s = "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.x.y"
    out = redact_text(s, RoutineMode.ADVANCED)
    assert "Bearer eyJ" not in out
    assert "[REDACTED:bearer]" in out


def test_redacts_email_and_phone() -> None:
    s = "contact user@example.com or (555) 123-4567"
    out = redact_text(s, RoutineMode.STANDARD)
    assert "user@example.com" not in out
    assert "[REDACTED:email]" in out
    assert "[REDACTED:phone]" in out


def test_luhn_valid_card_masked() -> None:
    # Classic valid Visa test PAN (Luhn passes)
    s = "pay with 4111111111111111 today"
    out = redact_text(s, RoutineMode.STANDARD)
    assert "4111111111111111" not in out
    assert "[REDACTED:payment_card]" in out


def test_non_luhn_digit_run_not_masked_as_card() -> None:
    s = "id 4111111111111112 end"
    out = redact_text(s, RoutineMode.STANDARD)
    assert "4111111111111112" in out


def test_jwt_shape_advanced_only() -> None:
    tok = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XwpLurnQuWlLeuiyCj2M"
    standard = redact_text(tok, RoutineMode.STANDARD)
    assert tok in standard  # not classified as jwt in standard mode
    advanced = redact_text(tok, RoutineMode.ADVANCED)
    assert tok not in advanced
    assert "[REDACTED:jwt_like]" in advanced


def test_private_ipv4_advanced() -> None:
    s = "server at 192.168.1.10"
    adv = redact_text(s, RoutineMode.ADVANCED)
    assert "192.168.1.10" not in adv
    std = redact_text(s, RoutineMode.STANDARD)
    assert "192.168.1.10" in std


def test_public_ip_paranoid_only() -> None:
    s = "dns 8.8.8.8"
    assert "8.8.8.8" in redact_text(s, RoutineMode.ADVANCED)
    paranoid = redact_text(s, RoutineMode.PARANOID)
    assert "8.8.8.8" not in paranoid
    assert "[REDACTED:ipv4]" in paranoid


def test_detect_findings_categories() -> None:
    s = "sk-abcdefghijklmnop email=a@b.co"
    fs = detect_findings(s, RoutineMode.ADVANCED)
    cats = {f.category for f in fs}
    assert "openai_sk" in cats
    assert "email" in cats


def test_sanitize_nested_dict() -> None:
    payload = {"msg": "reach me at user@site.org", "nested": {"k": "sk-12345678901234567890"}}
    clean = sanitize_mapping(payload, RoutineMode.ADVANCED)
    assert "user@site.org" not in clean["msg"]
    assert "[REDACTED:email]" in clean["msg"]
    assert "sk-" not in clean["nested"]["k"]


def test_structlog_processor_shape() -> None:
    ev = {"event": "x", "extra": {"token": "Bearer abcdefghijklmnop"}}
    out = redact_telemetry_processor(None, "info", ev)
    assert "Bearer" not in str(out["extra"]["token"])


def test_cli_missing_input_file_exits_2() -> None:
    import subprocess
    import sys
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    r = subprocess.run(
        [sys.executable, "-m", "tools.security", "--detect-only", "__missing_echoes_cli__.txt"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    assert r.returncode == 2
    assert "does not exist" in r.stderr
