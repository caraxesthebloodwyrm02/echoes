"""
MediaScan - Simple JSON Media Database Search

A lightweight library for searching media items (movies, TV series) in JSON files.
"""

from .core import MediaItem, MediaScanner, Movie, TVSeries
from .exceptions import JSONParseError, MediaScanError

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

__all__ = [
    "MediaItem",
    "Movie",
    "TVSeries",
    "MediaScanner",
    "MediaScanError",
    "JSONParseError",
]
