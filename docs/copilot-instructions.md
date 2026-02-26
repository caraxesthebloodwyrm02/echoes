# Copilot Instructions for Echoes (Workspace-Aligned)

## Role in this workspace
Echoes belongs to the **Common Desk** zone and serves assistant synthesis/orchestration functions.

## Authority order for tasks
1. User request in current chat
2. Workspace master policy: `VSCode-Workspace-BestPractices/AGENTS.md`
3. Echoes repo docs and implementation
4. Chamber authority files (`assistive-tool-contract`, `afloat`) when task impacts contract/implementation alignment

## Working boundaries
- Keep changes focused to `echoes` unless cross-repo edits are explicitly required.
- Treat generated artifacts/logs as non-authoritative.
- Prefer deterministic local workflows and reproducible scripts.

## Coding behavior
- Make minimal, surgical edits.
- Preserve existing style and conventions.
- Validate with closest relevant tests or checks when feasible.

## Communication behavior
- Be concise and evidence-based.
- Provide concrete file paths for findings and modifications.
- State assumptions when requirements are ambiguous.
