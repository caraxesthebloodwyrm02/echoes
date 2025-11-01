#!/usr/bin/env python3
"""Test loader import"""

try:
    from echoes.rag_langchain_loader import LANGCHAIN_AVAILABLE
    print(f"LANGCHAIN_AVAILABLE from loader: {LANGCHAIN_AVAILABLE}")
    
    if LANGCHAIN_AVAILABLE:
        from echoes.rag_langchain_loader import LangChainRAGLoader
        print("✓ LangChainRAGLoader imported successfully")
    else:
        print("✗ LangChain not available in loader")
except ImportError as e:
    print(f"✗ Failed to import from loader: {e}")
