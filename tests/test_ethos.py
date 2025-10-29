import os
import logging
from importlib import reload

import pytest


def _clear_env(monkeypatch):
    monkeypatch.delenv("ECHOES_RESEARCH_ONLY", raising=False)
    monkeypatch.delenv("ECHOES_EMBEDDINGS_PROVIDER", raising=False)
    monkeypatch.delenv("ECHOES_PARTNERSHIP", raising=False)


def test_enforce_sets_defaults(monkeypatch):
    _clear_env(monkeypatch)
    # Ensure OPENAI_API_KEY absence doesn't raise
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    import core.ethos as ethos
    ethos.enforce()

    assert os.environ.get("ECHOES_RESEARCH_ONLY") == "1"
    assert os.environ.get("ECHOES_EMBEDDINGS_PROVIDER") == "openai"
    assert os.environ.get("ECHOES_PARTNERSHIP") == "OpenAI"


def test_enforce_respects_existing_provider(monkeypatch, caplog):
    _clear_env(monkeypatch)
    monkeypatch.setenv("ECHOES_EMBEDDINGS_PROVIDER", "custom")

    import core.ethos as ethos
    caplog.set_level(logging.WARNING, logger=ethos.__name__)

    ethos.enforce()

    # Should not override an explicitly-set provider
    assert os.environ.get("ECHOES_EMBEDDINGS_PROVIDER") == "custom"
    # Should warn about non-canonical provider
    assert any("Non-canonical embeddings provider" in r.getMessage() for r in caplog.records)


def test_enforce_does_not_log_secrets(monkeypatch, caplog):
    _clear_env(monkeypatch)
    secret = "sk-test-secret-123"
    monkeypatch.setenv("OPENAI_API_KEY", secret)

    import core.ethos as ethos
    caplog.set_level(logging.INFO, logger=ethos.__name__)

    caplog.clear()
    ethos.enforce()

    # Ensure no log lines contain the secret value
    for rec in caplog.records:
        assert secret not in (rec.getMessage() or "")


def test_enforce_idempotent(monkeypatch):
    _clear_env(monkeypatch)
    import core.ethos as ethos

    ethos.enforce()
    first_values = (
        os.environ.get("ECHOES_RESEARCH_ONLY"),
        os.environ.get("ECHOES_EMBEDDINGS_PROVIDER"),
        os.environ.get("ECHOES_PARTNERSHIP"),
    )

    # Call again should not change values
    ethos.enforce()
    second_values = (
        os.environ.get("ECHOES_RESEARCH_ONLY"),
        os.environ.get("ECHOES_EMBEDDINGS_PROVIDER"),
        os.environ.get("ECHOES_PARTNERSHIP"),
    )

    assert first_values == second_values
