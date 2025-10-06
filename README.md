# AI Advisor

Unified codebase for the AI Advisor project.

## Setup & Usage

1. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   pip install pre-commit && pre-commit install
   ```

3. Run tests:

   ```bash
   pytest
   ```

4. Run automation tasks (examples):

   ```bash
   # Dry-run: scan for foreign dependencies (no changes)
   python -m automation.scripts.run_automation --task "Foreign Dependency Sanitize" --dry-run

   # Apply: remove Node/foreign artifacts, add guardrails
   python -c "from automation.tasks.foreign_dependency_sanitize import foreign_dependency_sanitize; from automation.core.context import Context; foreign_dependency_sanitize(Context(dry_run=False, extra_data={'apply_changes': True, 'delete_node_configs': True, 'assume_yes': True}))"

   # Run security monitoring
   python -m automation.scripts.run_automation --task "Security Monitoring"
   ```

## Project Structure

- `app/` - Main application code
- `automation/` - Automation framework (security, cleanup, guardrails)
- `packages/` - Shared libraries
- `tests/` - Integration/end-to-end tests
- `docs/` - Documentation

## What Can My Agent Do?

Your AI Advisor excels at **semantic understanding** and **practical assistance**:

### Science Domain: Practical Health Solutions
- **Immediate remedies** for headaches, muscle pain, digestive issues
- **Actionable advice** instead of medical disclaimers
- **Natural, accessible solutions** anyone can try

### Commerce Domain: Talent Discovery & Income
- **Semantic analysis** of your communication patterns
- **Talent identification** (writing, analysis, creativity)
- **Income opportunities** and skill development paths

### Arts Domain: Interest-Based Exploration
- **Personality routing** to matching art forms
- **Multi-domain connections** (history, painting, music)
- **Progressive skill building** and community connections

**[Read Full Agent Capabilities →](AGENT_CAPABILITIES.md)**

## Quick Start

```bash
# 1. Set up environment
pip install -r requirements.txt
pip install pre-commit && pre-commit install

# 2. Start the API
cd src && python main.py

# 3. Open documentation
# http://localhost:8000/docs
```

**[Complete Setup Guide →](GET_STARTED_NOW.md)**

## Documentation Hub

| Document | Purpose | Status |
|----------|---------|---------|
| **[AGENT_CAPABILITIES.md](AGENT_CAPABILITIES.md)** | What the agent can do | Complete |
| **[GET_STARTED_NOW.md](GET_STARTED_NOW.md)** | Quick setup & usage | Complete |
| **[docs/API_REFERENCE.md](docs/API_REFERENCE.md)** | Complete API documentation | Complete |
| **[docs/SAFETY_GUIDE.md](docs/SAFETY_GUIDE.md)** | Safety controls & procedures | Complete |
| **[docs/DOMAIN_EXPANSION_PLAN.md](docs/DOMAIN_EXPANSION_PLAN.md)** | Development roadmap | Complete |

## Development & Automation

### Pre-commit Hooks
```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

### Automation Tasks
- Run any task via:
  ```bash
  python -m automation.scripts.run_automation --task "Task Name"
  ```
- See `automation/config/automation_config.yaml` for available tasks.

### Testing
```bash
pytest tests/ -v --cov=app --cov-report=term
```

### Code Quality
- **Black** - Code formatting
- **Flake8** - Linting
- **MyPy** - Type checking
- **Bandit** - Security scanning

## Safety, Security & Automation Guardrails

- **Foreign Dependency Guardrails**: Node.js/JS and other non-Python artifacts are automatically detected and blocked in CI, pre-commit, and weekly automation.
- **Security Automation**: Bandit, Safety, and environment checks are run via `Security Monitoring` automation task.
- **Dry-run mode**: All automation tasks support dry-run for safe preview.
- **Pre-commit & CI**: Automated guardrails prevent reintroduction of foreign dependencies.

**[Safety Guide →](docs/SAFETY_GUIDE.md)**

## API Endpoints

### Core Features
- `POST /api/assertions/validate` - Validate claims with provenance
- `POST /api/hil/feedback` - Human-in-the-loop feedback
- `POST /api/agent/execute` - Execute agent actions safely
- `GET /api/health` - System health check
- `GET /api/metrics` - Performance metrics

### Interactive Documentation
**[Swagger UI → http://localhost:8000/docs](http://localhost:8000/docs)**

## Current Status

| Component | Status | Coverage |
|-----------|--------|----------|
| Core API | Production Ready | 90% |
| Safety Controls | Operational | 95% |
| Pre-commit Hooks | Automated | 100% |
| CI/CD Pipeline | Enhanced | 100% |
| Science Domain | Ready for Implementation | 0% |
| Commerce Domain | Ready for Implementation | 0% |
| Arts Domain | Ready for Implementation | 0% |

## Contributing

1. **Fork** the repository
2. **Set up** pre-commit hooks: `pre-commit install`
3. **Create** feature branch: `git checkout -b feature/amazing-feature`
4. **Write** tests and code
5. **Run** quality checks: `pre-commit run --all-files`
6. **Submit** pull request

## License

MIT License - see [LICENSE](LICENSE) file for details.
