# Contributing to Echoes

## 📋 Important Notice

**Consent-Based License**: Before contributing to this project, you must obtain explicit consent from the licensor. Please read the [LICENSE](LICENSE) file and contact Erfan Kabir (irfankabir02@gmail.com) to request consent for contribution.

## Development Setup

### Prerequisites
- Python 3.12+
- Git
- Windows Subsystem for Linux (WSL) or native Linux/Mac

### Quick Start
1. Clone the repository:
   ```bash
   git clone https://github.com/caraxesthebloodwyrm02/echoes.git
   cd echoes
   ```

2. Set up virtual environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   # or
   source .venv/bin/activate  # Linux/Mac
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Install development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```

5. Run tests:
   ```bash
   pytest tests/
   ```

## Project Structure

```
echoes/
├── docs/           # Documentation
├── demos/          # Demo scripts and examples
├── tests/          # Test files
├── docker/         # Docker configuration
├── src/            # Source code
├── requirements.txt
├── README.md
└── CONTRIBUTING.md
```

## Development Guidelines

### Code Style
- Follow PEP 8
- Use type hints
- Write docstrings for public functions
- Use black for code formatting

### Testing
- Write tests for new features
- Maintain test coverage above 80%
- Run tests before committing: `pytest tests/`

### Git Workflow
- Create feature branches from `main`
- Use descriptive commit messages
- Squash commits when merging
- Keep PRs small and focused

### Documentation
- Update documentation for new features
- Keep README.md current
- Use Markdown for all documentation
- See `docs/RAG_OPENAI_MIGRATION.md` for OpenAI embeddings RAG setup
 
## Safety & Research-Only Guidelines

- Research-only. No commercial use. See RESEARCH_ACCESS_GUIDE.md and docs/SCIENTIFIC_API_REFERENCE.md.
- Respect physics guardrails. If a result is marked "dormant," treat it as a pause to gather clearer evidence.
- Prefer reversible changes over irreversible ones. Ship small, testable steps.
- Seek repeating patterns. One-off spikes are noise until they repeat.
- Sidechain smoothing reduces spikes; do not remove it to force higher scores.
- Consensus matters. Forwarding requires physics "active" and a sufficient consensus verdict.
- Encryption: use AES-GCM with AAD contexts. Never hard-code keys or secrets; use environment variables.
- Logs: do not include secrets or raw sensitive payloads. Keep audit logs minimal and masked.
- Tone: keep docs simple, risk-aware, and kind. Use plain language; avoid jargon when possible.
- Production: set ECHOES_ENCRYPTION_FORCE=true and restrict CORS/hosts.

## Getting Help
- Check existing issues and documentation first
- Create detailed bug reports with reproduction steps
- Ask questions in discussions

## License
By contributing, you agree that your contributions will be licensed under the same license as the project.
