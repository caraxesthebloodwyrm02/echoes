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

"""Streamlined provider connectivity test script."""

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


def _load_env_var_from_files(var_name: str, files: list[Path]) -> None:
    """Load an environment variable from the first config file that defines it."""
    if os.getenv(var_name):
        return

    for config_path in files:
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


def test_provider_connectivity() -> bool:
    """Test basic connectivity to configured LLM provider."""
    print("🔍 Testing Provider Connectivity")
    print("=" * 40)

    # Ensure provider is set, even if not in current environment
    _load_env_var_from_files(
        "LLM_PROVIDER",
        [Path(".env"), Path("minicon/.env")],
    )

    # Check environment variables
    required_vars = {
        "OPENAI_API_KEY": "OpenAI API Key",
        "LLM_PROVIDER": "LLM Provider (openai/ollama/gemini)",
    }

    print("\n📋 Environment Check:")
    all_present = True
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            if "KEY" in var:
                print(f"  ✓ {description}: Set (length: {len(value)})")
            else:
                print(f"  ✓ {description}: {value}")
        else:
            print(f"  ✗ {description}: Not set")
            all_present = False

    if not all_present:
        print("\n❌ Missing required environment variables.")
        return False

    # Test LLM client initialization
    print("\n🔧 Client Initialization:")
    try:
        client = LLMClient()
        print(
            f"  ✓ LLMClient initialized: provider={client.provider}, model={client.model}"
        )
    except Exception as e:
        print(f"  ✗ LLMClient initialization failed: {e}")
        return False

    # Test basic completion (lightweight)
    print("\n🚀 Basic Completion Test:")
    try:
        response = client.complete("Say 'Hello' in exactly 6 characters.")
        if response and len(response.strip()) > 0:
            print(f"  ✓ Response received: '{response.strip()}'")
            return True
        print("  ✗ Empty or invalid response")
        return False
    except Exception as e:
        print(f"  ✗ Completion failed: {e}")
        return False


def main() -> int:
    """Run streamlined connectivity tests."""
    success = test_provider_connectivity()

    print("\n" + "=" * 40)
    if success:
        print("✅ CONNECTIVITY TEST PASSED")
        print("🎉 Provider is ready for use!")
        return 0
    print("❌ CONNECTIVITY TEST FAILED")
    print("💡 Check your API keys and network configuration.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
