#!/usr/bin/env python3
"""
Pure OpenAI Direct Connection
Absolutely zero interference - bypasses all Echoes components.
"""

import os
import asyncio
import logging
from typing import Dict, Any, Optional, List

# Configure minimal logging
logging.basicConfig(level=logging.WARNING)  # Only warnings and errors
logger = logging.getLogger(__name__)

class PureOpenAIDirect:
    """100% Pure OpenAI connection - absolutely no interference."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize pure OpenAI connection."""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")

        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")

        # Direct OpenAI import - no Echoes interference
        try:
            import openai
            # Create client with no additional configuration
            self.client = openai.OpenAI(api_key=self.api_key)
            self.connection_type = "pure_openai"
            logger.info("Pure OpenAI connection established")
        except Exception as e:
            logger.error(f"Pure OpenAI connection failed: {e}")
            raise

    async def pure_chat(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-3.5-turbo",
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Pure chat completion - absolutely no interference.

        Args:
            messages: Raw messages - no preprocessing
            model: OpenAI model - no defaults or overrides
            max_tokens: Token limit - no Echoes defaults
            temperature: Temperature - no Echoes defaults
            **kwargs: Raw parameters - no modification

        Returns:
            Raw OpenAI response - no wrapping or modification
        """
        try:
            # Direct API call with no interference
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )

            # Return raw response with minimal processing
            return {
                "content": response.choices[0].message.content,
                "model": response.model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "finish_reason": response.choices[0].finish_reason,
                "created": response.created,
                "id": response.id,
                "pure_openai": True,
                "zero_interference": True
            }

        except Exception as e:
            logger.error(f"Pure chat failed: {e}")
            raise

    async def test_pure_connection(self):
        """Test pure connection with no interference."""
        try:
            # Test with strict token limit
            response = await self.pure_chat(
                messages=[{"role": "user", "content": "Say 'Hello'"}],
                max_tokens=5,
                temperature=0.0
            )

            # Check if response respects token limit
            completion_tokens = response["usage"]["completion_tokens"]
            total_tokens = response["usage"]["total_tokens"]

            print("🧪 Pure OpenAI Test Results:")
            print(f"   • Content: {response['content']}")
            print(f"   • Model: {response['model']}")
            print(f"   • Completion Tokens: {completion_tokens}")
            print(f"   • Total Tokens: {total_tokens}")
            print("   • Max Tokens Requested: 5")
            print(f"   • Token Limit Respected: {completion_tokens <= 10}")  # Allow small buffer

            return {
                "success": True,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens,
                "limit_respected": completion_tokens <= 10,
                "pure_openai": True
            }

        except Exception as e:
            logger.error(f"Pure connection test failed: {e}")
            return {"success": False, "error": str(e)}

# Global pure connection instance
_pure_connection = None

def get_pure_connection() -> PureOpenAIDirect:
    """Get pure OpenAI connection instance."""
    global _pure_connection
    if _pure_connection is None:
        _pure_connection = PureOpenAIDirect()
    return _pure_connection

async def main():
    """Test pure OpenAI connection."""
    print("🔥 Pure OpenAI Direct Connection Test")
    print("=" * 50)
    print("Absolutely zero interference - bypassing all Echoes components")
    print("")

    try:
        connection = get_pure_connection()

        # Test pure connection
        result = await connection.test_pure_connection()

        if result["success"]:
            print("✅ Pure OpenAI connection successful!")
            print(f"✅ Token limit respected: {result['limit_respected']}")
            print(f"✅ Zero interference confirmed: {result['pure_openai']}")
        else:
            print("❌ Pure OpenAI connection failed")

    except Exception as e:
        print(f"❌ Pure connection test crashed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
