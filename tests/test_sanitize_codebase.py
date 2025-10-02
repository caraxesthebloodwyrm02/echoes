import os
import shutil
import tempfile
from automation.tasks import sanitize_codebase
from automation.core.context import Context

def test_sanitize_codebase_removes_cache(tmp_path, caplog):
    # Setup fake cache dirs
    cache_dirs = ['__pycache__', 'build', 'dist', 'node_modules']
    for d in cache_dirs:
        (tmp_path / d).mkdir()
    
    # Use context.extra to override project root
    ctx = Context(dry_run=False)
    ctx.extra["project_root"] = str(tmp_path)
    
    sanitize_codebase.run(ctx)
    
    # Verify directories were removed
    for d in cache_dirs:
        assert not (tmp_path / d).exists()
    
    # Verify log output contains "Removed"
    assert "Removed" in caplog.text

def test_sanitize_codebase_dry_run(tmp_path, caplog):
    cache_dirs = ['__pycache__', 'build']
    for d in cache_dirs:
        (tmp_path / d).mkdir()
    
    # Use context.extra to override project root
    ctx = Context(dry_run=True)
    ctx.extra["project_root"] = str(tmp_path)
    
    sanitize_codebase.run(ctx)
    
    # Verify directories were NOT removed in dry run
    for d in cache_dirs:
        assert (tmp_path / d).exists()
    
    # Verify log output contains "[DRY RUN]"
    assert "[DRY RUN]" in caplog.text
