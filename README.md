# Echoes Platform

Overview. Architecture. Setup. Maintenance.
- Backend: backend/
- Frontend: frontend/
- Assets: assets/
- Tools: tools/
- Docs: docs/

## Key Features

This project includes several advanced, self-aware systems designed to improve robustness and developer interaction.

### 1. Documentation-Driven Security

The system includes a `GuardrailMiddleware` that actively enforces security protocols defined in the project's own documentation (`docs/glimpse/DEPLOYMENT_AND_OPERATIONS.md`). This ensures that the application's behavior is always consistent with its specification.

For a detailed summary and demonstration output, see the [Core Systems README](core/README.md).

### 2. Context-Aware AI Agent

We have implemented a `ContextAwareAPICall` system that can reason about the codebase and the user's recent activity (trajectory). This agent can use a multi-step tool-use workflow to:
1.  **Search** for relevant files in the codebase.
2.  **Read** the contents of those files.
3.  **Synthesize** the information to answer complex, context-dependent queries.

An end-to-end demonstration can be run via the [run_context_aware_call.py](examples/run_context_aware_call.py) script. The full implementation details are in the [Core Systems README](core/README.md).

---

## 📋 Project Status & Findings

### Recent Updates (October 2025)
- ✅ Implemented Context-Aware AI Agent with multi-step reasoning
- ✅ Created Documentation-Driven Security middleware
- ✅ Resolved multiple dependency vulnerabilities
- ✅ Added comprehensive testing and documentation

### Known Issues & Solutions
For a complete list of findings, issues, and solutions, see [FINDINGS_AND_SOLUTIONS.md](docs/FINDINGS_AND_SOLUTIONS.md)

**Quick Fixes:**
```bash
# Fix dependency vulnerabilities
python scripts/manage_deps.py

# Install pre-commit hooks
pre-commit install

# Run security audit
pip-audit -r requirements.txt
```

---

## Setup

1. Backend: cd backend && poetry install
2. Frontend: cd frontend && npm install
3. Dev: make dev

License: MIT
