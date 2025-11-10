#!/usr/bin/env python3
"""
Echoes Reconstruction Protocol - Step 1: Data Integrity Verification

This script performs comprehensive integrity verification of all critical
components following the Echoes Reconstruction Protocol.
"""

import hashlib
import os
import json
import sys
from pathlib import Path
from datetime import datetime, timezone


def calculate_file_checksum(filepath, algorithm="sha256"):
    """Calculate checksum for a file."""
    hash_func = hashlib.new(algorithm)
    try:
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_func.update(chunk)
        return hash_func.hexdigest()
    except Exception as e:
        return f"ERROR: {str(e)}"


def verify_directory_integrity(base_path, output_file="integrity_check_step1.json"):
    """Verify integrity of critical files in the project."""
    integrity_data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "protocol": "Echoes Reconstruction Protocol v1.0",
        "phase": "Step 1: Data Integrity Verification",
        "files": {},
        "directories": [],
        "anomalies": [],
        "baseline_checksums": {
            # Expected checksums for known authentic files
            "api/main.py": "8f4d2e6c9b7a1f5e8d3a9c6b2e4f7a1",  # Placeholder - would be real checksums
            "api/pattern_detection.py": "5e8d3a9c6b2e4f7a1d5c8b9e2f6a3d",
            "api/self_rag.py": "9c6b2e4f7a1d5c8b9e2f6a3d4e7b8f5",
            "glimpse/sampler_openai.py": "2e4f7a1d5c8b9e2f6a3d4e7b8f5c9a",
            "glimpse/batch_helpers.py": "7a1d5c8b9e2f6a3d4e7b8f5c9a2e4f",
            "app/agents/agent.py": "1d5c8b9e2f6a3d4e7b8f5c9a2e4f7a",
            "app/agents/models.py": "8b9e2f6a3d4e7b8f5c9a2e4f7a1d5c",
        },
    }

    print("🔍 Performing Step 1: Data Integrity Verification")
    print("=" * 60)

    # Critical files to verify
    critical_files = [
        "api/main.py",
        "api/pattern_detection.py",
        "api/self_rag.py",
        "glimpse/sampler_openai.py",
        "glimpse/batch_helpers.py",
        "app/agents/agent.py",
        "app/agents/models.py",
    ]

    integrity_score = 0
    total_files = len(critical_files)

    for file_path in critical_files:
        full_path = os.path.join(base_path, file_path)
        if os.path.exists(full_path):
            checksum = calculate_file_checksum(full_path)
            expected_checksum = integrity_data["baseline_checksums"].get(
                file_path, "unknown"
            )

            integrity_data["files"][file_path] = {
                "checksum_sha256": checksum,
                "expected_checksum": expected_checksum,
                "size_bytes": os.path.getsize(full_path),
                "exists": True,
                "integrity_verified": (
                    checksum.startswith(expected_checksum[:16])
                    if expected_checksum != "unknown"
                    else "baseline_not_available"
                ),
            }

            if (
                checksum.startswith(expected_checksum[:16])
                and expected_checksum != "unknown"
            ):
                print(f"✅ {file_path}: INTEGRITY VERIFIED ({checksum[:16]}...)")
                integrity_score += 1
            else:
                print(
                    f"⚠️  {file_path}: CHECKSUM MISMATCH OR NO BASELINE ({checksum[:16]}...)"
                )
                integrity_data["anomalies"].append(f"Checksum mismatch for {file_path}")
        else:
            integrity_data["files"][file_path] = {
                "exists": False,
                "error": "File not found",
            }
            integrity_data["anomalies"].append(f"Critical file missing: {file_path}")
            print(f"❌ {file_path}: FILE NOT FOUND")

    # Check for middleware directories that should be removed
    middleware_dirs = ["src/rag_orbit", "openai_rag"]
    for mdir in middleware_dirs:
        if os.path.exists(os.path.join(base_path, mdir)):
            integrity_data["anomalies"].append(
                f"Middleware directory still exists: {mdir}"
            )
            print(f"⚠️  Middleware directory detected: {mdir}")
        else:
            print(f"✅ Middleware directory properly removed: {mdir}")

    # Get directory listing
    try:
        integrity_data["directories"] = [
            d
            for d in os.listdir(base_path)
            if os.path.isdir(os.path.join(base_path, d))
        ]
    except Exception as e:
        integrity_data["directories"] = []
        integrity_data["anomalies"].append(f"Could not list directories: {str(e)}")

    # Save integrity report
    with open(output_file, "w") as f:
        json.dump(integrity_data, f, indent=2)

    print(f"\n📄 Integrity report saved to: {output_file}")

    # Summary
    existing_files = sum(
        1 for f in integrity_data["files"].values() if f.get("exists", False)
    )
    anomalies = len(integrity_data["anomalies"])
    integrity_percentage = (integrity_score / total_files) * 100

    print(f"\n📊 Integrity Check Summary:")
    print(f"   Files checked: {total_files}")
    print(f"   Files present: {existing_files}")
    print(
        f"   Integrity verified: {integrity_score}/{total_files} ({integrity_percentage:.1f}%)"
    )
    print(f"   Anomalies: {anomalies}")

    if anomalies == 0 and integrity_percentage >= 80:
        print("✅ STEP 1 COMPLETE: Data integrity verified, proceeding to Step 2")
        return True
    else:
        print(
            f"⚠️  STEP 1 ISSUES: {anomalies} anomalies detected, integrity at {integrity_percentage:.1f}%"
        )
        return False


if __name__ == "__main__":
    base_path = "e:/Projects/Echoes"
    success = verify_directory_integrity(base_path)
    sys.exit(0 if success else 1)
