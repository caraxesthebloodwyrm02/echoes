This PR adds tools for diagnosing pip/tempfile issues and makes the integration test more resilient to environment quirks.

- Adds repo-local temp probe and admin helper scripts
- Makes integration_test.ps1 robust (skip pip on broken envs, use /health readiness)
- Adds CI trigger to validate reproducibility on clean runners
 
Note: trigger edit to force PR diff - updated at 2025-10-08T02:42:36Z
