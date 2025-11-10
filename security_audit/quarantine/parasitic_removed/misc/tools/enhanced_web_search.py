"""
Enhanced Web Search Tools for EchoesAssistantV2

Provides more reliable web search capabilities using multiple approaches.
"""

import logging
import os
from datetime import datetime
from typing import Any

import requests

from .base import BaseTool, ToolResult

logger = logging.getLogger(__name__)


class EnhancedWebSearchTool(BaseTool):
    """
    Enhanced web search tool with multiple fallback methods.
    """

    def __init__(self):
        """Initialize the enhanced web search tool."""
        super().__init__(
            name="web_search",
            description="Search the web for real-time information using multiple search providers",
        )
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
        )

        # API keys for premium providers
        self.brave_api_key = os.getenv("BRAVE_SEARCH_API_KEY")
        self.serper_api_key = os.getenv("SERPER_API_KEY")  # Google search via Serper
        self.tavily_api_key = os.getenv("TAVILY_API_KEY")  # Alternative search API

    def to_openai_schema(self) -> dict[str, Any]:
        """Generate OpenAI function calling schema."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query - what you want to find on the web",
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "Maximum number of results to return (default: 5)",
                            "default": 5,
                            "minimum": 1,
                            "maximum": 10,
                        },
                    },
                    "required": ["query"],
                },
            },
        }

    def __call__(self, query: str, max_results: int = 5) -> ToolResult:
        """
        Perform web search with multiple fallback methods.

        Args:
            query: Search query
            max_results: Maximum number of results

        Returns:
            ToolResult with search results
        """
        try:
            # Try different search methods in order of preference
            results = []

            # 1. Try Tavily API (most reliable)
            if self.tavily_api_key:
                results = self._search_tavily(query, max_results)
                if results:
                    logger.info("Used Tavily API for search")

            # 2. Try Serper API (Google search)
            if not results and self.serper_api_key:
                results = self._search_serper(query, max_results)
                if results:
                    logger.info("Used Serper API for search")

            # 3. Try Brave Search API
            if not results and self.brave_api_key:
                results = self._search_brave(query, max_results)
                if results:
                    logger.info("Used Brave API for search")

            # 4. Fallback to DuckDuckGo HTML scraping
            if not results:
                results = self._search_duckduckgo_html(query, max_results)
                if results:
                    logger.info("Used DuckDuckGo HTML scraping for search")

            # 5. Last resort - simulated results for testing
            if not results:
                results = self._get_simulated_results(query, max_results)
                logger.warning("Used simulated results for testing")

            # Format results
            formatted_results = []
            for result in results[:max_results]:
                formatted_results.append(
                    {
                        "title": result.get("title", ""),
                        "url": result.get("url", ""),
                        "snippet": result.get("snippet", ""),
                        "source": result.get("source", "Unknown"),
                    }
                )

            return ToolResult(
                success=True,
                data={
                    "query": query,
                    "results": formatted_results,
                    "total_results": len(formatted_results),
                    "search_time": datetime.now().isoformat(),
                },
                error=None,
            )

        except Exception as e:
            logger.error(f"Web search error: {str(e)}")
            return ToolResult(
                success=False, data=None, error=f"Web search failed: {str(e)}"
            )

    def _search_tavily(self, query: str, max_results: int) -> list[dict[str, Any]]:
        """Search using Tavily API."""
        try:
            url = "https://api.tavily.com/search"
            payload = {
                "api_key": self.tavily_api_key,
                "query": query,
                "search_depth": "basic",
                "include_answer": False,
                "include_raw_content": False,
                "max_results": max_results,
            }

            response = self.session.post(url, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()

            results = []
            for item in data.get("results", []):
                results.append(
                    {
                        "title": item.get("title", ""),
                        "url": item.get("url", ""),
                        "snippet": item.get("content", ""),
                        "source": "Tavily",
                    }
                )

            return results

        except Exception as e:
            logger.error(f"Tavily search error: {str(e)}")
            return []

    def _search_serper(self, query: str, max_results: int) -> list[dict[str, Any]]:
        """Search using Serper API (Google search)."""
        try:
            url = "https://google.serper.dev/search"
            payload = {"q": query, "num": max_results}

            headers = {
                "X-API-KEY": self.serper_api_key,
                "Content-Type": "application/json",
            }

            response = self.session.post(url, headers=headers, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()

            results = []
            for item in data.get("organic", []):
                results.append(
                    {
                        "title": item.get("title", ""),
                        "url": item.get("link", ""),
                        "snippet": item.get("snippet", ""),
                        "source": "Google (Serper)",
                    }
                )

            return results

        except Exception as e:
            logger.error(f"Serper search error: {str(e)}")
            return []

    def _search_brave(self, query: str, max_results: int) -> list[dict[str, Any]]:
        """Search using Brave Search API."""
        try:
            url = "https://api.search.brave.com/res/v1/web/search"
            headers = {
                "Accept": "application/json",
                "X-Subscription-Token": self.brave_api_key,
            }
            params = {"q": query, "count": max_results}

            response = self.session.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            results = []
            for item in data.get("web", {}).get("results", []):
                results.append(
                    {
                        "title": item.get("title", ""),
                        "url": item.get("url", ""),
                        "snippet": item.get("description", ""),
                        "source": "Brave Search",
                    }
                )

            return results

        except Exception as e:
            logger.error(f"Brave search error: {str(e)}")
            return []

    def _search_duckduckgo_html(
        self, query: str, max_results: int
    ) -> list[dict[str, Any]]:
        """Search using DuckDuckGo HTML scraping (fallback method)."""
        try:
            # Use DuckDuckGo's HTML version
            url = "https://html.duckduckgo.com/html/"
            params = {"q": query, "kl": "us-en"}

            response = self.session.post(url, data=params, timeout=10)
            response.raise_for_status()

            # Parse HTML results
            import re

            html = response.text

            # Extract results using regex
            results = []

            # Find result blocks
            result_pattern = r'<a rel="nofollow" class="result__a" href="([^"]+)">([^<]+)</a>.*?<a[^>]*class="result__a"[^>]*>([^<]+)</a>'
            matches = re.findall(result_pattern, html, re.DOTALL)

            for match in matches[:max_results]:
                url, title, snippet = match
                # Clean up the results
                title = re.sub(r"<[^>]+>", "", title).strip()
                snippet = re.sub(r"<[^>]+>", "", snippet).strip()

                if title and url:
                    results.append(
                        {
                            "title": title,
                            "url": url,
                            "snippet": snippet[:200] + "..."
                            if len(snippet) > 200
                            else snippet,
                            "source": "DuckDuckGo",
                        }
                    )

            return results

        except Exception as e:
            logger.error(f"DuckDuckGo HTML search error: {str(e)}")
            return []

    def _get_simulated_results(
        self, query: str, max_results: int
    ) -> list[dict[str, Any]]:
        """Get simulated results for testing when no search methods work."""
        logger.warning("Using simulated search results - no search API available")

        # Create relevant simulated results based on query
        simulated = [
            {
                "title": f"Search results for: {query}",
                "url": "https://example.com/search-info",
                "snippet": f"This is a simulated result for the query '{query}'. To get real search results, configure a search API key (TAVILY_API_KEY, SERPER_API_KEY, or BRAVE_SEARCH_API_KEY).",
                "source": "Simulated",
            },
            {
                "title": "OpenAI API Documentation",
                "url": "https://platform.openai.com/docs",
                "snippet": "Official documentation for OpenAI's API, including function calling and tool use capabilities.",
                "source": "Simulated",
            },
            {
                "title": "Configuring Search APIs",
                "url": "https://example.com/search-config",
                "snippet": "Learn how to configure search API keys for real-time web search capabilities. Supported providers: Tavily, Serper (Google), Brave Search.",
                "source": "Simulated",
            },
        ]

        return simulated[:max_results]


def create_enhanced_web_search_tools() -> list[BaseTool]:
    """Create enhanced web search tools."""
    return [EnhancedWebSearchTool()]
