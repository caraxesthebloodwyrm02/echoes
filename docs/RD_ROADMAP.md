# Realtime Preview — Unified Research–Development Roadmap

## Vision
Maintain interpretive depth while moving from prototype to production via versioned milestones and feedback loops.

## Milestones
- **v0.1 Research Demo**
  - Demos and tests runnable via `launcher.py`
  - Basic metrics captured from `get_full_state()`
- **v0.3 Logging Instrumentation**
  - Add optional periodic snapshot logger (no external deps) writing JSON under `exports/metrics/`
  - Toggle via configuration flag
- **v0.5 Internal Test Release**
  - IDE/editor plugin prototype using `process_input()` bridge
  - Security checks enforced before exports
- **v0.7 Domain Packs**
  - Pluggable analyzers and suggester packs per domain (writing, coding, education)
- **v1.0 Public-Ready Tool**
  - Hardened APIs, docs, and packaging; optional GUI layer

## Feedback Loop
- **Data In**: autosave + export JSON, security reports
- **Analysis**: offline scripts aggregate velocity, intensity, health
- **Insights**: update analyzers/suggesters; refine thresholds
- **Deployment**: bump minor version; document deltas

## Interfaces and Ownership
- **Core Glimpse**: trajectory + renderer (engineering)
- **Adapters**: input sources (integration teams)
- **Security**: policy and enforcement (security team)
- **Analytics**: research data scripts (research team)

## Change Management
- Version functions at module boundary if semantics change.
- Maintain backward compatibility for `process_input` and `get_full_state`.
- Document new visualization modes and configs in README.

## Risks & Mitigations
- **Interface drift** → versioning + tests in `test_suite.py`.
- **Performance regressions** → benchmarks on window sizes.
- **Security gaps** → require `run_security_check()` in production flows.
