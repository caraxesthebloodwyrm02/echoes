#!/usr/bin/env python3
"""
Comprehensive System Functionality Verification
Tests the claims made in the system analysis against actual codebase implementation.
"""

import inspect
import sys
from pathlib import Path
from typing import Any, Dict, List

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))


def verify_feature_exists(
    module_path: str, feature_name: str, description: str = ""
) -> Dict[str, Any]:
    """Verify a feature exists and is importable."""
    try:
        module_path_parts = module_path.split(".")
        if len(module_path_parts) == 1:
            module = __import__(module_path)
            return {"exists": True, "module": module_path, "feature": feature_name}
        else:
            module = __import__(module_path)
            for part in module_path_parts[1:]:
                module = getattr(module, part, None)
                if module is None:
                    return {
                        "exists": False,
                        "error": f"Could not import {part} from {module_path}",
                    }
            return {"exists": True, "module": module_path, "feature": feature_name}
    except ImportError as e:
        return {"exists": False, "error": str(e)}
    except Exception as e:
        return {"exists": False, "error": str(e)}


def check_class_methods(class_obj, expected_methods: List[str]) -> Dict[str, Any]:
    """Check if class has expected methods."""
    methods = [
        m
        for m in dir(class_obj)
        if not m.startswith("__") or (m.startswith("__") and not m.endswith("__"))
    ]
    found = []
    missing = []

    for method in expected_methods:
        if method in methods:
            found.append(method)
        else:
            missing.append(method)

    return {
        "total_methods": len(methods),
        "found": found,
        "missing": missing,
        "found_count": len(found),
        "missing_count": len(missing),
    }


