# Path Handler Migration Guide

**Date:** 2025-01-15
**Status:** ✅ **READY FOR MIGRATION**

---

## Overview

Migrate from inconsistent, hardcoded path handling to centralized `SmartPathHandler` system.

**Benefits:**
- ✅ Security: Path traversal attack prevention
- ✅ Consistency: Single source of truth for paths
- ✅ Cross-platform: Works on Windows, Linux, macOS
- ✅ Type-safe: Pydantic validation
- ✅ Maintainable: Centralized configuration

---

## Issues Found in Current Codebase

### 1. **Hardcoded Paths** (`src/batch_processor.py`)
```python
# ❌ BEFORE: Hardcoded relative paths
INPUT_DIR = "data/input_samples"
OUTPUT_DIR = "data/outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)
```

**Issues:**
- Not cross-platform
- No validation
- Manual directory creation
- Inconsistent with project structure

### 2. **Mixed Path Handling** (`batch/processing/document_processor.py`)
```python
# ❌ BEFORE: Mixed pathlib and string operations
self.input_dir = Path(input_dir)
pattern = str(self.input_dir / self.file_pattern)
files = [Path(f) for f in glob.glob(pattern)]
```

**Issues:**
- Converting between Path and str
- Inefficient
- Prone to errors

### 3. **Basic PathResolver** (`utils/path_resolver.py`)
```python
# ❌ BEFORE: Limited functionality
def resolve_path(self, relative_path: str) -> Path:
    resolved = (self.base_dir / relative_path).resolve()
    resolved.relative_to(self.base_dir)
    return resolved
```

**Issues:**
- No category-based routing
- Limited validation
- No path registry
- Manual security checks

---

## Migration Steps

### Step 1: Import SmartPathHandler

```python
# ✅ NEW: Import SmartPathHandler
from packages.core.path_handler import (
    SmartPathHandler,
    PathCategory,
    get_path,
    resolve_path,
    ensure_dir
)
```

### Step 2: Replace Hardcoded Paths

**Before:**
```python
# src/batch_processor.py
INPUT_DIR = "data/input_samples"
OUTPUT_DIR = "data/outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def process_file(path, task, dry_run=False):
    out_path = os.path.join(OUTPUT_DIR, out_name)
```

**After:**
```python
# src/batch_processor.py
from packages.core.path_handler import get_path, PathCategory

def process_file(path, task, dry_run=False):
    # Automatic directory creation
    out_path = get_path(PathCategory.OUTPUTS, out_name, create=True)
```

### Step 3: Migrate PathResolver Usage

**Before:**
```python
# batch/processing/document_processor.py
from utils.path_resolver import PathResolver

path_resolver = PathResolver()
path_resolver.ensure_directory(self.output_dir)
```

**After:**
```python
# batch/processing/document_processor.py
from packages.core.path_handler import ensure_dir, get_path, PathCategory

# Option 1: Use ensure_dir
ensure_dir(self.output_dir)

# Option 2: Use category-based path
output_path = get_path(PathCategory.OUTPUTS, create=True)
```

### Step 4: Update File Discovery

**Before:**
```python
# batch/processing/document_processor.py
pattern = str(self.input_dir / self.file_pattern)
files = [Path(f) for f in glob.glob(pattern)]
```

**After:**
```python
# batch/processing/document_processor.py
from packages.core.path_handler import get_path_handler, PathCategory

handler = get_path_handler()
files = handler.list_files(PathCategory.INPUTS, pattern=self.file_pattern)
```

### Step 5: Migrate Settings Paths

**Before:**
```python
# config/settings.py
data_dir: Path = Field(default_factory=lambda: get_project_root() / "data")
logs_dir: Path = Field(default_factory=lambda: get_project_root() / "logs")
```

**After:**
```python
# config/settings.py
from packages.core.path_handler import get_path, PathCategory

data_dir: Path = Field(default_factory=lambda: get_path(PathCategory.DATA))
logs_dir: Path = Field(default_factory=lambda: get_path(PathCategory.LOGS))
```

---

## Complete Migration Examples

### Example 1: Batch Processor

