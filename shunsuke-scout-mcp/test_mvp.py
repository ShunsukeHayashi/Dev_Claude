#!/usr/bin/env python3
"""MVP test script for YAML Context Engineering MCP Server."""

import asyncio
import sys
from pathlib import Path

from yaml_context_engineering import YamlContextServer, Config
from yaml_context_engineering.utils.logging import setup_logging, get_logger

# Create a logger for this module
logger = get_logger(__name__)


async def test_basic_extraction():
    """Test basic URL content extraction and YAML generation."""
    logger.rule("🧪 MVP Test: Basic Content Extraction")
    
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
        logger.success(f"✅ Content fetched successfully!")
        logger.info(f"   - Status: {result['status_code']}")
        logger.info(f"   - Title: {result.get('title', 'N/A')}")
        logger.info(f"   - Content length: {len(result['content'])} chars")
        
        # Step 2: Extract structure
        logger.info("🔍 Extracting hierarchical structure...")
        structure = await server.structure_extractor.extract(result["content"])
        
        logger.success("✅ Structure extracted!")
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
            logger.success(f"✅ YAML documentation generated!")
            logger.info(f"   - File: {write_result['path']}")
        else:
            logger.error(f"❌ Failed to write file: {write_result.get('error')}")
            return False
        
        # Step 4: Generate index
        logger.info("📚 Generating index file...")
        index_result = await server.file_manager.execute("generate_index")
        
        if index_result["success"]:
            logger.success(f"✅ Index generated!")
            logger.info(f"   - File: {index_result['path']}")
        
        # Display file content sample
        output_path = Path(write_result["path"])
        if output_path.exists():
            with open(output_path, 'r') as f:
                content = f.read()
                logger.rule("📄 Generated File Preview")
                logger.print(content[:500] + "..." if len(content) > 500 else content)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await server.web_fetcher.close()


async def test_multiple_tools():
    """Test using multiple tools together."""
    logger.rule("🧪 MVP Test: Multi-tool Workflow")
    
    config = Config.from_env()
    config.output.output_base_directory = Path("./test_output/multi_tool")
    
    server = YamlContextServer(config)
    
    # Test content with URLs
    test_content = """
    # Documentation Portal
    
    Welcome to our documentation. Check out these resources:
    - [API Documentation](https://api.example.com/docs)
    - [User Guide](https://guide.example.com)
    - [Examples](https://examples.example.com)
    
    ## Getting Started
    
    Follow these steps to get started with our platform.
    """
    
    try:
        # Test URL discovery
        logger.info("🔍 Testing URL discovery...")
        urls = await server.url_discovery.discover(test_content, "example.com")
        
        logger.success(f"✅ Found {len(urls)} URLs")
        for url_info in urls:
            logger.info(f"   - {url_info['url']} (priority: {url_info['priority_score']:.2f})")
        
        # Test structure extraction
        logger.info("🔍 Testing structure extraction...")
        structure = await server.structure_extractor.extract(test_content)
        
        logger.success("✅ Structure extracted!")
        for heading in structure["structured_headings"]:
            logger.info(f"   - L{heading['level']}: {heading['text']}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return False


async def main():
    """Run all MVP tests."""
    setup_logging("INFO", structured=False)
    
    logger.rule("🚀 YAML Context Engineering MVP Test Suite", style="bold green")
    
    # Run tests
    tests = [
        ("Basic Content Extraction", test_basic_extraction),
        ("Multi-tool Workflow", test_multiple_tools)
    ]
    
    results = []
    for test_name, test_func in tests:
        logger.print(f"\n🏃 Running: {test_name}")
        success = await test_func()
        results.append((test_name, success))
    
    # Summary
    logger.rule("📊 Test Summary", style="bold")
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        logger.print(f"{status} - {test_name}")
    
    logger.print(f"\n🎯 Total: {passed}/{total} tests passed")
    
    if passed == total:
        logger.success("🎉 All tests passed! MVP is working!")
        sys.exit(0)
    else:
        logger.error("❌ Some tests failed")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())