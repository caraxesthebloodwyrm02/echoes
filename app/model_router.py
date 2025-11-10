"""
Dynamic Model Router for EchoesAssistantV2

Intelligently selects the most appropriate GPT-4o model based on:
- Task complexity
- Need for web search
- Tool requirements
- Prompt characteristics
"""

import asyncio
import hashlib
import logging
import re
import time
from collections import defaultdict
import os

_ORCH_ENABLED = os.getenv("ECHOES_ORCHESTRAL_ENABLED", "").lower() in (
    "1",
    "true",
    "yes",
    "on",
)
try:
    if _ORCH_ENABLED:
        from app.orchestral_model_router import route_request_with_orchestral, get_orchestral_routing_status  # type: ignore
    else:
        route_request_with_orchestral = None  # type: ignore
        get_orchestral_routing_status = None  # type: ignore
except Exception:  # pragma: no cover
    route_request_with_orchestral = None  # type: ignore
    get_orchestral_routing_status = None  # type: ignore

logger = logging.getLogger(__name__)


class ModelRouter:
    """
    Routes requests to the most appropriate GPT-4o model.
    """

    def __init__(self):
        """Initialize the model router with default settings."""
        self.default_model = "gpt-4o-mini"
        self.complexity_threshold = 0.7
        self.web_search_indicators = [
            "current",
            "latest",
            "today's",
            "recent",
            "search for",
            "find information",
            "look up",
            "what's new",
            "update on",
            "news about",
            "current status",
            "happening now",
            "today",
            "now",
            "real-time",
            "live",
            "breaking",
            "just released",
        ]
        self.complexity_indicators = [
            "analyze",
            "compare",
            "explain",
            "why",
            "how",
            "complex",
            "detailed",
            "in-depth",
            "step by step",
            "reasoning",
            "break down",
            "evaluate",
            "critique",
            "problem solve",
            "synthesize",
            "integrate",
            "comprehensive",
            "thorough",
            "detailed analysis",
            "deep dive",
            "investigate",
        ]
        self.math_indicators = [
            "solve",
            "equation",
            "integral",
            "derivative",
            "calculus",
            "algebra",
            "matrix",
            "theorem",
            "proof",
            "probability",
            "statistics",
            "variance",
            "regression",
            "polynomial",
            "limit",
            "series",
            "sigma",
            "pi",
            "gradient",
            "vector",
        ]
        self.science_indicators = [
            "physics",
            "chemistry",
            "biology",
            "experiment",
            "molecule",
            "quantum",
            "thermodynamics",
            "neuroscience",
            "astrophysics",
            "hypothesis",
            "simulation",
            "laboratory",
            "molecular",
            "genetics",
            "organic",
            "reaction",
            "particle",
            "spectroscopy",
        ]
        self.coding_indicators = [
            "code",
            "algorithm",
            "function",
            "class",
            "method",
            "recursive",
            "refactor",
            "optimize",
            "debug",
            "compile",
            "python",
            "javascript",
            "java",
            "c++",
            "c#",
            "rust",
            "typescript",
            "sql",
            "data structure",
            "Glimpse test",
        ]

    def select_model(self, prompt: str, tools: list[dict] = None) -> str:
        """
        Select the most appropriate model based on prompt and tools.

        Args:
            prompt: User's input prompt
            tools: List of tools being used

        Returns:
            str: Selected model name
        """
        # Priority 1: Check if web search is needed but tools are also required
        # Note: gpt-4o-search-preview doesn't support tools, so use gpt-4o for tool + search
        if self._needs_web_search(prompt, tools) and tools:
            logger.debug("Web search with tools detected, selecting gpt-4o")
            return "gpt-4o"
        # Priority 2: Check if web search is needed without tools
        elif self._needs_web_search(prompt, tools):
            logger.debug("Web search detected, selecting gpt-4o-search-preview")
            return "gpt-4o-search-preview"

        # Priority 3: Specialized math/science/coding tasks
        specialized_model = self._select_specialized_model(prompt)
        if specialized_model:
            logger.debug("Specialized task detected, selecting %s", specialized_model)
            return specialized_model

        # Priority 4: Check for complex reasoning tasks
        if self._is_complex_task(prompt):
            logger.debug("Complex task detected, selecting gpt-4o")
            return "gpt-4o"

        # Default to mini for simple tasks
        logger.debug("Simple task detected, selecting gpt-4o-mini")
        return self.default_model

    def _needs_web_search(self, prompt: str, tools: list[dict] = None) -> bool:
        """
        Determine if the prompt requires web search capabilities.

        Args:
            prompt: User prompt
            tools: List of available tools

        Returns:
            bool: True if web search is needed
        """
        prompt_lower = prompt.lower()

        # Check for explicit search triggers in prompt
        for indicator in self.web_search_indicators:
            if indicator in prompt_lower:
                return True

        # Check if any tools require web search
        if tools:
            search_tools = [
                t
                for t in tools
                if t.get("name") in ["web_search", "get_web_page_content", "browser"]
            ]
            if search_tools:
                return True

        # Check for questions about recent events or current information
        recent_patterns = [
            r"\b(2024|2025)\b",
            r"\bthis (week|month|year)\b",
            r"\brecently\b",
            r"\blately\b",
            r"\bwhat\'s (happening|going on|new)\b",
        ]

        for pattern in recent_patterns:
            if re.search(pattern, prompt_lower):
                return True

        return False

    def _is_complex_task(self, prompt: str) -> bool:
        """
        Determine if the task requires advanced reasoning.

        Args:
            prompt: User prompt

        Returns:
            bool: True if task is complex
        """
        prompt_lower = prompt.lower()

        # Check for complexity indicators
        for indicator in self.complexity_indicators:
            if indicator in prompt_lower:
                return True

        # Check prompt length (longer prompts often indicate complexity)
        word_count = len(prompt.split())
        if word_count > 30:
            return True

        # Check for multi-part questions (indicated by multiple question marks)
        if prompt.count("?") > 1:
            return True

        # Check for comparison tasks
        comparison_patterns = [
            r"\bcompare\b",
            r"\bdifference\b",
            r"\bversus\b",
            r"\bvs\b",
            r"\bor\b.*\bor\b",
            r"\bbetween\b.*\band\b",
        ]

        for pattern in comparison_patterns:
            if re.search(pattern, prompt_lower):
                return True

        return False

    def _select_specialized_model(self, prompt: str) -> str | None:
        """Determine if prompt requires specialized reasoning models."""
        prompt_lower = prompt.lower()
        word_count = len(prompt.split())

        code_block = "```" in prompt or re.search(
            r"\b(def|class|import|public|private|interface|lambda)\b", prompt_lower
        )
        math_score = sum(1 for kw in self.math_indicators if kw in prompt_lower)
        science_score = sum(1 for kw in self.science_indicators if kw in prompt_lower)
        coding_score = sum(1 for kw in self.coding_indicators if kw in prompt_lower)

        equation_pattern = re.search(
            r"(=|∑|∫|√|π|≈|≥|≤|\^|\bprove\b|\bderive\b)", prompt_lower
        )
        scientific_pattern = re.search(
            r"\bmodel(?:ing)?\b|\bsimulate\b|\bhypothesis\b|\bexperiment\b",
            prompt_lower,
        )

        heavy_trigger = (
            word_count > 80
            or "multi-step" in prompt_lower
            or "step-by-step" in prompt_lower
            or "detailed" in prompt_lower
            or "comprehensive" in prompt_lower
            or "optimize" in prompt_lower
            or "refactor" in prompt_lower
            or "architect" in prompt_lower
        )

        # Coding dominance
        if coding_score >= 2 or code_block:
            return "o3" if heavy_trigger or coding_score >= 4 else "o3-mini"

        # Math dominance
        if math_score >= 2 or equation_pattern:
            return "o3" if heavy_trigger or math_score >= 4 else "o3-mini"

        # Science dominance
        if science_score >= 2 or scientific_pattern:
            return "o3" if heavy_trigger or science_score >= 4 else "o3-mini"

        return None


