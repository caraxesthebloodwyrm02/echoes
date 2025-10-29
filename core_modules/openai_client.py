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

"""API client implementations with error handling and retry logic."""

import logging
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from openai import APIError, APITimeoutError, OpenAI, RateLimitError

from config.settings import get_settings

logger = logging.getLogger(__name__)


class BaseAPIClient(ABC):
    """Base class for API clients with common functionality."""

    def __init__(self, max_retries: int = 3, retry_delay: float = 1.0):
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.logger = logging.getLogger(self.__class__.__name__)

    def _retry_request(self, func, *args, **kwargs):
        """Execute a request with retry logic."""
        last_exception = None

        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except (RateLimitError, APIError, APITimeoutError) as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delay * (2**attempt)  # Exponential backoff
                    self.logger.warning(f"Request failed (attempt {attempt + 1}/{self.max_retries}): {e}")
                    self.logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    self.logger.error(f"Request failed after {self.max_retries} attempts: {e}")
            except Exception as e:
                self.logger.error(f"Unexpected error: {e}")
                raise

        raise last_exception

    @abstractmethod
    def health_check(self) -> bool:
        """Check if the API is accessible."""
        pass


class OpenAIClient(BaseAPIClient):
    """OpenAI API client with enhanced error handling."""

    def __init__(self, api_key: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        settings = get_settings()

        self.api_key = api_key or settings.openai_api_key
        self.model = settings.openai_model
        self.timeout = settings.openai_timeout

        try:
            self.client = OpenAI(api_key=self.api_key, timeout=self.timeout)
        except Exception as e:
            self.logger.error(f"Failed to initialize OpenAI client: {e}")
            raise

    def health_check(self) -> bool:
        """Check OpenAI API connectivity."""
        try:
            # Simple test request
            response = self.client.models.list()
            return len(response.data) > 0
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False

    def generate_text(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        system_message: Optional[str] = None,
    ) -> Optional[str]:
        """Generate text using OpenAI API."""
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})

        def _request():
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )
            return response.choices[0].message.content

        try:
            return self._retry_request(_request)
        except Exception as e:
            self.logger.error(f"Text generation failed: {e}")
            return None

    def analyze_sentiment(self, text: str) -> Optional[Dict[str, Any]]:
        """Analyze sentiment of given text."""
        prompt = f"Analyze the sentiment of this text and provide a score from -1 (very negative) to 1 (very positive), along with a brief explanation: {text}"

        response = self.generate_text(
            prompt=prompt,
            max_tokens=200,
            temperature=0.3,
            system_message="You are a sentiment analysis expert. Provide concise, accurate analysis.",
        )

        if response:
            try:
                # Simple parsing - in practice, you'd want more robust parsing
                lines = response.strip().split("\n")
                score_line = next(
                    (line for line in lines if "score" in line.lower() or any(char.isdigit() for char in line)),
                    lines[0],
                )

                # Extract numeric score (simplified)
                import re

                score_match = re.search(r"-?\d+\.?\d*", score_line)
                score = float(score_match.group()) if score_match else 0.0

                return {
                    "sentiment_score": score,
                    "analysis": response,
                    "confidence": min(abs(score), 1.0),  # Simplified confidence
                }
            except Exception as e:
                self.logger.error(f"Failed to parse sentiment response: {e}")

        return None

    def summarize_text(self, text: str, max_length: int = 150) -> Optional[str]:
        """Summarize given text."""
        prompt = f"Summarize the following text in {max_length} words or less: {text}"

        return self.generate_text(
            prompt=prompt,
            max_tokens=max_length * 2,  # Allow some buffer
            temperature=0.5,
            system_message="You are a summarization expert. Provide concise, accurate summaries.",
        )


class APIClientManager:
    """Manager for multiple API clients."""

    def __init__(self):
        self.clients: Dict[str, BaseAPIClient] = {}
        self.logger = logging.getLogger(__name__)

    def register_client(self, name: str, client: BaseAPIClient):
        """Register an API client."""
        self.clients[name] = client
        self.logger.info(f"Registered API client: {name}")

    def get_client(self, name: str) -> Optional[BaseAPIClient]:
        """Get a registered client by name."""
        return self.clients.get(name)

    def health_check_all(self) -> Dict[str, bool]:
        """Check health of all registered clients."""
        results = {}
        for name, client in self.clients.items():
            try:
                results[name] = client.health_check()
            except Exception as e:
                self.logger.error(f"Health check failed for {name}: {e}")
                results[name] = False
        return results

    def cleanup(self):
        """Clean up resources."""
        self.clients.clear()
        self.logger.info("API client manager cleaned up")


# Global client manager instance
api_manager = APIClientManager()


def get_openai_client() -> OpenAIClient:
    """Get or create OpenAI client instance."""
    if "openai" not in api_manager.clients:
        client = OpenAIClient()
        api_manager.register_client("openai", client)
    return api_manager.get_client("openai")


def initialize_api_clients():
    """Initialize default API clients."""
    try:
        openai_client = OpenAIClient()
        api_manager.register_client("openai", openai_client)
        logger.info("API clients initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize API clients: {e}")
        raise


# Initialize on import
try:
    initialize_api_clients()
except Exception as e:
    logger.warning(f"API client initialization deferred: {e}")