**Before (`src/batch_processor.py`):**
```python
import os

INPUT_DIR = "data/input_samples"
OUTPUT_DIR = "data/outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def process_file(path, task, dry_run=False):
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    out_name = os.path.splitext(os.path.basename(path))[0] + f"_{task}.txt"
    out_path = os.path.join(OUTPUT_DIR, out_name)

    with open(out_path, "w", encoding="utf-8") as out_f:
        out_f.write(header + result)

def main(task, dry_run=False):
    files = [
        os.path.join(INPUT_DIR, f)
        for f in os.listdir(INPUT_DIR)
        if f.endswith(".txt")
    ]
```

**After:**
```python
from pathlib import Path
from packages.core.path_handler import get_path, PathCategory, get_path_handler

handler = get_path_handler()

def process_file(path: Path, task: str, dry_run: bool = False):
    # Read with Path
    text = path.read_text(encoding="utf-8")

    # Use smart path handler
    out_name = f"{path.stem}_{task}.txt"
    out_path = get_path(PathCategory.OUTPUTS, out_name, create=True)

    # Write with Path
    out_path.write_text(header + result, encoding="utf-8")

def main(task: str, dry_run: bool = False):
    # Use handler to list files
    files = handler.list_files(PathCategory.INPUTS, "*.txt")
```

### Example 2: Document Processor

**Before (`batch/processing/document_processor.py`):**
```python
from pathlib import Path
import glob
from utils.path_resolver import PathResolver

class DocumentProcessor:
    def __init__(self, input_dir: str, output_dir: str):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)

        path_resolver = PathResolver()
        path_resolver.ensure_directory(self.output_dir)

    def discover_files(self) -> List[Path]:
        pattern = str(self.input_dir / self.file_pattern)
        files = [Path(f) for f in glob.glob(pattern)]
        return files
```

**After:**
```python
from pathlib import Path
from typing import List
from packages.core.path_handler import (
    get_path_handler,
    get_path,
    PathCategory
)

class DocumentProcessor:
    def __init__(self, input_category: PathCategory = PathCategory.INPUTS):
        self.handler = get_path_handler()
        self.input_dir = get_path(input_category, create=True)
        self.output_dir = get_path(PathCategory.OUTPUTS, create=True)

    def discover_files(self) -> List[Path]:
        return self.handler.list_files(
            PathCategory.INPUTS,
            pattern=self.file_pattern
        )
```

### Example 3: Maintenance Cleanup

**Before (`batch/maintenance/cleanup.py`):**
```python
from config.settings import get_settings
from utils.path_resolver import PathResolver

class MaintenanceManager:
    def __init__(self):
        self.settings = get_settings()
        self.path_resolver = PathResolver()

    def cleanup_temp_files(self, max_age_days: int = 7):
        temp_dir = self.settings.temp_dir
        if not temp_dir.exists():
            return {"files_cleaned": 0}

        for file_path in temp_dir.rglob("*"):
            if file_path.is_file():
                # Manual cleanup logic
                pass
```

**After:**
```python
from packages.core.path_handler import get_path_handler

class MaintenanceManager:
    def __init__(self):
        self.handler = get_path_handler()

    def cleanup_temp_files(self, max_age_days: int = 7):
        # Built-in cleanup
        removed = self.handler.cleanup_temp(max_age_days=max_age_days)
        return {"files_cleaned": removed}
```

---

## Path Category Mapping

| Old Path | New Category | Example |
|----------|--------------|---------|
| `data/input_samples/` | `PathCategory.INPUTS` | `get_path(PathCategory.INPUTS)` |
| `data/outputs/` | `PathCategory.OUTPUTS` | `get_path(PathCategory.OUTPUTS)` |
| `logs/` | `PathCategory.LOGS` | `get_path(PathCategory.LOGS)` |
| `temp/` | `PathCategory.TEMP` | `get_path(PathCategory.TEMP)` |
| `data/cache/` | `PathCategory.CACHE` | `get_path(PathCategory.CACHE)` |
| `config/` | `PathCategory.CONFIG` | `get_path(PathCategory.CONFIG)` |
| `models/` | `PathCategory.MODELS` | `get_path(PathCategory.MODELS)` |
| `reports/` | `PathCategory.REPORTS` | `get_path(PathCategory.REPORTS)` |
| `artifacts/` | `PathCategory.ARTIFACTS` | `get_path(PathCategory.ARTIFACTS)` |
| `data/backups/` | `PathCategory.BACKUPS` | `get_path(PathCategory.BACKUPS)` |

