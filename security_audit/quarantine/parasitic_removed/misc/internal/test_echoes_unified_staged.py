#!/usr/bin/env python3
"""
Staged Unified System Test for Echoes
Runs tests in stages with clear progress indicators.
"""

import json
import os
import time
from pathlib import Path

# Echoes imports
from assistant_v2_core import EchoesAssistantV2


def test_stage_1_initialization():
    """Stage 1: Test system initialization."""
    print("\n" + "=" * 60)
    print("🚀 STAGE 1: SYSTEM INITIALIZATION")
    print("=" * 60)

    try:
        assistant = EchoesAssistantV2(enable_rag=True, rag_preset="openai-balanced")
        print("✅ Echoes Assistant initialized successfully")
        print("   RAG preset: openai-balanced")
        print(f"   RAG enabled: {assistant.rag is not None}")
        return assistant, True
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        return None, False


def test_stage_2_knowledge_setup(assistant):
    """Stage 2: Set up knowledge base."""
    print("\n" + "=" * 60)
    print("📚 STAGE 2: KNOWLEDGE BASE SETUP")
    print("=" * 60)

    # Create test documents
    test_docs_dir = Path("test_documents")
    test_docs_dir.mkdir(exist_ok=True)

    documents = {
        "echoes_overview.md": """# Echoes AI Platform Overview

Echoes is an enterprise-grade AI assistant platform with:
- OpenAI embeddings for RAG (text-embedding-3-large)
- In-memory cosine similarity search
- FastAPI backend with 21+ endpoints
- Multi-agent workflow system
- Business analysis tools

## Key Features
- Real-time streaming responses
- Function calling capabilities
- Document processing with LangChain
- RESTful API with authentication

## Performance
- Response time: <500ms (p95)
- Throughput: 100+ req/s
- Embedding dimension: 3072 (large model)
""",
        "business_guide.md": """# Business Implementation Guide

## Revenue Opportunities
1. Freelance Consulting: $150-250/hr
2. AI/ML Development: $100-200/hr
3. Research Services: $200-300/hr
4. Training/Courses: $97-497/course
5. Enterprise Licensing: $500-5,000/month
6. SaaS Product: $500-5,000/month

## 30-Day Projections
- Week 1: $0-1,000 (setup phase)
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
""",
        "technical_faq.md": """# Technical FAQ

### Q: How do I configure OpenAI API?
A: Set OPENAI_API_KEY environment variable.

### Q: What embedding models are supported?
A: text-embedding-3-large (3072d), text-embedding-3-small (1536d), text-embedding-ada-002 (1536d)

### Q: How does RAG work without FAISS?
A: Uses in-memory cosine similarity with normalized embeddings via NumPy.

### Q: What are the RAG presets?
A: openai-fast (small model), openai-balanced (large model), openai-accurate (large optimized)

### Q: Can I use custom documents?
A: Yes, use the LangChain loader utility for bulk ingestion.
""",
    }

    # Write documents
    for filename, content in documents.items():
        file_path = test_docs_dir / filename
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

    print(f"✅ Created {len(documents)} test documents")

    # Add documents to knowledge base
    try:
        docs_to_add = []
        for filename, content in documents.items():
            docs_to_add.append({"text": content, "metadata": {"source": filename}})

        result = assistant.add_knowledge(docs_to_add)
        print(f"✅ Added {result.get('documents_added', 0)} documents to knowledge base")
        return True
    except Exception as e:
        print(f"❌ Failed to add documents: {e}")
        return False


def test_stage_3_rag_retrieval(assistant):
    """Stage 3: Test RAG knowledge retrieval."""
    print("\n" + "=" * 60)
    print("🔍 STAGE 3: RAG KNOWLEDGE RETRIEVAL")
    print("=" * 60)

    queries = [
        "What are the key features of Echoes?",
        "How much can I earn from freelance consulting?",
        "What embedding models are supported?",
        "How does RAG work without FAISS?",
        "What are the 30-day revenue projections?",
    ]

    success_count = 0
    for query in queries:
        try:
            results = assistant._retrieve_context(query, top_k=3)
            if results and len(results) > 0:
                score = results[0].get("score", 0)
                print(f"✅ Query: {query[:50]}... -> Score: {score:.3f}")
                success_count += 1
            else:
                print(f"❌ Query: {query[:50]}... -> No results")
        except Exception as e:
            print(f"❌ Query: {query[:50]}... -> Error: {e}")

    print(f"\n📊 RAG Retrieval: {success_count}/{len(queries)} successful")
    return success_count >= 3  # At least 60% success


