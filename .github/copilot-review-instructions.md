# Copilot Code Review Instructions — Echoes

## Consent & Provenance

- DCoC provenance: AI-generated content must carry provenance metadata (model, timestamp, confidence).
- Never strip provenance headers from LLM responses.
- All data processing must respect consent boundaries.

## Code Quality

- Type hints required on all function signatures.
- No bare `print()` — use `structlog` or `logging`.
- Pydantic v2 for data models.
- Async-first for I/O operations.
- 120-character line length.

## Security

- Never interpolate user input into prompts without sanitization.
- Never use `eval()`, `exec()`, or `pickle` on untrusted input.
- Validate all user input at API boundaries with Pydantic models.
- Flag quarantined modules — do not modify without explicit approval.

## Shared Rules

- Flag scope expansion beyond PR description.
- Check dependency justification.
- Flag any secret/credential/env patterns.
- Conventional commits: `fix(api):`, `feat(assistant):`, etc.
