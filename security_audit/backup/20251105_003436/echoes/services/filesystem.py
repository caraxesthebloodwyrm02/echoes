# ----------------------------------------------------------------------
# Filesystem Tools wrapper.
# ----------------------------------------------------------------------
from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from echoes.utils.import_helpers import safe_import

# Try to import the real FilesystemTools
fs_mod, FS_AVAILABLE = safe_import("echoes.core.filesystem")

if FS_AVAILABLE:
    FilesystemTools = fs_mod.FilesystemTools  # type: ignore[attr-defined]
else:

    class FilesystemTools:
        """Minimal fallback filesystem tools."""

        def __init__(self, root_dir: str = "."):
            self.root_dir = Path(root_dir).resolve()

        def read_file(self, file_path: str) -> str:
            """Read file contents."""
            full_path = self.root_dir / file_path
            if not full_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")

            with open(full_path, encoding="utf-8") as f:
                return f.read()

        def write_file(self, file_path: str, content: str) -> bool:
            """Write content to file."""
            full_path = self.root_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)

            try:
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(content)
                return True
            except Exception:
                return False

        def list_files(self, directory: str = ".", pattern: str = "*") -> list[str]:
            """List files in directory."""
            full_path = self.root_dir / directory
            if not full_path.exists():
                return []

            files = []
            for file_path in full_path.glob(pattern):
                if file_path.is_file():
                    files.append(str(file_path.relative_to(self.root_dir)))
            return files

        def list_directories(self, directory: str = ".") -> list[str]:
            """List directories in directory."""
            full_path = self.root_dir / directory
            if not full_path.exists():
                return []

            dirs = []
            for dir_path in full_path.iterdir():
                if dir_path.is_dir():
                    dirs.append(str(dir_path.relative_to(self.root_dir)))
            return dirs

        def create_directory(self, directory: str) -> bool:
            """Create directory."""
            full_path = self.root_dir / directory
            try:
                full_path.mkdir(parents=True, exist_ok=True)
                return True
            except Exception:
                return False

        def delete_file(self, file_path: str) -> bool:
            """Delete file."""
            full_path = self.root_dir / file_path
            try:
                if full_path.is_file():
                    full_path.unlink()
                    return True
                return False
            except Exception:
                return False

        def delete_directory(self, directory: str) -> bool:
            """Delete directory."""
            full_path = self.root_dir / directory
            try:
                if full_path.is_dir():
                    shutil.rmtree(full_path)
                    return True
                return False
            except Exception:
                return False

        def move_file(self, source: str, destination: str) -> bool:
            """Move file."""
            src_path = self.root_dir / source
            dst_path = self.root_dir / destination

            try:
                dst_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(src_path), str(dst_path))
                return True
            except Exception:
                return False

        def copy_file(self, source: str, destination: str) -> bool:
            """Copy file."""
            src_path = self.root_dir / source
            dst_path = self.root_dir / destination

            try:
                dst_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(str(src_path), str(dst_path))
                return True
            except Exception:
                return False

        def get_file_info(self, file_path: str) -> dict[str, Any] | None:
            """Get file information."""
            full_path = self.root_dir / file_path
            if not full_path.exists():
                return None

            stat = full_path.stat()
            return {
                "path": str(full_path.relative_to(self.root_dir)),
                "size": stat.st_size,
                "modified": stat.st_mtime,
                "is_file": full_path.is_file(),
                "is_directory": full_path.is_dir(),
                "exists": True,
            }

        def search_files(self, pattern: str, directory: str = ".") -> list[str]:
            """Search for files by name pattern."""
            full_path = self.root_dir / directory
            if not full_path.exists():
                return []

            matches = []
            for file_path in full_path.rglob(pattern):
                if file_path.is_file():
                    matches.append(str(file_path.relative_to(self.root_dir)))
            return matches