def test_stage_4_tool_calling(assistant):
    """Stage 4: Test tool calling capabilities."""
    print("\n" + "=" * 60)
    print("🔧 STAGE 4: TOOL CALLING")
    print("=" * 60)

    # Test calculator tool
    try:
        response = assistant.process_message("Calculate 15% of 2500")
        if "375" in response or "15%" in response:
            print("✅ Calculator tool working")
            calc_success = True
        else:
            print(f"❌ Calculator tool unexpected response: {response[:100]}")
            calc_success = False
    except Exception as e:
        print(f"❌ Calculator tool failed: {e}")
        calc_success = False

    # Test web search tool (may fail without API keys)
    try:
        response = assistant.process_message("Search for AI trends 2024")
        if len(response) > 50 and "error" not in response.lower():
            print("✅ Web search tool working")
            search_success = True
        else:
            print("⚠️  Web search tool may need configuration")
            search_success = False
    except Exception as e:
        print(f"⚠️  Web search tool issue: {e}")
        search_success = False

    print(f"\n📊 Tool Calling: Calculator={calc_success}, WebSearch={search_success}")
    return calc_success or search_success  # At least one tool working


def test_stage_5_business_analysis(assistant):
    """Stage 5: Test business analysis functions."""
    print("\n" + "=" * 60)
    print("💼 STAGE 5: BUSINESS ANALYSIS")
    print("=" * 60)

    queries = [
        "Analyze the market opportunity for AI consulting",
        "Identify revenue streams for an AI platform",
        "Project revenue for 3 consulting clients at $200/hour",
    ]

    success_count = 0
    for query in queries:
        try:
            response = assistant.process_message(query)
            if len(response) > 100 and any(
                keyword in response.lower()
                for keyword in ["revenue", "market", "income", "opportunity"]
            ):
                print(f"✅ Business query: {query[:40]}... -> {len(response)} chars")
                success_count += 1
            else:
                print(f"❌ Business query: {query[:40]}... -> Insufficient response")
        except Exception as e:
            print(f"❌ Business query: {query[:40]}... -> Error: {e}")

    print(f"\n📊 Business Analysis: {success_count}/{len(queries)} successful")
    return success_count >= 2  # At least 66% success


def test_stage_6_complex_queries(assistant):
    """Stage 6: Test complex multimodal queries."""
    print("\n" + "=" * 60)
    print("🎯 STAGE 6: COMPLEX MULTIMODAL QUERIES")
    print("=" * 60)

    queries = [
        "Based on Echoes architecture, design a custom RAG system for legal documents",
        "Calculate potential revenue: $200/hour, 20 hours/week, for 3 months",
        "Create a workflow for onboarding enterprise clients using Echoes API",
    ]

    success_count = 0
    for query in queries:
        try:
            response = assistant.process_message(query)
            if len(response) > 150:
                print(f"✅ Complex query: {query[:40]}... -> {len(response)} chars")
                success_count += 1
            else:
                print(
                    f"❌ Complex query: {query[:40]}... -> Too short: {len(response)} chars"
                )
        except Exception as e:
            print(f"❌ Complex query: {query[:40]}... -> Error: {e}")

    print(f"\n📊 Complex Queries: {success_count}/{len(queries)} successful")
    return success_count >= 2  # At least 66% success


def test_stage_7_unanswered_questions(assistant):
    """Stage 7: Test historically unanswered questions."""
    print("\n" + "=" * 60)
    print("❓ STAGE 7: HISTORICALLY UNANSWERED QUESTIONS")
    print("=" * 60)

    queries = [
        "How do I implement custom embedding models?",
        "What's the optimal chunk size for technical docs?",
        "How to deploy Echoes on Kubernetes?",
        "Data privacy implications of OpenAI embeddings?",
        "How to migrate from existing RAG to Echoes?",
    ]

    success_count = 0
    for query in queries:
        try:
            # Try RAG first
            rag_results = assistant._retrieve_context(query, top_k=3)
            # Then full response
            response = assistant.process_message(query)

            has_rag = len(rag_results) > 0
            has_response = len(response) > 50

            if has_response:
                print(
                    f"✅ Unanswered: {query[:40]}... -> Response: {len(response)} chars, RAG: {len(rag_results)}"
                )
                success_count += 1
            else:
                print(f"❌ Unanswered: {query[:40]}... -> No meaningful response")
        except Exception as e:
            print(f"❌ Unanswered: {query[:40]}... -> Error: {e}")

    print(f"\n📊 Unanswered Questions: {success_count}/{len(queries)} addressed")
    return success_count >= 2  # At least 40% success (these are hard questions)


