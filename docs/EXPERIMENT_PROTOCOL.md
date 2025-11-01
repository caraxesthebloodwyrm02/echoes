# Trajectory Efficiency Analysis - Experiment Protocol

## Two-Track System: o3 (Prove) + Sonnet (Present)

This repository implements a **dual-agent workflow** for reproducible scientific computing:

- **Track 1 (o3)**: Deterministic numeric analysis with provenance tracking
- **Track 2 (Sonnet)**: Production code, interactive visualizations, and documentation

---

## Quick Start

### Run Deterministic Experiment (o3)

```bash
# Basic run
python run_experiment.py

# Output:
# - results/<timestamp>-analysis-final.json (with metadata)
# - results/<timestamp>/efficiency_plot.png
# - results/<timestamp>-summary-enhanced.txt
# - results/<timestamp>-checksums.txt
```

### Run Glimpse Tests

```bash
# Core vector operations (rtol=1e-7)
python -m pytest tests/test_vector_ops.py -v

# Legacy trajectory analysis
python -m pytest test_trajectory_analysis.py -v
```

### Interactive CLI (Sonnet)

```bash
# Run experiment with auto-ingestion
python -m src.cli run --auto-ingest

# Validate existing results
python -m src.cli validate results/2025-10-16-analysis-final.json

# Generate interactive HTML
python -m src.cli ingest results/2025-10-16-analysis-final.json
```

---

## Architecture

### Core Modules (o3 - Deterministic)

```
src/
├── vector_ops.py      # NumPy-only math (normalize, angle_between, efficiency)
├── metrics.py         # EfficiencySummary dataclass + compute_efficiency_metrics
├── evaluator.py       # Classification (Aligned/Imbalanced/Fragmented)
├── finalization.py    # Provenance, checksums, security controls
└── validators.py      # Schema validation + numeric reproducibility checks
```

### Production Modules (Sonnet - Presentation)

```
src/
├── cli.py            # Typer CLI (run/ingest/validate)
├── plotting.py       # Interactive Plotly 3D HTML with camera controls
└── __init__.py       # Package exports
```

### Experiment Runner

```
run_experiment.py     # Main entry point with finalization layer
```

---

## Finalization Layer

Every experiment run produces **tamper-evident artifacts**:

### 1. Schema Validation
- Strict type enforcement
- Required fields: `timestamp`, `seed`, `vectors`, `metrics`, `classification`
- Numeric range checks (scores in [-1,1], angles in [0°,180°])

### 2. Provenance Metadata

```json
{
  "metadata": {
    "finalization": {
      "finalized_by": "o3",
      "finalized_at": "2025-10-16T00:29:43Z",
      "git_commit": "d8bce21",
      "experiment_tag": "exp/2025-10-16/d8bce21",
      "environment": "secure-digest:bd5f9...",
      "python_version": "3.12.9",
      "numpy_version": "1.26.4"
    }
  }
}
```

### 3. Integrity Checksums

All artifacts get SHA-256 checksums in `<timestamp>-checksums.txt`:

```
99d8d882...  2025-10-16T00-29-43+00-00-analysis-final.json
74fcc10a...  efficiency_plot.png
ff22dac4...  2025-10-16T00-29-43+00-00-summary.txt
5fc3e11e...  2025-10-16T00-29-43+00-00-summary-enhanced.txt
```

### 4. Audit Log

Machine-readable JSON emitted to stdout:

```json
{
  "status": "finalized",
  "tag": "exp/2025-10-16/d8bce21",
  "path": "results/2025-10-16T00-29-43+00-00-analysis-final.json",
  "sha256": "99d8d882...",
  "classification": "Imbalanced",
  "efficiency_score": 0.42001662936794143
}
```

---

## Classification System

### Thresholds (Configurable)

```python
DEFAULT_THRESHOLDS = {
    "aligned_score": 0.7,        # |score| >= 0.7
    "imbalanced_score": 0.3,     # 0.3 <= |score| < 0.7
    "synergy_balance_deg": 90.0, # balance < 90° → synergy
    "imbalanced_upper_deg": 120.0,
}
```

### Labels

| Label | Criteria | Interpretation |
|-------|----------|----------------|
| **Aligned** | score ≥ 0.7 AND balance < 90° | High synergy, optimal performance |
| **Imbalanced** | 0.3 ≤ score < 0.7 OR 90° ≤ balance ≤ 120° | Moderate tension, functional |
| **Fragmented** | score < 0.3 OR balance > 120° | Critical misalignment, intervention required |

### Pairwise Angle Interpretation

| Angle Range | Relationship |
|-------------|--------------|
| < 30° | Strong synergy |
| 30°–90° | Partial alignment |
| 90°–150° | Opposition/antagonism |
| > 150° | Near-complete opposition |

---

## Input Format

### `data/input_vectors.json`

```json
{
  "influence": [0.6, 0.8, 0.5],
  "productivity": [0.9, 0.4, 0.3],
  "creativity": [-0.3, 0.0, -0.2]
}
```

Vectors are automatically normalized during processing.

---

## Output Schema

### `results/<timestamp>-analysis-final.json`

