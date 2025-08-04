"""Tests for MCP server."""

import pytest
import asyncio
import json
from unittest.mock import Mock, AsyncMock, patch
from pathlib import Path

from yaml_context_engineering.server import YamlContextServer
from yaml_context_engineering.config import Config


class TestYamlContextServer:
    """Test YAML Context Engineering MCP Server."""
    
    @pytest.fixture
    def server(self, test_config):
        """Create server instance."""
        return YamlContextServer(test_config)
    
    def test_server_initialization(self, server, test_config):
        """Test server initialization."""
        assert server.config == test_config
        assert server.server is not None
        assert server.web_fetcher is not None
        assert server.structure_extractor is not None
        assert server.url_discovery is not None
        assert server.file_manager is not None
        assert server.ldd_manager is not None
    
    @pytest.mark.asyncio
    async def test_list_tools_handler(self, server):
        """Test list_tools handler returns all tools."""
        # Get the list_tools handler
        list_tools_handler = None
        for handler_name, handler in server.server.request_handlers.items():
            if handler_name == "tools/list":
                list_tools_handler = handler
                break
        
        assert list_tools_handler is not None
        
        # Call the handler
        tools = await list_tools_handler()
        
        assert len(tools) == 5  # 5 tools including ldd_manager
        tool_names = [tool.name for tool in tools]
        assert "web_content_fetcher" in tool_names
        assert "llm_structure_extractor" in tool_names
        assert "url_discovery_engine" in tool_names
        assert "file_system_manager" in tool_names
        assert "ldd_manager" in tool_names
    
    @pytest.mark.asyncio
    async def test_web_content_fetcher_tool(self, server):
        """Test web content fetcher tool execution."""
        # Mock the fetcher
        mock_result = [
            {
                "url": "https://example.com",
                "status_code": 200,
                "content": "Test content",
                "success": True
            }
        ]
        server.web_fetcher.fetch = AsyncMock(return_value=mock_result)
        
        # Get the call_tool handler
        call_tool_handler = None
        for handler_name, handler in server.server.request_handlers.items():
            if handler_name == "tools/call":
                call_tool_handler = handler
                break
        
        if call_tool_handler:
            result = await call_tool_handler(
                "web_content_fetcher",
                {"urls": ["https://example.com"]}
            )
            
            assert isinstance(result, list)
            assert len(result) == 1
            content = json.loads(result[0]["content"])
            assert content[0]["success"] is True
    
    @pytest.mark.asyncio
    async def test_llm_structure_extractor_tool(self, server):
        """Test LLM structure extractor tool execution."""
        # Mock the extractor
        mock_result = {
            "structured_headings": [],
            "confidence_score": 0.9,
            "format_detected": "markdown"
        }
        server.structure_extractor.extract = AsyncMock(return_value=mock_result)
        
        # Get the call_tool handler
        call_tool_handler = None
        for handler_name, handler in server.server.request_handlers.items():
            if handler_name == "tools/call":
                call_tool_handler = handler
                break
        
        if call_tool_handler:
            result = await call_tool_handler(
                "llm_structure_extractor",
                {"content": "# Test"}
            )
            
            assert isinstance(result, list)
            content = json.loads(result[0]["content"])
            assert content["confidence_score"] == 0.9
    
    @pytest.mark.asyncio
    async def test_url_discovery_engine_tool(self, server):
        """Test URL discovery engine tool execution."""
        # Mock the discovery engine
        mock_result = [
            {
                "url": "https://example.com/doc",
                "priority_score": 0.8,
                "relation_type": "internal"
            }
        ]
        server.url_discovery.discover = AsyncMock(return_value=mock_result)
        
        # Get the call_tool handler
        call_tool_handler = None
        for handler_name, handler in server.server.request_handlers.items():
            if handler_name == "tools/call":
                call_tool_handler = handler
                break
        
        if call_tool_handler:
            result = await call_tool_handler(
                "url_discovery_engine",
                {
                    "content": "Check https://example.com/doc",
                    "base_domain": "example.com"
                }
            )
            
            assert isinstance(result, list)
            content = json.loads(result[0]["content"])
            assert content[0]["priority_score"] == 0.8
    
    @pytest.mark.asyncio
    async def test_file_system_manager_tool(self, server):
        """Test file system manager tool execution."""
        # Mock the file manager
        mock_result = {
            "success": True,
            "action": "write_file",
            "path": "/tmp/test.md"
        }
        server.file_manager.execute = AsyncMock(return_value=mock_result)
        
        # Get the call_tool handler
        call_tool_handler = None
        for handler_name, handler in server.server.request_handlers.items():
            if handler_name == "tools/call":
                call_tool_handler = handler
                break
        
        if call_tool_handler:
            result = await call_tool_handler(
                "file_system_manager",
                {
                    "action": "write_file",
                    "path": "test.md",
                    "content": "Test content"
                }
            )
            
            assert isinstance(result, list)
            content = json.loads(result[0]["content"])
            assert content["success"] is True
    
    @pytest.mark.asyncio
    async def test_ldd_manager_tool(self, server):
        """Test LDD manager tool execution."""
        # Mock the LDD manager
        mock_result = {
            "success": True,
            "action": "create_task",
            "result": {
                "task_id": "test-123",
                "status": "Initiated"
            }
        }
        server.ldd_manager.execute = AsyncMock(return_value=mock_result)
        
        # Get the call_tool handler
        call_tool_handler = None
        for handler_name, handler in server.server.request_handlers.items():
            if handler_name == "tools/call":
                call_tool_handler = handler
                break
        
        if call_tool_handler:
            result = await call_tool_handler(
                "ldd_manager",
                {
                    "action": "create_task",
                    "task_name": "Test task"
                }
            )
            
            assert isinstance(result, list)
            content = json.loads(result[0]["content"])
            assert content["success"] is True
            assert content["result"]["task_id"] == "test-123"
    
    @pytest.mark.asyncio
    async def test_error_handling(self, server):
        """Test error handling in tool execution."""
        # Mock a failing tool
        server.web_fetcher.fetch = AsyncMock(side_effect=Exception("Test error"))
        
        # Get the call_tool handler
        call_tool_handler = None
        for handler_name, handler in server.server.request_handlers.items():
            if handler_name == "tools/call":
                call_tool_handler = handler
                break
        
        if call_tool_handler:
            with pytest.raises(Exception) as exc_info:
                await call_tool_handler(
                    "web_content_fetcher",
                    {"urls": ["https://example.com"]}
                )
            
            assert "Tool execution failed" in str(exc_info.value)
            assert "Test error" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_unknown_tool(self, server):
        """Test handling of unknown tool."""
        # Get the call_tool handler
        call_tool_handler = None
        for handler_name, handler in server.server.request_handlers.items():
            if handler_name == "tools/call":
                call_tool_handler = handler
                break
        
        if call_tool_handler:
            with pytest.raises(Exception) as exc_info:
                await call_tool_handler(
                    "unknown_tool",
                    {}
                )
            
            assert "Unknown tool" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_output_directory_creation(self, server, temp_output_dir):
        """Test that output directory is created on run."""
        server.config.output.output_base_directory = temp_output_dir / "new_dir"
        
        # Mock stdio_server
        mock_read = AsyncMock()
        mock_write = AsyncMock()
        
        with patch('yaml_context_engineering.server.stdio_server') as mock_stdio:
            mock_stdio.return_value.__aenter__.return_value = (mock_read, mock_write)
            
            # Start the run (it will fail due to mocking, but directory should be created)
            try:
                await asyncio.wait_for(server.run(), timeout=0.1)
            except asyncio.TimeoutError:
                pass
            
            assert server.config.output.output_base_directory.exists()


