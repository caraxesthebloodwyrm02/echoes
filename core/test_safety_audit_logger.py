#!/usr/bin/env python3
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

"""
Unit tests for safety audit logger.
"""

import json
import os
import tempfile
from datetime import datetime

from src.safety.audit import AuditLogger


def test_audit_logger_creation():
    """Test that audit logger creates log file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        log_file = os.path.join(tmpdir, "test_audit.ndjson")
        audit = AuditLogger(log_file)
        assert os.path.exists(log_file)


def test_audit_logger_logs_operation():
    """Test that audit logger writes operation data."""
    with tempfile.TemporaryDirectory() as tmpdir:
        log_file = os.path.join(tmpdir, "test_audit.ndjson")
        audit = AuditLogger(log_file)

        # Log an operation
        audit.log(
            user="test_user",
            prompt="test prompt",
            response={"bias_score": 0.5, "explanation": "neutral"},
            outcome="success",
        )

        # Check log file contents
        with open(log_file, "r") as f:
            lines = f.readlines()
            assert len(lines) == 1

            entry = json.loads(lines[0])
            assert entry["user"] == "test_user"
            assert entry["prompt_hash"] == hash("test prompt")
            assert entry["outcome"] == "success"
            assert "bias_score" in entry["response_keys"]
            assert "ts" in entry
            assert isinstance(entry["ts"], str)


def test_audit_logger_multiple_entries():
    """Test that audit logger handles multiple log entries."""
    with tempfile.TemporaryDirectory() as tmpdir:
        log_file = os.path.join(tmpdir, "test_audit.ndjson")
        audit = AuditLogger(log_file)

        # Log multiple operations
        for i in range(3):
            audit.log(
                user=f"user_{i}",
                prompt=f"prompt_{i}",
                response={"result": i},
                outcome="success",
            )

        # Check all entries
        with open(log_file, "r") as f:
            lines = f.readlines()
            assert len(lines) == 3

            for i, line in enumerate(lines):
                entry = json.loads(line)
                assert entry["user"] == f"user_{i}"


def test_audit_logger_handles_special_characters():
    """Test that audit logger handles special characters in data."""
    with tempfile.TemporaryDirectory() as tmpdir:
        log_file = os.path.join(tmpdir, "test_audit.ndjson")
        audit = AuditLogger(log_file)

        # Log with special characters
        audit.log(
            user="test@user.com",
            prompt="prompt with special chars: !@#$%^&*()",
            response={"message": "response with ümlauts and émojis 😀"},
            outcome="success",
        )

        # Check that it was logged without errors
        with open(log_file, "r") as f:
            lines = f.readlines()
            assert len(lines) == 1
            entry = json.loads(lines[0])
            assert entry["user"] == "test@user.com"


def test_audit_logger_default_log_file():
    """Test that audit logger works with default log file."""
    audit = AuditLogger()  # Uses default "logs/audit.ndjson"

    # Should create logs directory if it doesn't exist
    audit.log(user="test", prompt="test", response={"test": "data"})

    # Check that default log file exists
    assert os.path.exists("logs/audit.ndjson")

    # Clean up
    if os.path.exists("logs/audit.ndjson"):
        os.remove("logs/audit.ndjson")
    if os.path.exists("logs"):
        os.rmdir("logs")


def test_audit_logger_privacy_hashing():
    """Test that prompts are hashed for privacy."""
    with tempfile.TemporaryDirectory() as tmpdir:
        log_file = os.path.join(tmpdir, "test_audit.ndjson")
        audit = AuditLogger(log_file)

        sensitive_prompt = "This contains sensitive information: password123"
        audit.log(user="test", prompt=sensitive_prompt, response={"result": "ok"})

        with open(log_file, "r") as f:
            entry = json.loads(f.read())
            # Prompt should be hashed, not stored in plain text
            assert entry["prompt_hash"] == hash(sensitive_prompt)
            assert "prompt" not in entry  # Should not contain plain text prompt


def test_audit_logger_timestamps():
    """Test that timestamps are properly formatted."""
    with tempfile.TemporaryDirectory() as tmpdir:
        log_file = os.path.join(tmpdir, "test_audit.ndjson")
        audit = AuditLogger(log_file)

        before_log = datetime.utcnow()
        audit.log("user", "prompt", {"result": "ok"})
        after_log = datetime.utcnow()

        with open(log_file, "r") as f:
            entry = json.loads(f.read())
            logged_time = datetime.fromisoformat(entry["ts"])

            # Timestamp should be between before and after
            assert before_log <= logged_time <= after_log
