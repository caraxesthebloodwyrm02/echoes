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

"""Deterministic trajectory efficiency experiment runner.

Reads base vectors from ``data/input_vectors.json`` (fallback: defaults hard-coded),
computes efficiency metrics, classifies the system, exports:

1. JSON results (schema-compliant) → ``results/<timestamp>-analysis.json``
2. Static PNG plot              → ``results/<timestamp>/efficiency_plot.png``
3. Human-readable summary        → ``results/<timestamp>-summary.txt``

All runs are fully reproducible: ``np.random.seed(42)`` and seed is recorded.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 (needed for 3D)

from src.evaluator import classify
from src.finalization import (
    finalize_analysis,
    generate_summary,
    write_checksums,
)
from src.metrics import compute_efficiency_metrics
from src.validators import validate_schema
from src.vector_ops import compute_efficiency_vector, normalize

# ---------------------------------------------------------------------------
# Constants & Paths
# ---------------------------------------------------------------------------

SEED = 42
DATA_PATH = Path("data/input_vectors.json")
RESULTS_DIR = Path("results")
RESULTS_DIR.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------


def _load_vectors() -> dict[str, list[float]]:
    if DATA_PATH.exists():
        with DATA_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)
            return data  # assume keys present
    # Fallback to default (matches original paper)
    return {
        "influence": [0.6, 0.8, 0.5],
        "productivity": [0.9, 0.4, 0.3],
        "creativity": [-0.3, 0.0, -0.2],
    }


def _make_timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _plot_png(vectors: dict[str, np.ndarray], out_path: Path) -> None:
    """Create a minimal 3D plot of the four vectors."""
    origin = np.zeros(3)
    color_map = {
        "influence": "blue",
        "productivity": "green",
        "creativity": "purple",
        "efficiency": "red",
    }

    fig = plt.figure(figsize=(6, 5), dpi=120)
    ax = fig.add_subplot(111, projection="3d")

    for name, vec in vectors.items():
        ax.quiver(
            *origin,
            *vec,
            length=1.0,
            color=color_map[name],
            label=name,
            arrow_length_ratio=0.15,
        )

    ax.set_xlabel("X (Conceptual)")
    ax.set_ylabel("Y (Emotional)")
    ax.set_zlabel("Z (Energetic)")
    ax.set_title("Trajectory Vectors")
    ax.legend(loc="upper left")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Main routine
# ---------------------------------------------------------------------------


def main() -> None:  # noqa: D401
    # Deterministic seed
    np.random.seed(SEED)

    # Timestamp for artifact names (Windows-safe: replace colons)
    ts = _make_timestamp()
    ts_safe = ts.replace(":", "-")
    ts_date = ts.split("T")[0]

    result_subdir = RESULTS_DIR / ts_date
    result_subdir.mkdir(parents=True, exist_ok=True)

    # Load base vectors
    base = _load_vectors()

    # Convert to numpy arrays
    influence = np.array(base["influence"], dtype=np.float64)
    productivity = np.array(base["productivity"], dtype=np.float64)
    creativity = np.array(base["creativity"], dtype=np.float64)

    # Compute metrics
    summary = compute_efficiency_metrics(influence, productivity, creativity)

    # Classification
    classification = classify(summary)

    # Plot PNG
    eff_vec = compute_efficiency_vector(influence, productivity, creativity)
    plot_vectors = {
        "influence": normalize(influence),
        "productivity": normalize(productivity),
        "creativity": normalize(creativity),
        "efficiency": eff_vec,
    }
    png_name = f"{ts_date}/efficiency_plot.png"
    png_path = RESULTS_DIR / png_name
    _plot_png(plot_vectors, png_path)

    # Assemble JSON output
    out: dict[str, object] = {
        "timestamp": ts,
        "seed": SEED,
        "vectors": {
            "influence": plot_vectors["influence"].round(3).tolist(),
            "productivity": plot_vectors["productivity"].round(3).tolist(),
            "creativity": plot_vectors["creativity"].round(3).tolist(),
            "efficiency": plot_vectors["efficiency"].round(3).tolist(),
        },
        "metrics": summary.to_dict(),
        "classification": classification,
        "artifacts": {
            "png": str(png_path),
        },
    }

    # Use Windows-safe filename
    json_path = RESULTS_DIR / f"{ts_safe}-analysis.json"
    with json_path.open("w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)

    # Human-readable summary (ASCII-safe for Windows console)
    summary_txt = (
        f"Trajectory Efficiency Analysis ({ts})\n"
        f"Seed: {SEED}\n\n"
        f"Efficiency Score: {summary.efficiency_score:.3f}\n"
        f"Balance Angle: {summary.balance_angle_deg:.2f} degrees\n"
        f"Classification: {classification['label']} ({classification['reason']})\n\n"
        f"Pairwise Angles (deg):\n"
        f"  Influence <-> Productivity: {summary.influence_productivity_deg:.2f}\n"
        f"  Influence <-> Creativity:   {summary.influence_creativity_deg:.2f}\n"
        f"  Productivity <-> Creativity:{summary.productivity_creativity_deg:.2f}\n"
    )

    txt_path = RESULTS_DIR / f"{ts_safe}-summary.txt"
    txt_path.write_text(summary_txt, encoding="utf-8")

    print(f"[OK] Results written to {json_path}")
    print(f"[OK] Plot written to {png_path}")
    print(f"[OK] Summary written to {txt_path}")

    # -----------------------------------------------------------------------
    # FINALIZATION LAYER
    # -----------------------------------------------------------------------

    # Step 1: Validate schema
    print("\n[Finalization] Validating schema...")
    try:
        validate_schema(out, strict=True)
        print("[OK] Schema validation passed")
    except ValueError as e:
        print(f"[ERROR] Schema validation failed: {e}")
        return

    # Step 2: Finalize with metadata
    print("[Finalization] Adding provenance metadata...")
    final_result = finalize_analysis(out, out_dir=RESULTS_DIR)
    print(f"[OK] Finalized: {final_result['tag']}")

    # Step 3: Generate enhanced summary
    print("[Finalization] Generating enhanced summary...")
    enhanced_summary = generate_summary(final_result["analysis"])
    enhanced_summary_path = RESULTS_DIR / f"{ts_safe}-summary-enhanced.txt"
    enhanced_summary_path.write_text(enhanced_summary, encoding="utf-8")
    print(f"[OK] Enhanced summary: {enhanced_summary_path}")

    # Step 4: Compute checksums
    print("[Finalization] Computing checksums...")
    artifact_paths = [
        Path(final_result["path"]),
        png_path,
        txt_path,
        enhanced_summary_path,
    ]
    checksum_file = RESULTS_DIR / f"{ts_safe}-checksums.txt"
    write_checksums(artifact_paths, checksum_file)
    print(f"[OK] Checksums: {checksum_file}")

    # Step 5: Emit audit log
    print("\n" + "=" * 70)
    print("FINALIZATION COMPLETE")
    print("=" * 70)
    audit_log = {
        "status": final_result["status"],
        "tag": final_result["tag"],
        "path": final_result["path"],
        "sha256": final_result["sha256"],
        "classification": out["classification"]["label"],
        "efficiency_score": out["metrics"]["efficiency_score"],
    }
    print(json.dumps(audit_log, indent=2))
    print("=" * 70)


if __name__ == "__main__":
    main()
