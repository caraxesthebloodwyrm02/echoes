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
Test script for ECHOES security scanner o1-preview integration
Tests the integration without making actual API calls
"""

import os
import sys

# Add the security directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "security"))

from scanner import O1PreviewSecurityAnalyzer, Vulnerability


def test_o1_validation_logic():
    """Test the o1-preview validation logic without API calls"""

    # Create test vulnerabilities
    test_vulns = [
        Vulnerability(
            tool="bandit",
            severity="low",
            title="Use of assert",
            description="Use of assert detected",
            file="test.py",
            line=10,
            cwe=None,
            confidence=0.8,
        ),
        Vulnerability(
            tool="semgrep",
            severity="high",
            title="SQL injection",
            description="Potential SQL injection vulnerability",
            file="api.py",
            line=25,
            cwe="CWE-89",
            confidence=0.6,
        ),
        Vulnerability(
            tool="bandit",
            severity="high",
            title="Hardcoded password",
            description="Possible hardcoded password",
            file="config.py",
            line=5,
            cwe=None,
            confidence=0.9,
        ),
        Vulnerability(
            tool="checkov",
            severity="medium",
            title="S3 bucket public access",
            description="S3 bucket allows public access",
            file="infra.tf",
            line=12,
            cwe=None,
            confidence=0.5,
        ),
    ]

    # Initialize analyzer
    analyzer = O1PreviewSecurityAnalyzer()

    # Test _requires_complex_analysis method
    print("Testing complex analysis detection...")

    complex_flags = []
    for i, vuln in enumerate(test_vulns):
        requires_complex = analyzer._requires_complex_analysis(vuln)
        complex_flags.append(requires_complex)
        print(f"  Vulnerability {i + 1} ({vuln.tool}): {'REQUIRES' if requires_complex else 'SKIPS'} complex analysis")
        print(f"    - Severity: {vuln.severity}, Confidence: {vuln.confidence}, CWE: {vuln.cwe}")

    # Verify expected results
    expected_complex = [
        False,
        True,
        True,
        True,
    ]  # vuln 2, 3, and 4 should be complex (high severity, CWE-89, low confidence)
    if complex_flags == expected_complex:
        print("Complex analysis detection working correctly")
    else:
        print(f"Complex analysis detection failed. Expected {expected_complex}, got {complex_flags}")
        return False

    # Test batch validation filtering
    print("\nTesting batch validation filtering...")
    batch_results = analyzer.batch_validate_vulnerabilities(test_vulns, max_workers=1)

    # Should only process complex vulnerabilities (indices 1, 2, 3)
    expected_keys = ["semgrep_1", "bandit_2", "checkov_3"]
    actual_keys = list(batch_results.keys())

    if set(actual_keys) == set(expected_keys):
        print("Batch validation filtering working correctly")
        print(f"   Processed {len(batch_results)} complex vulnerabilities")
    else:
        print(f"Batch validation filtering failed. Expected {expected_keys}, got {actual_keys}")
        return False

    # Test validation result structure
    for vuln_id, result in batch_results.items():
        required_fields = ["vulnerability_index", "validation", "original_vuln"]
        if not all(field in result for field in required_fields):
            print(f"Missing required fields in result for {vuln_id}")
            return False

        validation = result["validation"]
        if "is_valid" not in validation:
            print(f"Missing is_valid field in validation for {vuln_id}")
            return False

    print("Validation result structure correct")
    print("\nAll o1-preview integration tests passed!")
    return True


def test_vulnerability_dataclass():
    """Test the updated Vulnerability dataclass with o1_validation field"""

    print("\nTesting Vulnerability dataclass...")

    vuln = Vulnerability(
        tool="test",
        severity="medium",
        title="Test vulnerability",
        description="Test description",
        file="test.py",
        line=10,
        cwe="CWE-123",
        confidence=0.8,
        ai_analysis="Test AI analysis",
        o1_validation={"is_valid": True, "issue": None},
    )

    # Check all fields are accessible
    assert vuln.tool == "test"
    assert vuln.severity == "medium"
    assert vuln.o1_validation["is_valid"] == True
    assert vuln.o1_validation["issue"] is None

    print("Vulnerability dataclass working correctly")
    return True


if __name__ == "__main__":
    print("Testing ECHOES Security Scanner O1-Preview Integration\n")

    success = True

    try:
        success &= test_o1_validation_logic()
        success &= test_vulnerability_dataclass()

    except Exception as e:
        print(f"Test failed with exception: {e}")
        success = False

    if success:
        print("\nO1-preview integration is ready for deployment!")
        print("   Next: Test with actual API calls (requires valid OpenAI API key)")
    else:
        print("\nIntegration tests failed - please review implementation")
        sys.exit(1)
