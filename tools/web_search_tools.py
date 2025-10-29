"""
Web Search Tools for EchoesAssistantV2

Provides web search capabilities using various search APIs.
Implements OpenAI function calling compatible tools.
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
from urllib.parse import quote, urlencode
import requests
from datetime import datetime

from .base import BaseTool, ToolResult

logger = logging.getLogger(__name__)


class WebSearchTool(BaseTool):
    """
    Web search tool that uses multiple search APIs.
    Provides real-time web search capabilities.
    """
    
    def __init__(self, search_provider: str = "duckduckgo"):
        """
        Initialize web search tool.
        
        Args:
            search_provider: Search provider to use ("duckduckgo", "brave", "google_custom")
        """
        self.search_provider = search_provider
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # API keys for different providers
        self.brave_api_key = os.getenv("BRAVE_SEARCH_API_KEY")
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.google_search_engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID")
    
    @property
    def name(self) -> str:
        return "web_search"
    
    @property
    def description(self) -> str:
        return "Search the web for real-time information. Supports general web search, news, and academic queries."
    
    def to_openai_schema(self) -> Dict[str, Any]:
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
                            "description": "Search query - what you want to find on the web"
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "Maximum number of results to return (default: 5)",
                            "default": 5,
                            "minimum": 1,
                            "maximum": 10
                        },
                        "search_type": {
                            "type": "string",
                            "description": "Type of search to perform",
                            "enum": ["general", "news", "academic"],
                            "default": "general"
                        },
                        "safe_search": {
                            "type": "string",
                            "description": "Filter level for search results",
                            "enum": ["off", "moderate", "strict"],
                            "default": "moderate"
                        }
                    },
                    "required": ["query"]
                }
            }
        }
    
    def __call__(self, query: str, max_results: int = 5, search_type: str = "general", safe_search: str = "moderate") -> ToolResult:
        """
        Perform web search.
        
        Args:
            query: Search query
            max_results: Maximum number of results
            search_type: Type of search
            safe_search: Safe search level
            
        Returns:
            ToolResult with search results
        """
        try:
            # Choose search method based on provider and availability
            if self.search_provider == "brave" and self.brave_api_key:
                results = self._search_brave(query, max_results)
            elif self.search_provider == "google_custom" and self.google_api_key and self.google_search_engine_id:
                results = self._search_google_custom(query, max_results)
            else:
                # Default to DuckDuckGo (no API key required)
                results = self._search_duckduckgo(query, max_results)
            
            # Format results
            formatted_results = []
            for result in results[:max_results]:
                formatted_results.append({
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "snippet": result.get("snippet", ""),
                    "published_date": result.get("published_date"),
                    "source": result.get("source", "Unknown")
                })
            
            return ToolResult(
                success=True,
                data={
                    "query": query,
                    "search_type": search_type,
                    "results": formatted_results,
                    "total_results": len(formatted_results),
                    "search_time": datetime.now().isoformat()
                },
                error=None
            )
            
        except Exception as e:
            logger.error(f"Web search error: {str(e)}")
            return ToolResult(
                success=False,
                data=None,
                error=f"Web search failed: {str(e)}"
            )
    
    def _search_duckduckgo(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Search using DuckDuckGo Instant Answer API."""
        try:
            url = "https://api.duckduckgo.com/"
            params = {
                "q": query,
                "format": "json",
                "no_html": 1,
                "skip_disambig": 1
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            results = []
            
            # Add instant answer if available
            if data.get("AbstractText"):
                results.append({
                    "title": data.get("Heading", query),
                    "url": data.get("AbstractURL", ""),
                    "snippet": data.get("AbstractText", ""),
                    "source": "DuckDuckGo"
                })
            
            # Add related topics
            for topic in data.get("RelatedTopics", [])[:max_results-1]:
                if "Text" in topic and "FirstURL" in topic:
                    results.append({
                        "title": topic.get("Text", "").split(" - ")[0],
                        "url": topic.get("FirstURL", ""),
                        "snippet": topic.get("Text", ""),
                        "source": "DuckDuckGo"
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"DuckDuckGo search error: {str(e)}")
            return []
    
    def _search_brave(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Search using Brave Search API."""
        try:
            url = "https://api.search.brave.com/res/v1/web/search"
            headers = {
                "Accept": "application/json",
                "Accept-Encoding": "gzip",
                "X-Subscription-Token": self.brave_api_key
            }
            params = {
                "q": query,
                "count": max_results,
                "safesearch": "moderate"
            }
            
            response = self.session.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            results = []
            for item in data.get("web", {}).get("results", []):
                results.append({
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "snippet": item.get("description", ""),
                    "published_date": None,
                    "source": "Brave Search"
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Brave search error: {str(e)}")
            return []
    
    def _search_google_custom(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Search using Google Custom Search API."""
        try:
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                "key": self.google_api_key,
                "cx": self.google_search_engine_id,
                "q": query,
                "num": min(max_results, 10)  # Google API limit
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            results = []
            for item in data.get("items", []):
                results.append({
                    "title": item.get("title", ""),
                    "url": item.get("link", ""),
                    "snippet": item.get("snippet", ""),
                    "published_date": None,
                    "source": "Google Search"
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Google Custom Search error: {str(e)}")
            return []


class WebPageContentTool(BaseTool):
    """
    Tool to fetch and extract content from web pages.
    """
    
    def __init__(self):
        """Initialize the web page content tool."""
        super().__init__(
            name="get_web_page_content",
            description="Fetch and extract the main content from a web page URL"
        )
    
    def to_openai_schema(self) -> Dict[str, Any]:
        """Generate OpenAI function calling schema."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "URL of the web page to fetch"
                        },
                        "max_length": {
                            "type": "integer",
                            "description": "Maximum length of content to return (default: 5000)",
                            "default": 5000,
                            "minimum": 100,
                            "maximum": 20000
                        }
                    },
                    "required": ["url"]
                }
            }
        }
    
    def __call__(self, url: str, max_length: int = 5000) -> ToolResult:
        """
        Fetch content from a web page.
        
        Args:
            url: URL to fetch
            max_length: Maximum content length
            
        Returns:
            ToolResult with page content
        """
        try:
            # Basic validation
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            # Fetch the page
            response = requests.get(url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            response.raise_for_status()
            
            # Extract text content (basic implementation)
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text
            text = soup.get_text()
            
            # Clean up text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            # Truncate if necessary
            if len(text) > max_length:
                text = text[:max_length] + "... [truncated]"
            
            # Extract metadata
            title = soup.title.string if soup.title else "No title"
            meta_description = soup.find('meta', attrs={'name': 'description'})
            description = meta_description.get('content', '') if meta_description else ''
            
            return ToolResult(
                success=True,
                data={
                    "url": url,
                    "title": title,
                    "description": description,
                    "content": text,
                    "content_length": len(text),
                    "fetched_at": datetime.now().isoformat()
                },
                error=None
            )
            
        except ImportError:
            return ToolResult(
                success=False,
                data=None,
                error="BeautifulSoup not installed. Install with: pip install beautifulsoup4"
            )
        except Exception as e:
            logger.error(f"Web page fetch error: {str(e)}")
            return ToolResult(
                success=False,
                data=None,
                error=f"Failed to fetch web page: {str(e)}"
            )


def create_web_search_tools() -> List[BaseTool]:
    """
    Create and return web search tools.
    
    Returns:
        List of web search tool instances
    """
    tools = []
    
    # Add web search tool
    search_provider = os.getenv("SEARCH_PROVIDER", "duckduckgo")
    tools.append(WebSearchTool(search_provider=search_provider))
    
    # Add web page content tool
    tools.append(WebPageContentTool())
    
    return tools
