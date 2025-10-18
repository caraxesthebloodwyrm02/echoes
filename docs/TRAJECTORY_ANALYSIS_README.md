# Trajectory Analysis System

**Version:** 1.0.0
**Author:** Echoes Team

Modular vector analysis system for measuring influence, productivity, and creativity alignment in multi-dimensional trajectory spaces.

## Overview

The Trajectory Analysis System provides a rigorous mathematical framework for analyzing the relationship between three fundamental dimensions:

- **Influence**: Emotional + energetic drive (blue vector)
- **Productivity**: Conceptual + energetic output (green vector)
- **Creativity**: Innovation and ideation capacity (purple vector)
- **Efficiency**: Optimal balance point between the three (red vector)

### Key Features

✓ **Type-safe data models** with dataclasses and numpy type hints
✓ **Pure vector operations** (normalize, angle_between, compute_efficiency)
✓ **Comprehensive metrics** (efficiency score, balance factor, angular relationships)
✓ **3D visualization** with Matplotlib (static and interactive modes)
✓ **CLI interface** for batch processing and CI integration
✓ **Full test coverage** with pytest (27+ unit and integration tests)

## Installation

### Prerequisites

```bash
Python 3.12+
numpy>=1.26.4
pandas>=2.2.3
matplotlib>=3.7.0
```

### Setup

```bash
# Install dependencies (already in requirements.txt)
pip install numpy pandas matplotlib

# Run tests
pytest test_trajectory_analysis.py -v

# Run analysis
python trajectory_analysis.py --interactive
```

## Usage

### Command Line Interface

```bash
# Interactive 3D visualization
python trajectory_analysis.py --interactive

# Save results to JSON and plot to file
python trajectory_analysis.py --output results.json --save-plot trajectory.png

# Metrics only (no plotting, useful for CI)
python trajectory_analysis.py --no-plot

# Show version
python trajectory_analysis.py --version
```

### Python API

```python
from trajectory_analysis import (
    TrajectoryPoint,
    calculate_efficiency_metrics,
    plot_trajectory_3d,
    get_default_trajectory_data
)

# Load default trajectory data
points = get_default_trajectory_data()

# Calculate efficiency metrics
summary = calculate_efficiency_metrics(points)

# Print human-readable interpretation
print(summary.interpretation())

# Access specific metrics
print(f"Efficiency Score: {summary.efficiency_score:.3f}")
print(f"Balance Factor: {summary.balance_factor_degrees:.2f}°")

# Export to JSON
import json
with open('results.json', 'w') as f:
    json.dump(summary.to_dict(), f, indent=2)
```

### Custom Trajectory Data

```python
import numpy as np
from trajectory_analysis import TrajectoryPoint, calculate_efficiency_metrics

# Define custom trajectory points
points = [
    TrajectoryPoint(1, "Alpha", 100.0, 0.5, 0.5, 0.5),
    TrajectoryPoint(2, "Beta", 200.0, 0.6, 0.7, 0.8),
    TrajectoryPoint(3, "Leonardo da Vinci", 300.0, -0.3, 0.0, -0.2),
    # ... more points
]

# Calculate with custom base vectors
custom_influence = np.array([1.0, 0.0, 0.0])
custom_productivity = np.array([0.0, 1.0, 0.0])

summary = calculate_efficiency_metrics(
    points,
    influence_base=custom_influence,
    productivity_base=custom_productivity,
    creativity_archetype="Leonardo da Vinci"
)
```

## Architecture

### Module Structure

```
trajectory_analysis.py
├── DATA MODELS
│   ├── TrajectoryPoint      # Immutable point in 3D space
│   ├── VectorSet            # Collection of normalized vectors
│   └── EfficiencySummary    # Computed metrics + interpretation
│
├── VECTOR OPERATIONS
│   ├── normalize()          # Vector normalization
│   ├── angle_between()      # Angular separation (degrees)
│   └── compute_efficiency_vector()  # Balance point calculation
│
├── METRICS CALCULATION
│   └── calculate_efficiency_metrics()  # Full analysis pipeline
│
├── PLOTTING
│   └── plot_trajectory_3d()  # 3D visualization with vectors
│
├── DATA LOADING
│   ├── load_trajectory_data()  # Parse tuple data
│   └── get_default_trajectory_data()  # Default dataset
│
└── CLI INTERFACE
    ├── print_summary()      # Formatted console output
    └── main()               # Argument parsing + orchestration
```

### Design Principles

1. **Immutability**: All data models use `frozen=True` dataclasses
2. **Type Safety**: Full numpy type hints with `npt.NDArray[np.float64]`
3. **Validation**: Post-init checks ensure data integrity
4. **Pure Functions**: Vector operations have no side effects
5. **Separation of Concerns**: Data, logic, visualization, and CLI are decoupled

## Metrics Interpretation

### Efficiency Score

Mean dot product of efficiency vector with base vectors (range: -1 to 1)

- **> 0.5**: High alignment — system operates with strong synergy
- **0.2–0.5**: Moderate alignment — functional with some tension
- **< 0.2**: Low alignment — significant conflicts between dimensions

### Balance Factor

Average angular separation between base vectors (degrees)

- **< 60°**: High synergy — dimensions work together harmoniously
- **60–120°**: Moderate independence — dimensions operate somewhat independently
- **> 120°**: Antagonistic — dimensions work against each other

