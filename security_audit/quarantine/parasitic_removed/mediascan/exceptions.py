"""
Custom exceptions for MediaScan library.
"""


class MediaScanError(Exception):
    """Base exception for MediaScan library."""

    pass


class JSONParseError(MediaScanError):
    """Raised when JSON parsing fails."""

    def __init__(self, filepath: str, original_error: Exception):
        self.filepath = filepath
        self.original_error = original_error
        super().__init__(f"Failed to parse JSON in {filepath}: {original_error}")


class FileNotFoundError(MediaScanError):
    """Raised when search directory is not found."""

    pass


class InvalidMediaDataError(MediaScanError):
    """Raised when media data is invalid or malformed."""

    pass
