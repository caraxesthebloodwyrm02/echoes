# Safety & Security Rules

Applies to: all files, with special attention to `api/**`, `services/**`

## Golden Rules

- **Never** remove or weaken existing validation logic
- **Never** add bypass paths or "dev mode" shortcuts
- **Never** use `eval()`, `exec()`, or `pickle` on untrusted input
- **Always** validate all user input at API boundaries with Pydantic models

## Consent-Based Licensing

- Echoes operates under a Consent-Based License — all data processing must respect consent boundaries
- Never process, store, or transmit user data without explicit consent verification
- Audit all new data flows for consent compliance before merging

## DCoC Provenance

- All AI-generated content must carry provenance metadata (model, timestamp, confidence)
- Never strip or modify provenance headers from LLM responses
- Decision chain of custody (DCoC) must be preserved end-to-end

## Security Audit Awareness

- If any module is flagged for security quarantine, do not modify it without explicit approval
- Quarantined modules are marked in project documentation — check before editing
- All security-sensitive changes require test coverage before commit

## Injection Resistance

- Never interpolate user input into prompts without sanitization
- Never pass user input to shell commands, SQL queries, or dynamic imports
- API routes must validate content-type headers and reject unexpected payloads
