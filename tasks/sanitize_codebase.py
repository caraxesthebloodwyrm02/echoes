from automation.core.logger import log
from automation.core.context import Context
import os
import shutil

def run(context: Context):
    log.info("Starting codebase sanitization")
    
    # Allow override of project root via context for testing
    project_root = context.extra.get("project_root", os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
    
    cache_dirs = [
        '.pytest_cache', '__pycache__', '.coverage', 'coverage', '.sass-cache', 'build', 'dist', '.next', '.nuxt', 'tmp', 'node_modules'
    ]
    removed = 0
    
    for root, dirs, files in os.walk(project_root):
        for d in dirs:
            if d in cache_dirs:
                dir_path = os.path.join(root, d)
                if os.path.exists(dir_path):
                    if context.dry_run:
                        log.info(f"[DRY RUN] Would remove {dir_path}")
                    else:
                        try:
                            shutil.rmtree(dir_path)
                            log.success(f"Removed {dir_path}")
                            removed += 1
                        except Exception as e:
                            log.error(f"Failed to remove {dir_path}: {e}")
    
    log.info(f"Sanitization complete. Directories removed: {removed}")
