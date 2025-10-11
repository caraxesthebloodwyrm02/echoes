"""
Download cache module for tracking downloaded videos and transcriptions.

This module provides a persistent cache to track which YouTube videos have been
downloaded and transcribed, preventing redundant processing.
"""

import hashlib
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class DownloadCache:
    """
    A persistent cache for tracking downloaded videos and their transcriptions.

    The cache is stored as a JSON file and tracks:
    - Video URLs that have been downloaded
    - Video IDs that have been transcribed
    - File paths of downloaded videos
    - Timestamps of operations
    """

    def __init__(self, cache_file: str = "download_cache.json"):
        """
        Initialize the download cache.

        Args:
            cache_file: Path to the JSON file used to store the cache
        """
        self.cache_file = Path(cache_file)
        self._cache: Dict[str, dict] = {
            "version": "1.0",
            "downloaded": {},
            "transcribed": {},
            "file_paths": {},
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        self._load_cache()

    def _load_cache(self) -> None:
        """Load the cache from the JSON file if it exists."""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    self._cache = json.load(f)
                    # Ensure all required keys exist
                    for key in ["downloaded", "transcribed", "file_paths"]:
                        if key not in self._cache:
                            self._cache[key] = {}
                    logger.debug(f"Loaded cache from {self.cache_file} with {len(self._cache['downloaded'])} entries")
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Failed to load cache from {self.cache_file}: {e}")
            # Reset to default cache on error
            self._cache = {
                "version": "1.0",
                "downloaded": {},
                "transcribed": {},
                "file_paths": {},
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }

    def _save_cache(self) -> None:
        """Save the cache to the JSON file."""
        try:
            self._cache["updated_at"] = datetime.now(timezone.utc).isoformat()
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(self._cache, f, indent=2, ensure_ascii=False)
        except IOError as e:
            logger.error(f"Failed to save cache to {self.cache_file}: {e}")

    @staticmethod
    def _get_video_id(url: str) -> str:
        """Extract video ID from YouTube URL."""
        # Handle various YouTube URL formats
        if "youtube.com/watch" in url:
            import urllib.parse as urlparse

            parsed = urlparse.urlparse(url)
            video_id = urlparse.parse_qs(parsed.query).get("v")
            if video_id:
                return video_id[0]
        elif "youtu.be/" in url:
            return url.split("youtu.be/")[-1].split("?")[0].split("&")[0]

        # If we can't parse it, use a hash of the URL as an ID
        return hashlib.md5(url.encode("utf-8")).hexdigest()

    def is_downloaded(self, url: str) -> bool:
        """Check if a video has been downloaded."""
        video_id = self._get_video_id(url)
        return video_id in self._cache["downloaded"]

    def is_transcribed(self, url: str) -> bool:
        """Check if a video has been transcribed."""
        video_id = self._get_video_id(url)
        return video_id in self._cache["transcribed"]

    def get_file_path(self, url: str) -> Optional[str]:
        """Get the local file path for a downloaded video."""
        video_id = self._get_video_id(url)
        return self._cache["file_paths"].get(video_id)

    def mark_downloaded(self, url: str, file_path: str) -> None:
        """Mark a video as downloaded and store its file path."""
        video_id = self._get_video_id(url)
        self._cache["downloaded"][video_id] = {
            "url": url,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "file_path": file_path,
        }
        self._cache["file_paths"][video_id] = file_path
        self._save_cache()
        logger.debug(f"Marked video {video_id} as downloaded: {file_path}")

    def mark_transcribed(self, url: str, transcript_path: str) -> None:
        """Mark a video as transcribed."""
        video_id = self._get_video_id(url)
        self._cache["transcribed"][video_id] = {
            "url": url,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "transcript_path": transcript_path,
        }
        self._save_cache()
        logger.debug(f"Marked video {video_id} as transcribed: {transcript_path}")

    def get_downloaded_videos(self) -> List[dict]:
        """Get a list of all downloaded videos."""
        return list(self._cache["downloaded"].values())

    def get_transcribed_videos(self) -> List[dict]:
        """Get a list of all transcribed videos."""
        return list(self._cache["transcribed"].values())

    def clear(self) -> None:
        """Clear the cache."""
        self._cache = {
            "version": "1.0",
            "downloaded": {},
            "transcribed": {},
            "file_paths": {},
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        self._save_cache()
        logger.info("Download cache cleared")


# Create a default instance for convenience
download_cache = DownloadCache()


def get_download_cache(cache_file: str = "download_cache.json") -> DownloadCache:
    """Get a DownloadCache instance with the specified cache file."""
    return DownloadCache(cache_file)
