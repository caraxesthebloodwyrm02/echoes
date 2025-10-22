"""
Enhanced Filesystem Tools for EchoesAssistantV2

Safe filesystem operations with error handling and security.
"""

import os
import json
from typing import Dict, Any, List, Optional
from pathlib import Path


class FilesystemTools:
    """Safe filesystem operations."""

    def __init__(self, root_dir: Optional[str] = None, allowed_patterns: Optional[List[str]] = None):
        """Initialize filesystem tools."""
        self.root_dir = Path(root_dir or os.getcwd()).resolve()
        self.allowed_patterns = allowed_patterns or ["*"]
        
    def _is_safe_path(self, path: Path) -> bool:
        """Check if path is safe (within root and not sensitive)."""
        try:
            resolved = path.resolve()
            # Must be within root directory
            if not str(resolved).startswith(str(self.root_dir)):
                return False
            
            # Avoid sensitive paths
            sensitive = ['.git', '__pycache__', '.env', 'node_modules', '.venv', 'venv']
            path_parts = resolved.parts
            if any(s in path_parts for s in sensitive):
                return False
            
            return True
        except Exception:
            return False

    def list_directory(
        self,
        dirpath: str,
        pattern: str = "*",
        recursive: bool = False
    ) -> Dict[str, Any]:
        """List directory contents safely."""
        try:
            path = Path(dirpath).resolve()
            
            if not self._is_safe_path(path):
                return {"success": False, "error": "Access denied: path not allowed"}
            
            if not path.exists():
                return {"success": False, "error": f"Directory not found: {dirpath}"}
            
            if not path.is_dir():
                return {"success": False, "error": f"Not a directory: {dirpath}"}
            
            files = []
            dirs = []
            
            if recursive:
                items = path.rglob(pattern)
            else:
                items = path.glob(pattern)
            
            for item in items:
                if self._is_safe_path(item):
                    rel_path = str(item.relative_to(self.root_dir))
                    if item.is_file():
                        files.append({
                            "path": rel_path,
                            "name": item.name,
                            "size": item.stat().st_size,
                            "modified": item.stat().st_mtime
                        })
                    elif item.is_dir():
                        dirs.append({
                            "path": rel_path,
                            "name": item.name
                        })
            
            return {
                "success": True,
                "directory": dirpath,
                "files": files,
                "dirs": dirs,
                "total_files": len(files),
                "total_dirs": len(dirs)
            }
        
        except Exception as e:
            return {"success": False, "error": f"Error listing directory: {str(e)}"}

    def read_file(
        self,
        filepath: str,
        encoding: str = "utf-8",
        max_size: int = 1024 * 1024  # 1MB default
    ) -> Dict[str, Any]:
        """Read file contents safely."""
        try:
            path = Path(filepath).resolve()
            
            if not self._is_safe_path(path):
                return {"success": False, "error": "Access denied: path not allowed"}
            
            if not path.exists():
                return {"success": False, "error": f"File not found: {filepath}"}
            
            if not path.is_file():
                return {"success": False, "error": f"Not a file: {filepath}"}
            
            # Check file size
            file_size = path.stat().st_size
            if file_size > max_size:
                return {
                    "success": False,
                    "error": f"File too large: {file_size} bytes (max: {max_size})"
                }
            
            # Read file
            with open(path, 'r', encoding=encoding) as f:
                content = f.read()
            
            return {
                "success": True,
                "filepath": filepath,
                "content": content,
                "size": file_size,
                "lines": content.count('\n') + 1
            }
        
        except Exception as e:
            return {"success": False, "error": f"Error reading file: {str(e)}"}

    def write_file(
        self,
        filepath: str,
        content: str,
        encoding: str = "utf-8",
        create_dirs: bool = True
    ) -> Dict[str, Any]:
        """Write file contents safely."""
        try:
            path = Path(filepath).resolve()
            
            if not self._is_safe_path(path):
                return {"success": False, "error": "Access denied: path not allowed"}
            
            # Create parent directories if needed
            if create_dirs:
                path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file
            with open(path, 'w', encoding=encoding) as f:
                f.write(content)
            
            return {
                "success": True,
                "filepath": filepath,
                "size": path.stat().st_size,
                "created": not path.exists()
            }
        
        except Exception as e:
            return {"success": False, "error": f"Error writing file: {str(e)}"}

    def search_files(
        self,
        query: str,
        search_path: Optional[str] = None,
        file_pattern: str = "*",
        max_results: int = 50
    ) -> Dict[str, Any]:
        """Search for files by name or content."""
        try:
            base_path = Path(search_path or self.root_dir).resolve()
            
            if not self._is_safe_path(base_path):
                return {"success": False, "error": "Access denied: path not allowed"}
            
            results = []
            query_lower = query.lower()
            
            for item in base_path.rglob(file_pattern):
                if not self._is_safe_path(item):
                    continue
                
                if len(results) >= max_results:
                    break
                
                # Search by filename
                if query_lower in item.name.lower():
                    results.append({
                        "path": str(item.relative_to(self.root_dir)),
                        "name": item.name,
                        "match_type": "filename",
                        "is_dir": item.is_dir()
                    })
            
            return {
                "success": True,
                "query": query,
                "results": results,
                "total": len(results)
            }
        
        except Exception as e:
            return {"success": False, "error": f"Error searching files: {str(e)}"}

    def get_file_info(self, filepath: str) -> Dict[str, Any]:
        """Get file metadata."""
        try:
            path = Path(filepath).resolve()
            
            if not self._is_safe_path(path):
                return {"success": False, "error": "Access denied: path not allowed"}
            
            if not path.exists():
                return {"success": False, "error": f"File not found: {filepath}"}
            
            stat = path.stat()
            
            return {
                "success": True,
                "path": filepath,
                "name": path.name,
                "size": stat.st_size,
                "is_file": path.is_file(),
                "is_dir": path.is_dir(),
                "created": stat.st_ctime,
                "modified": stat.st_mtime,
                "extension": path.suffix
            }
        
        except Exception as e:
            return {"success": False, "error": f"Error getting file info: {str(e)}"}

    def get_directory_tree(
        self,
        dirpath: str,
        max_depth: int = 3,
        include_files: bool = True
    ) -> Dict[str, Any]:
        """Get directory tree structure."""
        try:
            path = Path(dirpath).resolve()
            
            if not self._is_safe_path(path):
                return {"success": False, "error": "Access denied: path not allowed"}
            
            if not path.exists() or not path.is_dir():
                return {"success": False, "error": f"Directory not found: {dirpath}"}
            
            def build_tree(p: Path, depth: int) -> Dict[str, Any]:
                if depth > max_depth:
                    return None
                
                node = {
                    "name": p.name,
                    "path": str(p.relative_to(self.root_dir)),
                    "is_dir": p.is_dir()
                }
                
                if p.is_dir():
                    children = []
                    try:
                        for item in sorted(p.iterdir()):
                            if not self._is_safe_path(item):
                                continue
                            if item.is_dir() or (include_files and item.is_file()):
                                child = build_tree(item, depth + 1)
                                if child:
                                    children.append(child)
                        node["children"] = children
                    except PermissionError:
                        pass
                else:
                    node["size"] = p.stat().st_size
                
                return node
            
            tree = build_tree(path, 0)
            
            return {
                "success": True,
                "tree": tree
            }
        
        except Exception as e:
            return {"success": False, "error": f"Error building tree: {str(e)}"}