# Optional helper API to route with orchestral when enabled
def route_request(prompt: str, context: dict | None = None) -> dict | str:
    if _ORCH_ENABLED and route_request_with_orchestral:
        return route_request_with_orchestral(prompt, context or {})
    router = ModelRouter()
    return router.select_model(prompt)


def routing_status() -> dict:
    if _ORCH_ENABLED and get_orchestral_routing_status:
        return get_orchestral_routing_status()
    return {"orchestral_enabled": False}


class ModelResponseCache:
    """
    Caches model responses to improve performance and reduce costs.
    """

    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600):
        """
        Initialize the cache.

        Args:
            max_size: Maximum number of cached responses
            ttl_seconds: Time-to-live for cached responses
        """
        self.cache = {}
        self.timestamps = {}
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.lock = asyncio.Lock()

    async def get(self, prompt: str, model: str) -> dict | None:
        """
        Get cached response if available and not expired.

        Args:
            prompt: The original prompt
            model: The model used

        Returns:
            dict: Cached response or None
        """
        key = self._generate_key(prompt, model)

        async with self.lock:
            if key not in self.cache:
                return None

            # Check if expired
            if time.time() - self.timestamps[key] > self.ttl_seconds:
                del self.cache[key]
                del self.timestamps[key]
                return None

            return self.cache[key]

    async def set(self, prompt: str, model: str, response: dict):
        """
        Cache the response.

        Args:
            prompt: The original prompt
            model: The model used
            response: The response to cache
        """
        key = self._generate_key(prompt, model)

        async with self.lock:
            # Remove oldest entries if cache is full
            while len(self.cache) >= self.max_size:
                oldest_key = min(self.timestamps.keys(), key=self.timestamps.get)
                del self.cache[oldest_key]
                del self.timestamps[oldest_key]

            self.cache[key] = response
            self.timestamps[key] = time.time()

    def _generate_key(self, prompt: str, model: str) -> str:
        """
        Generate a unique cache key.

        Args:
            prompt: The prompt
            model: The model name

        Returns:
            str: Unique cache key
        """
        # Use first 100 chars of prompt + model for key
        prompt_hash = hashlib.md5(prompt[:100].encode()).hexdigest()[:8]
        return f"{model}:{prompt_hash}"