### Angular Relationships

- **Influence ↔ Productivity**: Alignment between drive and output
- **Influence ↔ Creativity**: Alignment between drive and innovation
- **Productivity ↔ Creativity**: Balance between output and exploration

**Interpretation Guidelines:**

- Angles < 45° indicate strong alignment
- Angles 45–135° indicate independence
- Angles > 135° indicate conflict

## Example Output

```
======================================================================
TRAJECTORY EFFICIENCY ANALYSIS
======================================================================

Efficiency Vector: [0.459, 0.877, 0.146]
Efficiency Score: 0.418 (range: -1 to 1)
Balance Factor: 105.47°

Angular Relationships:
  Influence ↔ Productivity: 29.53°
  Influence ↔ Creativity:   133.93°
  Productivity ↔ Creativity: 152.94°

Interpretation:
  ⚠ Moderate alignment: Some tension exists but system is functional
  ⚠ Moderate independence: Dimensions operate somewhat independently
  ✓ Influence and productivity are strongly aligned
  ⚠ Creativity is undervalued relative to influence
  ⚠ Risk: Productivity may be suppressing creative exploration

======================================================================
```

### Actionable Insights

Based on the example output:

1. **Strength**: Influence and productivity are well-aligned (29.53°) — team is effective at driving and shipping
2. **Risk**: Creativity is antagonistic to productivity (152.94°) — output-focused culture may suppress innovation
3. **Recommendation**: Introduce exploratory cycles, diverse ideation sessions, or adjust KPIs to reward creative contributions

## Testing

### Run Tests

```bash
# Run all tests with verbose output
pytest test_trajectory_analysis.py -v

# Run with coverage
pytest test_trajectory_analysis.py --cov=trajectory_analysis --cov-report=html

# Run specific test class
pytest test_trajectory_analysis.py::TestNormalize -v
```

### Test Coverage

- **Data Models**: 8 tests (validation, immutability, properties)
- **Vector Operations**: 12 tests (normalization, angles, efficiency)
- **Metrics Calculation**: 5 tests (default data, custom vectors, edge cases)
- **Integration**: 2 tests (full workflow, expected values)

**Total**: 27 tests, 100% coverage of core functionality

## CI Integration

### GitHub Actions Example

```yaml
name: Trajectory Analysis Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - run: pip install numpy pandas matplotlib pytest
      - run: pytest test_trajectory_analysis.py -v
      - run: python trajectory_analysis.py --no-plot --output results.json
      - uses: actions/upload-artifact@v3
        with:
          name: trajectory-results
          path: results.json
```

## Advanced Usage

### Custom Visualization

```python
from trajectory_analysis import plot_trajectory_3d, VectorSet
import numpy as np

# Create custom vector set
vectors = VectorSet(
    influence=np.array([0.537, 0.716, 0.447]),
    productivity=np.array([0.874, 0.389, 0.292]),
    creativity=np.array([-0.832, 0.000, -0.555]),
    efficiency=np.array([0.459, 0.877, 0.146])
)

# Plot with custom settings
fig = plot_trajectory_3d(
    trajectory_points=points,
    vectors=vectors,
    title="Custom Trajectory Analysis",
    show=False,
    save_path=Path("custom_plot.pdf"),
    figsize=(14, 10),
    dpi=300
)
```

### Batch Processing

```python
import json
from pathlib import Path

# Process multiple trajectory datasets
for data_file in Path("data/").glob("trajectory_*.csv"):
    # Load custom data (implement your own loader)
    points = load_custom_data(data_file)

    # Calculate metrics
    summary = calculate_efficiency_metrics(points)

    # Save results
    output_file = data_file.with_suffix(".json")
    with open(output_file, 'w') as f:
        json.dump(summary.to_dict(), f, indent=2)

    print(f"Processed {data_file.name}: score={summary.efficiency_score:.3f}")
```

## Troubleshooting

### Common Issues

**Issue**: `ValueError: Cannot normalize zero vector`
**Solution**: Check that your trajectory points have non-zero coordinates

**Issue**: `ValueError: Creativity archetype 'X' not found`
**Solution**: Ensure your trajectory data includes the specified creativity archetype (default: "Leonardo da Vinci")

**Issue**: Plot doesn't display
**Solution**: Use `--interactive` flag or `--save-plot` to save to file

**Issue**: `ValueError: must be normalized (norm=1)`
**Solution**: VectorSet requires pre-normalized vectors. Use `normalize()` function first.

## Contributing

Contributions welcome! Areas for enhancement:

- [ ] CSV/JSON data loaders
- [ ] Interactive Plotly visualization
- [ ] Time-series trajectory analysis
- [ ] Multi-trajectory comparison
- [ ] Sensitivity analysis tools
- [ ] Optimization algorithms for efficiency maximization

## License

MIT License - Copyright (c) 2025 Echoes Project

## References

- **Vector Analysis**: Marsden, J. E., & Tromba, A. (2011). *Vector Calculus*. W.H. Freeman.
- **Efficiency Metrics**: Pareto, V. (1906). *Manual of Political Economy*.
- **Multi-dimensional Analysis**: Jolliffe, I. T. (2002). *Principal Component Analysis*. Springer.

## Contact

For questions or support, please open an issue on the project repository.
