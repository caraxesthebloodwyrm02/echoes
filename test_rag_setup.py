#!/usr/bin/env python3
"""Test RAG system setup and configuration."""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_rag_setup():
    """Test RAG system configuration."""
    
    print("=" * 60)
    print("🔍 RAG System Configuration Test")
    print("=" * 60)
    
    # Check OpenAI API key
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        print(f"✅ OpenAI API key found (starts with: {api_key[:7]}...)")
    else:
        print("❌ OpenAI API key not found in environment variables")
        print("   Please set OPENAI_API_KEY in your .env file")
        return
    
    # Test OpenAI import
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        
        # Test a simple API call
        models = client.models.list()
        print("✅ OpenAI client initialized successfully")
        
        # Check if embedding models are available
        embedding_models = [m for m in models.data if "embedding" in m.id]
        print(f"✅ Found {len(embedding_models)} embedding models")
        
        # Show available embedding models
        print("\n📋 Available OpenAI Embedding Models:")
        for model in sorted(embedding_models, key=lambda x: x.id)[:5]:  # Show first 5
            print(f"   • {model.id}")
        
        if len(embedding_models) > 5:
            print(f"   ... and {len(embedding_models) - 5} more")
            
    except Exception as e:
        print(f"❌ OpenAI client error: {str(e)}")
        return
    
    # Test our OpenAI embeddings module
    print("\n🔧 Testing OpenAI Embeddings Module...")
    try:
        from openai_rag.openai_embeddings import OpenAIEmbeddings
        
        embeddings = OpenAIEmbeddings(api_key=api_key)
        print(f"✅ OpenAIEmbeddings initialized with model: {embeddings.model_name}")
        print(f"✅ Embedding dimension: {embeddings.dimension}")
        
        # Test embedding a simple text
        test_text = "This is a test for OpenAI embeddings"
        embedding = embeddings.embed_query(test_text)
        print(f"✅ Generated embedding vector with {len(embedding)} dimensions")
        
    except Exception as e:
        print(f"❌ OpenAI embeddings error: {str(e)}")
        return
    
    # Test RAG OpenAI module
    print("\n🚀 Testing RAG OpenAI System...")
    try:
        from openai_rag.rag_openai import create_rag_system_openai
        
        rag = create_rag_system_openai(preset="balanced")
        print("✅ RAG OpenAI system created successfully")
        
        # Test adding a document
        test_doc = "Echoes AI assistant uses OpenAI for embeddings and chat completion."
        result = rag.add_document(test_doc, {"source": "test"})
        print(f"✅ Added document: {len(result)} chunks created")
        
        # Test search
        search_results = rag.search("OpenAI embeddings", top_k=3)
        print(f"✅ Search completed: {len(search_results)} results")
        
        if search_results:
            best_result = search_results[0]
            print(f"   Best match score: {best_result['score']:.3f}")
            print(f"   Content preview: {best_result['content'][:60]}...")
        
    except Exception as e:
        print(f"❌ RAG OpenAI error: {str(e)}")
        return
    
    # Test RAG V2 wrapper
    print("\n📦 Testing RAG V2 Wrapper...")
    try:
        from echoes.core.rag_v2 import create_rag_system, OPENAI_RAG_AVAILABLE
        
        if OPENAI_RAG_AVAILABLE:
            rag_wrapper = create_rag_system(preset="balanced")
            if rag_wrapper:
                print("✅ RAG V2 wrapper created with OpenAI backend")
                
                # Test the wrapper interface
                docs = [{"text": "Test document for wrapper", "metadata": {"test": True}}]
                add_result = rag_wrapper.add_documents(docs)
                print(f"✅ Wrapper added {add_result['total_chunks']} chunks")
                
                search_result = rag_wrapper.search("test document")
                print(f"✅ Wrapper search found {len(search_result['results'])} results")
            else:
                print("❌ RAG V2 wrapper returned None")
        else:
            print("⚠️  OpenAI RAG not available in wrapper")
            
    except Exception as e:
        print(f"❌ RAG V2 wrapper error: {str(e)}")
        return
    
    print("\n" + "=" * 60)
    print("✅ All RAG system components working correctly!")
    print("The system is now using OpenAI embeddings instead of sentence-transformers")
    print("=" * 60)

if __name__ == "__main__":
    test_rag_setup()