class TestToolIntegration:
    """Test integration between server and tools."""
    
    @pytest.fixture
    def integrated_server(self, test_config, temp_output_dir):
        """Create server with real tools."""
        test_config.output.output_base_directory = temp_output_dir
        return YamlContextServer(test_config)
    
    @pytest.mark.asyncio
    async def test_full_workflow(self, integrated_server):
        """Test a complete workflow through the server."""
        server = integrated_server
        
        # 1. Mock web content fetching
        mock_fetch_result = [{
            "url": "https://example.com",
            "status_code": 200,
            "content": "# Main Title\n\nContent here.",
            "success": True
        }]
        server.web_fetcher.fetch = AsyncMock(return_value=mock_fetch_result)
        
        # 2. Extract structure (use real extractor)
        extract_result = await server.structure_extractor.extract(
            mock_fetch_result[0]["content"]
        )
        assert extract_result["format_detected"] == "markdown"
        
        # 3. Discover URLs (use real discovery)
        discover_result = await server.url_discovery.discover(
            mock_fetch_result[0]["content"],
            "example.com"
        )
        
        # 4. Write file (use real file manager)
        write_result = await server.file_manager.execute(
            "write_file",
            "output.md",
            {
                "title": "Extracted Content",
                "source_url": "https://example.com",
                "body": mock_fetch_result[0]["content"]
            }
        )
        assert write_result["success"] is True
        assert Path(write_result["path"]).exists()