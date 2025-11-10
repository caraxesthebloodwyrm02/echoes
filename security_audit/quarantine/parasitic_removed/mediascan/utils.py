"""
Utility functions for MediaScan library.
"""

from .core import MediaItem


def format_media_info(media: MediaItem) -> str:
    """
    Format media item information as a readable string.

    Args:
        media: MediaItem to format

    Returns:
        Formatted string with media information
    """
    info = media.to_dict()

    lines = [
        f"🎬 Found {info['type']}: {info['title']}",
        f"📊 Rank: {info['rank']}",
        f"📁 File: {info['filepath']}",
        f"🎥 Director: {info['director']}",
    ]

    if info["year"] != "N/A":
        lines.append(f"📅 Year: {info['year']}")

    if info["type"] == "TV Series":
        lines.append(f"📺 Seasons: {info.get('seasons', 'N/A')}")
        lines.append(f"🎞️ Episodes: {info.get('episodes', 'N/A')}")

    return "\n".join(lines)


def export_to_csv(media_list: list[MediaItem], output_file: str) -> None:
    """
    Export a list of media items to CSV file.

    Args:
        media_list: List of MediaItem objects
        output_file: Path to output CSV file
    """
    import csv

    if not media_list:
        return

    with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["title", "rank", "type", "year", "director", "filepath"]
        if any(item.type == "TV Series" for item in media_list):
            fieldnames.extend(["seasons", "episodes"])

        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for item in media_list:
            row = item.to_dict()
            writer.writerow(row)


def filter_by_year(media_list: list[MediaItem], year: str) -> list[MediaItem]:
    """
    Filter media items by year.

    Args:
        media_list: List of MediaItem objects
        year: Year to filter by

    Returns:
        Filtered list of MediaItem objects
    """
    return [item for item in media_list if item.year == year]


def filter_by_type(media_list: list[MediaItem], media_type: str) -> list[MediaItem]:
    """
    Filter media items by type.

    Args:
        media_list: List of MediaItem objects
        media_type: Type to filter by ('Movie' or 'TV Series')

    Returns:
        Filtered list of MediaItem objects
    """
    return [item for item in media_list if item.type == media_type]
