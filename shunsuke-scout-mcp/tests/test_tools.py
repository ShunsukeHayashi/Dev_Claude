"""Tests for MCP tools."""

import pytest
import asyncio
import json
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from pathlib import Path

from yaml_context_engineering.tools import (
    WebContentFetcher,
    LLMStructureExtractor,
    URLDiscoveryEngine,
    FileSystemManager
)
from yaml_context_engineering.config import Config


class TestWebContentFetcher:
    """Test web content fetcher tool."""
    
    @pytest.fixture
    def fetcher(self, test_config):
        """Create fetcher instance."""
        return WebContentFetcher(test_config)
    
    @pytest.mark.asyncio
    async def test_fetch_valid_url(self, fetcher):
        """Test fetching valid URL."""
        # Mock aiohttp response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.headers = {"Content-Type": "text/html"}
        mock_response.text = AsyncMock(return_value="<html><body><h1>Test</h1></body></html>")
        mock_response.url = "https://example.com"
        mock_response.raise_for_status = Mock()
        
        with patch('aiohttp.ClientSession.get', return_value=mock_response):
            results = await fetcher.fetch(["https://example.com"])
            
            assert len(results) == 1
            result = results[0]
            assert result["success"] is True
            assert result["status_code"] == 200
            assert "Test" in result["content"]
            assert result["url"] == "https://example.com"
    
    @pytest.mark.asyncio
    async def test_fetch_invalid_url(self, fetcher):
        """Test fetching invalid URL."""
        results = await fetcher.fetch(["not-a-url"])
        
        assert len(results) == 1
        assert results[0]["success"] is False
        assert "Invalid URL format" in results[0]["error"]
    
    @pytest.mark.asyncio
    async def test_fetch_multiple_urls(self, fetcher):
        """Test fetching multiple URLs concurrently."""
        urls = [
            "https://example1.com",
            "https://example2.com",
            "invalid-url"
        ]
        
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.headers = {"Content-Type": "text/html"}
        mock_response.text = AsyncMock(return_value="<html><body>Content</body></html>")
        mock_response.url = "https://example.com"
        mock_response.raise_for_status = Mock()
        
        with patch('aiohttp.ClientSession.get', return_value=mock_response):
            results = await fetcher.fetch(urls)
            
            assert len(results) == 3
            assert results[0]["success"] is True
            assert results[1]["success"] is True
            assert results[2]["success"] is False
    
    @pytest.mark.asyncio
    async def test_extract_urls_from_html(self, fetcher, sample_html_content):
        """Test URL extraction from HTML content."""
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(sample_html_content, "lxml")
        urls = fetcher._extract_urls(soup, "https://example.com")
        
        assert len(urls) == 3
        assert "https://example.com/page1" in urls
        assert "https://example.com/page2" in urls
        assert "https://example.com" in urls
    
    @pytest.mark.asyncio
    async def test_cleanup(self, fetcher):
        """Test session cleanup."""
        # Create a session
        await fetcher._get_session()
        assert fetcher._session is not None
        
        # Clean up
        await fetcher.close()
        assert fetcher._session.closed


class TestLLMStructureExtractor:
    """Test LLM structure extractor tool."""
    
    @pytest.fixture
    def extractor(self, test_config):
        """Create extractor instance."""
        return LLMStructureExtractor(test_config)
    
    @pytest.mark.asyncio
    async def test_extract_markdown_structure(self, extractor, sample_markdown_content):
        """Test extracting structure from markdown."""
        result = await extractor.extract(sample_markdown_content)
        
        assert result["format_detected"] == "markdown"
        assert result["confidence_score"] > 0
        assert len(result["structured_headings"]) == 3
        
        # Check first heading
        h1 = result["structured_headings"][0]
        assert h1["level"] == 1
        assert h1["text"] == "Main Title"
        assert "Introduction paragraph" in h1["content"]
    
    @pytest.mark.asyncio
    async def test_extract_html_structure(self, extractor, sample_html_content):
        """Test extracting structure from HTML."""
        result = await extractor.extract(sample_html_content)
        
        assert result["format_detected"] == "html"
        assert len(result["structured_headings"]) > 0
        
        # Check extracted headings
        headings = result["structured_headings"]
        assert any(h["text"] == "Main Title" for h in headings)
    
    @pytest.mark.asyncio
    async def test_granularity_filtering(self, extractor, sample_markdown_content):
        """Test granularity filtering."""
        # L1 only
        result = await extractor.extract(
            sample_markdown_content,
            extraction_config={"granularity": "L1_only"}
        )
        assert all(h["level"] == 1 for h in result["structured_headings"])
        
        # L1_L2
        result = await extractor.extract(
            sample_markdown_content,
            extraction_config={"granularity": "L1_L2"}
        )
        max_level = max(h["level"] for h in self._flatten_headings(result["structured_headings"]))
        assert max_level <= 2
    
    def _flatten_headings(self, headings):
        """Flatten hierarchical headings for testing."""
        flat = []
        for h in headings:
            flat.append(h)
            if h.get("children"):
                flat.extend(self._flatten_headings(h["children"]))
        return flat
    
    @pytest.mark.asyncio
    async def test_content_summarization(self, extractor):
        """Test content summarization levels."""
        long_content = "This is a very long content. " * 100
        
        # Brief
        result = await extractor.extract(
            long_content,
            extraction_config={"summarization": "brief"}
        )
        assert len(result["content_summary"]) <= 203  # 200 + "..."
        
        # Full
        result = await extractor.extract(
            long_content,
            extraction_config={"summarization": "full"}
        )
        assert result["content_summary"] == long_content
    
    @pytest.mark.asyncio
    async def test_entity_extraction(self, extractor):
        """Test entity extraction."""
        content = """
        Check out https://example.com and contact us at test@example.com.
        
        ```python
        def hello():
            print("Hello")
        ```
        
        Learn about Machine Learning and Natural Language Processing.
        """
        
        result = await extractor.extract(content)
        entities = result["extracted_entities"]
        
        assert "https://example.com" in entities["urls"]
        assert "test@example.com" in entities["emails"]
        assert len(entities["code_blocks"]) == 1
        assert "Machine Learning" in entities["key_terms"]


