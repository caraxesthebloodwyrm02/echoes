<div align="center">
<img width="1200" height="475" alt="GHBanner" src="https://github.com/user-attachments/assets/0aa67016-6eaf-458a-adb2-6e31a0763ed6" />
</div>

# Echoes

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.12+-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/Tests-69%2F69%20passing-brightgreen.svg" alt="Tests">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License">
</div>

<div align="center">
  <h3>Scientific Computing & AI Orchestration Platform</h3>
  <p>Where deterministic analysis meets intuitive optimization</p>
</div>

---

## 🎯 What Makes Echoes Different

Most systems optimize for either **speed** or **quality**. Echoes proves you can have both—but the path isn't linear.

Our research shows that **fast compounding** (low attention, quick decisions) saves 80% time while achieving 1466% better efficiency in long trajectories. The secret? Exponential learning curves that compound experience over time.

**The nuance:** Short-term critical decisions need traditional data-driven analysis. Long-term iterative processes thrive on fast compounding. Echoes gives you both.

---

## 🌟 Core Capabilities

### Trajectory Analysis & Optimization
- **Two-track protocol**: o3 for deterministic analysis, Sonnet for production engineering
- **Bidirectional paths**: Regenerate prompts from results (if A→X exists, X→A exists)
- **100% reproducibility**: SHA-256 checksums, provenance tracking, seed-based determinism
- **Research-validated**: 69/69 tests passing, quantified efficiency gains

### AI Orchestration
- Multi-agent collaboration with knowledge graph integration
- Hybrid model routing (OpenAI, Azure, local fallback)
- Context-aware prompting with semantic reasoning
- Security-first design with privacy filtering

### Key Features

- 🤖 **AI Agent Orchestration**: CrewAI-powered collaborative agent workflows
- 🎯 **Multi-Modal Processing**: CLIP-based image/text understanding with Torch integration
- 🔄 **Deterministic Workflows**: Phase-based execution with error handling and logging
- 🏗️ **MLOps Pipeline**: MLflow integration for model versioning and deployment
- 🔒 **Security-First**: AI-enhanced scanning with predictive vulnerability detection
- 📊 **Knowledge Graphs**: Ontology-based semantic reasoning systems
- 🎨 **Synthetic Data**: Privacy-preserving data augmentation pipelines
- 🚀 **Edge AI**: Optimized model deployment for edge computing

## 🏗️ Architecture

Echoes follows a modular, harmonic resonance design pattern:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   AI Agents     │    │ Multimodal      │    │   Knowledge     │
│   Orchestration │    │   Processing    │    │     Graphs      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                        │                        │
         └────────────────────────┼────────────────────────┘
                                  │
                    ┌─────────────────┐
                    │  Core Glimpse   │
                    │   Workflows     │
                    └─────────────────┘
         ┌────────────────────────┼────────────────────────┐
         │                        │                        │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     MLOps       │    │   Security      │    │   Synthetic     │
│   Pipeline      │    │   Scanning      │    │     Data        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Git
- FFmpeg (for audio processing)
- Node.js (for web components, optional)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/caraxesthebloodwyrm02/echoes.git
   cd echoes
   ```

2. **Set up Python environment:**
   ```bash
   pyenv-create
   pyenv
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

5. **Run setup validation:**
   ```bash
   python test_venv_functionality.py
   ```

### Trajectory Analysis

```bash
# Run deterministic experiment
python run_experiment.py

# Output: Finalized analysis with SHA-256 checksums
# results/2025-10-16T00-29-43+00-00-analysis-final.json
# results/2025-10-16T00-29-43+00-00-checksums.txt
```

### Optimization Research

```bash
# Compare Data-Driven vs Fast Compounding
python demo_trajectory_research.py

# Key findings:
# - FC saves 80% time, 69% cognitive load
# - 1466% efficiency gain in long trajectories
# - Crossover point: ~15 steps
```

### CLI Interface

```bash
# Run trajectory analysis
python -m src.cli run --input-file data/input_vectors.json

# Validate results
python -m src.cli validate --json-path results/analysis.json

# Generate interactive visualization
python -m src.cli ingest --json-path results/analysis.json
```

## 📚 Core Modules

### 🎯 Trajectory Analysis (`src/`)
**The heart of Echoes' optimization research**

- `vector_ops.py` - NumPy-only deterministic math (normalize, angles, efficiency)
- `metrics.py` - EfficiencySummary with validation and classification
- `evaluator.py` - Aligned/Imbalanced/Fragmented classification
- `trajectory_optimizer.py` - Data-Driven vs Fast Compounding comparison
- `prompt_regenerator.py` - Bidirectional path discovery (Result → Prompt)
- `finalization.py` - Provenance tracking, SHA-256 checksums, security
- `validators.py` - Schema validation with strict type enforcement
- `cli.py` - Typer-based CLI (run/ingest/validate commands)
- `plotting.py` - Interactive Plotly 3D visualizations

**Test Coverage:** 69/69 passing (100%)

