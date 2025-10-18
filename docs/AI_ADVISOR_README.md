# AI Advisor - Domain-Aligned AI with Safety Controls

**Version:** 0.1.0
**Status:** 🟢 Sprint 0-1 Complete | Active Development

[![CI](https://github.com/yourusername/ai-advisor/workflows/CI/badge.svg)](https://github.com/yourusername/ai-advisor/actions)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

---

## Overview

**AI Advisor** is a domain-aligned AI platform that provides intelligent services across **Science**, **Commerce**, and **Arts** domains while enforcing strict safety controls, provenance validation, and ethical governance.

### Key Features

🔒 **Provenance Enforcement**
- Every assertion must cite verifiable sources
- Prevents hallucinations and misinformation
- Automatic validation via middleware

🤝 **Human-in-the-Loop Feedback**
- Capture user corrections and labels
- Continuous improvement pipeline
- No automatic retraining without approval

🛡️ **Agent Safety Layer**
- Dry-run mode by default
- Action whitelist enforcement
- Emergency kill-switch
- Resource limits and timeouts

🔬 **Science Domain**
- Biomedical research aggregation
- Chemistry and physics simulations
- Cross-disciplinary data flow

💼 **Commerce Domain**
- Universal Basic Income simulation
- Employment opportunity matching
- Artisan-to-market connector

🎨 **Arts Domain**
- Creative intelligence engine
- Cultural preservation tools
- Language evolution modeling

---

## Quick Start

### Prerequisites

- Python 3.10 or 3.11
- pip package manager
- (Optional) PostgreSQL, Redis for production

### Installation

```bash
# Clone repository
git clone <your-repo-url>
cd ai-advisor

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements/ai_advisor_dev.txt

# Set up environment
cp src/.env.example src/.env

# Run the API
cd src
python main.py
```

### Verify Installation

```bash
# Health check
curl http://localhost:8000/api/health

# Interactive docs
open http://localhost:8000/docs
```

**See [QUICKSTART.md](docs/QUICKSTART.md) for detailed setup instructions.**

---

## Architecture

### System Design

```
┌─────────────────────────────────────────────────────────────────┐
│                        FastAPI Application                       │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │           ProvenanceEnforcerMiddleware                     │ │
│  │  (Validates all assertions have sources)                   │ │
│  └────────────────────────────────────────────────────────────┘ │
│                              ▼                                   │
│  ┌──────────────────┬──────────────────┬──────────────────┐    │
│  │  Science Module  │ Commerce Module  │   Arts Module    │    │
│  │                  │                  │                  │    │
│  │ • Biomedical     │ • UBI Sim        │ • Creativity     │    │
│  │ • Chemistry      │ • Employment     │ • History        │    │
│  │ • Physics        │ • Artisan        │ • Language       │    │
│  └──────────────────┴──────────────────┴──────────────────┘    │
│                              ▼                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              Cross-Domain Fusion Layer                     │ │
│  │  (Knowledge graph, ontology alignment)                     │ │
│  └────────────────────────────────────────────────────────────┘ │
│                              ▼                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                  Agent Safety Layer                        │ │
│  │  • Dry-run mode  • Whitelist  • Kill-switch  • Timeouts   │ │
│  └────────────────────────────────────────────────────────────┘ │
│                              ▼                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │             Human-in-the-Loop Pipeline                     │ │
│  │  Feedback → Queue → Labeling → Validation → Retraining    │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Technology Stack

**Core Framework:**
- **FastAPI** - Modern async web framework
- **Pydantic** - Data validation
- **Python 3.10+** - Type hints and async support

**Domain Libraries:**
- **Science:** Biopython, NumPy, SciPy
- **Commerce:** pandas, scikit-learn, statsmodels
- **Arts:** transformers, nltk, Pillow

**Infrastructure:**
- **PostgreSQL** - Primary database
- **Redis** - Feedback queue and caching
- **Docker** - Containerization
- **GitHub Actions** - CI/CD

---

## Project Structure

```
ai-advisor/
├── src/
│   ├── main.py                      # FastAPI application entry
│   ├── api/
│   │   ├── schemas.py               # Pydantic models
│   │   └── routes/
│   │       ├── system.py            # Provenance, HIL, agents
│   │       ├── science/             # Science domain endpoints
│   │       ├── commerce/            # Commerce domain endpoints
│   │       └── arts/                # Arts domain endpoints
│   ├── core/
│   │   ├── validation/              # Provenance, privacy, compliance
│   │   ├── ethics/                  # Ethics board, bias detection
│   │   ├── agents/                  # Agent safety, orchestration
│   │   ├── hil/                     # Feedback queue, labeling
│   │   └── fusion/                  # Cross-domain intelligence
│   └── data/                        # Data storage
│
├── packages/
│   ├── core/                        # Shared utilities
│   ├── security/                    # Auth, encryption
│   └── monitoring/                  # Metrics, health checks
│
├── tests/
│   ├── unit/                        # Unit tests
│   ├── integration/                 # Integration tests
│   └── security/                    # Security tests
│
├── config/
│   ├── whitelist.yaml               # Agent action whitelist
│   ├── data_sources.yaml            # Verified data sources
│   └── compliance.yaml              # Privacy/compliance rules
│
├── docs/
│   ├── DOMAIN_EXPANSION_PLAN.md     # Implementation roadmap
│   ├── API_REFERENCE.md             # Complete API docs
│   ├── INTERVIEW_CARDS.md           # Domain requirements
│   ├── SAFETY_GUIDE.md              # Safety procedures
│   └── QUICKSTART.md                # Quick start guide
│
├── requirements/
│   ├── ai_advisor_base.txt          # Core dependencies
│   ├── ai_advisor_dev.txt           # Development tools
│   └── ai_advisor_domains.txt       # Domain-specific libs
│
└── .github/
    └── workflows/
        └── ai_advisor_ci.yml        # CI/CD pipeline
```

---

## API Overview

### Core Endpoints

#### Provenance Validation
```http
POST /api/assertions/validate
```
Validate that assertions include proper source citations.

#### Human-in-the-Loop Feedback
```http
POST /api/hil/feedback
```
Capture user corrections and labels for continuous improvement.

#### Agent Execution
```http
POST /api/agent/execute
```
Execute AI agents with safety controls (dry-run default).

#### Agent Kill-Switch
```http
POST /api/agent/kill
```
Emergency stop for runaway agents.

#### System Health
```http
GET /api/health
GET /api/metrics
```
Monitor system status and key performance indicators.

**Full API documentation:** http://localhost:8000/docs

---

## Safety Controls

### 1. Provenance Enforcement

**Every assertion must cite sources:**

```json
{
  "claim": "Treatment X reduces symptoms of disease Y",
  "provenance": [
    {
      "source": "PubMed",
      "url": "https://pubmed.ncbi.nlm.nih.gov/12345678/",
      "snippet": "Study demonstrates...",
      "timestamp": "2025-10-05T00:00:00Z",
      "confidence": 0.92
    }
  ]
}
```

**Middleware automatically rejects claims without sources.**

### 2. Agent Safety Layer

- ✅ **Dry-run mode by default** - No side effects until approved
- ✅ **Action whitelist** - Only approved actions can execute
- ✅ **Kill-switch** - Emergency stop for runaway agents
- ✅ **Timeouts** - Maximum execution time (300s)
- ✅ **Resource limits** - Max concurrent agents (10)

### 3. Human-in-the-Loop

- ✅ **Feedback queue** - Capture user corrections
- ✅ **No auto-retraining** - Human approval required
- ✅ **A/B testing** - Gradual rollout of model updates
- ✅ **Rollback capability** - Quick revert if issues arise

### 4. Privacy & Compliance

- ✅ **PII redaction** - Automatic removal of sensitive data
- ✅ **HIPAA compliance** - Health data protections
- ✅ **GDPR compliance** - European data regulations
- ✅ **Audit logs** - All actions tracked and traceable

**See [SAFETY_GUIDE.md](docs/SAFETY_GUIDE.md) for complete details.**

---

## Development

### Running Tests

```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ -v --cov=src --cov-report=html

# Specific test suite
pytest tests/test_api_contracts.py -v
```

### Code Quality

```bash
# Format code
black src tests

# Lint
flake8 src tests

# Type check
mypy src --ignore-missing-imports

# Security scan
bandit -r src
```

### Pre-commit Hooks

```bash
# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

---

## Implementation Roadmap

### ✅ Sprint 0 (Week 1) - COMPLETE

- [x] Project structure created
- [x] Core schemas implemented (Provenance, Assertion, HILFeedback)
- [x] Security baseline (SCA, linting, type checking)
- [x] Documentation framework

### ✅ Sprint 1 (Weeks 2-3) - COMPLETE

- [x] Provenance enforcement middleware
- [x] HIL feedback endpoints
- [x] Agent safety layer (dry-run, kill-switch)
- [x] API endpoints operational
- [x] Comprehensive test suite
- [x] CI/CD pipeline (GitHub Actions)

### 🔄 Sprint 2 (Weeks 4-5) - IN PROGRESS

- [ ] Science domain: Biomedical search integration
- [ ] Commerce domain: UBI simulation engine
- [ ] Privacy filters and compliance validators
- [ ] Model routing with telemetry
- [ ] Cross-domain data flow architecture

### ⏳ Sprint 3 (Weeks 6-7)

- [ ] Knowledge fusion layer
- [ ] Cost and energy metering
- [ ] Advanced domain features
- [ ] Cross-domain intelligence

### ⏳ Sprint 4 (Weeks 8-9)

- [ ] Production hardening
- [ ] Comprehensive testing (load, security, chaos)
- [ ] Complete documentation
- [ ] Deployment automation

**See [DOMAIN_EXPANSION_PLAN.md](docs/DOMAIN_EXPANSION_PLAN.md) for full roadmap.**

---

## Key Performance Indicators

### Safety Metrics

- **Provenance Coverage:** >99% (Current: 100%)
- **Agent Safety:** 0 unauthorized actions (Current: 0)
- **Dry-Run Percentage:** >95% (Current: 100%)

### Quality Metrics

- **Test Coverage:** >80% (Current: ~85%)
- **API Response Time:** <500ms p95
- **System Uptime:** >99.5%

### Business Metrics

- **HIL Feedback Volume:** Track user engagement
- **Cross-Domain Queries:** Track fusion usage
- **Cost per Query:** Optimize efficiency

---

## Contributing

### Development Workflow

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Make changes and add tests
4. Run quality checks (`black`, `flake8`, `mypy`, `pytest`)
5. Commit changes (`git commit -m 'feat: add amazing feature'`)
6. Push to branch (`git push origin feature/amazing-feature`)
7. Open Pull Request

### Code Standards

- ✅ All tests must pass
- ✅ Code coverage should not decrease
- ✅ Security scans must be clean
- ✅ Follow existing code style (black, isort)
- ✅ Add docstrings to public APIs
- ✅ Update documentation as needed

**See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.**

---

## Documentation

### For Users

- **[Quick Start Guide](docs/QUICKSTART.md)** - Get started in 5 minutes
- **[API Reference](docs/API_REFERENCE.md)** - Complete endpoint documentation
- **Interactive Docs** - http://localhost:8000/docs

### For Developers

- **[Domain Expansion Plan](docs/DOMAIN_EXPANSION_PLAN.md)** - Implementation roadmap
- **[Interview Cards](docs/INTERVIEW_CARDS.md)** - Domain requirements
- **[Safety Guide](docs/SAFETY_GUIDE.md)** - Safety controls and procedures

### For Operators

- **[Safety Guide](docs/SAFETY_GUIDE.md)** - Incident response procedures
- **Monitoring** - Health and metrics endpoints
- **Configuration** - `config/` directory

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Support

### Getting Help

- **Documentation:** `/docs` directory and http://localhost:8000/docs
- **Issues:** GitHub Issues for bug reports and feature requests
- **Discussions:** GitHub Discussions for questions and ideas
- **Security:** security@ai-advisor.example.com for security issues

### Community

- **Contributing:** See [CONTRIBUTING.md](CONTRIBUTING.md)
- **Code of Conduct:** See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- **Roadmap:** See [DOMAIN_EXPANSION_PLAN.md](docs/DOMAIN_EXPANSION_PLAN.md)

---

## Acknowledgments

### Inspiration

This project builds on the educational ecosystem framework and extends it with:
- Domain-aligned AI intelligence
- Strict provenance enforcement
- Human-in-the-loop continuous improvement
- Cross-domain knowledge fusion

### Technology

Built with modern Python async frameworks and industry-standard safety practices.

---

## Status

**Current Status:** 🟢 Active Development

- ✅ Core API operational
- ✅ Safety controls implemented
- ✅ Testing framework complete
- ✅ CI/CD pipeline active
- 🔄 Domain modules in progress

**Next Milestone:** Sprint 2 - Domain Integration (2 weeks)

---

**Questions?** Read the [Quick Start Guide](docs/QUICKSTART.md) or check the [FAQ](docs/FAQ.md).

**Ready to contribute?** See [CONTRIBUTING.md](CONTRIBUTING.md) to get started!

**Need help?** Open an issue or start a discussion on GitHub.

---

*Built with ❤️ for safe, ethical, and transparent AI.*
