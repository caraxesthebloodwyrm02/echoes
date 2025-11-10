# Key Rotation Procedures

This document defines standard operating procedures (SOP) for rotating API keys, access tokens, and signing secrets used by Echoes across environments.

## Objectives

- Minimize blast radius of credential compromise
- Meet compliance requirements for cryptographic key management
- Provide consistent, automated, and auditable rotation processes

## Scope

- API keys for external services (e.g., OpenAI, GitHub, Hugging Face)
- Internal service-to-service tokens
- Signing keys/secrets used for webhooks and package publishing

## Storage Backends

- Preferred: Cloud secret manager (e.g., AWS Secrets Manager, GCP Secret Manager, Azure Key Vault)
- Alternative (CI-only): GitHub Actions Encrypted Secrets
- Local dev: `.env` files managed via direnv or dotenv (never committed)

## Rotation Frequency

- External API keys: every 90 days or per vendor policy (whichever is stricter)
- High-privilege tokens: every 30 days
- Webhook signing secrets: every 180 days
- Immediate rotation upon suspicion of compromise

## Rotation Roles and Access

- Requester: Service owner creates rotation ticket
- Approver: Security (`@team/security`) and Maintainers (`@team/maintainers`)
- Executor: CI automation (preferred) or designated engineer

## Standard Rotation Workflow (Dual-Key Strategy)

1. Prepare
   - Open a rotation ticket with context and impacted services
   - Identify environment scopes: dev, staging, prod
2. Issue new key (Key-B)
   - Create in secret manager with version tag (e.g., `openai_api_key:v2025-11-10`)
   - Add metadata: owner, purpose, expiry date
3. Deploy with overlap
   - Update configuration to accept both Key-A (old) and Key-B (new) where supported
   - Roll out to dev → staging → prod
   - Monitor error rates and policy logs for anomalies
4. Switch default
   - Update application to use Key-B as the primary
   - Keep Key-A valid for fallback window (24–72 hours)
5. Decommission Key-A
   - Revoke old key
   - Remove from secret stores and configs
   - Close rotation ticket with evidence

## Automation (GitHub Actions)

- Use `workflow_dispatch` inputs to trigger rotations safely.
- Required steps:
  - Fetch latest key version
  - Create new secret and set labels
  - Update environment variables (`OPENAI_API_KEY`, `HUGGINGFACE_TOKEN`, etc.)
  - Create a changelog note and notify on Slack/Teams

Example step snippet:

```yaml
- name: Rotate OpenAI key (placeholder)
  run: |
    echo "Create and set new secret via cloud CLI or API"
```

## Rollback Plan

- If failures occur after switching to Key-B:
  - Immediately revert to Key-A (if not revoked)
  - Investigate service errors and policy logs
  - Reattempt rotation after remediation

## Monitoring & Evidence

- Logs: `EGRESS_LOG_FORMAT=json` helps correlate request failures to key issues
- Metrics: spike in `blocked_total` or 401/403 rates indicates auth drift
- Evidence to attach to rotation ticket:
  - Secret version IDs and timestamps
  - CI logs and deployment IDs
  - Screenshots of successful vendor-side validation

## Compliance Mapping

- SOC 2 CC6.1, CC6.6: Logical access and key management
- ISO/IEC 27001 A.8.24, A.8.28: Use of cryptography, secure key lifecycle
- NIST CSF PR.AC-1, PR.DS-5: Access control and data security

## References

- `POLICY_SPEC.md` — enforcement and auditing context
- `docs/POLICY_GOVERNANCE.md` — change management and approvals
- `docs/COMPLIANCE.md` — overall mapping and controls
