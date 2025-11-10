# Egress Policy Specification (POLICY_SPEC)

This document is the authoritative specification for the Echoes egress policy: what outbound network activity is permitted, how it is enforced and audited, and how changes are governed. It complements `docs/POLICY_GOVERNANCE.md` (process, auditing) by defining the technical contract and controls.

## 1. Scope and Objectives

- Default-deny posture for outbound network requests from Echoes services, tools, and tests.
- Explicit allowlist by service keyword (e.g., `openai`, `github`, `huggingface`).
- Deterministic behavior across local, CI, and production environments.
- Strong observability: structured logs, metrics, and CI artifacts.

## 2. Policy Model

- Allowlist tokens are matched against destination hostnames using case-insensitive substring match of a curated keyword set (e.g., token `openai` matches `api.openai.com`).
- Wildcards are prohibited (`*`, `all`, `any`).
- Empty allowlists are invalid in CI unless explicitly waived (see Governance).
- Denied requests are blocked prior to the actual network call where a shim exists; otherwise they are logged and prevented when feasible.

### 2.1 Sources of Truth

- Lock file: `core_modules/network/policy_allowlist.lock` (one token per line, comments with `#`).
- Runtime env: `EGRESS_ALLOWLIST` (comma-separated tokens). When present in CI, must match the lock file (drift protection).
- Enforcement flag: `EGRESS_ENFORCE=1` (default in CI). May be disabled locally for development use cases.

## 3. Configuration

Environment variables (full table in `docs/POLICY_GOVERNANCE.md`):

- `EGRESS_ENFORCE` (default `1`): Enable policy enforcement.
- `EGRESS_ALLOWLIST` (default `openai`): Comma-separated tokens.
- `EGRESS_LOG` (default `1`), `EGRESS_LOG_FORMAT` (`text`|`json`): Logging.
- `EGRESS_OTEL_ENABLE`, `EGRESS_PROM_ENABLE`: Optional metrics backends.
- CI hardening: `EGRESS_CI_FAIL_ON_BLOCKED`, `EGRESS_CI_ALLOW_DISABLE`, `EGRESS_CI_FAIL_ON_DRIFT`.

## 4. Enforcement

- Primary implementation: `core_modules/network/policy.py` provides:
  - A validator (`--verify`) that enforces the ruleset and drift checks.
  - A runtime guard that resolves destination hostnames and checks tokens before connect.
- Cross-language shims must call into a common decision function described in `docs/CROSS_LANGUAGE_SHIMS.md`.
- Python requests/urllib3 integration: wrapper or session factory that evaluates policy prior to `send()`.

### 4.1 Decision Contract

Given `method`, `url`, and optional metadata, return a decision tuple:

```
Decision = {
  "allowed": bool,
  "reason": "string",
  "matched_token": "string|null",
  "destination_host": "string",
}
```

If `allowed=false` and `EGRESS_ENFORCE=1`, raise a `PolicyViolation` prior to the network call. Always log a structured event.

## 5. Auditing and Telemetry

- CLI: `python -m core_modules.network.policy --verify --summary-out egress-summary.json`.
- Metrics: `allowed_total`, `blocked_total`; last N events summarized in CI artifacts.
- Logs: JSON entries include timestamp, host, token, decision, and caller.
- CI emits GitHub annotations on verification failures or large spike of blocked events.

## 6. Rules

1. Enforcement must be enabled in CI unless explicitly waived via `EGRESS_CI_ALLOW_DISABLE=1`.
2. Allowlist must be non-empty.
3. No wildcards or `all/any` tokens.
4. In CI, `EGRESS_ALLOWLIST` must match `policy_allowlist.lock` when `EGRESS_CI_FAIL_ON_DRIFT=1`.
5. Blocked requests must be logged with enough context to triage.

## 7. Change Management

- Lock file updates via PR only, reviewed by `@team/security` and `@team/maintainers`.
- Emergency changes require a `security-waiver` label and postmortem within 48 hours.
- See `docs/POLICY_GOVERNANCE.md` for the full process and CODEOWNERS list.

## 8. Cross-Language Shims

- See `docs/CROSS_LANGUAGE_SHIMS.md` for the interface and minimal adapters for Python, Node.js, and Go.
- Shims must not silently bypass the policy; they must call the decision contract and enforce it.

## 9. Compliance Mapping

- SOC 2 CC6.6, CC7.2: Logical access controls and monitoring.
- ISO/IEC 27001 A.8.20, A.8.21: Secure network services and segregation.
- NIST CSF PR.AC, PR.PT: Access control, protective technology.
- Key management and rotation procedures are defined in `docs/KEY_ROTATION.md`.

## 10. Versioning

- This specification is versioned with the repository. Breaking changes must update this file with a changelog entry in `CHANGELOG.md` and inform security maintainers.

## 11. References

- Implementation: `core_modules/network/policy.py`
- Governance: `docs/POLICY_GOVERNANCE.md`
- Shims: `docs/CROSS_LANGUAGE_SHIMS.md`
- Key Rotation: `docs/KEY_ROTATION.md`
- Compliance: `docs/COMPLIANCE.md`