---

## Quick Reference

### Get Path by Category
```python
from packages.core.path_handler import get_path, PathCategory

# Get base path
data_path = get_path(PathCategory.DATA)

# Get path with subpaths
model_file = get_path(PathCategory.MODELS, "checkpoint.pth")

# Auto-create parent directory
output_file = get_path(PathCategory.OUTPUTS, "result.txt", create=True)
```

### Resolve Any Path
```python
from packages.core.path_handler import resolve_path

# Resolve relative path
resolved = resolve_path("data/test.txt")

# Resolve with category context
resolved = resolve_path("test.txt", relative_to=PathCategory.DATA)
```

### List Files
```python
from packages.core.path_handler import get_path_handler, PathCategory

handler = get_path_handler()

# List all text files
files = handler.list_files(PathCategory.DATA, "*.txt")

# List recursively
files = handler.list_files(PathCategory.DATA, "**/*.py", recursive=True)
```

### Ensure Directory Exists
```python
from packages.core.path_handler import ensure_dir

# Create directory if needed
output_dir = ensure_dir("data/new_outputs")
```

---

## Testing Your Migration

### 1. Unit Tests
```bash
# Run path handler tests
pytest tests/test_path_handler.py -v
```

### 2. Integration Tests
```python
def test_migrated_code():
    """Test migrated code works correctly"""
    from packages.core.path_handler import get_path, PathCategory

    # Test path resolution
    data_path = get_path(PathCategory.DATA)
    assert data_path.exists()

    # Test file creation
    test_file = get_path(PathCategory.OUTPUTS, "test.txt", create=True)
    assert test_file.parent.exists()
```

### 3. Manual Verification
```python
# Print path statistics
from packages.core.path_handler import get_path_handler

handler = get_path_handler()
stats = handler.get_stats()
print(stats)
```

---

## Rollback Plan

If migration causes issues:

### Option 1: Keep Both Systems
```python
# Use old system
from utils.path_resolver import PathResolver

# Use new system
from packages.core.path_handler import get_path, PathCategory
```

### Option 2: Gradual Migration
- Migrate one module at a time
- Test thoroughly before moving to next module
- Keep old `PathResolver` for legacy code

---

## Checklist

- [ ] Replace hardcoded paths with `PathCategory`
- [ ] Update imports from `path_resolver` to `path_handler`
- [ ] Replace `os.path.join` with `get_path()` or Path operations
- [ ] Replace manual `os.makedirs` with `create=True` parameter
- [ ] Replace `glob.glob` with `handler.list_files()`
- [ ] Update settings to use `PathCategory`
- [ ] Run tests: `pytest tests/test_path_handler.py -v`
- [ ] Verify no broken imports
- [ ] Check all paths are within project root (security)
- [ ] Update documentation

---

## Files to Migrate

### High Priority (Hardcoded Paths)
1. ✅ `src/batch_processor.py` - INPUT_DIR, OUTPUT_DIR
2. ✅ `batch/processing/document_processor.py` - PathResolver usage
3. ✅ `batch/maintenance/cleanup.py` - temp/logs cleanup

### Medium Priority (PathResolver Usage)
4. Any file importing `from utils.path_resolver import PathResolver`
5. Config files using `get_project_root()`

### Low Priority (Already Using Path)
6. Files already using `pathlib.Path` correctly
7. Test files (can update gradually)

---

## Support

### Get Handler Stats
```python
from packages.core.path_handler import get_path_handler

handler = get_path_handler()
print(handler.get_stats())
```

### Debug Path Resolution
```python
from packages.core.path_handler import resolve_path

try:
    resolved = resolve_path("suspicious/path")
    print(f"Resolved: {resolved}")
except SecurityError as e:
    print(f"Security issue: {e}")
```

---

## Conclusion

**SmartPathHandler provides:**
- ✅ Security (path traversal prevention)
- ✅ Consistency (single source of truth)
- ✅ Maintainability (centralized configuration)
- ✅ Type safety (Pydantic validation)
- ✅ Cross-platform (works everywhere)

**Status:** Ready for migration

**Next Steps:**
1. Run tests: `pytest tests/test_path_handler.py -v`
2. Migrate high-priority files first
3. Test after each migration
4. Update documentation

---

**Created:** 2025-01-15
**Status:** ✅ READY FOR USE
