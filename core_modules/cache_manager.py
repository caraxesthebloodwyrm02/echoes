# MIT License
#
# Copyright (c) 2024 Echoes Project
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
Cache management system with file validation and locking mechanisms.
"""

import hashlib
import json
import logging
from contextlib import contextmanager
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional

from .safeguards import ProcessLock

# Configure logging
logger = logging.getLogger(__name__)


class CacheManager:
    """Manages file-based caching with checksums and write locking."""

    def __init__(self, cache_dir: str = ".cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.lock = ProcessLock(str(self.cache_dir / "cache.lock"))

    def _compute_file_hash(self, file_path: Path) -> str:
        """
        Compute MD5 hash of a file's contents.

        Args:
            file_path: Path to the file to hash

        Returns:
            str: Hexadecimal hash string
        """
        hasher = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    def _get_cache_path(self, file_hash: str) -> Path:
        """Get the cache file path for a given hash."""
        return self.cache_dir / f"{file_hash}.json"

    @contextmanager
    def write_lock(self):
        """Context manager for cache write operations."""
        with self.lock.acquire():
            yield

    def get_cached_result(self, file_path: Path, max_age: Optional[timedelta] = None) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached results if available and valid.

        Args:
            file_path: Path to the source file
            max_age: Maximum age of cache entry (optional)

        Returns:
            Dict or None: Cached results if valid, None otherwise
        """
        try:
            file_hash = self._compute_file_hash(file_path)
            cache_path = self._get_cache_path(file_hash)

            if not cache_path.exists():
                return None

            with open(cache_path, "r") as f:
                cached_data = json.load(f)

            # Check cache age if max_age specified
            if max_age:
                cache_time = datetime.fromisoformat(cached_data["timestamp"])
                if datetime.now() - cache_time > max_age:
                    logger.info(f"Cache entry for {file_path} expired")
                    return None

            logger.info(f"Cache hit for {file_path}")
            return cached_data["result"]

        except (IOError, json.JSONDecodeError, KeyError) as e:
            logger.warning(f"Cache read failed for {file_path}: {e}")
            return None

    def cache_result(self, file_path: Path, result: Dict[str, Any]):
        """
        Cache analysis results with file hash validation.

        Args:
            file_path: Path to the source file
            result: Analysis results to cache
        """
        try:
            with self.write_lock():
                file_hash = self._compute_file_hash(file_path)
                cache_path = self._get_cache_path(file_hash)

                cache_data = {
                    "timestamp": datetime.now().isoformat(),
                    "file_hash": file_hash,
                    "result": result,
                }

                with open(cache_path, "w") as f:
                    json.dump(cache_data, f, indent=2)

                logger.info(f"Cached results for {file_path}")

        except (IOError, json.JSONDecodeError) as e:
            logger.error(f"Failed to cache results for {file_path}: {e}")

    def invalidate_cache(self, file_path: Optional[Path] = None):
        """
        Invalidate cache entries.

        Args:
            file_path: Specific file to invalidate, or None for all
        """
        with self.write_lock():
            if file_path:
                try:
                    file_hash = self._compute_file_hash(file_path)
                    cache_path = self._get_cache_path(file_hash)
                    if cache_path.exists():
                        cache_path.unlink()
                        logger.info(f"Invalidated cache for {file_path}")
                except IOError as e:
                    logger.error(f"Failed to invalidate cache for {file_path}: {e}")
            else:
                # Clear all cache files
                for cache_file in self.cache_dir.glob("*.json"):
                    try:
                        cache_file.unlink()
                    except IOError:
                        continue
                logger.info("Cleared all cache entries")
