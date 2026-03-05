# Operational safety checklist

Use this checklist in PRs that touch tool execution, subprocess, or scripts.

## Before merge

- [ ] **Tool execution**: All tool dispatch goes through the **tool gate** (`tools.safe_dispatch_tool` / `execute_tool`): allowlist, payload validation, and audit logging. No direct registry `get_tool` + `func(payload)` from request/LLM paths without going through the gate.
- [ ] **Subprocess**: No `shell=True`; use argument lists and `shell=False`. See `verify_environment.py` and `docs/EXECUTION_SAFETY.md`.
- [ ] **Reconstruction / compile**: Scripts using `compile(..., "exec")` or similar are admin-only or controlled CLI; never exposed to user or LLM input. See `docs/EXECUTION_SAFETY.md`.

## Reference

- Tool gate: `tools/__init__.py` (`safe_dispatch_tool`, `execute_tool`)
- Execution safety: `docs/EXECUTION_SAFETY.md`
