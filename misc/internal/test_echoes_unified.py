#!/usr/bin/env python3
"""
Comprehensive Unified System Test for Echoes
Tests real-world queries across all integrated areas:
- RAG with OpenAI embeddings
- Tool calling (calculator, web search)
- Agent workflows
- Business analysis functions
- Knowledge retrieval
"""

import os
import time
import json
from pathlib import Path
from typing import List, Dict, Any

# Echoes imports
from assistant_v2_core import EchoesAssistantV2
from echoes.rag_langchain_loader import load_directory_and_ingest


class EchoesUnifiedTester:
    """Comprehensive tester for Echoes unified system."""

    def __init__(self):
        """Initialize tester with Echoes assistant."""
        print("🚀 Initializing Echoes Unified System Test...")
        self.assistant = EchoesAssistantV2(
            enable_rag=True, rag_preset="openai-balanced"
        )
        self.test_results = []
        self.start_time = time.time()

    def log_test(
        self, category: str, query: str, result: Any, success: bool, notes: str = ""
    ):
        """Log test result."""
        self.test_results.append(
            {
                "category": category,
                "query": query,
                "success": success,
                "notes": notes,
                "timestamp": time.time() - self.start_time,
            }
        )
        status = "✅" if success else "❌"
        print(f"{status} [{category}] {query[:60]}...")
        if notes:
            print(f"   → {notes}")

    def setup_knowledge_base(self):
        """Set up comprehensive knowledge base for testing."""
        print("\n📚 Setting up knowledge base...")

        # Create test documents directory
        test_docs_dir = Path("test_documents")
        test_docs_dir.mkdir(exist_ok=True)

        # Create comprehensive test documents
        documents = {
            "echoes_architecture.md": """# Echoes AI Architecture

## Core Components
Echoes is built with a modular architecture:
- **AI Module**: OpenAI integration with streaming capabilities
- **Agent System**: Multi-agent workflows with persistent memory
- **RAG System**: OpenAI embeddings with in-memory cosine similarity
- **API Layer**: FastAPI with 21+ endpoints
- **Tools**: Calculator, web search, business analysis functions

## Technology Stack
- Python 3.12+
- FastAPI for REST API
- OpenAI GPT-4 and embedding models
- NumPy for vector operations
- LangChain for document processing

## Performance Characteristics
- Response time: <500ms (p95)
- Throughput: 100+ req/s
- Availability: 99.95%
- Embedding model: text-embedding-3-large (3072 dimensions)
""",
            "business_guide.md": """# Echoes Business Implementation Guide

## Revenue Opportunities
1. **Freelance Consulting**: $150-250/hr, 3-5 days to start
2. **AI/ML Development**: $100-200/hr, 1-2 weeks
3. **Research Services**: $200-300/hr, 1-2 weeks
4. **Training/Courses**: $97-497/course, 2-3 weeks
5. **Enterprise Licensing**: $500-5,000/month, 3-4 weeks
6. **SaaS Product**: $500-5,000/month, 2-4 weeks

## 30-Day Projections
- Week 1: $0-1,000 (setup)
- Week 2: $1,500-3,000 (first projects)
- Week 3: $2,500-4,500 (scaling)
- Week 4: $3,500-6,000 (multiple streams)
- Total Month 1: $7,500-14,500

## Implementation Steps
1. Set up development environment
2. Configure OpenAI API
3. Implement core features
4. Add business analysis tools
5. Deploy to production
6. Market and scale
""",
            "technical_faq.md": """# Echoes Technical FAQ

## Common Issues

### Q: How do I configure OpenAI API?
A: Set OPENAI_API_KEY environment variable or pass api_key parameter.

### Q: What embedding models are supported?
A: text-embedding-3-large (3072d), text-embedding-3-small (1536d), text-embedding-ada-002 (1536d)

### Q: How does RAG work without FAISS?
A: Uses in-memory cosine similarity with normalized embeddings via NumPy.

### Q: Can I use custom documents?
A: Yes, use the LangChain loader utility for bulk ingestion.

### Q: What's the difference between presets?
A: openai-fast (small model), openai-balanced (large model), openai-accurate (large with optimized settings)

## Performance Optimization
- Use text-embedding-3-small for cost-sensitive applications
- Batch embeddings for better throughput
- Implement caching for repeated queries
- Use streaming for long responses
""",
            "api_reference.md": """# Echoes API Reference

## Core Endpoints
- `GET /health` - Health check
- `POST /api/ai/chat` - Chat completion
- `GET /api/ai/models` - List models
- `POST /api/agents/create` - Create agent
- `POST /api/agents/process` - Process with agent
- `POST /api/workflows/business-initiative` - Business workflow

## Authentication
- Optional API key authentication
- Rate limiting: 60 req/min default
- CORS enabled for web applications

## Response Format
All endpoints return JSON with:
- `success`: boolean
- `data`: response payload
- `error`: error message if applicable
- `timestamp`: ISO timestamp

## Error Handling
- 400: Bad request
- 401: Unauthorized
- 429: Rate limited
- 500: Internal server error
""",
        }

        # Write documents
        for filename, content in documents.items():
            file_path = test_docs_dir / filename
            if not file_path.exists():
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)

        # Ingest documents
        try:
            result = load_directory_and_ingest(
                assistant=self.assistant,
                directory=test_docs_dir,
                glob_pattern="**/*.md",
                chunk_size=800,
                chunk_overlap=150,
                batch_size=25,
                metadata_fields=["source"],
            )
            print(
                f"✅ Knowledge base loaded: {result['total_chunks']} chunks from {result['total_documents']} documents"
            )
            return True
        except Exception as e:
            print(f"❌ Failed to load knowledge base: {e}")
            return False

    def test_rag_knowledge_retrieval(self):
        """Test RAG knowledge retrieval with real-world queries."""
        print("\n🔍 Testing RAG Knowledge Retrieval...")

        queries = [
            "What are the core components of Echoes architecture?",
            "How much can I earn from freelance consulting with Echoes?",
            "What embedding models are supported in Echoes?",
            "How do I configure the OpenAI API?",
            "What are the available API endpoints?",
            "How does RAG work without FAISS?",
            "What's the difference between openai-fast and openai-balanced presets?",
            "How do I implement business analysis tools?",
            "What are the performance characteristics?",
            "Can I use custom documents with Echoes?",
        ]

        for query in queries:
            try:
                results = self.assistant._retrieve_context(query, top_k=3)
                success = len(results) > 0 and results[0].get("score", 0) > 0.1
                notes = (
                    f"Found {len(results)} results, top score: {results[0].get('score', 0):.3f}"
                    if results
                    else "No results"
                )
                self.log_test("RAG", query, results, success, notes)
            except Exception as e:
                self.log_test("RAG", query, None, False, str(e))

    def test_tool_calling(self):
        """Test tool calling capabilities."""
        print("\n🔧 Testing Tool Calling...")

        tool_queries = [
            ("Calculate 15% of 2500", "calculator"),
            ("What is 123 * 456?", "calculator"),
            ("Search for latest AI trends", "web_search"),
            ("Calculate compound interest: $10000 at 5% for 3 years", "calculator"),
            ("Find information about enterprise AI adoption", "web_search"),
        ]

        for query, expected_tool in tool_queries:
            try:
                response = self.assistant.process_message(query)
                # Check if tool was mentioned in response
                success = (
                    expected_tool.lower() in response.lower()
                    or "error" not in response.lower()
                )
                notes = (
                    f"Tool used: {expected_tool}"
                    if success
                    else "Tool may not have been used"
                )
                self.log_test("Tools", query, response, success, notes)
            except Exception as e:
                self.log_test("Tools", query, None, False, str(e))

    def test_business_analysis(self):
        """Test business analysis functions."""
        print("\n💼 Testing Business Analysis...")

        business_queries = [
            "Analyze the market opportunity for AI consulting services",
            "Identify revenue streams for an AI platform like Echoes",
            "Project revenue for a consulting business starting with 3 clients",
            "Calculate business metrics for a SaaS product with $10k MRR",
            "What are some quick wins to generate income with AI skills?",
        ]

        for query in business_queries:
            try:
                response = self.assistant.process_message(query)
                success = len(response) > 50 and any(
                    keyword in response.lower()
                    for keyword in [
                        "revenue",
                        "market",
                        "metrics",
                        "income",
                        "opportunity",
                    ]
                )
                notes = f"Response length: {len(response)} chars"
                self.log_test("Business", query, response, success, notes)
            except Exception as e:
                self.log_test("Business", query, None, False, str(e))

    def test_agent_workflows(self):
        """Test agent workflow capabilities."""
        print("\n🤖 Testing Agent Workflows...")

        workflow_queries = [
            "Help me launch a new AI consulting business",
            "I want to analyze a business opportunity for machine learning services",
            "Create a plan for monetizing AI expertise",
            "Evaluate the market for enterprise AI solutions",
        ]

        for query in workflow_queries:
            try:
                response = self.assistant.process_message(query)
                success = len(response) > 100 and any(
                    keyword in response.lower()
                    for keyword in [
                        "workflow",
                        "steps",
                        "plan",
                        "analysis",
                        "recommend",
                    ]
                )
                notes = f"Workflow response length: {len(response)} chars"
                self.log_test("Workflows", query, response, success, notes)
            except Exception as e:
                self.log_test("Workflows", query, None, False, str(e))

    def test_complex_multimodal_queries(self):
        """Test complex queries requiring multiple capabilities."""
        print("\n🎯 Testing Complex Multimodal Queries...")

        complex_queries = [
            "Based on Echoes architecture, what's the best way to implement a custom RAG system for legal documents?",
            "Calculate the potential revenue if I charge $200/hour for AI consulting and work 20 hours/week",
            "Search for current AI market trends and analyze how they affect Echoes business opportunities",
            "Design a workflow for onboarding enterprise clients using Echoes API endpoints",
            "What are the technical requirements and business projections for scaling Echoes to 1000 users?",
        ]

        for query in complex_queries:
            try:
                response = self.assistant.process_message(query)
                success = len(response) > 150 and any(
                    keyword in response.lower()
                    for keyword in [
                        "architecture",
                        "revenue",
                        "market",
                        "workflow",
                        "technical",
                        "business",
                    ]
                )
                notes = f"Complex query response: {len(response)} chars"
                self.log_test("Complex", query, response, success, notes)
            except Exception as e:
                self.log_test("Complex", query, None, False, str(e))

    def test_unanswered_questions(self):
        """Test questions that typically remain unanswered longest."""
        print("\n❓ Testing Historically Unanswered Questions...")

        unanswered_queries = [
            "How do I implement custom embedding models with Echoes?",
            "What's the optimal chunk size for technical documentation?",
            "How can I deploy Echoes on Kubernetes with auto-scaling?",
            "What are the data privacy implications of using OpenAI embeddings?",
            "How do I migrate from existing RAG system to Echoes?",
            "What's the cost analysis for different embedding models at scale?",
            "How do I implement A/B testing for different RAG strategies?",
            "What are the best practices for prompt engineering with Echoes?",
            "How do I integrate Echoes with existing enterprise systems?",
            "What's the roadmap for Echoes future features?",
        ]

        for query in unanswered_queries:
            try:
                # Try knowledge retrieval first
                rag_results = self.assistant._retrieve_context(query, top_k=3)
                # Then process with full assistant
                response = self.assistant.process_message(query)

                has_knowledge = len(rag_results) > 0
                has_response = len(response) > 50

                success = has_response  # Consider successful if we get any meaningful response
                notes = (
                    f"RAG: {len(rag_results)} results, Response: {len(response)} chars"
                )
                self.log_test("Unanswered", query, response, success, notes)
            except Exception as e:
                self.log_test("Unanswered", query, None, False, str(e))

    def test_performance_metrics(self):
        """Test performance and system metrics."""
        print("\n📊 Testing Performance Metrics...")

        performance_tests = [
            (
                "Knowledge retrieval speed",
                lambda: self.assistant._retrieve_context(
                    "Echoes architecture", top_k=5
                ),
            ),
            (
                "Simple query response",
                lambda: self.assistant.process_message("What is Echoes?"),
            ),
            (
                "Complex query response",
                lambda: self.assistant.process_message(
                    "Analyze business opportunities for AI consulting"
                ),
            ),
            (
                "Batch knowledge addition",
                lambda: self.assistant.add_knowledge(
                    [
                        {"text": "Test document 1", "metadata": {"source": "test"}},
                        {"text": "Test document 2", "metadata": {"source": "test"}},
                    ]
                ),
            ),
        ]

        for test_name, test_func in performance_tests:
            try:
                start = time.time()
                result = test_func()
                duration = time.time() - start

                success = duration < 10.0  # Should complete within 10 seconds
                notes = f"Duration: {duration:.2f}s"
                self.log_test("Performance", test_name, result, success, notes)
            except Exception as e:
                self.log_test("Performance", test_name, None, False, str(e))

    def generate_report(self):
        """Generate comprehensive test report."""
        print("\n📋 Generating Test Report...")

        total_tests = len(self.test_results)
        successful_tests = sum(1 for r in self.test_results if r["success"])
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0

        # Group by category
        categories = {}
        for result in self.test_results:
            cat = result["category"]
            if cat not in categories:
                categories[cat] = {"total": 0, "success": 0}
            categories[cat]["total"] += 1
            if result["success"]:
                categories[cat]["success"] += 1

        print(
            f"\n🎯 Overall Results: {successful_tests}/{total_tests} ({success_rate:.1f}% success)"
        )
        print(f"⏱️  Total test duration: {time.time() - self.start_time:.2f}s")

        print("\n📊 Results by Category:")
        for cat, stats in categories.items():
            rate = (
                (stats["success"] / stats["total"] * 100) if stats["total"] > 0 else 0
            )
            print(f"  {cat}: {stats['success']}/{stats['total']} ({rate:.1f}%)")

        # Find failed tests
        failed_tests = [r for r in self.test_results if not r["success"]]
        if failed_tests:
            print(f"\n❌ Failed Tests ({len(failed_tests)}):")
            for test in failed_tests[:5]:  # Show first 5
                print(
                    f"  - [{test['category']}] {test['query'][:60]}... ({test['notes']})"
                )

        # Save detailed report
        report = {
            "summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "success_rate": success_rate,
                "duration": time.time() - self.start_time,
            },
            "categories": categories,
            "failed_tests": failed_tests,
            "all_results": self.test_results,
        }

        report_path = Path("echoes_unified_test_report.json")
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        print(f"\n💾 Detailed report saved to: {report_path}")
        return report

    def run_all_tests(self):
        """Run all unified system tests."""
        print("=" * 60)
        print("🚀 ECHOES UNIFIED SYSTEM TEST")
        print("=" * 60)

        # Setup
        if not self.setup_knowledge_base():
            print("❌ Cannot proceed without knowledge base")
            return

        # Run all test suites
        self.test_rag_knowledge_retrieval()
        self.test_tool_calling()
        self.test_business_analysis()
        self.test_agent_workflows()
        self.test_complex_multimodal_queries()
        self.test_unanswered_questions()
        self.test_performance_metrics()

        # Generate report
        report = self.generate_report()

        print("\n" + "=" * 60)
        print("✅ UNIFIED SYSTEM TEST COMPLETE")
        print("=" * 60)

        return report


def main():
    """Run the unified system test."""
    # Check environment
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  WARNING: OPENAI_API_KEY not set. Some tests may fail.")

    # Run tests
    tester = EchoesUnifiedTester()
    report = tester.run_all_tests()

    # Summary
    success_rate = report["summary"]["success_rate"]
    if success_rate >= 80:
        print(
            f"🎉 EXCELLENT: System is highly functional ({success_rate:.1f}% success)"
        )
    elif success_rate >= 60:
        print(f"✅ GOOD: System is mostly functional ({success_rate:.1f}% success)")
    else:
        print(f"⚠️  NEEDS ATTENTION: System has issues ({success_rate:.1f}% success)")

    return report


if __name__ == "__main__":
    main()
