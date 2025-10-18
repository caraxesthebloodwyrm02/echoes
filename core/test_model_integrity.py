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

"""Comprehensive test for model provider integrity and configuration routing."""

import os
import sys
from pathlib import Path

# Ensure UTF-8 encoding for output
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    if sys.version_info >= (3, 7):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    else:
        import codecs

        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
        sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())

from prompting.core.llm_client import LLMClient

CONFIG_FILES = [Path(".env"), Path("minicon/.env")]


def _load_env_var_from_files(var_name: str) -> None:
    """Load environment variable from known configuration files if unset."""
    if os.getenv(var_name):
        return

    for config_path in CONFIG_FILES:
        try:
            lines = config_path.read_text(encoding="utf-8").splitlines()
        except FileNotFoundError:
            continue

        for line in lines:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue

            key, sep, value = stripped.partition("=")
            if sep and key.strip() == var_name:
                os.environ[var_name] = value.strip()
                return


def _ensure_required_env_vars() -> None:
    """Ensure critical environment variables are populated for tests."""
    required = [
        "OPENAI_API_KEY",
        "OLLAMA_API_KEY",
        "GOOGLE_API_KEY",
        "LLM_PROVIDER",
        "LLM_MODEL_PRIMARY",
    ]
    for var in required:
        _load_env_var_from_files(var)


def test_provider_routing() -> bool:
    """Test provider routing and model assignment."""
    print("=== Testing Provider Routing ===")

    test_configs = [
        {
            "LLM_PROVIDER": "openai",
            "expected_provider": "openai",
            "expected_model": "gpt-4.1",
        },
        {
            "LLM_PROVIDER": "ollama",
            "expected_provider": "ollama",
            "expected_model": "llama3.1:8b",
        },
        {
            "LLM_PROVIDER": "gemini",
            "expected_provider": "gemini",
            "expected_model": "gemini-1.5-flash",
        },
    ]

    all_passed = True
    for config in test_configs:
        os.environ["LLM_PROVIDER"] = config["LLM_PROVIDER"]

        try:
            client = LLMClient()
            if (
                client.provider == config["expected_provider"]
                and client.model == config["expected_model"]
            ):
                print(
                    f"✓ {config['LLM_PROVIDER']}: provider={client.provider}, model={client.model}"
                )
            else:
                print(
                    f"✗ {config['LLM_PROVIDER']}: Expected provider={config['expected_provider']} model={config['expected_model']}, "
                    f"got provider={client.provider} model={client.model}"
                )
                all_passed = False
        except Exception as e:
            print(f"✗ {config['LLM_PROVIDER']}: Error - {e}")
            all_passed = False

    return all_passed


def test_model_override() -> bool:
    """Test model override functionality."""
    print("\n=== Testing Model Override ===")

    os.environ["LLM_PROVIDER"] = "openai"
    os.environ["LLM_MODEL"] = "gpt-4o"

    try:
        client = LLMClient()
        if client.model == "gpt-4o":
            print("✓ Model override works: gpt-4o")
            return True
        print(f"✗ Model override failed: expected gpt-4o, got {client.model}")
        return False
    except Exception as e:
        print(f"✗ Model override error: {e}")
        return False


def test_environment_variables() -> bool:
    """Test environment variable loading."""
    print("\n=== Testing Environment Variables ===")

    required_vars = {
        "OPENAI_API_KEY": "OpenAI API key",
        "OLLAMA_API_KEY": "Ollama API key",
        "GOOGLE_API_KEY": "Google API key",
        "LLM_PROVIDER": "Provider selection",
        "LLM_MODEL_PRIMARY": "Primary model",
    }

    all_set = True
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            print(f"✓ {var}: Set ({description})")
        else:
            print(f"✗ {var}: Not set ({description})")
            all_set = False

    return all_set


def test_json_parsing() -> bool:
    """Test JSON response parsing."""
    print("\n=== Testing JSON Parsing ===")

    test_cases = [
        ('{"summary":"ok","solution":"step1"}', {"summary": "ok", "solution": "step1"}),
        ('```json\n{"summary":"ok"}\n```', {"summary": "ok"}),
        ("invalid json", None),
    ]

    client = LLMClient()
    all_passed = True

    for i, (input_text, expected) in enumerate(test_cases):
        parsed = client.parse_json_response(input_text)
        if parsed == expected:
            print(f"✓ Test case {i + 1}: {parsed}")
        else:
            print(f"✗ Test case {i + 1}: Expected {expected}, got {parsed}")
            all_passed = False

    return all_passed


def test_api_connectivity() -> bool:
    """Test actual API connectivity (lightweight)."""
    print("\n=== Testing API Connectivity ===")

    original_provider = os.getenv("LLM_PROVIDER", "openai")
    original_model = os.getenv("LLM_MODEL", "gpt-4.1")

    os.environ["LLM_PROVIDER"] = "openai"
    os.environ["LLM_MODEL"] = "gpt-4.1"

    try:
        client = LLMClient()
        response = client.complete("Say 'Hello' in exactly one word.")
        if response and len(response.strip()) > 0:
            print(f"✓ OpenAI connectivity: Response received ({len(response)} chars)")
            connectivity_ok = True
        else:
            print("✗ OpenAI connectivity: Empty or no response")
            connectivity_ok = False
    except Exception as e:
        print(f"✗ OpenAI connectivity failed: {e}")
        connectivity_ok = False

    os.environ["LLM_PROVIDER"] = original_provider
    os.environ["LLM_MODEL"] = original_model

    return connectivity_ok


def main() -> int:
    """Run all integrity tests."""
    _ensure_required_env_vars()
    print("Testing Model Provider Integrity and Configuration Routing")
    print("=" * 60)

    tests = [
        ("Provider Routing", test_provider_routing),
        ("Model Override", test_model_override),
        ("Environment Variables", test_environment_variables),
        ("JSON Parsing", test_json_parsing),
        ("API Connectivity", test_api_connectivity),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"[FAIL] {test_name}: Unexpected error - {e}")
            results.append((test_name, False))

    print("\n" + "=" * 60)
    print("RESULTS SUMMARY:")

    passed = 0
    total = len(results)

    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"  {status}: {test_name}")
        if result:
            passed += 1

    print(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        print("ALL TESTS PASSED: Model provider integrity is confirmed!")
        return 0

    print("SOME TESTS FAILED: Check configuration and connectivity.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
