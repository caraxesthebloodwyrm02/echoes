python test_unified_simple.py#!/usr/bin/env python3
"""Simple Echoes Unified System Test - No emojis"""

import os
import sys
import time

print("=" * 70)
print("ECHOES UNIFIED SYSTEM TEST")
print("=" * 70)

# Check environment
if not os.getenv("OPENAI_API_KEY"):
    print("\nWARNING: OPENAI_API_KEY not set")
else:
    print("\nOK: OPENAI_API_KEY is set")

# Test 1: Initialize
print("\n" + "-" * 70)
print("TEST 1: System Initialization")
print("-" * 70)

try:
    from assistant_v2_core import EchoesAssistantV2
    print("OK: Imported EchoesAssistantV2")
    
    assistant = EchoesAssistantV2(enable_rag=True, rag_preset="openai-balanced")
    print("OK: Initialized Echoes with RAG")
    print(f"    RAG enabled: {assistant.rag is not None}")
    
except Exception as e:
    print(f"FAIL: Initialization failed: {e}")
    sys.exit(1)

# Test 2: Add Knowledge
print("\n" + "-" * 70)
print("TEST 2: Knowledge Base Setup")
print("-" * 70)

try:
    test_docs = [
        {"text": "Echoes uses OpenAI embeddings with in-memory cosine similarity.", "metadata": {"source": "overview"}},
        {"text": "Revenue: Consulting $150-250/hr, AI Development $100-200/hr.", "metadata": {"source": "business"}},
        {"text": "Supported models: text-embedding-3-large, text-embedding-3-small.", "metadata": {"source": "technical"}},
        {"text": "RAG presets: openai-fast, openai-balanced, openai-accurate.", "metadata": {"source": "presets"}},
        {"text": "LangChain loader supports PDF, Word, Markdown, HTML, CSV, JSON, Excel.", "metadata": {"source": "loader"}}
    ]
    
    result = assistant.add_knowledge(test_docs)
    docs_added = result.get("documents_added", len(test_docs))
    print(f"OK: Added {docs_added} documents to knowledge base")
    
except Exception as e:
    print(f"FAIL: Knowledge setup failed: {e}")
    sys.exit(1)

# Test 3: RAG Retrieval
print("\n" + "-" * 70)
print("TEST 3: RAG Knowledge Retrieval")
print("-" * 70)

rag_queries = [
    "What is Echoes?",
    "What revenue opportunities exist?",
    "What embedding models are supported?",
    "What are the RAG presets?",
    "What document formats does LangChain support?"
]

rag_success = 0
for query in rag_queries:
    try:
        results = assistant._retrieve_context(query, top_k=2)
        if results and len(results) > 0:
            score = results[0].get("score", 0)
            print(f"OK: '{query}' -> Score: {score:.3f}")
            rag_success += 1
        else:
            print(f"FAIL: '{query}' -> No results")
    except Exception as e:
        print(f"FAIL: '{query}' -> Error: {e}")

print(f"\nRAG Retrieval: {rag_success}/{len(rag_queries)} successful")

# Test 4: Tool Calling
print("\n" + "-" * 70)
print("TEST 4: Tool Calling")
print("-" * 70)

tool_queries = [
    ("Calculate 25% of 4000", "calculator"),
    ("What is 150 * 20?", "calculator")
]

tool_success = 0
for query, tool_name in tool_queries:
    try:
        response = assistant.chat(query)
        if len(response) > 20:
            print(f"OK: '{query}' -> {len(response)} chars")
            tool_success += 1
        else:
            print(f"FAIL: '{query}' -> Insufficient response")
    except Exception as e:
        print(f"FAIL: '{query}' -> Error: {e}")

print(f"\nTool Calling: {tool_success}/{len(tool_queries)} successful")

# Test 5: Business Analysis
print("\n" + "-" * 70)
print("TEST 5: Business Analysis")
print("-" * 70)

business_queries = [
    "Analyze market opportunity for AI consulting",
    "Identify revenue streams for an AI platform",
    "Project revenue for 3 clients at $200/hour"
]

business_success = 0
for query in business_queries:
    try:
        response = assistant.chat(query)
        if len(response) > 100:
            print(f"OK: '{query[:40]}...' -> {len(response)} chars")
            business_success += 1
        else:
            print(f"FAIL: '{query[:40]}...' -> Too short ({len(response)} chars)")
    except Exception as e:
        print(f"FAIL: '{query[:40]}...' -> Error: {e}")

print(f"\nBusiness Analysis: {business_success}/{len(business_queries)} successful")

# Test 6: Complex Queries
print("\n" + "-" * 70)
print("TEST 6: Complex Multimodal Queries")
print("-" * 70)

complex_queries = [
    "Design a RAG system for legal documents using Echoes architecture",
    "Calculate revenue: $200/hour, 20 hours/week, 12 weeks",
    "Create a workflow for enterprise client onboarding"
]

complex_success = 0
for query in complex_queries:
    try:
        response = assistant.chat(query)
        if len(response) > 150:
            print(f"OK: '{query[:40]}...' -> {len(response)} chars")
            complex_success += 1
        else:
            print(f"FAIL: '{query[:40]}...' -> Too short ({len(response)} chars)")
    except Exception as e:
        print(f"FAIL: '{query[:40]}...' -> Error: {e}")

print(f"\nComplex Queries: {complex_success}/{len(complex_queries)} successful")

# Test 7: Performance
print("\n" + "-" * 70)
print("TEST 7: Performance Metrics")
print("-" * 70)

try:
    start = time.time()
    results = assistant._retrieve_context("Echoes platform", top_k=3)
    retrieval_time = time.time() - start
    print(f"OK: Knowledge retrieval: {retrieval_time:.3f}s for {len(results)} results")
except Exception as e:
    print(f"FAIL: Knowledge retrieval failed: {e}")

try:
    start = time.time()
    response = assistant.chat("What is Echoes?")
    query_time = time.time() - start
    print(f"OK: Simple query: {query_time:.3f}s")
except Exception as e:
    print(f"FAIL: Simple query failed: {e}")

# Summary
print("\n" + "=" * 70)
print("TEST SUMMARY")
print("=" * 70)

total_tests = 5
passed_tests = sum([
    rag_success >= 3,
    tool_success >= 1,
    business_success >= 2,
    complex_success >= 2
])

success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

print(f"\nOverall: {passed_tests}/{total_tests} test categories passed ({success_rate:.0f}%)")
print(f"\n  RAG Retrieval: {rag_success}/{len(rag_queries)}")
print(f"  Tool Calling: {tool_success}/{len(tool_queries)}")
print(f"  Business Analysis: {business_success}/{len(business_queries)}")
print(f"  Complex Queries: {complex_success}/{len(complex_queries)}")

if success_rate >= 80:
    print(f"\nEXCELLENT: System is highly functional ({success_rate:.0f}%)")
elif success_rate >= 60:
    print(f"\nGOOD: System is mostly functional ({success_rate:.0f}%)")
else:
    print(f"\nNEEDS ATTENTION: System has issues ({success_rate:.0f}%)")

print("\n" + "=" * 70)
print("TEST COMPLETE")
print("=" * 70)
