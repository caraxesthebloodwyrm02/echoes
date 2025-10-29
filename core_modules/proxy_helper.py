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

"""Proxy configuration helper for HTTP clients."""

import os
from typing import Any, Dict, Optional, Union


def get_proxy_url() -> Optional[str]:
    """Return the configured proxy URL from environment variables."""
    return os.getenv("OPENAI_PROXY") or os.getenv("HTTP_PROXY") or os.getenv("HTTPS_PROXY")


def get_proxies() -> Dict[str, str]:
    """Return a proxies dictionary suitable for HTTP clients."""
    proxy_url = get_proxy_url()
    if not proxy_url:
        return {}
    return {"http": proxy_url, "https": proxy_url}


def create_httpx_client(
    *,
    proxies: Optional[Union[Dict[str, str], str]] = None,
    **kwargs: Any,
) -> Any:
    """Create a configured HTTPX client that respects proxy settings."""
    try:
        from httpx import Client as HTTPXClient
    except ImportError as exc:  # pragma: no cover
        raise ImportError("httpx is required for proxy support; install httpx") from exc

    if proxies is None:
        proxies = get_proxies()

    client_kwargs: Dict[str, Any] = {"trust_env": True, **kwargs}

    if proxies:
        if isinstance(proxies, str):
            proxy_url = proxies
        else:
            proxy_url = proxies.get("http") or proxies.get("https")
        if proxy_url:
            os.environ.setdefault("HTTP_PROXY", proxy_url)
            os.environ.setdefault("HTTPS_PROXY", proxy_url)

    return HTTPXClient(**client_kwargs)
