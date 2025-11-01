"""
Script to clean and organize the root directory by moving non-essential files
to appropriate subdirectories while keeping key files at the root.
"""
import os
import shutil
from pathlib import Path
from typing import List, Set, Dict, Tuple, Optional
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('root_cleanup.log'),
        logging.StreamHandler()
    ]
)

class RootOrganizer:
    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir).resolve()
        self.backup_dir = self.root_dir / '.root_backup'
        self.logger = logging.getLogger(__name__)
        
        # Files to keep at root
        self.keep_at_root = {
            # Core project files
            'README.md', 'LICENSE', 'CHANGELOG.md', 'CONTRIBUTING.md', 'SECURITY.md',
            'pyproject.toml', 'setup.py', 'requirements.txt', 'requirements-full.txt',
            'setup.cfg', 'MANIFEST.in', 'VERSION', 'Makefile',
            
            # Configuration files
            '.gitignore', '.gitattributes', '.gitmodules', '.pre-commit-config.yaml',
            '.env', '.env.example', '.env.template', 'pytest.ini',
            
            # Documentation
            'TERMINOLOGY.md', 'GLIMPSE_TERMINOLOGY.md', 'TESTING_GUIDE.md',
            
            # Key scripts
            'run_tests.py', 'start_api.py', 'deploy_production.sh',
        }
        
        # Directories to keep at root
        self.keep_dirs = {
            'app', 'api', 'tests', 'docs', 'scripts', 'config', 'data', 'assets',
            'glimpse', 'core_modules', 'automation', 'demos', 'examples', 'venv',
            'vector_index', 'models', 'monitoring', 'docker', 'deploy', 'ci', 'cli'
        }
        
        # File patterns to move to specific directories
        self.move_patterns = {
            '*.md': 'docs',
            '*.txt': 'docs',
            '*.log': 'logs',
            '*.json': 'config',
            '*.yaml': 'config',
            '*.yml': 'config',
            '*.bat': 'scripts',
            '*.sh': 'scripts',
            '*.ps1': 'scripts',
            '*.py': 'scripts',  # Will be filtered by keep_at_root
        }
        
        # Create required directories
        self.ensure_directories()
    
    def ensure_directories(self):
        """Ensure all target directories exist."""
        required_dirs = {
            self.root_dir / 'docs',
            self.root_dir / 'scripts',
            self.root_dir / 'config',
            self.root_dir / 'logs',
            self.backup_dir
        }
        
        for directory in required_dirs:
            directory.mkdir(exist_ok=True, parents=True)
    
    def should_keep_at_root(self, path: Path) -> bool:
        """Check if a file should be kept at root."""
        # Keep directories in the keep_dirs set
        if path.is_dir():
            return path.name in self.keep_dirs or path.name.startswith('.')
            
        # Keep files in the keep_at_root set
        if path.name in self.keep_at_root:
            return True
            
        # Keep hidden files at root
        if path.name.startswith('.'):
            return True
            
        return False
    
    def get_target_directory(self, path: Path) -> Optional[Path]:
        """Determine the target directory for a file."""
        if self.should_keep_at_root(path):
            return None
            
        # Check file patterns
        for pattern, target_dir in self.move_patterns.items():
            if path.match(pattern):
                return self.root_dir / target_dir
                
        # Default to 'misc' for files that don't match any pattern
        return self.root_dir / 'misc'
    
    def backup_file(self, path: Path) -> Path:
        """Create a backup of a file before moving it."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = self.backup_dir / f"{timestamp}_{path.name}"
        
        if path.is_dir():
            shutil.copytree(path, backup_path, dirs_exist_ok=True)
        else:
            shutil.copy2(path, backup_path)
            
        return backup_path
    
    def organize(self, dry_run: bool = True):
        """Organize the root directory."""
        moved = []
        skipped = []
        errors = []
        
        self.logger.info(f"Starting organization of {self.root_dir}")
        if dry_run:
            self.logger.info("Running in dry-run mode (no files will be moved)")
        
        for item in self.root_dir.iterdir():
            try:
                if self.should_keep_at_root(item):
                    self.logger.debug(f"Keeping at root: {item.name}")
                    skipped.append(item.name)
                    continue
                
                target_dir = self.get_target_directory(item)
                if not target_dir:
                    self.logger.debug(f"No target directory for {item.name}, skipping")
                    skipped.append(item.name)
                    continue
                
                target_path = target_dir / item.name
                
                if dry_run:
                    self.logger.info(f"Would move: {item.name} -> {target_path.relative_to(self.root_dir)}")
                    moved.append(item.name)
                    continue
                
                # Create backup before moving
                backup_path = self.backup_file(item)
                self.logger.debug(f"Created backup at: {backup_path}")
                
                # Move the file/directory
                if item.is_dir():
                    shutil.move(str(item), str(target_path))
                else:
                    target_path.parent.mkdir(exist_ok=True, parents=True)
                    shutil.move(str(item), str(target_path))
                
                moved.append(item.name)
                self.logger.info(f"Moved: {item.name} -> {target_path.relative_to(self.root_dir)}")
                
            except Exception as e:
                self.logger.error(f"Error processing {item.name}: {str(e)}")
                errors.append((item.name, str(e)))
        
        # Print summary
        self.logger.info("\n=== Organization Results ===")
        self.logger.info(f"Files moved: {len(moved)}")
        self.logger.info(f"Files skipped: {len(skipped)}")
        self.logger.info(f"Errors: {len(errors)}")
        
        if moved and not dry_run:
            self.logger.info("\nBackup of moved files is available at:")
            self.logger.info(f"  {self.backup_dir}")
        
        if errors:
            self.logger.warning("\nEncountered errors with the following files:")
            for file, error in errors:
                self.logger.warning(f"  {file}: {error}")
        
        if dry_run:
            self.logger.info("\nThis was a dry run. No files were actually moved.")
            self.logger.info("Run with --apply to perform the actual file organization.")
        else:
            self.logger.info("\nOrganization complete!")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Organize the root directory by moving non-essential files to appropriate subdirectories.')
    parser.add_argument('--apply', action='store_true', help='Actually perform the file operations (default: dry run)')
    parser.add_argument('--root', type=str, default='.', help='Root directory to organize (default: current directory)')
    parser.add_argument('--debug', action='store_true', help='Enable debug output')
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    organizer = RootOrganizer(args.root)
    organizer.organize(dry_run=not args.apply)


if __name__ == '__main__':
    main()
