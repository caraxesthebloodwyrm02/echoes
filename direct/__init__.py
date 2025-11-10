"""
EchoesAI Direct Connection System
Bypasses all middleware for authentic input-output properties.
Explicit direct connection to OpenAI API with no interference.
"""

__version__ = "1.0.0-Direct"
__author__ = "Atmosphere Team"
__description__ = "EchoesAI with direct OpenAI connection - zero middleware"

import os
import sys
import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

# Configure logging for direct connection
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class EchoesDirectConnection:
    """Direct EchoesAI connection with zero middleware interference."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize direct connection."""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = None
        self.connection_status = "disconnected"
        self.middleware_bypassed = True

        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")

        # Pure OpenAI import - bypass all Echoes components
        try:
            import openai

            # Create client with no Echoes interference
            self.client = openai.OpenAI(api_key=self.api_key)
            self.connection_status = "direct"
            logger.info("🔌 EchoesAI Direct Connection: Established")
        except Exception as e:
            logger.error("❌ Direct connection failed: %s", e)
            raise

    async def direct_chat(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-3.5-turbo",
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Direct chat completion with zero middleware interference.

        Args:
            messages: Pure message list with no preprocessing
            model: OpenAI model identifier (no Echoes defaults)
            max_tokens: Maximum tokens (no Echoes interference)
            temperature: Response randomness (no Echoes defaults)
            **kwargs: Additional parameters passed directly to OpenAI

        Returns:
            Raw OpenAI response with no modification
        """
        try:
            logger.info("🚀 Direct chat request to %s", model)

            # Pure API call - bypass all Echoes components
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,  # No Echoes DEFAULT_MAX_TOKENS override
                temperature=temperature,  # No Echoes DEFAULT_TEMPERATURE override
                **kwargs,  # Pass through raw parameters
            )

            # Raw response extraction - no Echoes wrapping
            result = {
                "content": response.choices[0].message.content,
                "model": response.model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                },
                "finish_reason": response.choices[0].finish_reason,
                "created": response.created,
                "id": response.id,
                "direct_connection": True,
                "middleware_bypassed": True,
                "echoes_defaults_bypassed": True,
            }

            logger.info(
                "✅ Direct response received: %d tokens", response.usage.total_tokens
            )
            return result

        except Exception as e:
            logger.error("❌ Direct chat failed: %s", e)
            raise

    async def direct_stream(
        self, messages: List[Dict[str, str]], model: str = "gpt-3.5-turbo", **kwargs
    ):
        """
        Direct streaming with zero middleware interference.
        """
        try:
            logger.info("🌊 Direct streaming to %s", model)

            # Direct streaming - no middleware buffering
            stream = self.client.chat.completions.create(
                model=model, messages=messages, stream=True, **kwargs
            )

            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield {
                        "content": chunk.choices[0].delta.content,
                        "direct_stream": True,
                        "middleware_bypassed": True,
                    }

        except Exception as e:
            logger.error("❌ Direct stream failed: %s", e)
            raise

    def get_connection_status(self) -> Dict[str, Any]:
        """Get direct connection status."""
        return {
            "status": self.connection_status,
            "middleware_bypassed": self.middleware_bypassed,
            "api_key_configured": bool(self.api_key),
            "client_initialized": self.client is not None,
            "connection_type": "direct_openai",
            "interference_level": "zero",
        }


def get_direct_connection() -> EchoesDirectConnection:
    """Get global direct connection instance."""
    if not hasattr(get_direct_connection, "_instance"):
        get_direct_connection._instance = EchoesDirectConnection()
    return get_direct_connection._instance


async def test_direct_connection():
    """Test direct connection functionality."""
    logger.info("🧪 Testing EchoesAI Direct Connection...")

    try:
        connection = get_direct_connection()

        # Test direct chat
        test_response = await connection.direct_chat(
            messages=[
                {
                    "role": "user",
                    "content": "EchoesAI direct connection test - respond with 'DIRECT'",
                }
            ],
            max_tokens=10,
        )

        if "DIRECT" in test_response["content"]:
            logger.info("✅ Direct connection test successful")
            return True
        else:
            logger.warning("⚠️ Unexpected response: %s", test_response["content"])
            return False

    except (ValueError, RuntimeError, ConnectionError) as e:
        logger.error("❌ Direct connection test failed: %s", e)
        return False


def main():
    """Main entry point for EchoesAI Direct Connection."""
    print("🚀 EchoesAI Direct Connection System")
    print("=" * 50)
    print("Zero Middleware - Authentic I/O Properties")
    print("Version: 1.0.0-Direct")
    print("")

    # Show connection status
    try:
        connection = get_direct_connection()
        status = connection.get_connection_status()

        print("📊 Connection Status:")
        for key, value in status.items():
            print(f"   • {key.replace('_', ' ').title()}: {value}")

        print("")
        print("🎯 Features:")
        print("   ✅ Zero middleware interference")
        print("   ✅ Authentic input-output properties")
        print("   ✅ Direct OpenAI API connection")
        print("   ✅ No request preprocessing")
        print("   ✅ No response modification")
        print("   ✅ Raw token tracking")
        print("   ✅ Unfiltered streaming")

    except (ImportError, AttributeError, TypeError) as e:
        logger.error("❌ Failed to initialize direct connection: %s", e)

    print("")
    print("Usage:")
    print("  python -m Echoes.direct.test")
    print("  python -m Echoes.direct.demo")
    print("  python -m Echoes.direct.stream")


if __name__ == "__main__":
    main()