def test_stage_8_performance(assistant):
    """Stage 8: Test performance metrics."""
    print("\n" + "=" * 60)
    print("📊 STAGE 8: PERFORMANCE METRICS")
    print("=" * 60)

    # Test knowledge retrieval speed
    try:
        start = time.time()
        results = assistant._retrieve_context("Echoes features", top_k=5)
        retrieval_time = time.time() - start
        print(
            f"✅ Knowledge retrieval: {retrieval_time:.3f}s for {len(results)} results"
        )
        retrieval_ok = retrieval_time < 2.0
    except Exception as e:
        print(f"❌ Knowledge retrieval failed: {e}")
        retrieval_ok = False

    # Test simple query speed
    try:
        start = time.time()
        response = assistant.process_message("What is Echoes?")
        query_time = time.time() - start
        print(f"✅ Simple query: {query_time:.3f}s")
        query_ok = query_time < 10.0
    except Exception as e:
        print(f"❌ Simple query failed: {e}")
        query_ok = False

    print(
        f"\n📊 Performance: Retrieval={'OK' if retrieval_ok else 'SLOW'}, Query={'OK' if query_ok else 'SLOW'}"
    )
    return retrieval_ok and query_ok


def generate_summary_report(stage_results):
    """Generate summary report."""
    print("\n" + "=" * 60)
    print("📋 UNIFIED SYSTEM TEST SUMMARY")
    print("=" * 60)

    total_stages = len(stage_results)
    passed_stages = sum(1 for result in stage_results.values() if result)

    print(f"\n🎯 Overall: {passed_stages}/{total_stages} stages passed")

    for stage, passed in stage_results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status} {stage}")

    success_rate = (passed_stages / total_stages * 100) if total_stages > 0 else 0

    if success_rate >= 80:
        print(f"\n🎉 EXCELLENT: System is highly functional ({success_rate:.1f}%)")
    elif success_rate >= 60:
        print(f"\n✅ GOOD: System is mostly functional ({success_rate:.1f}%)")
    else:
        print(f"\n⚠️  NEEDS ATTENTION: System has issues ({success_rate:.1f}%)")

    # Save report
    report = {
        "timestamp": time.time(),
        "total_stages": total_stages,
        "passed_stages": passed_stages,
        "success_rate": success_rate,
        "stage_results": stage_results,
    }

    with open("echoes_test_summary.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print("\n💾 Report saved to: echoes_test_summary.json")
    return report


def main():
    """Run staged unified system test."""
    print("🚀 ECHOES UNIFIED SYSTEM TEST - STAGED VERSION")

    # Check environment
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  WARNING: OPENAI_API_KEY not set. Some tests may fail.")

    stage_results = {}

    # Stage 1: Initialization
    assistant, stage_results["Initialization"] = test_stage_1_initialization()
    if not assistant:
        print("❌ Cannot continue without successful initialization")
        return

    # Stage 2: Knowledge Setup
    stage_results["Knowledge Setup"] = test_stage_2_knowledge_setup(assistant)

    # Stage 3: RAG Retrieval
    stage_results["RAG Retrieval"] = test_stage_3_rag_retrieval(assistant)

    # Stage 4: Tool Calling
    stage_results["Tool Calling"] = test_stage_4_tool_calling(assistant)

    # Stage 5: Business Analysis
    stage_results["Business Analysis"] = test_stage_5_business_analysis(assistant)

    # Stage 6: Complex Queries
    stage_results["Complex Queries"] = test_stage_6_complex_queries(assistant)

    # Stage 7: Unanswered Questions
    stage_results["Unanswered Questions"] = test_stage_7_unanswered_questions(assistant)

    # Stage 8: Performance
    stage_results["Performance"] = test_stage_8_performance(assistant)

    # Generate summary
    report = generate_summary_report(stage_results)

    print("\n" + "=" * 60)
    print("✅ STAGED UNIFIED TEST COMPLETE")
    print("=" * 60)

    return report


if __name__ == "__main__":
    main()
