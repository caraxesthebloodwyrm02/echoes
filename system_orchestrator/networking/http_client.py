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

# MIT License
# Copyright (c) 2025 Echoes Project

"""
HTTP Client with httpx and asyncio support
"""

import logging
from typing import Dict, Optional

import httpx
from openai import OpenAI

logger = logging.getLogger(__name__)


class HTTPClient:
    """
    HTTP client using httpx and requests
    Supports both sync and async operations
    """

    def __init__(self, timeout: int = 30, max_retries: int = 3):
        self.timeout = timeout
        self.max_retries = max_retries
        self.logger = logging.getLogger(__name__)

        # Create httpx client
        self.client = httpx.Client(
            timeout=timeout, transport=httpx.HTTPTransport(retries=max_retries)
        )
        self.async_client = httpx.AsyncClient(
            timeout=timeout, transport=httpx.AsyncHTTPTransport(retries=max_retries)
        )

    def get(self, url: str, **kwargs) -> httpx.Response:
        """Synchronous GET request"""
        try:
            response = self.client.get(url, **kwargs)
            response.raise_for_status()
            return response
        except Exception as e:
            self.logger.error(f"GET request failed: {e}")
            raise

    def post(self, url: str, **kwargs) -> httpx.Response:
        """Synchronous POST request"""
        try:
            response = self.client.post(url, **kwargs)
            response.raise_for_status()
            return response
        except Exception as e:
            self.logger.error(f"POST request failed: {e}")
            raise

    async def async_get(self, url: str, **kwargs) -> httpx.Response:
        """Asynchronous GET request"""
        try:
            response = await self.async_client.get(url, **kwargs)
            response.raise_for_status()
            return response
        except Exception as e:
            self.logger.error(f"Async GET request failed: {e}")
            raise

    async def async_post(self, url: str, **kwargs) -> httpx.Response:
        """Asynchronous POST request"""
        try:
            response = await self.async_client.post(url, **kwargs)
            response.raise_for_status()
            return response
        except Exception as e:
            self.logger.error(f"Async POST request failed: {e}")
            raise

    def close(self):
        """Close HTTP clients"""
        self.client.close()

    async def aclose(self):
        """Close async HTTP client"""
        await self.async_client.aclose()


class OpenAIClient:
    """OpenAI client for Windsurf integration"""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.model = model
        self.logger = logging.getLogger(__name__)

        if api_key:
            self.client = OpenAI(api_key=api_key)
        else:
            self.logger.warning("OpenAI API key not provided")
            self.client = None

    def chat_completion(self, messages: list, **kwargs) -> Optional[str]:
        """Create chat completion"""
        if not self.client:
            self.logger.error("OpenAI client not initialized")
            return None

        try:
            response = self.client.chat.completions.create(
                model=self.model, messages=messages, **kwargs
            )
            return response.choices[0].message.content
        except Exception as e:
            self.logger.error(f"OpenAI API error: {e}")
            return None

    def orchestrate_command(
        self, command: str, context: Optional[Dict] = None
    ) -> Optional[str]:
        """Use OpenAI to orchestrate system commands intelligently"""
        if not self.client:
            return None

        messages = [
            {
                "role": "system",
                "content": "You are a Windows system orchestrator assistant. "
                "Provide safe, efficient system commands and explanations.",
            },
            {
                "role": "user",
                "content": f"Command request: {command}\nContext: {context or {}}",
            },
        ]

        return self.chat_completion(messages)


__all__ = ["HTTPClient", "OpenAIClient"]
