#!/usr/bin/env python3
"""
Secure Coordinate Handler
Version 1.0.0

Comprehensive solution for secure coordinate data handling and privacy protection.
Addresses the critical vulnerability of coordinate data exposure in the codebase.
"""

import hashlib
import logging
from typing import List, Tuple

from data_sanitizer import data_sanitizer
from utils.coordinates import Coordinates


class SecureCoordinateHandler:
    """
    Secure coordinate handling system that prevents data exposure.
    """

    def __init__(self):
        self.logger = logging.getLogger("SecureCoordinateHandler")
        self._setup_logging()
        self.coordinate_cache = {}
        self.privacy_level = "high"

    def _setup_logging(self):
        """Setup secure logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )

    def create_secure_coordinate(
        self, lat: float, lng: float, label: str = "unknown"
    ) -> Coordinates:
        """
        Create a coordinate object with security validation and audit trail.

        Args:
            lat: Latitude value
            lng: Longitude value
            label: Descriptive label for audit purposes

        Returns:
            Coordinates object with security metadata
        """
        # Validate input
        is_valid, error_msg = data_sanitizer.validate_coordinate_input(lat, lng)
        if not is_valid:
            raise ValueError(f"Invalid coordinate input: {error_msg}")

        # Create coordinate with sanitization
        coord = Coordinates(lat, lng)

        # Audit the creation
        data_sanitizer.audit_coordinate_usage(f"create_{label}", coord)

        # Cache for performance
        coord_hash = self._get_coordinate_hash(lat, lng)
        self.coordinate_cache[coord_hash] = {
            "coordinate": coord,
            "label": label,
            "created_at": __import__("time").time(),
        }

        self.logger.info(f"Secure coordinate created for {label}: {coord_hash[:8]}")
        return coord

    def _get_coordinate_hash(self, lat: float, lng: float) -> str:
        """Create a hash of coordinate data for tracking."""
        coord_string = f"{lat:.6f},{lng:.6f}"
        return hashlib.sha256(coord_string.encode()).hexdigest()

    def get_sanitized_coordinate_string(self, coord: Coordinates) -> str:
        """
        Get a privacy-safe string representation of coordinates.

        Args:
            coord: Coordinates object

        Returns:
        """
        # Reduce precision for privacy
        sanitized_lat = round(coord.latitude, 2)
        sanitized_lng = round(coord.longitude, 2)

        return f"[{sanitized_lat:.2f}, {sanitized_lng:.2f}]"

    def mask_coordinate_in_text(self, text: str) -> str:
        """
        Mask all coordinate data in text for safe display.

            text: Text containing coordinate data

        Returns:
            Text with coordinates masked
        """
        # Pattern to match coordinate-like numbers
        coordinate_pattern = r"(\d+\.\d+)"

        def mask_coordinate(match):
            coord = float(match.group(1))
            # Round to 2 decimal places for privacy
            masked = round(coord, 2)
            return f"{masked}***"

        return __import__("re").sub(coordinate_pattern, mask_coordinate, text)

    def validate_coordinate_privacy(self, text: str) -> Tuple[bool, List[str]]:
        """
        Validate that text doesn't expose coordinate data inappropriately.

        Args:
            text: Text to validate

        Returns:
            Tuple of (is_safe, list_of_issues)
        """
        issues = []

        # Check for full precision coordinates
        full_precision_pattern = r"\d+\.\d{4,}"
        if __import__("re").search(full_precision_pattern, text):
            issues.append("Full precision coordinates detected")

        # Check for coordinate patterns in logs
        if any(pattern in text.lower() for pattern in ["lat:", "lng:", "latitude:", "longitude:"]):
            issues.append("Coordinate labels detected in output")

        return len(issues) == 0, issues

    def sanitize_print_output(self, *args, **kwargs):
        """
        Secure print function that sanitizes coordinate data.

        Args:
            *args: Print arguments
            **kwargs: Print keyword arguments
        """
        sanitized_args = []

        for arg in args:
            if isinstance(arg, str):
                # Mask coordinate data in strings
                sanitized_arg = self.mask_coordinate_in_text(str(arg))
                sanitized_args.append(sanitized_arg)
            else:
                sanitized_args.append(arg)

        # Validate privacy before printing
        for arg in sanitized_args:
            if isinstance(arg, str):
                is_safe, issues = self.validate_coordinate_privacy(arg)
                if not is_safe:
                    self.logger.warning(f"Privacy issue in print output: {issues}")

        # Safe print
        print(*sanitized_args, **kwargs)

    def secure_coordinate_display(self, coord: Coordinates, context: str = "general") -> str:
        """
        Get a context-appropriate display of coordinates.

        Args:
            coord: Coordinates object

        Returns:
            Safe coordinate display string
        """
        if context == "debug":
            return f"[{coord.latitude:.6f}, {coord.longitude:.6f}]"
        elif context == "log":
            return f"[{round(coord.latitude, 3):.3f}, {round(coord.longitude, 3):.3f}]"
        else:
            return f"[{round(coord.latitude, 2):.2f}, {round(coord.longitude, 2):.2f}]"


# Global secure coordinate handler
secure_coords = SecureCoordinateHandler()

# Monkey patch print for security
_original_print = print


def secure_print(*args, **kwargs):
    """Secure print function that sanitizes coordinate data."""
    secure_coords.sanitize_print_output(*args, **kwargs)


# Replace built-in print with secure version in this module
import builtins

builtins.print = secure_print
