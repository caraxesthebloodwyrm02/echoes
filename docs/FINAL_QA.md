# Final QA Checklist — Policy, Shims, Bandit, Key Rotation

Use this checklist before release or major merges. Link any evidence (artifacts, screenshots, CI run URLs) to each item.

## A. Policy Specification and Governance
- [ ] `POLICY_SPEC.md` present at repo root and reflects the current implementation
- [ ] `docs/POLICY_GOVERNANCE.md` up to date with env vars, CI rules, and artifacts
- [ ] Lock file `core_modules/network/policy_allowlist.lock` exists and contains expected tokens
- [ ] CODEOWNERS include policy and security-critical files (spec, governance, lock, workflows)

## B. Cross-Language Shims
- [ ] `docs/CROSS_LANGUAGE_SHIMS.md` present and reviewed by owners of Python/Node/Go components
- [ ] Python shim pattern validated (requests/urllib3 wrapper blocks non-allowlisted hosts)
- [ ] Node.js shim pattern validated (fetch/axios wrapper)
- [ ] Go shim pattern validated (`net/http` client wrapper)
- [ ] No wildcard or bypass paths in shims; all call the decision contract

## C. Bandit Integration
- [ ] `bandit.yaml` exists and is used across tools
- [ ] `requirements-security.txt` includes `bandit>=1.7.5`
- [ ] `.github/workflows/enforce-ml-safety.yml` runs Bandit and uploads `bandit-report.json` (non-blocking)
- [ ] `ci/gh-actions/enforce-ml-safety.yml` runs Bandit and uploads `bandit-report.json` (non-blocking)
- [ ] VS Code tasks/pre-commit (if enabled) align with `bandit.yaml`
- [ ] Latest CI run shows uploaded Bandit artifact

## D. Key Rotation
- [ ] `docs/KEY_ROTATION.md` present with rotation SOP (dual-key), automation, rollback
- [ ] Rotation ticket template exists or is referenced in team docs
- [ ] GitHub environments or secret manager entries labeled with versions (e.g., `vYYYY-MM-DD`)
- [ ] Evidence of a dry-run or last rotation recorded (timestamps, logs)

## E. Compliance Mapping
- [ ] `docs/COMPLIANCE.md` contains quick references to POLICY_SPEC, POLICY_GOVERNANCE, KEY_ROTATION
- [ ] Controls mapped to SOC 2, ISO 27001, NIST CSF for policy and key management
- [ ] CI artifacts retained per retention policy (SARIF, SBOM, Bandit, policy summary)

## F. CI Artifacts & Observability
- [ ] Policy verification summary produced in CI: `egress-summary.json` (if configured)
- [ ] Security artifacts uploaded: `pip-audit-results.sarif`, `safety-report.txt`, `sbom/cyclonedx-sbom.xml`, `bandit-report.json`
- [ ] GitHub annotations appear for failures/warnings

## G. Smoke Tests (Manual)
- [ ] Allowed host request succeeds (e.g., `https://api.openai.com` when `openai` token present)
- [ ] Blocked host request raises/returns policy violation with structured log entry
- [ ] Changing `EGRESS_ALLOWLIST` in CI triggers drift detection (if enabled)

## H. Sign-off
- [ ] Security reviewer: @team/security
- [ ] Maintainer reviewer: @team/maintainers
- [ ] Date and CI run link:
