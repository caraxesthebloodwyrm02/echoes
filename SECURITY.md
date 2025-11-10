# Security Policy

## Supported Versions

Use this section to tell people about which versions of your project are
currently being supported with security updates.

| Version | Supported          |
| ------- | ------------------ |
| 5.1.x   | :white_check_mark: |
| 5.0.x   | :x:                |
| 4.0.x   | :white_check_mark: |
| < 4.0   | :x:                |

## Reporting a Vulnerability

Please report vulnerabilities via GitHub Issues or security advisories. Provide reproduction steps and affected versions. We aim to acknowledge reports within 72 hours and provide status updates weekly until resolution.

## Outbound Network Enforcement

Echoes enforces a default‑deny outbound egress policy to prevent silent telemetry and accidental data exfiltration.

- Enforcement is centralized in `core_modules/network/policy.py`.
- Tests run with sockets disabled by default (via `pytest-socket`).
- Allowed hosts are controlled through environment variables:
  - `EGRESS_ENFORCE` (default `1`): enable/disable enforcement.
  - `EGRESS_ALLOWLIST` (default `openai`): comma‑separated tokens matched against hostnames.
  - `EGRESS_LOG` (default `1`): `0` silent, `1` basic, `2` verbose.
  - `EGRESS_AUTOPATCH` (default `1`): auto‑patch `requests` to block unauthorized calls.

CI runs `pip-audit`, `safety`, and produces an SBOM (CycloneDX) under the ML Security workflow to detect vulnerable dependencies.
