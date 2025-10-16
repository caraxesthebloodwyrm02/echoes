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
Privacy Middleware for API Endpoint Protection
"""

from functools import wraps
from typing import Any, Callable, Dict, List

from .privacy_filter import PrivacyFilter


class PrivacyMiddleware:
    """
    Middleware for automatic PII filtering on API responses

    Usage:
        middleware = PrivacyMiddleware(filter_mode="mask")

        @middleware.filter_response
        def my_endpoint():
            return {"data": "response with PII"}
    """

    def __init__(self, filter_mode: str = "mask"):
        """
        Initialize middleware

        Args:
            filter_mode: "redact", "anonymize", or "mask"
        """
        self.filter_mode = filter_mode
        self.privacy_filter = PrivacyFilter()

    def filter_response(self, func: Callable) -> Callable:
        """Decorator to filter PII from API responses"""

        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)

            # Filter the response based on type
            if isinstance(result, dict):
                return self._filter_dict(result)
            elif isinstance(result, list):
                return self._filter_list(result)
            elif isinstance(result, str):
                return self._filter_string(result)
            else:
                # Convert to string, filter, then try to convert back
                result_str = str(result)
                filtered_str = self._filter_string(result_str)
                try:
                    return type(result)(filtered_str)
                except (ValueError, TypeError):
                    return filtered_str

        return wrapper

    def _filter_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Filter PII from dictionary"""
        filtered = {}

        for key, value in data.items():
            if isinstance(value, dict):
                filtered[key] = self._filter_dict(value)
            elif isinstance(value, list):
                filtered[key] = self._filter_list(value)
            elif isinstance(value, str):
                filtered[key] = self._filter_string(value)
            else:
                filtered[key] = value

        return filtered

    def _filter_list(self, data: List[Any]) -> List[Any]:
        """Filter PII from list"""
        filtered = []

        for item in data:
            if isinstance(item, dict):
                filtered.append(self._filter_dict(item))
            elif isinstance(item, list):
                filtered.append(self._filter_list(item))
            elif isinstance(item, str):
                filtered.append(self._filter_string(item))
            else:
                filtered.append(item)

        return filtered

    def _filter_string(self, text: str) -> str:
        """Filter PII from string based on configured mode"""
        if self.filter_mode == "redact":
            return self.privacy_filter.redact(text)
        elif self.filter_mode == "anonymize":
            return self.privacy_filter.anonymize(text, deterministic=True)
        elif self.filter_mode == "mask":
            return self.privacy_filter.mask(text)
        else:
            # Default to mask
            return self.privacy_filter.mask(text)
