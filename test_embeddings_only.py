#!/usr/bin/env python3
"""Test OpenAI embeddings module only."""

import sys
import os
sys.path.insert(0, os.getcwd())

try:
    from core_modules.openai_embeddings import OpenAIEmbeddings
    print("✅ OpenAIEmbeddings imported successfully")
    
    # Try to initialize
    embeddings = OpenAIEmbeddings()
    print(f"✅ Initialized with model: {embeddings.model_name}")
    print(f"✅ Dimension: {embeddings.dimension}")
    
    # Try to embed something
    test_text = "Hello, this is a test"
    result = embeddings.embed_query(test_text)
    print(f"✅ Generated embedding: {len(result)} dimensions")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
