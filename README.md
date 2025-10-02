# Python Automation Framework

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI/CD](https://github.com/caraxesthebloodwyrm02/echoes/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/caraxesthebloodwyrm02/echoes/actions)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A robust, context-aware Python automation framework for security, maintenance, and monitoring tasks.

## Features

- 🛡️ Security-first design
- 🔄 Context-aware task execution
- 🧪 Comprehensive test coverage
- 📝 Structured logging
- 🔧 Extensible architecture
- ⚡ CLI and programmatic interfaces

## Installation

```bash
# Clone the repository
git clone https://github.com/caraxesthebloodwyrm02/echoes.git
cd echoes

# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Running Tasks

```bash
# Run a specific task type and frequency
python -m automation.scripts.run_automation --task-type cleanup --frequency monthly

# Dry run mode
python -m automation.scripts.run_automation --task-type security --frequency daily --dry-run
```

### Configuration

Edit `config/automation_config.yaml` to configure tasks and schedules.

## Development

### Project Structure

```
.
├── automation/           # Main package
│   ├── config/          # Configuration files
│   ├── core/            # Core framework components
│   ├── scripts/         # Entry point scripts
│   ├── tasks/           # Task implementations
│   └── tests/           # Test suite
├── docs/               # Documentation
└── scripts/            # Utility scripts
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=automation --cov-report=html
```

## CI/CD

This project uses GitHub Actions for CI/CD. The workflow includes:

- Linting with `black` and `flake8`
- Type checking with `mypy`
- Unit testing with `pytest`
- Code coverage reporting
- Automated version bumping and releases

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

Distributed under the MIT License. See `LICENSE` for more information.

## Contact

Your Name - [@your_twitter](https://twitter.com/your_twitter)

Project Link: [https://github.com/caraxesthebloodwyrm02/echoes](https://github.com/caraxesthebloodwyrm02/echoes) Framework (Context-Aware, Safety-Hardened)

## Overview
- Modular, config-driven automation for security, cleanup, maintenance, and monitoring
- Context-aware: every task receives system/user/environment info
- Safety-hardened: dry-run, pre-checks, robust error handling

## Structure
```
automation/
  core/
    context.py
    logger.py
    config.py
    orchestrator.py
  tasks/
    sanitize_codebase.py
    ... (add more tasks)
  scripts/
    run_automation.py
  config/
    automation_config.yaml
  logs/
```

## Usage
### Run a Task
```sh
python automation/scripts/run_automation.py --task-type cleanup --frequency monthly
```
- Use `--dry-run` for safety preview

### Add a Task
- Implement `run(context)` in `automation/tasks/<taskname>.py`
- Register in `automation/config/automation_config.yaml`

## Safety Features
- Dry-run mode for all destructive actions
- Context object for environment/user awareness
- Exception handling and logging
- Configurable via YAML

## Extending
- Add new modules to `tasks/`
- Add new frequencies/types in config
- Use context for custom safety logic

---

**This framework is ready for production automation with proven patterns and hardened safety.**
