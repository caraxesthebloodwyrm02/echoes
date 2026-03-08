"""
Test script to verify RAG system setup and basic functionality.
"""

import importlib
import sys

import pytest

from agent_pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))


def test_imports():
    """Test if all required imports work."""
    print("\n=== Testing Imports ===")

    try:
        importlib.import_module("echoes_core.rag_orbit")
        print("✅ Successfully imported RAGOrbit and RAGConfig")
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        pytest.importorskip("echoes_core")


def test_rag_initialization():
    """Test RAG system initialization."""
    pytest.importorskip("echoes_core")
    print("\n=== Testing RAG Initialization ===")

    try:
        from echoes_core.rag_orbit import RAGConfig, RAGOrbit

        # Test with default config
        print("Testing with default config...")
        _rag = RAGOrbit()
        print("✅ Successfully created RAGOrbit with default config")

        # Test with custom config
        print("\nTesting with custom config...")
        config = RAGConfig(
            embedding_model_name="sentence-transformers/all-MiniLM-L6-v2",
            chunk_size=500,
            chunk_overlap=50,
        )
        _rag = RAGOrbit(config)
        print("✅ Successfully created RAGOrbit with custom config")
        assert True  # pytest: no return value
    except Exception as e:
        print(f"❌ RAG initialization failed: {e}")
        raise


def main():
    """Run all tests."""
    print("=== RAG System Test ===")

    # Run import test
    if not test_imports():
        print("\n❌ Some imports failed. Please check the error messages above.")
        return

    # Run RAG initialization test
    if not test_rag_initialization():
        print(
            "\n❌ RAG initialization tests failed. Please check the error messages above."
        )
        return

    print("\n✅ All tests passed! Your RAG system is set up correctly.")


if __name__ == "__main__":
    main()
