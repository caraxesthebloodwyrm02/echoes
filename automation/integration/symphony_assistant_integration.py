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
Assistant API Integration with Symphony Components
Provides credit-efficient OpenAI assistance integration
"""

import asyncio
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx

from melody_structure.master_channel import MasterChannel


class SymphonyAssistantClient:
    """Credit-efficient OpenAI assistance client for Symphony ecosystem"""

    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url.rstrip("/")
        self.client = httpx.AsyncClient(timeout=30.0)
        self.cache_dir = Path("automation/cache/assistant")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    def _cache_key(self, prompt: str, **kwargs) -> str:
        """Generate cache key for request"""
        content = f"{prompt}|{json.dumps(kwargs, sort_keys=True)}"
        return hashlib.md5(content.encode()).hexdigest()

    def _load_cache(self, key: str) -> Optional[Dict[str, Any]]:
        """Load cached response"""
        cache_file = self.cache_dir / f"{key}.json"
        if cache_file.exists():
            try:
                with open(cache_file, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return None
        return None

    def _save_cache(self, key: str, response: Dict[str, Any]):
        """Save response to cache"""
        cache_file = self.cache_dir / f"{key}.json"
        try:
            with open(cache_file, "w") as f:
                json.dump(response, f, indent=2)
        except IOError:
            pass  # Cache write failures are non-critical

    async def query_with_cache(
        self, prompt: str, use_cache: bool = True, **kwargs
    ) -> Dict[str, Any]:
        """Query assistant with intelligent caching"""
        cache_key = self._cache_key(prompt, **kwargs)

        # Check cache first
        if use_cache:
            cached = self._load_cache(cache_key)
            if cached:
                return {"cached": True, **cached}

        # Make API call
        try:
            response = await self.client.post(
                f"{self.base_url}/assistant/query",
                json={
                    "prompt": prompt,
                    "temperature": kwargs.get("temperature", 0.2),
                    "max_tokens": kwargs.get("max_tokens", 512),
                    "metadata": kwargs.get("metadata", {}),
                },
            )
            response.raise_for_status()
            result = response.json()
            result["cached"] = False

            # Cache successful responses
            if use_cache and response.status_code == 200:
                self._save_cache(cache_key, result)

            return result

        except httpx.RequestError as e:
            return {
                "error": f"Request failed: {str(e)}",
                "cached": False,
                "fallback": self._generate_fallback_response(prompt),
            }

    def _generate_fallback_response(self, prompt: str) -> str:
        """Generate fallback response when API is unavailable"""
        # Simple pattern-based responses for common queries
        prompt_lower = prompt.lower()

        if "complexity" in prompt_lower:
            return "Based on code analysis, complexity metrics show areas for potential refactoring. Consider breaking down large functions and improving separation of concerns."
        elif "security" in prompt_lower:
            return "Security scan completed. Review identified vulnerabilities and implement recommended fixes. Focus on input validation and secure coding practices."
        elif "performance" in prompt_lower:
            return "Performance analysis suggests optimization opportunities. Consider caching frequently accessed data and optimizing database queries."
        elif "test" in prompt_lower:
            return "Testing coverage is below target thresholds. Prioritize adding unit tests for critical paths and edge cases."
        else:
            return "I'm currently operating in offline mode. Please check your OpenAI API connection and try again. Local analysis capabilities remain available."

    async def get_models(self) -> List[str]:
        """Get available models (cached for efficiency)"""
        try:
            response = await self.client.get(f"{self.base_url}/assistant/models")
            response.raise_for_status()
            return response.json().get("models", [])
        except Exception:
            return ["gpt-4o-mini", "gpt-4o"]  # Fallback defaults


class CreditEfficientPatterns:
    """Patterns for using OpenAI assistance without excessive credits"""

    @staticmethod
    def batch_similar_queries(queries: List[str]) -> str:
        """Batch similar queries to reduce API calls"""
        if len(queries) <= 1:
            return queries[0] if queries else ""

        # Combine into single comprehensive query
        combined = "Please analyze the following related aspects:\n\n"
        for i, query in enumerate(queries, 1):
            combined += f"{i}. {query}\n"

        combined += "\nProvide integrated analysis addressing all points."
        return combined

    @staticmethod
    def create_contextual_templates() -> Dict[str, str]:
        """Pre-defined templates for common Symphony scenarios"""
        return {
            "code_review": "Review this code for quality, security, and best practices: {code}",
            "architecture_feedback": "Analyze this system architecture design: {design}\nProvide improvement suggestions.",
            "testing_strategy": "Recommend testing strategy for: {component}\nFocus on coverage and critical paths.",
            "performance_analysis": "Analyze performance bottlenecks in: {code}\nSuggest optimizations.",
            "security_assessment": "Perform security assessment on: {component}\nIdentify vulnerabilities and fixes.",
        }

    @staticmethod
    def intelligent_caching_strategy(query: str) -> bool:
        """Determine if query should be cached aggressively"""
        # Cache queries that are likely to be repeated
        cache_indicators = [
            "review",
            "analyze",
            "assess",
            "evaluate",
            "best practices",
            "recommendations",
            "guidance",
        ]

        return any(indicator in query.lower() for indicator in cache_indicators)


class MasterChannelIntegration:
    """Integration layer for assistant API with master channel"""

    def __init__(self):
        self.master = MasterChannel()
        self.assistant = SymphonyAssistantClient()

    async def assisted_compress_and_glue(self, input_data: dict) -> dict:
        """Compress and glue with AI assistance"""
        # Standard processing
        compressed = self.master.compress_and_glue(input_data)

        # Get AI insights for optimization
        optimization_prompt = f"""
        Analyze this compressed data structure for optimization opportunities:
        {json.dumps(compressed, indent=2)}

        Suggest improvements for data flow, error handling, or performance.
        """

        try:
            insights = await self.assistant.query_with_cache(
                optimization_prompt, use_cache=True, temperature=0.3, max_tokens=256
            )

            if "content" in insights:
                compressed["ai_optimization_insights"] = insights["content"]
                compressed["ai_cached"] = insights.get("cached", False)

        except Exception as e:
            compressed["ai_error"] = str(e)

        return compressed

    async def assisted_finalize(self, master_data: dict) -> str:
        """Finalize with AI-powered summary and recommendations"""
        # Standard finalization
        result = self.master.finalize(master_data)

        # Enhance with AI insights
        summary_prompt = f"""
        Provide executive summary and actionable recommendations for this Symphony operation:

        Operation Result: {result}

        Focus on key outcomes, potential improvements, and next steps.
        """

        try:
            summary = await self.assistant.query_with_cache(
                summary_prompt, use_cache=True, temperature=0.2, max_tokens=384
            )

            if "content" in summary:
                enhanced_result = (
                    f"{result}\n\n--- AI-Enhanced Analysis ---\n{summary['content']}"
                )
                if summary.get("cached"):
                    enhanced_result += "\n[Analysis from cache]"
                return enhanced_result

        except Exception as e:
            result += f"\n\n[AI Analysis unavailable: {str(e)}]"

        return result


# Example usage patterns
async def demo_credit_efficient_usage():
    """Demonstrate credit-efficient assistant integration"""

    async with SymphonyAssistantClient() as assistant:
        # 1. Batch related queries
        queries = [
            "How can I improve code quality in the knowledge graph system?",
            "What are best practices for RDF data modeling?",
            "How should I handle ontology validation errors?",
        ]

        batched_query = CreditEfficientPatterns.batch_similar_queries(queries)
        response = await assistant.query_with_cache(batched_query, use_cache=True)
        print(f"Batched analysis: {len(response.get('content', ''))} characters")

        # 2. Use templates for common scenarios
        templates = CreditEfficientPatterns.create_contextual_templates()

        code_sample = "def process_data(data): return [x*2 for x in data if x > 0]"
        review_query = templates["code_review"].format(code=code_sample)

        review = await assistant.query_with_cache(review_query, use_cache=True)
        print(f"Code review: {review.get('cached', False) and 'Cached' or 'Fresh'}")

        # 3. Master channel integration
        integrator = MasterChannelIntegration()

        test_data = {"component": "assistant_api", "status": "integration_test"}
        compressed = await integrator.assisted_compress_and_glue(test_data)
        final = await integrator.assisted_finalize({"compressed_data": compressed})

        print(f"Enhanced finalization: {len(final)} characters")

        return {
            "batched_response_length": len(response.get("content", "")),
            "review_cached": review.get("cached", False),
            "finalization_length": len(final),
            "compression_keys": list(compressed.keys()),
        }


if __name__ == "__main__":
    # Run demo
    result = asyncio.run(demo_credit_efficient_usage())
    print("Credit-efficient integration demo completed:", result)
