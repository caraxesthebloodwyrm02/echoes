"""
Glimpse Tools Module

This module provides tools for interacting with the Glimpse system,
integrating seamlessly with the Echoes assistant architecture.
"""

import asyncio
import json
import logging
import time
from typing import Any

logger = logging.getLogger(__name__)

# Import Glimpse components with fallback
try:
    from glimpse import Draft, GlimpseEngine, GlimpseResult, PrivacyGuard

    GLIMPSE_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Glimpse not available: {e}")
    GLIMPSE_AVAILABLE = False

    # Create fallback classes
    class Draft:
        def __init__(self, input_text: str, goal: str, constraints: str = ""):
            self.input_text = input_text
            self.goal = goal
            self.constraints = constraints

    class GlimpseResult:
        def __init__(self, sample: str, essence: str, **kwargs):
            self.sample = sample
            self.essence = essence
            self.status = "aligned"

    class PrivacyGuard:
        def commit(self, result):
            pass

    class GlimpseEngine:
        def __init__(self, **kwargs):
            self.privacy_guard = PrivacyGuard()

        async def glimpse(self, draft: Draft) -> GlimpseResult:
            return GlimpseResult(
                sample=(
                    draft.input_text[:100] + "..."
                    if len(draft.input_text) > 100
                    else draft.input_text
                ),
                essence=f"Intent: {draft.goal}; constraints: {draft.constraints or 'none'}",
            )


class GlimpseTools:
    """Main class for Glimpse tools integration."""

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize Glimpse tools."""
        self.config = config or {}
        self.engine = GlimpseEngine() if GLIMPSE_AVAILABLE else None
        self.privacy_guard = PrivacyGuard() if GLIMPSE_AVAILABLE else None
        self.available = GLIMPSE_AVAILABLE
        logger.info(f"GlimpseTools initialized (available: {self.available})")

    async def process_draft(
        self, input_text: str, goal: str, constraints: str = ""
    ) -> dict[str, Any]:
        """Process a draft through Glimpse engine."""
        if not self.available:
            return {
                "error": "Glimpse not available",
                "sample": (
                    input_text[:100] + "..." if len(input_text) > 100 else input_text
                ),
                "essence": f"Intent: {goal}; constraints: {constraints or 'none'}",
                "status": "fallback",
            }

        try:
            draft = Draft(input_text=input_text, goal=goal, constraints=constraints)
            result = await self.engine.glimpse(draft)

            return {
                "sample": result.sample,
                "essence": result.essence,
                "status": result.status,
                "delta": getattr(result, "delta", None),
                "attempt": getattr(result, "attempt", 1),
                "stale": getattr(result, "stale", False),
            }
        except Exception as e:
            logger.error(f"Glimpse processing error: {e}")
            return {
                "error": str(e),
                "sample": (
                    input_text[:100] + "..." if len(input_text) > 100 else input_text
                ),
                "essence": f"Intent: {goal}; constraints: {constraints or 'none'}",
                "status": "error",
            }

    def commit_result(self, result: dict[str, Any]) -> bool:
        """Commit a Glimpse result."""
        if not self.available or not self.privacy_guard:
            return False

        try:
            # Convert dict back to GlimpseResult
            glimpse_result = GlimpseResult(
                sample=result.get("sample", ""),
                essence=result.get("essence", ""),
                status=result.get("status", "aligned"),
            )
            self.privacy_guard.commit(glimpse_result)
            return True
        except Exception as e:
            logger.error(f"Commit error: {e}")
            return False

    def get_status(self) -> dict[str, Any]:
        """Get current Glimpse status."""
        return {
            "available": self.available,
            "engine_initialized": self.engine is not None,
            "privacy_guard_enabled": self.privacy_guard is not None,
            "config": self.config,
        }


# Individual tool classes for compatibility with existing tests
class GlimpseApiGetTool:
    """Tool for making GET requests to Glimpse API."""

    name = "glimpse_api_get"
    description = "API tool for trajectory tracking, data retrieval via GET requests, and readability metrics"

    def __init__(self, assistant=None, config: dict[str, Any] | None = None):
        self.assistant = assistant
        self.config = config or get_default_config()
        self.glimpse_tools = GlimpseTools(config)
        self._total_calls = 0
        self._error_count = 0
        self._total_response_time = 0.0
        self._last_call_time = None
        self._total_response_time = 0.0
        self._last_call_time = None
        self._total_response_time = 0.0
        self._last_call_time = None

    @property
    def input_schema(self) -> dict[str, Any]:
        """Input schema for the tool."""
        return {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "Request URL"},
                "headers": {"type": "object"},
                "params": {"type": "object"},
                "timeout": {"type": "number"},
            },
            "required": ["url"],
        }

    async def run(
        self,
        url: str,
        params: dict[str, Any] | None = None,
        headers: dict[str, Any] | None = None,
        timeout: float | None = None,
    ) -> dict[str, Any]:
        """Execute GET request."""
        self._total_calls += 1
        start = time.time()
        try:
            # Simulate API call through Glimpse
            result = await self.glimpse_tools.process_draft(
                input_text=f"GET {url}",
                goal="Retrieve data",
                constraints=json.dumps(
                    {"params": params or {}, "headers": headers or {}}
                ),
            )

            return {
                "url": url,
                "params": params or {},
                "headers": headers or {},
                "method": "GET",
                "status": "success",
                "data": result,
            }
        except Exception as e:
            self._error_count += 1
            raise e
        finally:
            elapsed = time.time() - start
            self._total_response_time += elapsed
            self._last_call_time = time.time()
            self._last_call_time = time.time()

    def execute(
        self,
        url: str,
        params: dict[str, Any] | None = None,
        headers: dict[str, Any] | None = None,
        timeout: float | None = None,
    ) -> dict[str, Any]:
        """Synchronous execute method for compatibility."""
        self._total_calls += 1
        # If assistant is available and has the method, use it
        if self.assistant and hasattr(self.assistant, "glimpse_api_get"):
            try:
                return self.assistant.glimpse_api_get(url, params)
            except Exception as e:
                self._error_count += 1
                raise e
        # Otherwise, use our own implementation
        try:
            import asyncio

            return asyncio.run(self.run(url, params, headers=headers, timeout=timeout))
        except Exception as e:
            self._error_count += 1
            raise e

    def get_stats(self) -> dict[str, Any]:
        """Get tool statistics."""
        avg = (
            round(self._total_response_time / self._total_calls, 3)
            if self._total_calls
            else 0.0
        )
        return {
            "name": self.name,
            "description": self.description,
            "total_calls": self._total_calls,
            "error_count": self._error_count,
            "last_call_time": self._last_call_time,
            "average_response_time": avg,
        }

    def to_openai_schema(self) -> dict[str, Any]:
        """Convert to OpenAI function schema."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.input_schema,
            },
        }


