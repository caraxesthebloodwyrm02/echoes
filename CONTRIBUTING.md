# Contributing to EchoesAI

Thank you for supporting secure, ethical, and high-quality AI! Please help us keep the codebase robust by following these policies:

## Code Quality & Pre-commit
- All changes must pass pre-commit hooks (`black`, `ruff`, security, yaml linting).
- See `.pre-commit-config.yaml` and run `pre-commit install` after cloning.

## CI/CD and Testing
- All PRs must pass **all-green** CI checks (see `.github/workflows/ci.yml`).
- Add/extend self-tests in `/tests/` as needed (use `pytest`).
- Coverage below 85% will fail the main build (configured in `root_configs/pytest.ini`).
- Outbound network is disabled by default in tests via `pytest-socket`. Mark any networked tests with `@pytest.mark.network` (skipped by default). Use `@pytest.mark.integration` for external service tests.
- Run tests locally with the sanitized config: `pytest -c root_configs/pytest.ini`.

## How to Contribute
- Fork, make a topic branch, add focused commits, and open a PR.
- File bugs/feature requests as [GitHub Issues](https://github.com/caraxesthebloodwyrm02/echoes/issues).
- Update documentation clearly if you add features or change behavior.

---

By contributing you agree to uphold the project’s Consent-Based License (see `LICENSE` for full terms).
