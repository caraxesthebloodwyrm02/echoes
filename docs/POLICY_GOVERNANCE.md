# Policy Governance and Configuration Auditing

## Overview

This document outlines the governance model for the egress policy system, including configuration auditing, CI integration, and change management processes.

## Policy Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `EGRESS_ENFORCE` | `1` | Enable/disable policy enforcement |
| `EGRESS_ALLOWLIST` | `openai` | Comma-separated list of allowed host keywords |
| `EGRESS_LOG` | `1` | Logging level (0=silent, 1=basic, 2=verbose) |
| `EGRESS_LOG_FORMAT` | `text` | Log format (`text` or `json`) |
| `EGRESS_OTEL_ENABLE` | `0` | Enable OpenTelemetry metrics |
| `EGRESS_PROM_ENABLE` | `0` | Enable Prometheus metrics |
| `EGRESS_CI_FAIL_ON_BLOCKED` | `0` | Fail CI on blocked events |
| `EGRESS_CI_ALLOW_DISABLE` | `0` | Allow enforcement disabled in CI |
| `EGRESS_CI_FAIL_ON_DRIFT` | `0` | Fail CI on allowlist drift |

### CLI Interface

The policy module provides a comprehensive CLI for management and verification:

```bash
# Print current configuration
python -m core_modules.network.policy --print

# Print configuration as JSON
python -m core_modules.network.policy --print --json

# Verify policy configuration
python -m core_modules.network.policy --verify

# Generate summary report
python -m core_modules.network.policy --summary-out egress-summary.json
```

## Configuration Auditing

### Verification Rules

The policy verification enforces the following rules in CI environments:

1. **Enforcement Requirement**: `EGRESS_ENFORCE` must be `1` unless `EGRESS_CI_ALLOW_DISABLE=1`
2. **Non-empty Allowlist**: Allowlist cannot be empty
3. **No Wildcards**: Wildcard tokens (`*`, `all`, `any`) are prohibited
4. **Drift Detection**: Allowlist must match the locked version in `policy_allowlist.lock`
5. **Blocked Events**: Optional failure on blocked events when `EGRESS_CI_FAIL_ON_BLOCKED=1`

### Lock File Management

The `policy_allowlist.lock` file provides version control for allowed hosts:

- **Location**: `core_modules/network/policy_allowlist.lock`
- **Format**: One token per line, comments start with `#`
- **Updates**: Must be done via PR with security/maintainer review
- **Verification**: CI checks for drift between env allowlist and lock file

Example lock file:
```
# Egress Policy Allowlist Lock
# One token per line, comments start with #
# This file locks the allowed host keywords to prevent drift
# Update via PR review only

openai
```

## CI Integration

### GitHub Actions Workflow

The main CI workflow (`.github/workflows/ci.yml`) includes:

1. **Policy Verification**: Runs `policy --verify` with summary output
2. **Artifact Upload**: Uploads `egress-summary.json` as CI artifact
3. **Blocked Event Detection**: Emits warnings for each unique blocked host
4. **Security Scanning**: Runs `pip-audit`, `safety`, and `bandit`
5. **SBOM Generation**: Creates CycloneDX software bill of materials
6. **Version Verification**: Prevents security tooling downgrades

### GitHub Annotations

The CI system emits GitHub Annotations for:
- Policy verification failures
- Blocked egress events
- Security vulnerability findings
- Version requirement violations

### Artifact Management

CI artifacts include:
- `egress-summary.json`: Policy metrics and recent events
- `security-reports`: SARIF, safety, and bandit reports
- `sbom`: CycloneDX software bill of materials
- `coverage-xml`: Test coverage reports

## Change Management

### CODEOWNERS

The following files require security/maintainer review:
- `core_modules/network/policy.py`
- `core_modules/network/policy_allowlist.lock`
- `.github/workflows/ci.yml`
- `.github/workflows/enforce-ml-safety.yml`
- `SECURITY.md`, `POLICY_SPEC.md`, `COMPLIANCE.md`
- `bandit.yaml`, `requirements-security.txt`
- `tools/verify_versions.py`

### Review Process

1. **Policy Changes**: Must be reviewed by `@team/security` and `@team/maintainers`
2. **Lock File Updates**: Require justification and security review
3. **CI Workflow Changes**: Must maintain security guarantees
4. **Emergency Changes**: Use `security-waiver` label with documented rationale

### Compliance Requirements

- **SOC 2**: Access controls, change management, monitoring
- **ISO 27001**: Information security policies, incident management
- **NIST CSF**: Identify, Protect, Detect, Respond, Recover

## Monitoring and Alerting

### Metrics Collection

The policy system supports multiple monitoring backends:

1. **Runtime Metrics**: `allowed_total`, `blocked_total`, recent events
2. **OpenTelemetry**: Optional export to OTEL endpoints
3. **Prometheus**: Optional Prometheus metrics
4. **Structured Logging**: JSON format with timestamps and metadata

### Alert Configuration

Configure alerts for:
- High rate of blocked events
- Policy verification failures
- Security tooling downgrades
- Drift detection violations

## Security Considerations

### Threat Model

1. **Policy Bypass**: Attempts to disable enforcement or use wildcards
2. **Drift Attacks**: Unauthorized changes to allowlist
3. **Dependency Attacks**: Downgrading security tooling
4. **CI Compromise**: Tampering with verification logic

### Mitigation Strategies

1. **Defense in Depth**: Multiple verification layers
2. **Principle of Least Privilege**: Minimal default allowlist
3. **Fail Safe**: Default deny posture
4. **Audit Trail**: Comprehensive logging and metrics
5. **Separation of Duties**: Required multiple reviewers for changes

## Best Practices

### Configuration Management

1. **Version Control**: All policy changes tracked in git
2. **Environment Parity**: Consistent settings across environments
3. **Change Documentation**: Clear commit messages and PR descriptions
4. **Rollback Planning**: Documented rollback procedures

### Operational Procedures

1. **Regular Audits**: Weekly automated security scans
2. **Incident Response**: Documented response to policy violations
3. **Training**: Team education on policy requirements
4. **Testing**: Comprehensive test coverage for policy logic

### Troubleshooting

Common issues and resolutions:

1. **CI Failures**: Check egress-summary.json for blocked events
2. **Drift Detection**: Compare env allowlist with lock file
3. **Version Conflicts**: Run `tools/verify_versions.py` locally
4. **Logging Issues**: Verify `EGRESS_LOG_FORMAT` and `EGRESS_LOG` settings

## References

- [Network Policy Implementation](core_modules/network/policy.py)
- [Security Requirements](requirements-security.txt)
- [CI Configuration](.github/workflows/ci.yml)
- [Compliance Mapping](COMPLIANCE.md)
- [Key Rotation Procedures](docs/KEY_ROTATION.md)