class ModelMetrics:
    """
    Tracks model usage metrics for monitoring and optimization.
    """

    def __init__(self):
        """Initialize metrics tracking."""
        self.metrics = {
            "total_requests": 0,
            "model_usage": defaultdict(int),
            "response_times": defaultdict(list),
            "errors": defaultdict(int),
            "cache_hits": defaultdict(int),
            "cache_misses": defaultdict(int),
        }
        self.lock = asyncio.Lock()

    def record_usage_sync(
        self,
        model: str,
        response_time: float,
        success: bool = True,
        cached: bool = False,
    ):
        """
        Synchronous version of record_usage for non-async contexts.

        Args:
            model: Model name
            response_time: Response time in seconds
            success: Whether the request was successful
            cached: Whether the response was from cache
        """
        self.metrics["total_requests"] += 1
        self.metrics["model_usage"][model] += 1
        self.metrics["response_times"][model].append(response_time)

        if not success:
            self.metrics["errors"][model] += 1

        if cached:
            self.metrics["cache_hits"][model] += 1
        else:
            self.metrics["cache_misses"][model] += 1

    async def record_usage(
        self,
        model: str,
        response_time: float,
        success: bool = True,
        cached: bool = False,
    ):
        """
        Record model usage metrics.

        Args:
            model: Model name
            response_time: Response time in seconds
            success: Whether the request was successful
            cached: Whether the response was from cache
        """
        async with self.lock:
            self.record_usage_sync(model, response_time, success, cached)

    async def get_metrics(self) -> dict:
        """
        Get current metrics with statistics.

        Returns:
            dict: Metrics summary
        """
        async with self.lock:
            stats = self.metrics.copy()

            # Calculate response time statistics
            for model, times in list(stats["response_times"].items()):
                if times:
                    stats["response_times"][model] = {
                        "count": len(times),
                        "avg": sum(times) / len(times),
                        "min": min(times),
                        "max": max(times),
                        "p95": (
                            sorted(times)[int(len(times) * 0.95)]
                            if len(times) > 20
                            else max(times)
                        ),
                    }

            # Calculate cache hit rates
            stats["cache_hit_rate"] = {}
            for model in list(stats["model_usage"].keys()):
                hits = stats["cache_hits"].get(model, 0)
                misses = stats["cache_misses"].get(model, 0)
                total = hits + misses
                if total > 0:
                    stats["cache_hit_rate"][model] = hits / total

            return stats

    async def reset_metrics(self):
        """Reset all metrics."""
        async with self.lock:
            self.metrics = {
                "total_requests": 0,
                "model_usage": defaultdict(int),
                "response_times": defaultdict(list),
                "errors": defaultdict(int),
                "cache_hits": defaultdict(int),
                "cache_misses": defaultdict(int),
            }
