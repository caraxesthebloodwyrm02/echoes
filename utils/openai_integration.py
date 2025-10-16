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
#
# Copyright (c) 2025 Echoes Project
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
Streamlined OpenAI Integration Module
Unified interface for OpenAI API interactions with automatic configuration
"""

import logging
import os
from typing import Any, Dict, List, Optional

from utils.safe_imports import safe_import

logger = logging.getLogger(__name__)


class OpenAIIntegration:
    """Unified OpenAI integration with automatic configuration and fallbacks"""

    def __init__(self):
        self._client = None
        self._agents_available = False
        self._configured = False

        self._configure()

    def _configure(self) -> bool:
        """Configure OpenAI integration with automatic setup"""
        try:
            # Check environment variables
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                logger.warning("OPENAI_API_KEY not found in environment")
                return False

            # Try to import and configure OpenAI
            openai_success, openai_module = safe_import("openai")
            if not openai_success:
                logger.error("OpenAI package not available")
                return False

            # Configure OpenAI client
            # Use new client-based API for OpenAI v1.0+
            try:
                self._client = openai_module.OpenAI(api_key=api_key)
                logger.info("✓ OpenAI client initialized (v1.0+ API)")
            except AttributeError:
                # Fallback for older versions
                openai_module.api_key = api_key
                self._client = openai_module
                logger.info("✓ OpenAI client initialized (legacy API)")

            # Try to configure Agents SDK
            agents_success, agents_module = safe_import("agents")
            if agents_success:
                self._agents_available = True
                logger.info("✓ OpenAI Agents SDK available")
            else:
                logger.warning("OpenAI Agents SDK not available - using basic client")

            # Set default model
            self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
            self.max_retries = int(os.getenv("OPENAI_MAX_RETRIES", "3"))
            self.timeout = int(os.getenv("OPENAI_TIMEOUT", "30"))

            self._configured = True
            logger.info("✓ OpenAI integration configured successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to configure OpenAI integration: {e}")
            return False

    @property
    def is_configured(self) -> bool:
        """Check if OpenAI integration is properly configured"""
        return self._configured

    @property
    def agents_available(self) -> bool:
        """Check if OpenAI Agents SDK is available"""
        return self._agents_available

    def create_completion(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> Optional[str]:
        """Create a completion using OpenAI API"""
        if not self._configured:
            logger.error("OpenAI integration not configured")
            return None

        try:
            response = self._client.chat.completions.create(
                model=model or self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=self.timeout,
                **kwargs,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI completion failed: {e}")
            return None

    def create_chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> Optional[str]:
        """Create a chat completion with custom messages"""
        if not self._configured:
            logger.error("OpenAI integration not configured")
            return None

        try:
            response = self._client.chat.completions.create(
                model=model or self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=self.timeout,
                **kwargs,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI chat completion failed: {e}")
            return None

    def create_agent(
        self, name: str, instructions: str, model: Optional[str] = None, **kwargs
    ) -> Optional[Any]:
        """Create an OpenAI Agent if Agents SDK is available"""
        if not self._agents_available:
            logger.warning("OpenAI Agents SDK not available")
            return None

        try:
            from agents import Agent

            return Agent(
                name=name,
                instructions=instructions,
                model=model or self.model,
                **kwargs,
            )
        except Exception as e:
            logger.error(f"Failed to create agent: {e}")
            return None

    def run_agent(self, agent: Any, input_text: str, **kwargs) -> Optional[Any]:
        """Run an agent if Agents SDK is available"""
        if not self._agents_available:
            logger.warning("OpenAI Agents SDK not available")
            return None

        try:
            from agents import Runner

            return Runner.run(agent, input_text, **kwargs)
        except Exception as e:
            logger.error(f"Failed to run agent: {e}")
            return None

    def validate_connection(self) -> bool:
        """Validate OpenAI API connection"""
        if not self._configured:
            return False

        try:
            # Simple test completion
            response = self.create_completion(
                "Hello, please respond with 'OK' if you can read this.",
                model="gpt-3.5-turbo",  # Use cheaper model for testing
                temperature=0,
                max_tokens=10,
            )
            return response is not None and "OK" in response.upper()
        except Exception as e:
            logger.error(f"OpenAI connection validation failed: {e}")
            return False

    def get_status(self) -> Dict[str, Any]:
        """Get integration status"""
        return {
            "configured": self._configured,
            "agents_available": self._agents_available,
            "model": getattr(self, "model", None),
            "max_retries": getattr(self, "max_retries", None),
            "timeout": getattr(self, "timeout", None),
            "connection_valid": self.validate_connection()
            if self._configured
            else False,
        }


# Global instance for easy access
_openai_integration: Optional[OpenAIIntegration] = None


def get_openai_integration() -> OpenAIIntegration:
    """Get singleton OpenAI integration instance"""
    global _openai_integration
    if _openai_integration is None:
        _openai_integration = OpenAIIntegration()
    return _openai_integration


def quick_completion(prompt: str, **kwargs) -> Optional[str]:
    """Quick completion using global integration"""
    integration = get_openai_integration()
    return integration.create_completion(prompt, **kwargs)


def validate_openai_setup() -> bool:
    """Validate complete OpenAI setup"""
    integration = get_openai_integration()
    status = integration.get_status()

    logger.info("OpenAI Integration Status:")
    logger.info(f"  Configured: {status['configured']}")
    logger.info(f"  Agents Available: {status['agents_available']}")
    logger.info(f"  Model: {status['model']}")
    logger.info(f"  Connection Valid: {status['connection_valid']}")

    return status["configured"] and status["connection_valid"]


# Auto-initialize on import
if __name__ != "__main__":
    logger.info("Initializing OpenAI integration...")
    integration = get_openai_integration()
    if integration.is_configured:
        logger.info("OpenAI integration ready")
    else:
        logger.warning("OpenAI integration not configured - check OPENAI_API_KEY")
