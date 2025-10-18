# MIT License
#
# Copyright (c) 2024 Echoes Project
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import json
import sys
import types

import pytest
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
    from automation.integration.symphony_assistant_integration import (
        SymphonyAssistantClient,
    )

    # Create a client and point its cache_dir to a temp directory
    client = SymphonyAssistantClient()
    client.cache_dir = tmp_path
    tmp_file_key = "testkey123"

    # Craft a fake response that would normally be saved; include content and status
    response = {
        "model": "gpt-4.1",
        "content": "This is a test response",
        "usage": {"total_tokens": 10},
        "status_code": 200,
        "_request": {"model": "gpt-4.1", "temperature": 0.2, "max_tokens": 128},
    }

    # Call the protected save method (we're testing its behavior)
    client._save_cache(tmp_file_key, response)

    saved_file = tmp_path / f"{tmp_file_key}.json"
    assert saved_file.exists()

    data = json.loads(saved_file.read_text())

    # Check that response is saved without metadata (simplified cache)
    assert "_cache_meta" not in data
    assert data["content"] == "This is a test response"
    assert data["model"] == "gpt-4.1"
    assert data.get("_request", {}).get("model") == "gpt-4.1"
