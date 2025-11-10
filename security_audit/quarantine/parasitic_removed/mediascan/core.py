"""
Core classes for MediaScan library.
"""

import json
from pathlib import Path
from typing import Any

from .exceptions import InvalidMediaDataError, JSONParseError


class MediaItem:
    """Base class for media items (movies or TV series)."""

    def __init__(self, title: str, rank: int, filepath: str, **kwargs):
        self.title = title
        self.rank = rank
        self.filepath = filepath
        self.year = str(kwargs.get("year", "N/A"))
        self.director = kwargs.get("director", "Unknown")
        self.type = kwargs.get("type", "Movie")

    def to_dict(self) -> dict[str, Any]:
        """Convert the media item to a dictionary."""
        return {
            "title": self.title,
            "rank": self.rank,
            "filepath": self.filepath,
            "year": self.year,
            "director": self.director,
            "type": self.type,
        }

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(title='{self.title}', rank={self.rank})"


class Movie(MediaItem):
    """Class representing a movie."""

    def __init__(self, title: str, rank: int, filepath: str, **kwargs):
        super().__init__(title, rank, filepath, type="Movie", **kwargs)


class TVSeries(MediaItem):
    """Class representing a TV series."""

    def __init__(self, title: str, rank: int, filepath: str, **kwargs):
        super().__init__(title, rank, filepath, type="TV Series", **kwargs)
        self.seasons = str(kwargs.get("seasons", "N/A"))
        self.episodes = str(kwargs.get("episodes", "N/A"))

    def to_dict(self) -> dict[str, Any]:
        """Convert the TV series to a dictionary."""
        result = super().to_dict()
        result.update({"seasons": self.seasons, "episodes": self.episodes})
        return result


class MediaScanner:
    """Scanner for searching media items in JSON files."""

    def __init__(self, search_directory: str):
        """
        Initialize the MediaScanner.

        Args:
            search_directory: Directory to search for JSON files
        """
        self.search_directory = Path(search_directory)
        if not self.search_directory.exists():
            raise FileNotFoundError(f"Directory not found: {search_directory}")

        self._json_files: list[Path] = []
        self._cache: dict[str, MediaItem | None] = {}

    def _find_json_files(self) -> list[Path]:
        """Find all JSON files in the search directory."""
        if not self._json_files:
            self._json_files = list(self.search_directory.rglob("*.json"))
        return self._json_files

    def _parse_json_file(self, filepath: Path) -> list[dict[str, Any]]:
        """Parse a JSON file and return its data."""
        try:
            with open(filepath, encoding="utf-8") as f:
                data = json.load(f)

            if not isinstance(data, list):
                raise InvalidMediaDataError(f"Expected list of items in {filepath}")

            return data

        except json.JSONDecodeError as e:
            raise JSONParseError(str(filepath), e)
        except (OSError, PermissionError) as e:
            raise MediaScanError(f"Error reading {filepath}: {e}")

    def _create_media_item(
        self, item_data: dict[str, Any], rank: int, filepath: Path
    ) -> MediaItem:
        """Create appropriate MediaItem subclass from data."""
        title = item_data.get("title")
        if not title:
            raise InvalidMediaDataError(f"Missing title in item from {filepath}")

        # Extract common fields
        common_data = {
            "year": item_data.get("year", "N/A"),
            "director": item_data.get("director", "Unknown"),
        }

        # Determine if it's a TV series or movie
        if item_data.get("type", "").lower() == "tv" or "seasons" in item_data:
            tv_data = {
                "seasons": item_data.get("seasons", "N/A"),
                "episodes": item_data.get("episodes", "N/A"),
                **common_data,
            }
            return TVSeries(title, rank, str(filepath), **tv_data)
        else:
            return Movie(title, rank, str(filepath), **common_data)

    def find_by_title(self, title: str, use_cache: bool = True) -> MediaItem | None:
        """
        Find a media item by title.

        Args:
            title: Title to search for (case-insensitive, partial match)
            use_cache: Whether to use cached results

        Returns:
            MediaItem if found, None otherwise
        """
        cache_key = f"title:{title.lower()}"

        if use_cache and cache_key in self._cache:
            return self._cache[cache_key]

        for filepath in self._find_json_files():
            try:
                data = self._parse_json_file(filepath)

                for i, item in enumerate(data, 1):
                    if not isinstance(item, dict):
                        continue

                    item_title = item.get("title", "")
                    if title.lower() in item_title.lower():
                        media_item = self._create_media_item(item, i, filepath)

                        if use_cache:
                            self._cache[cache_key] = media_item

                        return media_item

            except (JSONParseError, InvalidMediaDataError):
                # Silently handle parsing errors for individual files
                continue

        if use_cache:
            self._cache[cache_key] = None
        return None

    def find_by_director(self, director: str) -> list[MediaItem]:
        """
        Find all media items by director.

        Args:
            director: Director name to search for (case-insensitive, partial match)

        Returns:
            List of MediaItem objects
        """
        results = []

        for filepath in self._find_json_files():
            try:
                data = self._parse_json_file(filepath)

                for i, item in enumerate(data, 1):
                    if not isinstance(item, dict):
                        continue

                    item_director = item.get("director", "")
                    if director.lower() in item_director.lower():
                        media_item = self._create_media_item(item, i, filepath)
                        results.append(media_item)

            except (JSONParseError, InvalidMediaDataError):
                continue

        return results

    def list_all(self, limit: int | None = None) -> list[MediaItem]:
        """
        List all media items found in JSON files.

        Args:
            limit: Maximum number of items to return

        Returns:
            List of MediaItem objects
        """
        all_items = []

        for filepath in self._find_json_files():
            try:
                data = self._parse_json_file(filepath)

                for i, item in enumerate(data, 1):
                    if not isinstance(item, dict):
                        continue

                    try:
                        media_item = self._create_media_item(item, i, filepath)
                        all_items.append(media_item)
                    except InvalidMediaDataError:
                        continue

            except (JSONParseError, InvalidMediaDataError):
                continue

        # Sort by rank
        all_items.sort(key=lambda x: x.rank)

        if limit:
            all_items = all_items[:limit]

        return all_items

    def clear_cache(self) -> None:
        """Clear the search cache."""
        self._cache.clear()

    def get_stats(self) -> dict[str, Any]:
        """Get statistics about the media database."""
        json_files = self._find_json_files()
        total_items = len(self.list_all())

        return {
            "json_files": len(json_files),
            "total_items": total_items,
            "search_directory": str(self.search_directory),
            "cache_size": len(self._cache),
        }
