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
