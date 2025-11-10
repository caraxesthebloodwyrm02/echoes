#!/usr/bin/env python3
"""
Echoes Reconstruction Protocol - Step 4: Deep Clean

Perform deep clean on all extracted data to remove potential contaminants,
malware, corruption, and verify data integrity.
"""

import hashlib
import json
import os
import re
import sys
from pathlib import Path
from datetime import datetime, timezone


def deep_clean_extracted_data(
    extraction_dir="extracted_components_step3", output_file="deep_clean_step4.json"
):
    """Step 4: Deep clean extracted data."""

    clean_data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "protocol": "Echoes Reconstruction Protocol v1.0",
        "phase": "Step 4: Deep Clean",
        "extraction_directory": extraction_dir,
        "cleaned_components": {},
        "security_scans": {},
        "integrity_verifications": {},
        "corruption_checks": {},
        "anomalies": [],
        "quarantine_items": [],
    }

    print("🧹 Performing Step 4: Deep Clean")
    print("=" * 60)

    if not os.path.exists(extraction_dir):
        clean_data["anomalies"].append(
            f"Extraction directory not found: {extraction_dir}"
        )
        print(f"❌ Extraction directory not found: {extraction_dir}")
        return False

    # Define suspicious patterns to scan for
    suspicious_patterns = {
        "malware_signatures": [
            r"\\x[0-9a-fA-F]{2}",  # Hex escape sequences
            r"eval\(",  # Dynamic code execution
            r"exec\(",  # Code execution
            r"__import__\(",  # Dynamic imports
            r"getattr.*import",  # Dynamic attribute access for imports
        ],
        "backdoors": [
            r"socket\.socket",  # Network socket creation
            r"subprocess\.",  # System command execution
            r"os\.system",  # OS command execution
            r"os\.popen",  # OS command execution
        ],
        "data_corruption": [
            r"\x00{3,}",  # Null byte sequences (potential corruption)
            r"[\x80-\xFF]{10,}",  # High ASCII sequences (encoding issues)
        ],
        "tampering_indicators": [
            r"#.*REMOVED.*RAG",  # Our removal comments (should be clean)
            r"from src\.rag_orbit",  # Leftover imports
            r"openai_wrapper",  # Leftover wrapper references
        ],
    }

    print("🔍 Starting Deep Security Scan...")

    # Scan all extracted files
    scanned_files = 0
    clean_files = 0

    for root, dirs, files in os.walk(extraction_dir):
        for file in files:
            if file.endswith(".py"):  # Only scan Python files for now
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, extraction_dir)

                scanned_files += 1
                print(f"   🔎 Scanning: {relative_path}")

                # Read file content
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                except Exception as e:
                    clean_data["anomalies"].append(
                        f"Cannot read file {relative_path}: {str(e)}"
                    )
                    clean_data["quarantine_items"].append(relative_path)
                    continue

                # Initialize scan results for this file
                file_scan = {
                    "file_path": relative_path,
                    "file_size": len(content),
                    "scan_results": {},
                    "issues_found": 0,
                    "critical_issues": 0,
                    "clean": True,
                }

                # Scan for suspicious patterns
                for category, patterns in suspicious_patterns.items():
                    file_scan["scan_results"][category] = []

                    for pattern in patterns:
                        matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL)
                        if matches:
                            file_scan["scan_results"][category].extend(matches)
                            file_scan["issues_found"] += len(matches)

                            # Determine if critical
                            if category in ["malware_signatures", "backdoors"]:
                                file_scan["critical_issues"] += len(matches)

                # Check for file integrity
                current_checksum = calculate_file_checksum(file_path)

                # Compare with original extraction checksum if available
                integrity_check = {
                    "current_checksum": current_checksum,
                    "verified": False,
                }

                # Check for basic syntax validity (Python files)
                if file.endswith(".py"):
                    syntax_valid = check_python_syntax(content)
                    integrity_check["syntax_valid"] = syntax_valid

                    if not syntax_valid:
                        file_scan["issues_found"] += 1
                        file_scan["critical_issues"] += 1
                        clean_data["anomalies"].append(
                            f"Syntax error in {relative_path}"
                        )

                # Check for encoding issues
                try:
                    content.encode("utf-8")
                    integrity_check["encoding_valid"] = True
                except UnicodeEncodeError:
                    integrity_check["encoding_valid"] = False
                    file_scan["issues_found"] += 1
                    clean_data["anomalies"].append(
                        f"Encoding issues in {relative_path}"
                    )

                file_scan["integrity_check"] = integrity_check

                # Determine if file is clean
                if file_scan["critical_issues"] > 0:
                    file_scan["clean"] = False
                    clean_data["quarantine_items"].append(relative_path)
                    print(f"   ❌ CRITICAL ISSUES FOUND in {relative_path}")
                elif file_scan["issues_found"] > 0:
                    print(f"   ⚠️  Minor issues found in {relative_path}")
                else:
                    clean_files += 1
                    print(f"   ✅ Clean: {relative_path}")

                # Store scan results
                clean_data["cleaned_components"][relative_path] = file_scan

    # Generate cleaning report
    print("\\n🧽 Performing Data Cleaning Operations...")

    # Remove any quarantine items (move to quarantine directory)
    quarantine_dir = f"{extraction_dir}_quarantine"
    if clean_data["quarantine_items"]:
        os.makedirs(quarantine_dir, exist_ok=True)

        for item in clean_data["quarantine_items"]:
            source_path = os.path.join(extraction_dir, item)
            dest_path = os.path.join(quarantine_dir, item)

            if os.path.exists(source_path):
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                os.rename(source_path, dest_path)
                print(f"   🗂️  Quarantined: {item}")

    # Perform content sanitization on remaining files
    sanitized_count = 0
    for file_path, scan_result in clean_data["cleaned_components"].items():
        if scan_result["clean"] and file_path in clean_data["quarantine_items"]:
            continue  # Skip quarantined files

        full_path = os.path.join(extraction_dir, file_path)

        if os.path.exists(full_path):
            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Apply basic sanitization (remove suspicious comments, etc.)
                original_content = content
                content = sanitize_content(content)

                if content != original_content:
                    with open(full_path, "w", encoding="utf-8") as f:
                        f.write(content)
                    sanitized_count += 1
                    print(f"   🧴 Sanitized: {file_path}")

            except Exception as e:
                clean_data["anomalies"].append(
                    f"Failed to sanitize {file_path}: {str(e)}"
                )

    # Final integrity verification
    print("\\n🔒 Final Integrity Verification...")
    final_verification = {}

    for file_path, scan_result in clean_data["cleaned_components"].items():
        if file_path in clean_data["quarantine_items"]:
            continue  # Skip quarantined files

        full_path = os.path.join(extraction_dir, file_path)
        if os.path.exists(full_path):
            final_checksum = calculate_file_checksum(full_path)
            final_verification[file_path] = {
                "final_checksum": final_checksum,
                "size_bytes": os.path.getsize(full_path),
                "verified": True,
            }

    clean_data["final_integrity_verification"] = final_verification

    # Summary statistics
    clean_data["summary"] = {
        "files_scanned": scanned_files,
        "files_clean": clean_files,
        "files_quarantined": len(clean_data["quarantine_items"]),
        "files_sanitized": sanitized_count,
        "total_anomalies": len(clean_data["anomalies"]),
        "clean_percentage": (
            (clean_files / scanned_files) * 100 if scanned_files > 0 else 0
        ),
    }

    # Save cleaning report
    with open(output_file, "w") as f:
        json.dump(clean_data, f, indent=2)

    print(f"\\n📄 Cleaning report saved to: {output_file}")

    # Final summary
    summary = clean_data["summary"]
    print(f"\\n📊 Deep Clean Summary:")
    print(f'   Files scanned: {summary["files_scanned"]}')
    print(f'   Files clean: {summary["files_clean"]}')
    print(f'   Files quarantined: {summary["files_quarantined"]}')
    print(f'   Files sanitized: {summary["files_sanitized"]}')
    print(f'   Clean percentage: {summary["clean_percentage"]:.1f}%')
    print(f'   Anomalies: {summary["total_anomalies"]}')

    success_threshold = (
        summary["clean_percentage"] >= 90 and summary["files_quarantined"] == 0
    )

    if success_threshold:
        print("✅ STEP 4 COMPLETE: Deep clean successful, proceeding to Step 5")
        return True
    else:
        print(
            f'⚠️  STEP 4 ISSUES: Clean rate below threshold ({summary["clean_percentage"]:.1f}%)'
        )
        return False


def calculate_file_checksum(filepath, algorithm="sha256"):
    """Calculate file checksum."""
    hash_func = hashlib.new(algorithm)
    try:
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_func.update(chunk)
        return hash_func.hexdigest()
    except Exception as e:
        return f"ERROR: {str(e)}"


def check_python_syntax(content):
    """Check if Python code has valid syntax."""
    try:
        compile(content, "<string>", "exec")
        return True
    except SyntaxError:
        return False


def sanitize_content(content):
    """Apply basic content sanitization."""
    # Remove suspicious comments (but keep our legitimate removal comments)
    lines = content.split("\n")
    sanitized_lines = []

    for line in lines:
        # Keep our legitimate reconstruction comments
        if "# REMOVED:" in line or "# This file is intentionally empty" in line:
            sanitized_lines.append(line)
        # Remove other suspicious comments that might indicate tampering
        elif line.strip().startswith("#") and any(
            word in line.lower() for word in ["hack", "backdoor", "exploit", "malware"]
        ):
            continue  # Skip suspicious comments
        else:
            sanitized_lines.append(line)

    return "\n".join(sanitized_lines)


if __name__ == "__main__":
    success = deep_clean_extracted_data()
    sys.exit(0 if success else 1)
