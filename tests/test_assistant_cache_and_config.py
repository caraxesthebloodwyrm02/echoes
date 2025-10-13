import os
import json
from pathlib import Path
import tempfile

import pytest
import sys
import types

from minicon.config import Config


def test_switch_api_key_valid_and_invalid(monkeypatch):
    # Ensure environment keys are picked up
    monkeypatch.setenv("OPENAI_API_KEY_PRIMARY", "primary-key-123")
    monkeypatch.delenv("OPENAI_API_KEY_SECONDARY", raising=False)

    cfg = Config.from_env()

    # Switching to primary should work
    cfg.switch_api_key("PRIMARY")
    assert cfg.active_openai_key == "PRIMARY"

    # Switching to secondary without a key should raise
    with pytest.raises(ValueError):
        cfg.switch_api_key("SECONDARY")


def test_cache_response_saved(tmp_path):
    # Prevent import-time dependency errors by stubbing melody_structure.master_channel
    pkg = types.ModuleType("melody_structure")
    mod = types.ModuleType("melody_structure.master_channel")
    # Minimal MasterChannel stub used by symphony_assistant_integration
    class _MasterChannelStub:
        def compress_and_glue(self, input_data):
            return input_data

        def finalize(self, master_data):
            return str(master_data)

    mod.MasterChannel = _MasterChannelStub
    sys.modules["melody_structure"] = pkg
    sys.modules["melody_structure.master_channel"] = mod

    # Import the client after stubbing the dependency
    from automation.integration.symphony_assistant_integration import SymphonyAssistantClient

    # Create a client and point its cache_dir to a temp directory
    client = SymphonyAssistantClient()
    client.cache_dir = tmp_path
    tmp_file_key = "testkey123"

    # Craft a fake response that would normally be saved; include content and status
    response = {
        "model": "gpt-4o-mini",
        "content": "This is a test response",
        "usage": {"total_tokens": 10},
        "status_code": 200,
        "_request": {"model": "gpt-4o-mini", "temperature": 0.2, "max_tokens": 128}
    }

    # Call the protected save method (we're testing its behavior)
    client._save_cache(tmp_file_key, response)

    saved_file = tmp_path / f"{tmp_file_key}.json"
    assert saved_file.exists()

    data = json.loads(saved_file.read_text())

    # Check that response is saved without metadata (simplified cache)
    assert "_cache_meta" not in data
    assert data["content"] == "This is a test response"
    assert data["model"] == "gpt-4o-mini"
    assert data.get("_request", {}).get("model") == "gpt-4o-mini"
