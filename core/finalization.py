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

"""Finalization layer for trajectory analysis experiments.

Ensures determinism, integrity, security, and traceability of all artifacts.
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np


def get_git_commit() -> str:
    """Get current git commit SHA (7 chars)."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short=7", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
            timeout=5,
        )
        return result.stdout.strip()
    except (
        subprocess.CalledProcessError,
        subprocess.TimeoutExpired,
        FileNotFoundError,
    ):
        return "unknown"


def get_environment_fingerprint() -> str:
    """Generate secure environment digest."""
    env_data = {
        "os": platform.system(),
        "os_version": platform.version(),
        "python": sys.version,
        "numpy": np.__version__,
        "hostname_hash": hashlib.sha256(platform.node().encode()).hexdigest()[:16],
    }

    fingerprint = json.dumps(env_data, sort_keys=True).encode()
    return hashlib.sha256(fingerprint).hexdigest()[:16]


def compute_sha256(file_path: Path) -> str:
    """Compute SHA-256 checksum of file."""
    sha256_hash = hashlib.sha256()

    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)

    return sha256_hash.hexdigest()


def secure_write(file_path: Path, content: str | bytes, read_only: bool = True) -> None:
    """Atomic write with optional read-only enforcement.

    Uses tempfile → rename pattern to prevent partial writes.
    """
    import tempfile

    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    # Write to temp file first
    mode = "wb" if isinstance(content, bytes) else "w"
    encoding = None if isinstance(content, bytes) else "utf-8"

    with tempfile.NamedTemporaryFile(
        mode=mode, encoding=encoding, dir=file_path.parent, delete=False
    ) as tmp:
        tmp.write(content)
        tmp_path = Path(tmp.name)

    # Atomic rename
    tmp_path.replace(file_path)

    # Set read-only if requested
    if read_only and os.name != "nt":  # Skip on Windows (permission issues)
        os.chmod(file_path, 0o444)


def finalize_analysis(
    analysis_data: Dict[str, Any],
    git_commit: Optional[str] = None,
    out_dir: Path = Path("results"),
) -> Dict[str, Any]:
    """Finalize analysis with metadata, checksums, and security controls.

    Parameters
    ----------
    analysis_data
        Raw analysis output from run_experiment
    git_commit
        Git commit SHA (auto-detected if None)
    out_dir
        Output directory for finalized artifacts

    Returns
    -------
    dict
        Finalization summary with paths and checksums
    """
    # Get provenance data
    if git_commit is None:
        git_commit = get_git_commit()

    timestamp = analysis_data.get("timestamp", datetime.now(timezone.utc).isoformat())

    # Create experiment tag
    date_str = timestamp.split("T")[0]
    exp_tag = f"exp/{date_str}/{git_commit}"

    # Add finalization metadata
    finalized_data = {
        **analysis_data,
        "metadata": {
            "finalization": {
                "finalized_by": "o3",
                "finalized_at": datetime.now(timezone.utc).isoformat(),
                "git_commit": git_commit,
                "experiment_tag": exp_tag,
                "environment": f"secure-digest:{get_environment_fingerprint()}",
                "python_version": sys.version.split()[0],
                "numpy_version": np.__version__,
            }
        },
    }

    # Generate safe filename (replace colons with hyphens for Windows)
    safe_timestamp = timestamp.replace(":", "-")
    final_filename = f"{safe_timestamp}-analysis-final.json"
    final_path = out_dir / final_filename

    # Secure write
    json_content = json.dumps(finalized_data, indent=2)
    secure_write(
        final_path, json_content, read_only=False
    )  # Keep writable for checksums

    # Compute checksum
    json_checksum = compute_sha256(final_path)

    return {
        "status": "finalized",
        "tag": exp_tag,
        "path": str(final_path),
        "sha256": json_checksum,
        "analysis": finalized_data,
    }


def generate_summary(analysis_data: Dict[str, Any]) -> str:
    """Generate concise 2-5 line summary with findings and interventions."""
    classification = analysis_data.get("classification", {})
    metrics = analysis_data.get("metrics", {})

    label = classification.get("label", "Unknown")
    score = metrics.get("efficiency_score", 0)
    balance = metrics.get("balance_angle_deg", 0)

    angles = metrics.get("pairwise_angles_deg", {})
    ip_angle = angles.get("influence_productivity", 0)
    ic_angle = angles.get("influence_creativity", 0)
    pc_angle = angles.get("productivity_creativity", 0)

    # Principal findings
    findings = []
    findings.append(
        f"System classified as {label} (score={score:.3f}, balance={balance:.1f}°)"
    )

    if ip_angle < 45:
        findings.append(f"Strong influence-productivity alignment ({ip_angle:.1f}°)")

    if pc_angle > 135:
        findings.append(
            f"Productivity-creativity opposition detected ({pc_angle:.1f}°)"
        )
    elif ic_angle > 120:
        findings.append(
            f"Creativity undervalued relative to influence ({ic_angle:.1f}°)"
        )

    # Interventions
    interventions = []
    if label == "Fragmented":
        interventions.append("URGENT: Conduct leadership realignment workshop")
        interventions.append(
            "Separate productivity/creativity tracks with clear handoffs"
        )
    elif label == "Imbalanced":
        interventions.append(
            "Introduce structured ideation sessions (weekly 2-hour blocks)"
        )
        interventions.append(
            "Balance KPIs: add innovation metrics alongside output metrics"
        )
    else:  # Aligned
        interventions.append(
            "Maintain current balance through quarterly efficiency audits"
        )
        interventions.append("Document successful practices for knowledge transfer")

    # Format summary
    summary_lines = ["TRAJECTORY EFFICIENCY SUMMARY", "=" * 50, ""]
    summary_lines.extend(f"• {f}" for f in findings[:3])
    summary_lines.extend(["", "RECOMMENDED INTERVENTIONS:"])
    summary_lines.extend(f"→ {i}" for i in interventions[:2])

    return "\n".join(summary_lines)


def write_checksums(artifact_paths: list[Path], checksum_file: Path) -> None:
    """Write SHA-256 checksums for all artifacts."""
    checksums = []

    for path in artifact_paths:
        if path.exists():
            checksum = compute_sha256(path)
            checksums.append(f"{checksum}  {path.name}")

    checksum_content = "\n".join(checksums) + "\n"
    secure_write(checksum_file, checksum_content, read_only=False)
