#!/usr/bin/env python3
"""Test script for YAML Context Engineering MCP Server."""

import sys
import os
import asyncio
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

async def test_server():
    """Test the MCP server functionality."""
    print("🧪 Testing YAML Context Engineering MCP Server")
    
    # Set environment variables
    os.environ['PYTHONPATH'] = str(Path(__file__).parent / "src")
    os.environ['MCP_OUTPUT_DIRECTORY'] = str(Path.home() / "generated_contexts_test")
    
    try:
        # Import and create server
        from yaml_context_engineering.server import YamlContextServer
        from yaml_context_engineering.config import Config
        
        # Create configuration
        config = Config.from_env()
        config.output.output_base_directory = Path(os.environ['MCP_OUTPUT_DIRECTORY'])
        config.validate()
        
        server = YamlContextServer(config)
        
        print("✅ Server created successfully")
        
        # Test tool listing
        print("\n📋 Testing list_tools():")
        tools = await server.list_tools()
        print(f"  Found {len(tools)} tools")
        for tool in tools:
            print(f"  - {tool['name']}: {tool.get('description', 'No description')[:60]}...")
        
        # Test a simple tool call
        print("\n🔧 Testing file_system_manager tool:")
        result = await server.call_tool(
            "file_system_manager",
            {
                "action": "create_directory",
                "directory_path": os.path.join(os.environ['MCP_OUTPUT_DIRECTORY'], "test_dir")
            }
        )
        print(f"  Result: {result}")
        
        print("\n✅ All tests passed!")
        print(f"\n📁 Output directory: {os.environ['MCP_OUTPUT_DIRECTORY']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(test_server())