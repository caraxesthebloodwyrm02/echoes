import json
import os
from dataclasses import asdict, dataclass
from json.decoder import JSONDecodeError
from typing import Any


@dataclass
class MediaItem:
    """Base class for media items (movies or TV series)."""

    title: str
    rank: int
    file: str
    year: str = "N/A"
    director: str = "Unknown"
    type: str = "Movie"

    def to_dict(self) -> dict[str, Any]:
        """Convert the media item to a dictionary."""
        return asdict(self)


@dataclass
class Movie(MediaItem):
    """Class representing a movie."""

    def __post_init__(self):
        self.type = "Movie"


@dataclass
class TVSeries(MediaItem):
    """Class representing a TV series."""

    seasons: str = "N/A"
    episodes: str = "N/A"
    network: str = "Unknown"
    status: str = "Unknown"

    def __post_init__(self):
        self.type = "TV Series"


def find_media(media_title: str, search_dir: str) -> MediaItem | None:
    """
    Search for a media item (movie or TV series) by title in all JSON files within a directory.

    Args:
        media_title: Title of the media to search for
        search_dir: Directory to search for JSON files

    Returns:
        MediaItem if found, None otherwise
    """
    for root, _, files in os.walk(search_dir):
        for file in files:
            if not file.endswith(".json"):
                continue

            filepath = os.path.join(root, file)
            try:
                with open(filepath, encoding="utf-8") as f:
                    try:
                        data = json.load(f)
                    except JSONDecodeError as e:
                        print(f"⚠️ Error decoding JSON in {filepath}: {e}")
                        continue

                    if not isinstance(data, list):
                        continue

                    for i, item in enumerate(data, 1):
                        if not isinstance(item, dict):
                            continue

                        title = item.get("title")
                        if not title or media_title.lower() not in title.lower():
                            continue

                        # Determine if it's a TV series or movie
                        if item.get("type", "").lower() == "tv" or "seasons" in item:
                            return TVSeries(
                                title=item.get("title", "Unknown"),
                                rank=i,
                                file=filepath,
                                year=item.get("year", "N/A"),
                                director=item.get("director", "Unknown"),
                                seasons=item.get("seasons", "N/A"),
                                episodes=item.get("episodes", "N/A"),
                                network=item.get("network", "Unknown"),
                                status=item.get("status", "Unknown"),
                            )
                        return Movie(
                            title=item.get("title", "Unknown"),
                            rank=i,
                            file=filepath,
                            year=item.get("year", "N/A"),
                            director=item.get("director", "Unknown"),
                        )

            except (PermissionError, OSError) as e:
                print(f"⚠️ Error reading {filepath}: {e}")
    return None


def print_media_info(media: MediaItem | None) -> None:
    """Print information about the found media item."""
    if not media:
        print(f"❌ Media not found in any JSON files in {search_directory}")
        return

    info = media.to_dict()
    print(f"🎬 Found {info['type']}: {info['title']}")
    print(f"📊 Rank: {info['rank']}")
    print(f"📁 File: {info['file']}")
    print(f"🎥 Director: {info['director']}")
    if info["year"] != "N/A":
        print(f"📅 Year: {info['year']}")
    if info["type"] == "TV Series":
        print(f"📺 Seasons: {info.get('seasons', 'N/A')}")
        print(f"🎞️ Episodes: {info.get('episodes', 'N/A')}")
        if info.get("network", "Unknown") != "Unknown":
            print(f"📡 Network: {info['network']}")
        if info.get("status", "Unknown") != "Unknown":
            print(f"📺 Status: {info['status']}")


# Example usage
if __name__ == "__main__":
    search_directory = "e:/Projects/Echoes"  # Include sample TV series file
    media_to_find = "Game of Thrones"  # Popular TV series
    print(f"🔍 Searching for: {media_to_find}")
    result = find_media(media_to_find, search_directory)
    print_media_info(result)
