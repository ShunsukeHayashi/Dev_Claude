#!/usr/bin/env python3
"""Simple MVP test script for YAML Context Engineering MCP Server."""

import asyncio
import sys
from pathlib import Path
import logging

from yaml_context_engineering import YamlContextServer, Config
from yaml_context_engineering.utils.logging import setup_logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


async def test_basic_extraction():
    """Test basic URL content extraction and YAML generation."""
    print("\n" + "=" * 50)
    print("🧪 MVP Test: Basic Content Extraction")
    print("=" * 50)
    
    # Setup
    config = Config.from_env()
    config.log_level = "INFO"
    config.output.output_base_directory = Path("./test_output")
    
    server = YamlContextServer(config)
    
    # Test URL (using a simple, reliable site)
    test_url = "https://www.example.com"
    
    try:
        # Step 1: Fetch web content
        logger.info(f"📥 Fetching content from {test_url}...")
        fetch_results = await server.web_fetcher.fetch([test_url])
        
        if not fetch_results or not fetch_results[0]["success"]:
            logger.error("❌ Failed to fetch content")
            return False
        
        result = fetch_results[0]
        logger.info("✅ Content fetched successfully!")
        logger.info(f"   - Status: {result['status_code']}")
        logger.info(f"   - Title: {result.get('title', 'N/A')}")
        logger.info(f"   - Content length: {len(result['content'])} chars")
        
        # Step 2: Extract structure
        logger.info("🔍 Extracting hierarchical structure...")
        structure = await server.structure_extractor.extract(result["content"])
        
        logger.info("✅ Structure extracted!")
        logger.info(f"   - Format detected: {structure['format_detected']}")
        logger.info(f"   - Total headings: {structure['total_headings']}")
        logger.info(f"   - Confidence: {structure['confidence_score']:.2f}")
        
        # Step 3: Generate YAML documentation
        logger.info("📝 Generating YAML documentation...")
        filename = "example_com_extracted"
        write_result = await server.file_manager.execute(
            "write_file",
            f"{filename}.md",
            {
                "title": result.get("title", "Example.com Content"),
                "source_url": test_url,
                "language": result.get("language", "en"),
                "body": result["content"],
                "hierarchy_levels": structure.get("hierarchy_levels", []),
                "extraction_confidence": structure.get("confidence_score", 0.0)
            }
        )
        
        if write_result["success"]:
            logger.info("✅ YAML documentation generated!")
            logger.info(f"   - File: {write_result['path']}")
        else:
            logger.error(f"❌ Failed to write file: {write_result.get('error')}")
            return False
        
        # Display file content sample
        output_path = Path(write_result["path"])
        if output_path.exists():
            with open(output_path, 'r') as f:
                content = f.read()
                print("\n" + "=" * 50)
                print("📄 Generated File Preview")
                print("=" * 50)
                print(content[:500] + "..." if len(content) > 500 else content)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await server.web_fetcher.close()


async def main():
    """Run MVP test."""
    setup_logging("INFO", structured=False)
    
    print("\n" + "=" * 60)
    print("🚀 YAML Context Engineering MVP Test")
    print("=" * 60)
    
    # Run test
    success = await test_basic_extraction()
    
    if success:
        print("\n🎉 MVP Test Passed! The system is working correctly!")
        
        # Show final message
        print("\n" + "=" * 60)
        print("✅ YAML Context Engineering MCP Server MVP is ready!")
        print("=" * 60)
        print("\nYou can now:")
        print("1. Use the CLI: python3.11 -m yaml_context_engineering.cli extract <URL>")
        print("2. Start the MCP server: yaml-context-mcp")
        print("3. Integrate with Claude Code via MCP protocol")
        sys.exit(0)
    else:
        print("\n❌ MVP Test Failed")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())