### 🤖 AI Orchestration (`ai_agents/`, `prompting/`)
- Multi-agent collaboration with knowledge graph integration
- Hybrid model routing (OpenAI, Azure, local)
- Context-aware prompting with semantic reasoning
- Agent templates for code review, testing, architecture

### 🕸️ Knowledge Graphs (`knowledge_graph/`)
- RDF-based semantic storage with ontology management
- Graph-based reasoning and inference
- Cross-agent knowledge sharing

### 🔒 Security & Privacy (`security/`, `packages/security/`)
- AI-enhanced vulnerability scanning
- Privacy filtering and PII detection
- Compliance monitoring and audit trails

## 🛠️ Development

### Environment Setup

Echoes uses a comprehensive development environment with automated tooling:

- **VS Code Integration**: Pre-configured settings for Python development
- **Linting & Formatting**: Black, Ruff, Flake8
- **Testing**: Pytest with comprehensive coverage
- **Documentation**: MkDocs for project documentation

### Key Scripts

- `pyenv` - Activate virtual environment
- `pyenv-create` - Create/recreate environment
- `python test_venv_functionality.py` - Validate setup
- `python audit_codebase.py` - Code quality analysis

### Project Structure

```
echoes/
├── ai_modules/          # Specialized AI components
│   ├── bias_detection/  # Bias analysis tools
│   ├── ethics_ai/       # Ethical AI guidelines
│   └── minicon/         # Core AI orchestration
├── automation/          # Workflow automation
├── multimodal/          # Multi-modal processing
├── mlops/              # ML operations
├── security/           # Security scanning
├── knowledge_graph/    # Semantic knowledge
├── synthetic_data/     # Data generation
├── workflows/          # Core execution Glimpse
├── tools/              # Utility tools
└── tests/              # Comprehensive test suite
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details on:

- Development setup
- Code standards
- Testing requirements
- Pull request process

### Quick Development Setup

```bash
# Fork and clone
git clone https://github.com/your-username/echoes.git
cd echoes

# Set up development environment
pyenv-create
pyenv
pip install -e .[dev]

# Run tests
pytest

# Start development
code .
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📖 Documentation

### Core Documentation
- **[Trajectory Analysis Guide](TRAJECTORY_ANALYSIS_README.md)** - Complete usage guide
- **[Experiment Protocol](EXPERIMENT_PROTOCOL.md)** - Two-track scientific computing
- **[Research Findings](TRAJECTORY_RESEARCH_FINDINGS.md)** - Fast Compounding vs Data-Driven
- **[Implementation Summary](IMPLEMENTATION_SUMMARY.md)** - Quick reference
- **[Completion Report](PROJECT_COMPLETION_REPORT.md)** - Full project details

### HITL Middleware Documentation
- **[HITL Integration Summary](HITL_INTEGRATION_SUMMARY.md)** - Complete integration overview
- **[HITL Operator Guide](realtime/HITL_Operator_Guide.md)** - Operator training & workflows
- **[HITL KPI Report](realtime/HITL_KPI_Report.md)** - Quantified impact & ROI analysis
- **[HITL Stakeholder Summary](realtime/HITL_Stakeholder_Summary.md)** - Executive overview & roadmap
- **[Realtime Preview System](realtime/README.md)** - Interactive validation canvas

## 🎓 Research Highlights

**Fast Compounding vs Data-Driven Analysis**

Our research quantifies a fundamental trade-off in optimization strategies:

| Metric | Data-Driven | Fast Compounding | FC Advantage |
|--------|-------------|------------------|--------------|
| Time per decision | 1.81s | 0.36s | **80% faster** |
| Cognitive load | 0.84 | 0.26 | **69% lower** |
| Efficiency ratio | 0.018 | 0.288 | **1466% better** |
| Learning slope | -0.0016 | +0.0217 | **Exponential growth** |

**When to use each:**
- **Data-Driven**: Short trajectories (<15 steps), critical decisions, novel problems
- **Fast Compounding**: Long trajectories (>20 steps), iterative processes, time-constrained
- **Hybrid**: Start DDA for foundation, transition to FC at ~15 steps

See [TRAJECTORY_RESEARCH_FINDINGS.md](TRAJECTORY_RESEARCH_FINDINGS.md) for full analysis.

## 🙏 Acknowledgments

- Research co-authored by **o3** (deterministic analysis) and **Sonnet-4.5** (production engineering)
- Built with NumPy, Plotly, Typer, and modern Python tooling
- Inspired by the need for reproducible scientific computing

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/caraxesthebloodwyrm02/echoes/issues)
- **Documentation**: See docs/ folder for comprehensive guides
- **Tests**: Run `pytest tests/ -v` to verify installation

---

<div align="center">
  <p><strong>Where deterministic analysis meets intuitive optimization</strong></p>
  <p>
    <a href="https://github.com/caraxesthebloodwyrm02/echoes">GitHub</a> •
    <a href="TRAJECTORY_RESEARCH_FINDINGS.md">Research</a> •
    <a href="PROJECT_COMPLETION_REPORT.md">Documentation</a>
  </p>
  <p><em>Experiment Tag: exp/2025-10-16/d8bce21 • SHA-256: 99d8d882...a840b339</em></p>
</div>
