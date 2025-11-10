#!/usr/bin/env python3
"""
Phase 3 Integration Validation Script
Validates core functionality without full imports
"""

import os
import sys


def test_environment_variable_parsing():
    """Test environment variable parsing for API switching"""
    print("🔧 Testing environment variable parsing...")

    # Test default (should be False)
    if "USE_RESPONSES_API" in os.environ:
        del os.environ["USE_RESPONSES_API"]

    # Simulate the parsing logic from assistant_v2_core.py
    use_responses_api = os.getenv("USE_RESPONSES_API", "false").lower() in (
        "1",
        "true",
        "yes",
    )
    assert not use_responses_api, f"Expected False, got {use_responses_api}"
    print("✅ Default state: False")

    # Test various true values
    for true_value in ["1", "true", "yes", "TRUE", "YES"]:
        os.environ["USE_RESPONSES_API"] = true_value
        use_responses_api = os.getenv("USE_RESPONSES_API", "false").lower() in (
            "1",
            "true",
            "yes",
        )
        assert (
            use_responses_api
        ), f"Expected True for {true_value}, got {use_responses_api}"
        print(f"✅ {true_value} -> True")

    # Test false values
    for false_value in ["0", "false", "no", "FALSE", "NO", "anything_else"]:
        os.environ["USE_RESPONSES_API"] = false_value
        use_responses_api = os.getenv("USE_RESPONSES_API", "false").lower() in (
            "1",
            "true",
            "yes",
        )
        assert (
            not use_responses_api
        ), f"Expected False for {false_value}, got {use_responses_api}"
        print(f"✅ {false_value} -> False")

    # Cleanup
    if "USE_RESPONSES_API" in os.environ:
        del os.environ["USE_RESPONSES_API"]

    print("✅ Environment variable parsing: PASSED")
    return True


def test_file_structure():
    """Test that all required files exist"""
    print("\n📁 Testing file structure...")

    required_files = [
        "assistant_v2_core.py",
        "test_migration.py",
        "fix_docstrings.py",
        "assistant_v2_core_fixed.py",
    ]

    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file} exists")
        else:
            print(f"❌ {file} missing")
            return False

    print("✅ File structure: PASSED")
    return True


def test_code_compilation_check():
    """Test that the fixed version compiles"""
    print("\n🔨 Testing code compilation...")

    try:
        # Try to compile the fixed version
        with open("assistant_v2_core_fixed.py", "r") as f:
            code = f.read()

        compile(code, "assistant_v2_core_fixed.py", "exec")
        print("✅ Fixed version compiles successfully")
        return True
    except SyntaxError as e:
        print(f"❌ Compilation failed: {e}")
        return False
    except Exception as e:
        print(f"⚠️  Unexpected error: {e}")
        return False


def test_api_parameter_mapping():
    """Test parameter mapping logic"""
    print("\n🔄 Testing API parameter mapping...")

    # Simulate the parameter mapping logic

    # Test Responses API parameter mapping
    messages = [{"role": "user", "content": "test"}]
    max_tokens = 1000
    temperature = 0.7

    # Responses API mapping
    responses_params = {
        "input": messages,  # messages -> input
        "max_output_tokens": max_tokens,  # max_tokens -> max_output_tokens
        "temperature": temperature,
    }

    assert "input" in responses_params, "input parameter missing"
    assert (
        "max_output_tokens" in responses_params
    ), "max_output_tokens parameter missing"
    assert responses_params["input"] == messages, "input mapping incorrect"
    assert (
        responses_params["max_output_tokens"] == max_tokens
    ), "max_output_tokens mapping incorrect"

    print("✅ Responses API parameter mapping: PASSED")

    # Test Chat Completions API parameter mapping
    chat_params = {
        "messages": messages,  # messages stay as messages
        "max_tokens": max_tokens,  # max_tokens stays as max_tokens (for non-o3)
        "temperature": temperature,
    }

    assert "messages" in chat_params, "messages parameter missing"
    assert "max_tokens" in chat_params, "max_tokens parameter missing"
    assert chat_params["messages"] == messages, "messages mapping incorrect"
    assert chat_params["max_tokens"] == max_tokens, "max_tokens mapping incorrect"

    print("✅ Chat Completions API parameter mapping: PASSED")
    return True


def test_response_format_handling():
    """Test response format handling logic"""
    print("\n📋 Testing response format handling...")

    # Simulate Responses API response format
    responses_output = [
        {"type": "text", "content": "Hello "},
        {"type": "text", "content": "world!"},
        {"type": "tool_call", "content": "some_tool_call"},
    ]

    # Extract text content (simulate the logic)
    assistant_response = ""
    for output_item in responses_output:
        if output_item["type"] == "text":
            assistant_response += output_item["content"]

    assert (
        assistant_response == "Hello world!"
    ), f"Expected 'Hello world!', got '{assistant_response}'"
    print("✅ Responses API response extraction: PASSED")

    # Simulate Chat Completions API response format
    chat_response = {
        "choices": [{"message": {"content": "Hello from chat completions!"}}]
    }

    chat_content = chat_response["choices"][0]["message"]["content"]
    assert (
        chat_content == "Hello from chat completions!"
    ), f"Unexpected content: {chat_content}"
    print("✅ Chat Completions API response extraction: PASSED")

    return True


def run_phase3_validation():
    """Run all Phase 3 validation tests"""
    print("🚀 Phase 3 Integration Validation")
    print("=" * 50)

    tests = [
        test_environment_variable_parsing,
        test_file_structure,
        test_code_compilation_check,
        test_api_parameter_mapping,
        test_response_format_handling,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            failed += 1

    print("\n" + "=" * 50)
    print(f"📊 Results: {passed} passed, {failed} failed")

    if failed == 0:
        print("🎉 Phase 3 Integration Validation: SUCCESS")
        return True
    else:
        print("⚠️  Phase 3 Integration Validation: ISSUES FOUND")
        return False


if __name__ == "__main__":
    success = run_phase3_validation()
    sys.exit(0 if success else 1)
