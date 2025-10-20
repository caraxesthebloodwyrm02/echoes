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

"""
DataIntegrationUnit - Handles smart web search, community scraping, and dataset aggregation
"""

import asyncio
from datetime import datetime
from typing import Any, Dict


class DataSource:
    """Represents a data source with its configuration"""

    def __init__(self, name: str, source_type: str, config: Dict[str, Any]):
        self.name = name
        self.source_type = source_type
        self.config = config
        self.last_accessed = None
        self.success_rate = 1.0


class DataIntegrationUnit:
    """Handles external data acquisition and integration"""

    def __init__(self):
        self.data_sources = {
            "huggingface": DataSource(
                "HuggingFace Hub",
                "api",
                {"base_url": "https://huggingface.co/api", "rate_limit": 100},
            ),
            "reddit": DataSource(
                "Reddit",
                "community",
                {"base_url": "https://reddit.com/r/", "rate_limit": 60},
            ),
            "github": DataSource(
                "GitHub",
                "repository",
                {"base_url": "https://api.github.com", "rate_limit": 5000},
            ),
            "arxiv": DataSource(
                "ArXiv",
                "academic",
                {"base_url": "http://export.arxiv.org/api/query", "rate_limit": 3},
            ),
        }

        self.search_strategies = {
            "technical": ["github", "huggingface", "arxiv"],
            "community": ["reddit", "github"],
            "academic": ["arxiv", "huggingface"],
            "general": ["reddit", "github"],
        }

    async def gather_data(self, query: str, context: Dict[str, Any], mode: str = "technical") -> Dict[str, Any]:
        """
        Gather relevant data from multiple sources

        Args:
            query: Search query
            context: Context information
            mode: Search mode (technical, community, academic, general)

        Returns:
            Aggregated data from multiple sources
        """
        sources_to_use = self.search_strategies.get(mode, ["github", "reddit"])

        # Prepare search tasks
        search_tasks = []
        for source_name in sources_to_use:
            if source_name in self.data_sources:
                task = self._search_source(source_name, query, context)
                search_tasks.append(task)

        # Execute searches concurrently
        results = await asyncio.gather(*search_tasks, return_exceptions=True)

        # Aggregate results
        aggregated_data = {
            "query": query,
            "mode": mode,
            "timestamp": datetime.now().isoformat(),
            "sources": {},
            "summary": {
                "total_results": 0,
                "successful_sources": 0,
                "failed_sources": 0,
            },
        }

        for i, result in enumerate(results):
            source_name = sources_to_use[i]
            if isinstance(result, Exception):
                aggregated_data["sources"][source_name] = {
                    "status": "error",
                    "error": str(result),
                    "data": [],
                }
                aggregated_data["summary"]["failed_sources"] += 1
            else:
                aggregated_data["sources"][source_name] = result
                aggregated_data["summary"]["total_results"] += len(result.get("data", []))
                aggregated_data["summary"]["successful_sources"] += 1

        return aggregated_data

    async def _search_source(self, source_name: str, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Search a specific data source"""
        source = self.data_sources[source_name]

        # Update last accessed
        source.last_accessed = datetime.now()

        # Simulate API calls (in real implementation, would make actual HTTP requests)
        if source_name == "github":
            return await self._search_github(query, context)
        elif source_name == "huggingface":
            return await self._search_huggingface(query, context)
        elif source_name == "reddit":
            return await self._search_reddit(query, context)
        elif source_name == "arxiv":
            return await self._search_arxiv(query, context)
        else:
            return {"status": "unsupported", "data": []}

    async def _search_github(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Search GitHub repositories and code"""
        # Simulate GitHub API search
        await asyncio.sleep(0.1)  # Simulate network delay

        # Extract programming language from context
        language = self._extract_language_from_context(context)

        # Mock results based on query
        mock_results = [
            {
                "type": "repository",
                "name": f"awesome-{query.replace(' ', '-')}",
                "description": f"A curated list of {query} resources",
                "stars": 1250,
                "language": language,
                "url": f"https://github.com/awesome/{query.replace(' ', '-')}",
                "relevance_score": 0.9,
            },
            {
                "type": "code",
                "file": f"{query.replace(' ', '_')}.py",
                "repository": f"example/{query.replace(' ', '-')}-toolkit",
                "snippet": f"# Example implementation of {query}\ndef main():\n    pass",
                "url": f"https://github.com/example/{query.replace(' ', '-')}-toolkit",
                "relevance_score": 0.8,
            },
        ]

        return {
            "status": "success",
            "source": "github",
            "data": mock_results,
            "metadata": {
                "query": query,
                "language_filter": language,
                "total_found": len(mock_results),
            },
        }

    async def _search_huggingface(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Search HuggingFace models and datasets"""
        await asyncio.sleep(0.1)

        mock_results = [
            {
                "type": "model",
                "name": f"{query.replace(' ', '-')}-base",
                "description": f"Pre-trained model for {query} tasks",
                "downloads": 50000,
                "task": self._infer_ml_task(query),
                "url": f"https://huggingface.co/models/{query.replace(' ', '-')}-base",
                "relevance_score": 0.85,
            },
            {
                "type": "dataset",
                "name": f"{query.replace(' ', '-')}-dataset",
                "description": f"Dataset for {query} research",
                "size": "10GB",
                "url": f"https://huggingface.co/datasets/{query.replace(' ', '-')}-dataset",
                "relevance_score": 0.75,
            },
        ]

        return {
            "status": "success",
            "source": "huggingface",
            "data": mock_results,
            "metadata": {"query": query, "inferred_task": self._infer_ml_task(query)},
        }

    def _extract_language_from_context(self, context: Dict[str, Any]) -> str:
        """Extract programming language from context"""
        if "current_file" in context:
            file_path = context["current_file"]
            if file_path:
                ext = file_path.split(".")[-1].lower()
                lang_map = {
                    "py": "Python",
                    "js": "JavaScript",
                    "ts": "TypeScript",
                    "java": "Java",
                    "cpp": "C++",
                    "c": "C",
                    "go": "Go",
                    "rs": "Rust",
                }
                return lang_map.get(ext, "Python")

        return "Python"  # Default

    def _infer_ml_task(self, query: str) -> str:
        """Infer ML task type from query"""
        query_lower = query.lower()

        if any(word in query_lower for word in ["classify", "classification", "categorize"]):
            return "classification"
        elif any(word in query_lower for word in ["generate", "generation", "create"]):
            return "generation"
        elif any(word in query_lower for word in ["translate", "translation"]):
            return "translation"
        elif any(word in query_lower for word in ["summarize", "summary"]):
            return "summarization"
        else:
            return "general"
