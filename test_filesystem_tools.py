#!/usr/bin/env python3
"""Test script for filesystem tools."""

from assistant_v2_core import EchoesAssistantV2

def test_filesystem_tools():
    """Test that filesystem tools are properly registered."""
    
    print("Initializing EchoesAssistantV2 with tools...")
    assistant = EchoesAssistantV2(enable_tools=True)
    
    print("\nAvailable tools:")
    tools = assistant.list_tools()
    for tool in tools:
        print(f"  - {tool}")
    
    print("\nFilesystem tools:")
    filesystem_tools = [
        'read_file', 'write_file', 'list_directory', 
        'search_files', 'create_directory', 'get_file_info'
    ]
    
    for tool_name in filesystem_tools:
        if tool_name in tools:
            print(f"  ✓ {tool_name}")
        else:
            print(f"  ✗ {tool_name} - NOT FOUND")
    
    print(f"\nTotal tools loaded: {len(tools)}")
    
    # Test a simple tool call
    if 'list_directory' in tools:
        print("\nTesting list_directory tool...")
        result = assistant.tool_registry.execute('list_directory', dirpath='.')
        if result.success:
            print(f"  ✓ Found {result.data['total_files']} files and {result.data['total_directories']} directories")
        else:
            print(f"  ✗ Error: {result.error}")

if __name__ == "__main__":
    test_filesystem_tools()