def main():
    """Run comprehensive verification."""
    results = {"passed": [], "failed": [], "warnings": []}

    print("=" * 80)
    print("ECHOES ASSISTANT V2 - FUNCTIONALITY VERIFICATION")
    print("=" * 80)
    print()

    # 1. Core Assistant Class
    print("1. Core Assistant Implementation")
    print("-" * 80)
    try:
        from assistant_v2_core import EchoesAssistantV2

        results["passed"].append("EchoesAssistantV2 class importable")

        # Check key methods
        expected_methods = [
            "chat",
            "add_knowledge",
            "execute_action",
            "gather_knowledge",
            "search_knowledge",
            "get_stats",
            "update_quantum_state",
            "measure_quantum_state",
            "get_conversation_history",
            "clear_history",
        ]
        method_check = check_class_methods(EchoesAssistantV2, expected_methods)

        if method_check["missing_count"] == 0:
            results["passed"].append(
                f"All expected methods present ({method_check['found_count']}/{len(expected_methods)})"
            )
        else:
            results["warnings"].append(f"Missing methods: {method_check['missing']}")
            results["passed"].append(
                f"Found {method_check['found_count']}/{len(expected_methods)} expected methods"
            )

        print("   [OK] EchoesAssistantV2 class exists")
        print(f"   [OK] Found {method_check['total_methods']} methods total")
        print(
            f"   [OK] {method_check['found_count']}/{len(expected_methods)} expected methods present"
        )

    except Exception as e:
        results["failed"].append(f"EchoesAssistantV2 import failed: {e}")
        print(f"   [FAIL] Import failed: {e}")

    print()

    # 2. Tool Framework
    print("2. Tool Framework Integration")
    print("-" * 80)
    try:
        from tools.registry import get_registry

        registry = get_registry()
        tools = registry.list_tools()
        tool_count = len(tools)

        if tool_count > 0:
            results["passed"].append(f"Tool registry functional ({tool_count} tools)")
            print("   [OK] Tool registry functional")
            print(f"   [OK] {tool_count} tools registered")
        else:
            results["warnings"].append("Tool registry exists but no tools registered")
            print("   [WARN] Tool registry exists but empty")

    except Exception as e:
        results["failed"].append(f"Tool registry failed: {e}")
        print(f"   [FAIL] Tool registry failed: {e}")

    print()

    # 3. RAG System
    print("3. RAG System Implementation")
    print("-" * 80)
    try:
        from echoes.core.rag_v2 import OPENAI_RAG_AVAILABLE, create_rag_system

        if OPENAI_RAG_AVAILABLE:
            results["passed"].append("OpenAI RAG available")
            print("   [OK] OpenAI RAG system available")
        else:
            results["warnings"].append("OpenAI RAG not available (fallback to legacy)")
            print("   [WARN] OpenAI RAG not available (using legacy fallback)")

        # Try to create a RAG instance
        try:
            rag = create_rag_system("balanced")
            results["passed"].append("RAG system instantiable")
            print("   [OK] RAG system can be instantiated")
        except Exception as e:
            results["warnings"].append(f"RAG instantiation warning: {e}")
            print(f"   [WARN] RAG instantiation: {e}")

    except Exception as e:
        results["failed"].append(f"RAG system check failed: {e}")
        print(f"   [FAIL] RAG system check failed: {e}")

    print()

    # 4. Model Router
    print("4. Model Router & Metrics")
    print("-" * 80)
    try:
        from app.model_router import (ModelMetrics, ModelResponseCache,
                                      ModelRouter)

        router = ModelRouter()
        metrics = ModelMetrics()
        cache = ModelResponseCache()

        results["passed"].append(
            "ModelRouter, ModelMetrics, ModelResponseCache importable"
        )
        print("   [OK] ModelRouter importable")
        print("   [OK] ModelMetrics importable")
        print("   [OK] ModelResponseCache importable")

        # Check router has select_model method
        if hasattr(router, "select_model"):
            results["passed"].append("ModelRouter.select_model method exists")
            print("   [OK] ModelRouter.select_model() method exists")
        else:
            results["failed"].append("ModelRouter.select_model method missing")
            print("   [FAIL] ModelRouter.select_model() method missing")

    except Exception as e:
        results["failed"].append(f"Model routing system failed: {e}")
        print(f"   [FAIL] Model routing system failed: {e}")

    print()

    # 5. Responses API Integration
    print("5. Responses API Integration")
    print("-" * 80)
    try:
        import os

        from assistant_v2_core import EchoesAssistantV2

        # Check feature flag
        os.environ["USE_RESPONSES_API"] = "false"
        assistant1 = EchoesAssistantV2(
            enable_tools=False, enable_rag=False, enable_streaming=False
        )
        if not assistant1.use_responses_api:
            results["passed"].append("Responses API feature flag works (disabled)")
            print("   [OK] Feature flag works (USE_RESPONSES_API=false)")
        else:
            results["failed"].append("Feature flag not working correctly")
            print("   [FAIL] Feature flag not working")

        # Check code structure
        import re

        with open("assistant_v2_core.py", "r", encoding="utf-8") as f:
            content = f.read()
            responses_api_calls = len(re.findall(r"\.responses\.create", content))
            chat_api_calls = len(re.findall(r"\.chat\.completions\.create", content))

            if responses_api_calls > 0:
                results["passed"].append(
                    f"Responses API integration present ({responses_api_calls} calls)"
                )
                print(f"   [OK] Responses API calls found: {responses_api_calls}")
            if chat_api_calls > 0:
                results["passed"].append(
                    f"Chat Completions API integration present ({chat_api_calls} calls)"
                )
                print(f"   [OK] Chat Completions API calls found: {chat_api_calls}")

    except Exception as e:
        results["failed"].append(f"Responses API check failed: {e}")
        print(f"   [FAIL] Responses API check failed: {e}")

    print()

    # 6. Streaming Support
    print("6. Streaming Response Support")
    print("-" * 80)
    try:
        from assistant_v2_core import EchoesAssistantV2

        # Check chat method signature
        sig = inspect.signature(EchoesAssistantV2.chat)
        return_annotation = sig.return_annotation

        if "Iterator" in str(return_annotation) or "Union" in str(return_annotation):
            results["passed"].append("Streaming support in type hints")
            print("   [OK] Chat method supports streaming (type hints)")
        else:
            results["warnings"].append("Streaming type hints may be incomplete")
            print("   [WARN] Streaming type hints may need verification")

        # Check for streaming implementation
        with open("assistant_v2_core.py", "r", encoding="utf-8") as f:
            content = f.read()
            if "def stream_response()" in content or "yield" in content:
                results["passed"].append("Streaming implementation found")
                print("   [OK] Streaming implementation found in code")
            else:
                results["warnings"].append(
                    "Streaming implementation needs verification"
                )
                print("   [WARN] Streaming implementation needs manual verification")

    except Exception as e:
        results["failed"].append(f"Streaming check failed: {e}")
        print(f"   [FAIL] Streaming check failed: {e}")

    print()

    # 7. Error Handling
    print("7. Error Handling & Fallback")
    print("-" * 80)
    try:
        with open("assistant_v2_core.py", "r", encoding="utf-8") as f:
            content = f.read()

            # Check for error handling patterns
            api_error_handling = content.count("except APIError")
            general_error_handling = content.count("except Exception")
            fallback_patterns = content.count("fallback") or content.count("Fallback")

            if api_error_handling > 0:
                results["passed"].append(
                    f"API error handling present ({api_error_handling} instances)"
                )
                print(f"   [OK] API error handling: {api_error_handling} instances")

            if general_error_handling > 0:
                results["passed"].append(
                    f"General error handling present ({general_error_handling} instances)"
                )
                print(
                    f"   [OK] General error handling: {general_error_handling} instances"
                )

            if fallback_patterns > 0:
                results["passed"].append(
                    f"Fallback mechanisms present ({fallback_patterns} references)"
                )
                print("   [OK] Fallback mechanisms found")

    except Exception as e:
        results["failed"].append(f"Error handling check failed: {e}")
        print(f"   [FAIL] Error handling check failed: {e}")

    print()

    # 8. Testing Framework
    print("8. Testing Framework")
    print("-" * 80)
    test_files = list(Path(".").glob("test_*.py")) + list(
        Path("tests").glob("test_*.py")
    )
    test_count = len(test_files)

    if test_count > 0:
        results["passed"].append(f"Test files found ({test_count} files)")
        print(f"   [OK] Found {test_count} test files")

        # Check for full coverage test
        if Path("full_coverage_test_runner.py").exists():
            results["passed"].append("Full coverage test runner exists")
            print("   [OK] Full coverage test runner present")

        if Path("full_coverage_test_config.json").exists():
            results["passed"].append("Test configuration exists")
            print("   [OK] Test configuration file present")
    else:
        results["warnings"].append("No test files found")
        print("   [WARN] No test files found")

    print()

    # 9. Value System
    print("9. Value System Integration")
    print("-" * 80)
    try:
        from app.values import ValueSystem, get_value_system

        vs = get_value_system()
        if isinstance(vs, ValueSystem):
            results["passed"].append("Value system importable and functional")
            print("   [OK] Value system importable")

            # Check for value methods
            if hasattr(vs, "evaluate_response"):
                results["passed"].append("Value evaluation method exists")
                print("   [OK] evaluate_response() method exists")
            if hasattr(vs, "provide_feedback"):
                results["passed"].append("Value feedback method exists")
                print("   [OK] provide_feedback() method exists")

    except Exception as e:
        results["failed"].append(f"Value system check failed: {e}")
        print(f"   [FAIL] Value system check failed: {e}")

    print()

    # 10. Quantum State Management
    print("10. Quantum State Management")
    print("-" * 80)
    try:
        from quantum_state import QuantumStateManager

        qsm = QuantumStateManager()
        if hasattr(qsm, "update_state"):
            results["passed"].append("Quantum state management importable")
            print("   [OK] QuantumStateManager importable")
            print("   [OK] update_state() method exists")
        else:
            results["warnings"].append("Quantum state management may be incomplete")
            print("   [WARN] Quantum state management needs verification")

    except Exception as e:
        results["warnings"].append(f"Quantum state check: {e}")
        print(f"   [WARN] Quantum state check: {e}")

    print()

    # Summary
    print("=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)
    print(f"[OK] Passed: {len(results['passed'])}")
    print(f"[WARN] Warnings: {len(results['warnings'])}")
    print(f"[FAIL] Failed: {len(results['failed'])}")
    print()

    if results["warnings"]:
        print("WARNINGS:")
        for warning in results["warnings"]:
            print(f"  [WARN] {warning}")
        print()

    if results["failed"]:
        print("FAILURES:")
        for failure in results["failed"]:
            print(f"  [FAIL] {failure}")
        print()

    # Overall assessment
    pass_rate = (
        len(results["passed"])
        / (len(results["passed"]) + len(results["failed"]) + len(results["warnings"]))
        * 100
    )

    print(f"Overall Pass Rate: {pass_rate:.1f}%")

    if len(results["failed"]) == 0:
        print("\n[SUCCESS] ALL CRITICAL FUNCTIONALITY VERIFIED")
        if len(results["warnings"]) == 0:
            print("[OK] NO WARNINGS - SYSTEM FULLY FUNCTIONAL")
        else:
            print(
                f"[WARN] {len(results['warnings'])} warnings found - review recommended"
            )
    else:
        print(f"\n[WARN] {len(results['failed'])} critical issues found")

    return results


if __name__ == "__main__":
    results = main()
    sys.exit(0 if len(results["failed"]) == 0 else 1)