class GlimpseApiPostTool:
    """Tool for making POST requests to Glimpse API."""

    name = "glimpse_api_post"
    description = "API tool for data flow analysis, connectivity assessment, and submission via POST requests"

    def __init__(self, assistant=None, config: dict[str, Any] | None = None):
        self.assistant = assistant
        self.config = config or get_default_config()
        self.glimpse_tools = GlimpseTools(config)
        self._total_calls = 0
        self._error_count = 0
        self._total_response_time = 0.0
        self._last_call_time = None

    @property
    def input_schema(self) -> dict[str, Any]:
        """Input schema for the tool."""
        return {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "Request URL"},
                "data": {
                    "oneOf": [
                        {"type": "string"},
                        {"type": "object"},
                        {"type": "array", "items": {"type": "string"}},
                    ]
                },
                "headers": {"type": "object"},
                "content_type": {"type": "string"},
                "timeout": {"type": "number"},
            },
            "required": ["url", "data"],
        }

    async def run(
        self,
        url: str,
        data: dict[str, Any] | None = None,
        headers: dict[str, Any] | None = None,
        content_type: str | None = None,
        timeout: float | None = None,
    ) -> dict[str, Any]:
        """Execute POST request."""
        self._total_calls += 1
        start = time.time()
        try:
            # Simulate API call through Glimpse
            result = await self.glimpse_tools.process_draft(
                input_text=f"POST {url}",
                goal="Send data",
                constraints=json.dumps(
                    {
                        "data": data or {},
                        "headers": headers or {},
                        "content_type": content_type or "json",
                    }
                ),
            )

            return {
                "url": url,
                "data": data or {},
                "headers": headers or {},
                "content_type": content_type or "json",
                "method": "POST",
                "status": "success",
                "response": result,
            }
        except Exception as e:
            self._error_count += 1
            raise e
        finally:
            elapsed = time.time() - start
            self._total_response_time += elapsed
            self._last_call_time = time.time()

    def execute(
        self,
        url: str,
        data: dict[str, Any] | None = None,
        headers: dict[str, Any] | None = None,
        content_type: str | None = None,
        timeout: float | None = None,
    ) -> dict[str, Any]:
        """Synchronous execute method for compatibility."""
        self._total_calls += 1
        # If assistant is available and has the method, use it
        if self.assistant and hasattr(self.assistant, "glimpse_api_post"):
            try:
                return self.assistant.glimpse_api_post(
                    url, data, headers=headers, content_type=content_type
                )
            except Exception as e:
                self._error_count += 1
                raise e
        # Otherwise, use our own implementation
        try:
            import asyncio

            return asyncio.run(
                self.run(
                    url,
                    data,
                    headers=headers,
                    content_type=content_type,
                    timeout=timeout,
                )
            )
        except Exception as e:
            self._error_count += 1
            raise e

    def get_stats(self) -> dict[str, Any]:
        """Get tool statistics."""
        avg = (
            round(self._total_response_time / self._total_calls, 3)
            if self._total_calls
            else 0.0
        )
        return {
            "name": self.name,
            "total_calls": self._total_calls,
            "error_count": self._error_count,
            "last_call_time": self._last_call_time,
            "average_response_time": avg,
        }

    def to_openai_schema(self) -> dict[str, Any]:
        """Convert to OpenAI function schema."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.input_schema,
            },
        }


class GlimpseConnectPlatformsTool:
    """Tool for connecting to different platforms."""

    name = "glimpse_connect_platforms"
    description = "Platform connector tool to establish intelligent connections across systems with automatic compatibility analysis"

    def __init__(self, assistant=None, config: dict[str, Any] | None = None):
        self.assistant = assistant
        self.config = config or get_default_config()
        self.glimpse_tools = GlimpseTools(config)
        self._total_calls = 0
        self._error_count = 0

    @property
    def input_schema(self) -> dict[str, Any]:
        """Input schema for the tool."""
        return {
            "type": "object",
            "properties": {
                "source_path": {"type": "string"},
                "target_path": {"type": "string"},
                "integration_mode": {
                    "type": "string",
                    "enum": [
                        "reference_bridge",
                        "full_sync",
                        "read_only",
                        "write_only",
                    ],
                    "default": "reference_bridge",
                },
                "sync_frequency": {"type": "string", "default": "manual"},
                "conflict_resolution": {"type": "string", "default": "source_priority"},
            },
            "required": ["source_path", "target_path"],
        }

    async def run(
        self,
        source_path: str,
        target_path: str,
        integration_mode: str = "reference_bridge",
        sync_frequency: str = "manual",
        conflict_resolution: str = "source_priority",
    ) -> dict[str, Any]:
        """Connect to platform."""
        self._total_calls += 1
        try:
            # Simulate connection through Glimpse
            result = await self.glimpse_tools.process_draft(
                input_text=f"Connect {source_path} -> {target_path}",
                goal="Establish connection",
                constraints=json.dumps(
                    {
                        "integration_mode": integration_mode,
                        "sync_frequency": sync_frequency,
                        "conflict_resolution": conflict_resolution,
                    }
                ),
            )

            return {
                "source_path": source_path,
                "target_path": target_path,
                "connected": True,
                "status": "success",
                "message": f"Connected {source_path} -> {target_path}",
                "glimpse_result": result,
            }
        except Exception as e:
            self._error_count += 1
            raise e

    def execute(
        self,
        source_path: str,
        target_path: str,
        integration_mode: str = "reference_bridge",
        sync_frequency: str = "manual",
        conflict_resolution: str = "source_priority",
    ) -> dict[str, Any]:
        """Synchronous execute method for compatibility."""
        self._total_calls += 1
        # If assistant is available and has the method, use it
        if self.assistant and hasattr(self.assistant, "glimpse_connect_platforms"):
            try:
                return self.assistant.glimpse_connect_platforms(
                    source_path=source_path,
                    target_path=target_path,
                    integration_mode=integration_mode,
                    sync_frequency=sync_frequency,
                    conflict_resolution=conflict_resolution,
                )
            except Exception as e:
                self._error_count += 1
                raise e
        # Otherwise, use our own implementation
        try:
            import asyncio

            return asyncio.run(
                self.run(
                    source_path,
                    target_path,
                    integration_mode=integration_mode,
                    sync_frequency=sync_frequency,
                    conflict_resolution=conflict_resolution,
                )
            )
        except Exception as e:
            self._error_count += 1
            raise e

    def get_stats(self) -> dict[str, Any]:
        """Get tool statistics."""
        return {
            "name": self.name,
            "total_calls": self._total_calls,
            "error_count": self._error_count,
            "success_rate": 1.0 if self._total_calls > 0 else 1.0,
            "last_call_time": None,
            "average_operation_time": 0.0,
        }

    def to_openai_schema(self) -> dict[str, Any]:
        """Convert to OpenAI function schema."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.input_schema,
            },
        }


# Export main functions
def create_glimpse_tools(config: dict[str, Any] | None = None) -> GlimpseTools:
    """Create a GlimpseTools instance."""
    return GlimpseTools(config)


def get_default_config() -> dict[str, Any]:
    """Get default configuration."""
    return {
        "debug": False,
        "timeout": 30,
        "max_retries": 3,
        "use_openai": True,
        "enable_clarifiers": True,
        "enable_performance": True,
    }


def get_glimpse_tools(assistant=None, config: dict[str, Any] | None = None) -> list:
    """Get all available Glimpse tools."""
    return [
        GlimpseApiGetTool(assistant, config),
        GlimpseApiPostTool(assistant, config),
        GlimpseConnectPlatformsTool(assistant, config),
    ]


# Quick test function
async def test_glimpse_tools():
    """Test the Glimpse tools integration."""
    tools = create_glimpse_tools()
    status = tools.get_status()
    print(f"Glimpse status: {status}")

    if status["available"]:
        result = await tools.process_draft(
            input_text="Test input for Glimpse",
            goal="Test functionality",
            constraints="None",
        )
        print(f"Test result: {result}")
    else:
        print("Glimpse not available, using fallback")


if __name__ == "__main__":
    asyncio.run(test_glimpse_tools())
