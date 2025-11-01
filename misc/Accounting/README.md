# Automated Auditor Experiment (AAE): Accounting & Accountability Framework

## Research Question

**To what extent can a code-based system (AI-driven) replicate the accuracy, efficiency, and judgment of a human-led accounting and audit process?**

## Quick Start

```python
from Accounting import create_default_experiment

# Create experiment
experiment = create_default_experiment(
    name="AAE_Pilot_2025_01",
    dataset_size="medium",
    groups=['human', 'ai', 'hybrid', 'oracle']
)

# Run experiment
results = experiment.run()
print(f"Hybrid scored {results.hybrid_score} vs Human {results.human_score}")