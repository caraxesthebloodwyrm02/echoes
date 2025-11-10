#!/usr/bin/env python3
"""Test LangChain imports"""

try:
    import langchain_community

    print(f"✓ langchain_community version: {langchain_community.__version__}")
except ImportError as e:
    print(f"✗ langchain_community import failed: {e}")

try:
    import langchain_text_splitters

    print("✓ langchain_text_splitters imported successfully")
except ImportError as e:
    print(f"✗ langchain_text_splitters import failed: {e}")

try:
    from langchain_community.document_loaders import (DirectoryLoader,
                                                      PyPDFLoader)

    print("✓ Document loaders imported successfully")
except ImportError as e:
    print(f"✗ Document loaders import failed: {e}")

try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    print("✓ Text splitter imported successfully")
except ImportError as e:
    print(f"✗ Text splitter import failed: {e}")

print("\nTesting basic functionality...")
try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    test_doc = "This is a test document. " * 100
    chunks = splitter.split_text(test_doc)
    print(f"✓ Text splitting works: {len(chunks)} chunks created")
except Exception as e:
    print(f"✗ Text splitting failed: {e}")
