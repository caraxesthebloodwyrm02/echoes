# Requirements File Consolidation Plan

**Date**: November 2, 2025  
**Priority**: HIGH  
**Issue**: 31 requirements files, 64 dependency conflicts

## Current State

### Primary Files (Keep)
- `pyproject.toml` - ✅ Modern standard, use as authoritative source
- `requirements.txt` - ✅ Main requirements (auto-generated note)
- `requirements_production.txt` - ✅ Production-specific (minimal)
- `setup.py` - ✅ For backward compatibility

### Files to Archive/Remove

**Backup Files** (Move to archive):
- `.root_backup/*/requirements*.txt` - Old backups
- Archive these to `.archive/requirements/`

**Documentation Files** (Move to docs archive):
- `docs/requirements*.txt` - Example/locked files
- Move to `docs/archive/requirements/`

**Miscellaneous** (Review and potentially remove):
- `misc/*/requirements*.txt` - Module-specific
- `requirements-cluster.txt` - If not actively used
- `requirements-full.txt` - If redundant with pyproject.toml
- `requirements_modular.txt` - If redundant

## Recommended Structure

```
pyproject.toml          # Single source of truth
requirements.txt        # Generated from pyproject.toml (base)
requirements-dev.txt    # Development tools (from pyproject.toml [dev])
requirements-prod.txt   # Production minimal (from requirements_production.txt)
requirements-lock.txt   # Exact versions for production (generated)
```

## Action Plan

1. **Use pyproject.toml as authoritative**
   - All dependencies defined there
   - Use optional dependencies for dev/prod

2. **Generate requirements.txt from pyproject.toml**
   ```bash
   pip-compile pyproject.toml --output-file=requirements.txt
   ```

3. **Archive old files**
   - Move backups to `.archive/`
   - Move docs examples to `docs/archive/`

4. **Test installation**
   - Verify requirements.txt works
   - Test in clean environment

## Dependency Resolution

From analysis, key conflicts resolved:
- `openai`: Use `>=1.3.7` (matches pyproject.toml)
- `fastapi`: Use `>=0.104.1` (matches pyproject.toml)
- Others: Use versions from pyproject.toml

**Status**: Plan ready for implementation

