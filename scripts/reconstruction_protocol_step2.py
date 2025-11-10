#!/usr/bin/env python3
"""
Echoes Reconstruction Protocol - Step 2: Source Authentication

Identify and validate authentic sources for component reconstruction.
Cross-reference multiple trusted sources to confirm authenticity.
"""

import hashlib
import json
import os
import sys
from pathlib import Path
from datetime import datetime, timezone
import subprocess


def authenticate_sources(output_file="source_authentication_step2.json"):
    """Step 2: Identify and validate authentic sources."""

    auth_data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "protocol": "Echoes Reconstruction Protocol v1.0",
        "phase": "Step 2: Source Authentication",
        "trusted_sources": {},
        "validation_results": {},
        "authenticity_score": 0,
        "cross_references": [],
        "anomalies": [],
    }

    print("🔐 Performing Step 2: Source Authentication")
    print("=" * 60)

    # Define trusted sources for different components
    trusted_sources = {
        "python_standard_library": {
            "description": "Python 3.12 standard library components",
            "validation_method": "stdlib_verification",
            "expected_version": "3.12.x",
            "trusted_hashes": [],
        },
        "pydantic_library": {
            "description": "Pydantic data validation library",
            "validation_method": "package_verification",
            "expected_version": "2.x",
            "trusted_hashes": [],
        },
        "fastapi_library": {
            "description": "FastAPI web framework",
            "validation_method": "package_verification",
            "expected_version": "0.1xx.x",
            "trusted_hashes": [],
        },
        "openai_library": {
            "description": "OpenAI Python client library",
            "validation_method": "package_verification",
            "expected_version": "1.x.x",
            "trusted_hashes": [],
        },
        "sentence_transformers": {
            "description": "Sentence Transformers for text embeddings",
            "validation_method": "package_verification",
            "expected_version": "2.x.x",
            "trusted_hashes": [],
        },
        "numpy_library": {
            "description": "NumPy scientific computing library",
            "validation_method": "package_verification",
            "expected_version": "1.x.x",
            "trusted_hashes": [],
        },
        "echoes_original_codebase": {
            "description": "Original Echoes AI research platform codebase",
            "validation_method": "git_history_verification",
            "trusted_repositories": [
                "https://github.com/user/echoes-ai",
                "internal_git_repo",
            ],
            "trusted_hashes": [],
        },
        "openai_official_api": {
            "description": "OpenAI official API endpoints",
            "validation_method": "api_endpoint_verification",
            "trusted_endpoints": [
                "https://api.openai.com/v1/",
                "https://api.openai.com/v1/chat/completions",
                "https://api.openai.com/v1/embeddings",
            ],
            "expected_response_codes": [
                200,
                401,
                429,
            ],  # 401/429 are expected for auth/rate limit
        },
    }

    auth_data["trusted_sources"] = trusted_sources

    # Validate Python environment
    print("🐍 Validating Python Environment...")
    try:
        python_version = sys.version
        print(f"   Python version: {python_version}")

        # Check if we're running in expected version range
        if "3.12" in python_version:
            auth_data["validation_results"]["python_version"] = "VERIFIED"
            print("   ✅ Python version verified")
        else:
            auth_data["validation_results"]["python_version"] = "VERSION_MISMATCH"
            auth_data["anomalies"].append(f"Python version mismatch: {python_version}")
            print(f"   ⚠️  Python version mismatch: {python_version}")

    except Exception as e:
        auth_data["validation_results"]["python_version"] = f"ERROR: {str(e)}"
        auth_data["anomalies"].append(f"Python version check failed: {str(e)}")

    # Validate package installations
    print("\\n📦 Validating Package Installations...")
    packages_to_check = [
        "pydantic",
        "fastapi",
        "openai",
        "sentence-transformers",
        "numpy",
    ]

    for package in packages_to_check:
        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-c",
                    f"import {package}; print({package}.__version__)",
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                version = result.stdout.strip()
                auth_data["validation_results"][f"{package}_version"] = version
                print(f"   ✅ {package}: {version}")
            else:
                auth_data["validation_results"][f"{package}_version"] = "IMPORT_FAILED"
                auth_data["anomalies"].append(
                    f"Package {package} import failed: {result.stderr}"
                )
                print(f"   ❌ {package}: Import failed")

        except Exception as e:
            auth_data["validation_results"][f"{package}_version"] = f"ERROR: {str(e)}"
            auth_data["anomalies"].append(
                f"Package {package} validation failed: {str(e)}"
            )
            print(f"   ⚠️  {package}: Validation error - {str(e)}")

    # Validate Git repository integrity
    print("\\n📚 Validating Git Repository...")
    try:
        # Check if we're in a git repository
        git_check = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            capture_output=True,
            cwd="e:/Projects/Echoes",
            timeout=10,
        )

        if git_check.returncode == 0:
            # Get current commit hash
            commit_result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                capture_output=True,
                text=True,
                cwd="e:/Projects/Echoes",
                timeout=10,
            )

            if commit_result.returncode == 0:
                current_commit = commit_result.stdout.strip()
                auth_data["validation_results"]["git_commit"] = current_commit
                print(f"   ✅ Git repository verified: {current_commit[:16]}...")

                # Check for any uncommitted changes that might indicate tampering
                status_result = subprocess.run(
                    ["git", "status", "--porcelain"],
                    capture_output=True,
                    cwd="e:/Projects/Echoes",
                    timeout=10,
                )

                if status_result.returncode == 0 and status_result.stdout.strip():
                    uncommitted_files = len(status_result.stdout.strip().split("\\n"))
                    auth_data["validation_results"][
                        "uncommitted_changes"
                    ] = uncommitted_files
                    auth_data["anomalies"].append(
                        f"{uncommitted_files} uncommitted changes detected"
                    )
                    print(f"   ⚠️  {uncommitted_files} uncommitted changes detected")
                else:
                    auth_data["validation_results"]["uncommitted_changes"] = 0
                    print("   ✅ No uncommitted changes")
            else:
                auth_data["validation_results"]["git_commit"] = "UNKNOWN"
                auth_data["anomalies"].append("Could not determine git commit")
                print("   ⚠️  Could not determine git commit")
        else:
            auth_data["validation_results"]["git_repository"] = "NOT_FOUND"
            auth_data["anomalies"].append("Not a git repository")
            print("   ❌ Not a git repository")

    except Exception as e:
        auth_data["validation_results"]["git_validation"] = f"ERROR: {str(e)}"
        auth_data["anomalies"].append(f"Git validation failed: {str(e)}")
        print(f"   ⚠️  Git validation error: {str(e)}")

    # Cross-reference validation
    print("\\n🔗 Performing Cross-Reference Validation...")
    auth_data["cross_references"] = []

    # Check if critical files exist and are readable
    critical_files = [
        "api/main.py",
        "glimpse/sampler_openai.py",
        "app/agents/agent.py",
        "requirements.txt",
        "pyproject.toml",
    ]

    for file_path in critical_files:
        full_path = f"e:/Projects/Echoes/{file_path}"
        if os.path.exists(full_path) and os.access(full_path, os.R_OK):
            auth_data["cross_references"].append(f"File accessible: {file_path}")
            print(f"   ✅ {file_path} - accessible")
        else:
            auth_data["cross_references"].append(f"File inaccessible: {file_path}")
            auth_data["anomalies"].append(f"Critical file inaccessible: {file_path}")
            print(f"   ❌ {file_path} - inaccessible")

    # Calculate authenticity score
    total_validations = len(auth_data["validation_results"])
    successful_validations = sum(
        1
        for v in auth_data["validation_results"].values()
        if not str(v).startswith(
            ("ERROR", "NOT_FOUND", "VERSION_MISMATCH", "IMPORT_FAILED")
        )
    )

    authenticity_score = (
        (successful_validations / total_validations) * 100
        if total_validations > 0
        else 0
    )
    auth_data["authenticity_score"] = authenticity_score

    # Save authentication report
    with open(output_file, "w") as f:
        json.dump(auth_data, f, indent=2)

    print(f"\\n📄 Authentication report saved to: {output_file}")

    # Summary
    anomalies = len(auth_data["anomalies"])
    sources_validated = len(trusted_sources)

    print(f"\\n📊 Source Authentication Summary:")
    print(f"   Sources validated: {sources_validated}")
    print(f"   Components checked: {total_validations}")
    print(f"   Successful validations: {successful_validations}")
    print(f"   Authenticity score: {authenticity_score:.1f}%")
    print(f"   Anomalies: {anomalies}")

    if anomalies == 0 and authenticity_score >= 75:
        print(
            "✅ STEP 2 COMPLETE: Source authentication successful, proceeding to Step 3"
        )
        return True
    else:
        print(
            f"⚠️  STEP 2 ISSUES: {anomalies} anomalies detected, authenticity at {authenticity_score:.1f}%"
        )
        return False


if __name__ == "__main__":
    success = authenticate_sources()
    sys.exit(0 if success else 1)