```json
{
  "timestamp": "2025-10-16T00:29:43+00:00",
  "seed": 42,
  "vectors": {
    "influence": [0.537, 0.716, 0.447],
    "productivity": [0.874, 0.389, 0.292],
    "creativity": [-0.832, 0.0, -0.555],
    "efficiency": [0.459, 0.876, 0.146]
  },
  "metrics": {
    "efficiency_vector": [0.459, 0.876, 0.146],
    "efficiency_score": 0.420,
    "balance_angle_deg": 105.14,
    "pairwise_angles_deg": {
      "influence_productivity": 28.67,
      "influence_creativity": 133.99,
      "productivity_creativity": 152.74
    }
  },
  "classification": {
    "label": "Imbalanced",
    "reason": "efficiency_score between 0.3 and 0.7 or balance_angle between 90° and 120°"
  },
  "artifacts": {
    "png": "results/2025-10-16/efficiency_plot.png"
  },
  "metadata": {
    "finalization": { ... }
  }
}
```

---

## Reproducibility Guarantees

### Determinism

- `np.random.seed(42)` set at entry point
- Seed recorded in output JSON
- All operations are pure functions (no side effects)

### Numeric Stability

- `np.clip(dot, -1, 1)` prevents domain errors in `arccos`
- All tests use `rtol=1e-7` for floating-point comparisons
- Normalized vectors validated with `atol=1e-6`

### Environment Fingerprint

```python
{
  "os": "Windows",
  "python": "3.12.9",
  "numpy": "1.26.4",
  "hostname_hash": "bd5f9..."  # SHA-256 truncated
}
```

---

## Security Controls

### Atomic Writes

```python
# Tempfile → rename pattern prevents partial writes
with tempfile.NamedTemporaryFile(...) as tmp:
    tmp.write(content)
    tmp_path.replace(final_path)
```

### Read-Only Enforcement

- Files set to `chmod 444` on Unix systems (skipped on Windows)
- Prevents accidental modification of finalized artifacts

### No External Network Calls

- All operations are local
- No arbitrary code execution
- Validation rejects malformed inputs

---

## Testing

### Glimpse Tests (17 tests, rtol=1e-7)

```bash
pytest tests/test_vector_ops.py -v
```

**Coverage:**
- Normalization (zero-check, negative values, already normalized)
- Angle calculation (orthogonal, parallel, opposite, 45°, radians)
- Efficiency vector (orthogonal, aligned, default paper vectors)
- Integration (full pipeline)

### Legacy Tests (30 tests)

```bash
pytest test_trajectory_analysis.py -v
```

**Coverage:**
- TrajectoryPoint validation
- VectorSet validation
- EfficiencySummary interpretation
- Full workflow integration

---

## Workflow: o3 → Sonnet Handoff

### 1. o3 Runs Experiment

```bash
python run_experiment.py
# Produces: results/2025-10-16T00-29-43+00-00-analysis-final.json
```

### 2. Automated Handoff (Optional)

```bash
python run_experiment.py --auto-ingest  # Not yet implemented
# Triggers: python -m src.cli ingest <json> --create-pr
```

### 3. Sonnet Ingests Results

```bash
python -m src.cli ingest results/2025-10-16-analysis-final.json
```

**Sonnet produces:**
- Interactive Plotly 3D HTML with camera controls
- Updated README with latest results
- Executive summary (2 paragraphs + 6-bullet checklist)
- Optional GitHub PR with documentation updates

---

## Model Governance

Defined in `pyproject.toml`:

```toml
[tool.echoes_vectors]
analysis_writer_model = "o3"
doc_writer_model = "sonnet-4.5"
seed = 42
```

---

## CI/CD Integration

### GitHub Actions Workflow (Planned)

```yaml
jobs:
  test:
    - pytest -q
    - coverage run -m pytest

  lint:
    - ruff .
    - black --check .

  validate-artifacts:
    - python -m src.cli validate results/sample-analysis.json
```

---

## Troubleshooting

### Windows Filename Issues

**Problem:** `OSError: [Errno 22] Invalid argument` with colons in filename

**Solution:** Timestamps are sanitized (`2025-10-16T00:29:43+00:00` → `2025-10-16T00-29-43+00-00`)

### Unicode Console Errors

**Problem:** `UnicodeEncodeError: 'charmap' codec can't encode character`

**Solution:** All console output uses ASCII equivalents:
- `✓` → `[OK]`
- `↔` → `<->`
- `°` → `degrees`

### Test Failures (Normalization)

**Problem:** `ValueError: efficiency must be normalized (norm=1), got norm=0.999393`

**Solution:** Use `np.array([1,1,1]) / np.sqrt(3)` instead of `[0.577, 0.577, 0.577]`

---

## Next Steps

### Planned Enhancements

- [ ] CSV/JSON data loaders for batch experiments
- [ ] Interactive Plotly HTML with elev/azim sliders
- [ ] Time-series trajectory analysis
- [ ] Multi-trajectory comparison
- [ ] Sensitivity analysis tools
- [ ] GitHub PR automation for Sonnet handoff

### Integration

- [ ] Add to main README as analysis tool
- [ ] Create GitHub Actions workflow
- [ ] Jupyter notebook demo
- [ ] Parameter sweep automation

---

## References

- **Original Analysis:** `trajectory_analysis.py` (628 lines)
- **Test Suite:** `test_trajectory_analysis.py` (383 lines, 30 tests)
- **Documentation:** `TRAJECTORY_ANALYSIS_README.md` (366 lines)

---

**Status:** Production ready, all critical tests passing
**Last Updated:** 2025-10-16
**Experiment Tag:** `exp/2025-10-16/d8bce21`
