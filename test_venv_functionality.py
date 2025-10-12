#!/usr/bin/env python3
"""Test OpenAI and API synchronization functionality."""

import importlib
import sys

# Ensure UTF-8 encoding for output
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    if sys.version_info >= (3, 7):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    else:
        import codecs

        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
        sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())


def test_openai() -> bool:
    """Test OpenAI import and basic functionality."""
    try:
        openai = importlib.import_module("openai")
        print(f"[OK] OpenAI version: {openai.__version__}")
        return True
    except ImportError as exc:
        print(f"[FAIL] OpenAI import failed: {exc}")
        return False


def test_cryptography() -> bool:
    """Test cryptography library."""
    try:
        importlib.import_module("cryptography")
        print("[OK] Cryptography available")
        return True
    except ImportError as exc:
        print(f"[FAIL] Cryptography import failed: {exc}")
        return False


def test_authlib() -> bool:
    """Test Authlib library."""
    try:
        importlib.import_module("authlib")
        print("[OK] Authlib available")
        return True
    except ImportError as exc:
        print(f"[FAIL] Authlib import failed: {exc}")
        return False


def test_llm_client() -> bool:
    """Test LLM client functionality."""
    try:
        from prompting.core.llm_client import LLMClient

        LLMClient()
        print("[OK] LLMClient import and instantiation successful")
        return True
    except Exception as exc:
        print(f"[FAIL] LLMClient test failed: {exc}")
        return False


def main() -> int:
    """Run all tests."""
    print("Testing .venv compatibility and functionality...")
    print()

    tests = [
        test_openai,
        test_cryptography,
        test_authlib,
        test_llm_client,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        print()

    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("SUCCESS: All functionality tests passed!")
        return 0

    print("WARNING: Some tests failed. Check dependencies.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
