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

# MIT License
#
# Copyright (c) 2025 Echoes Project

"""
Configuration Validation Tool
Validates all settings for stability and security issues
"""

import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def validate_workspace_config():
    """Validate workspace configuration"""
    print("=" * 70)
    print("CONFIGURATION VALIDATION REPORT")
    print("=" * 70)
    print()

    issues = []
    warnings = []
    successes = []

    # Check 1: Validate packages/core/config
    print("1. Checking packages/core/config/__init__.py...")
    try:
        from packages.core.config import Config

        # Check if extra="forbid" is set
        config_source = Path("packages/core/config/__init__.py").read_text()
        if 'extra="forbid"' in config_source or "extra='forbid'" in config_source:
            successes.append("[PASS] Security: extra='forbid' is set (CRITICAL FIX)")
        elif 'extra="allow"' in config_source or "extra='allow'" in config_source:
            issues.append("[FAIL] CRITICAL: extra='allow' found - security risk!")
        else:
            warnings.append("[WARN] Could not determine extra field policy")

        # Try to instantiate
        try:
            cfg = Config()
            successes.append("[PASS] Config loads successfully")
        except Exception as e:
            warnings.append(f"[WARN] Config load issue: {e}")
    except Exception as e:
        issues.append(f"✗ Cannot import Config: {e}")

    print()

    # Check 2: Validate workspace settings
    print("2. Checking config/workspace_settings.py...")
    try:
        from config.workspace_settings import get_settings, validate_workspace_settings

        successes.append("[PASS] workspace_settings module imports successfully")

        # Get settings
        try:
            settings = get_settings()
            successes.append("[PASS] Unified settings loads successfully")

            # Validate
            report = validate_workspace_settings()

            if report["status"] == "OK":
                successes.append("[PASS] All workspace settings validated")
            else:
                for problem in report.get("problems", []):
                    if problem["severity"] == "CRITICAL":
                        issues.append(
                            f"[FAIL] CRITICAL: {problem['setting']} - {problem['issue']}"
                        )
                    elif problem["severity"] == "HIGH":
                        warnings.append(
                            f"[WARN] HIGH: {problem['setting']} - {problem['issue']}"
                        )
                    else:
                        warnings.append(
                            f"[WARN] {problem['severity']}: {problem['setting']} - {problem['issue']}"
                        )

        except Exception as e:
            warnings.append(f"[WARN] Settings validation issue: {e}")

    except ImportError:
        warnings.append("[WARN] workspace_settings not available (optional)")
    except Exception as e:
        issues.append(f"[FAIL] workspace_settings error: {e}")

    print()

    # Check 3: Validate Windsurf config
    print("3. Checking .windsurf/config.json...")
    windsurf_config = Path(".windsurf/config.json")
    if windsurf_config.exists():
        try:
            import json

            config_data = json.loads(windsurf_config.read_text())

            # Check timeout settings
            if "stability" in config_data:
                stability = config_data["stability"]
                if stability.get("max_response_time_ms", 0) > 0:
                    successes.append(
                        f"[PASS] Response timeout: {stability['max_response_time_ms']}ms"
                    )
                if stability.get("request_timeout_ms", 0) > 0:
                    successes.append(
                        f"[PASS] Request timeout: {stability['request_timeout_ms']}ms"
                    )
                if stability.get("max_memory_mb", 0) > 0:
                    successes.append(
                        f"[PASS] Memory limit: {stability['max_memory_mb']}MB"
                    )

            # Check AI settings
            if "ai" in config_data:
                ai = config_data["ai"]
                if "rate_limit" in ai:
                    rate = ai["rate_limit"]
                    successes.append(
                        f"[PASS] Rate limit: {rate.get('requests_per_minute', 0)} req/min"
                    )

        except Exception as e:
            warnings.append(f"[WARN] Windsurf config parse error: {e}")
    else:
        warnings.append("[WARN] .windsurf/config.json not found (optional)")

    print()

    # Check 4: Validate agent knowledge layer
    print("4. Checking ai_agents/agent_knowledge_layer.py...")
    try:
        from utils.safe_imports import get_safe_agent_knowledge_layer

        successes.append("[PASS] Safe agent knowledge layer imports successfully")

        # Try to instantiate
        try:
            akl = get_safe_agent_knowledge_layer(enable_kg=False)  # Test without KG
            stats = akl.get_stats()
            successes.append(
                f"[PASS] Safe agent knowledge layer instantiates (KG: {stats['enabled']})"
            )
        except Exception as e:
            warnings.append(f"[WARN] Agent knowledge layer instantiation issue: {e}")

    except ImportError as e:
        warnings.append(f"[WARN] Safe agent knowledge layer not available: {e}")
    except Exception as e:
        issues.append(f"[FAIL] Agent knowledge layer error: {e}")

    print()

    # Check 5: Validate orchestrator integration
    print("5. Checking ai_agents/orchestrator.py integration...")
    try:
        from ai_agents.orchestrator import AIAgentOrchestrator

        successes.append("[PASS] AIAgentOrchestrator imports successfully")

        # Try to instantiate with knowledge layer
        try:
            orch = AIAgentOrchestrator(enable_knowledge_layer=False)
            if hasattr(orch, "knowledge_layer"):
                successes.append("[PASS] Orchestrator has knowledge_layer attribute")
            else:
                warnings.append("[WARN] Orchestrator missing knowledge_layer attribute")
        except Exception as e:
            warnings.append(f"[WARN] Orchestrator instantiation issue: {e}")

    except ImportError as e:
        issues.append(f"[FAIL] Cannot import AIAgentOrchestrator: {e}")
    except Exception as e:
        issues.append(f"[FAIL] Orchestrator error: {e}")

    print()

    # Print results
    print("=" * 70)
    print("VALIDATION RESULTS")
    print("=" * 70)
    print()

    if successes:
        print(f"SUCCESSES ({len(successes)}):")
        for success in successes:
            print(f"  {success}")
        print()

    if warnings:
        print(f"WARNINGS ({len(warnings)}):")
        for warning in warnings:
            print(f"  {warning}")
        print()

    if issues:
        print(f"CRITICAL ISSUES ({len(issues)}):")
        for issue in issues:
            print(f"  {issue}")
        print()

    # Summary
    print("=" * 70)
    if issues:
        print("STATUS: FAILED - Critical issues found")
        print(f"Action Required: Fix {len(issues)} critical issue(s)")
        return False
    elif warnings:
        print("STATUS: WARNINGS - Minor issues or optional features")
        print(f"Review: {len(warnings)} warning(s)")
        return True
    else:
        print("STATUS: PASSED - All validations successful")
        print(f"Successes: {len(successes)}")
        return True


if __name__ == "__main__":
    print()
    success = validate_workspace_config()
    print()

    sys.exit(0 if success else 1)