class TestURLDiscoveryEngine:
    """Test URL discovery engine."""
    
    @pytest.fixture
    def discovery(self, test_config):
        """Create discovery engine instance."""
        return URLDiscoveryEngine(test_config)
    
    @pytest.mark.asyncio
    async def test_discover_urls(self, discovery):
        """Test URL discovery from content."""
        content = """
        Visit our documentation at https://docs.example.com/api
        Check the guide at https://example.com/guide
        External resource: https://external.com/resource
        """
        
        results = await discovery.discover(content, "example.com")
        
        assert len(results) == 3
        # Check priority scoring
        api_url = next(r for r in results if "/api" in r["url"])
        assert api_url["priority_score"] > 0.5
        assert api_url["estimated_content_value"] == "high"
    
    @pytest.mark.asyncio
    async def test_url_filtering(self, discovery):
        """Test URL filtering."""
        content = """
        https://example.com/page1
        https://example.com/page2
        https://other.com/page
        """
        
        results = await discovery.discover(
            content,
            "example.com",
            filters=[r"page1"]
        )
        
        assert len(results) == 1
        assert "page1" in results[0]["url"]
    
    @pytest.mark.asyncio
    async def test_relation_type_detection(self, discovery):
        """Test relation type detection."""
        content = """
        https://example.com/internal
        https://api.example.com/endpoint
        https://external.com/resource
        """
        
        results = await discovery.discover(content, "example.com")
        
        relations = {r["url"]: r["relation_type"] for r in results}
        assert relations["https://example.com/internal"] == "internal"
        assert relations["https://api.example.com/endpoint"] == "subdomain"
        assert relations["https://external.com/resource"] == "external"
    
    @pytest.mark.asyncio
    async def test_content_value_estimation(self, discovery):
        """Test content value estimation."""
        assert discovery._estimate_content_value("https://example.com/api/docs") == "high"
        assert discovery._estimate_content_value("https://example.com/examples") == "medium"
        assert discovery._estimate_content_value("https://example.com/blog") == "low"
        assert discovery._estimate_content_value("https://example.com/random") == "unknown"


class TestFileSystemManager:
    """Test file system manager."""
    
    @pytest.fixture
    def file_manager(self, test_config, temp_output_dir):
        """Create file manager instance."""
        test_config.output.output_base_directory = temp_output_dir
        return FileSystemManager(test_config)
    
    @pytest.mark.asyncio
    async def test_create_directory(self, file_manager):
        """Test directory creation."""
        result = await file_manager.execute(
            "create_directory",
            "test_dir/sub_dir"
        )
        
        assert result["success"] is True
        assert Path(result["path"]).exists()
        assert Path(result["path"]).is_dir()
    
    @pytest.mark.asyncio
    async def test_write_simple_file(self, file_manager):
        """Test simple file writing."""
        result = await file_manager.execute(
            "write_file",
            "test.txt",
            "Hello, World!"
        )
        
        assert result["success"] is True
        assert Path(result["path"]).exists()
        
        with open(result["path"], 'r') as f:
            assert f.read() == "Hello, World!"
    
    @pytest.mark.asyncio
    async def test_write_context_file(self, file_manager):
        """Test context file writing with YAML frontmatter."""
        content = {
            "title": "Test Context",
            "source_url": "https://example.com",
            "language": "en",
            "body": "# Content\n\nThis is the content."
        }
        
        result = await file_manager.execute(
            "write_file",
            "context.md",
            content
        )
        
        assert result["success"] is True
        
        with open(result["path"], 'r') as f:
            file_content = f.read()
            assert "---" in file_content
            assert "title: Test Context" in file_content
            assert "# Content" in file_content
    
    @pytest.mark.asyncio
    async def test_sanitize_path(self, file_manager):
        """Test path sanitization."""
        result = await file_manager.execute(
            "sanitize_path",
            path='test<>:"|?*.txt'
        )
        
        assert result["success"] is True
        assert result["sanitized_path"] == "test_______.txt"
    
    @pytest.mark.asyncio
    async def test_generate_index(self, file_manager):
        """Test index generation."""
        # Create some test files
        await file_manager.execute("write_file", "doc1.md", {"title": "Doc 1", "body": "Content 1"})
        await file_manager.execute("write_file", "doc2.md", {"title": "Doc 2", "body": "Content 2"})
        
        # Generate index
        result = await file_manager.execute("generate_index")
        
        assert result["success"] is True
        index_path = Path(result["path"])
        assert index_path.exists()
        
        with open(index_path, 'r') as f:
            index_content = f.read()
            assert "# Context Index" in index_content
            assert "doc1.md" in index_content
            assert "doc2.md" in index_content
    
    @pytest.mark.asyncio
    async def test_complex_directory_structure(self, file_manager):
        """Test creating complex directory structure."""
        structure = {
            "docs": {
                "api": {},
                "guides": {}
            },
            "examples": {}
        }
        
        result = await file_manager.execute(
            "create_directory",
            "project",
            structure
        )
        
        assert result["success"] is True
        assert Path(result["path"]).exists()
        assert (Path(result["path"]) / "docs" / "api").exists()
        assert (Path(result["path"]) / "docs" / "guides").exists()
        assert (Path(result["path"]) / "examples").exists()