#!/usr/bin/env python3
"""Simple test to verify MCP server starts correctly."""

import sys
import os
import asyncio
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

async def main():
    """Test basic server instantiation."""
    print("🧪 Testing YAML Context Engineering MCP Server")
    
    # Set environment variables
    os.environ['PYTHONPATH'] = str(Path(__file__).parent / "src")
    os.environ['MCP_OUTPUT_DIRECTORY'] = str(Path.home() / "generated_contexts_test")
    
    try:
        # Import modules
        from yaml_context_engineering.server import YamlContextServer
        from yaml_context_engineering.config import Config
        from mcp.server import stdio
        
        print("✅ Imports successful")
        
        # Create configuration
        config = Config.from_env()
        config.output.output_base_directory = Path(os.environ['MCP_OUTPUT_DIRECTORY'])
        config.validate()
        
        print("✅ Configuration created")
        
        # Create server
        server = YamlContextServer(config)
        print("✅ Server created successfully")
        
        # Check server attributes
        print(f"\n📋 Server info:")
        print(f"  - Name: {server.config.server_name}")
        print(f"  - Version: {server.config.server_version}")
        print(f"  - Output dir: {server.config.output.output_base_directory}")
        
        # Check if server has MCP server instance
        if hasattr(server, 'server'):
            print("✅ MCP server instance found")
            print(f"  - Type: {type(server.server)}")
            print(f"  - Name: {server.server.name}")
        else:
            print("❌ No MCP server instance found")
        
        print("\n✅ Basic test passed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())