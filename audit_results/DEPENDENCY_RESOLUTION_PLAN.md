# Dependency Resolution Plan

**Date**: November 2, 2025  
**Priority**: HIGH (64 conflicts identified)

## Summary

- **Total Requirements Files**: 31
- **Total Dependencies**: 213
- **Conflicts**: 64 packages with conflicting versions
- **Outdated**: 4 packages

## Strategy

### Phase 1: Identify Primary Requirements File

**Recommendation**: Use `pyproject.toml` as single source of truth
- Already exists and is modern Python standard
- Supports optional dependencies
- Better for packaging

### Phase 2: Consolidate Dependencies

1. **Review Main Requirements**:
   - `requirements.txt` - Base dependencies
   - `pyproject.toml` - Package definition
   - `setup.py` - Legacy support

2. **Archive Backup/Misc Files**:
   - Move `.root_backup/*/requirements.txt` to archive
   - Move `misc/*/requirements.txt` to archive or remove
   - Move `docs/*/requirements*.txt` to archive

3. **Consolidate Active Files**:
   - Keep: `requirements.txt` (base)
   - Keep: `requirements-dev.txt` (development)
   - Keep: `requirements-prod.txt` (production)
   - Keep: `pyproject.toml` (as authoritative)

### Phase 3: Resolve Conflicts

**Key Conflicts** (from audit):
- `openai`: Multiple versions (>=1.0.0, ==1.3.7, ==2.6.1, ==2.5.0, >=1.3.7)
- `fastapi`: Multiple versions
- Many others...

**Resolution Strategy**:
1. Use latest stable version that satisfies all constraints
2. For production: Pin exact versions (`==`)
3. For development: Use minimum versions (`>=`)

## Action Items

1. ✅ Create dependency consolidation script
2. ⏳ Review each conflict and determine correct version
3. ⏳ Update all requirements files
4. ⏳ Test installation
5. ⏳ Generate requirements-lock.txt for production

## Recommended Primary Dependencies

Based on `pyproject.toml` review:

```toml
[project]
dependencies = [
    "openai>=1.3.7",
    "fastapi>=0.104.1",
    "uvicorn[standard]>=0.24.0",
    # ... (use pyproject.toml as source)
]
```

**Next Step**: Review pyproject.toml and use as authoritative source for all dependencies.

---

**Status**: Plan created - Ready for implementation

