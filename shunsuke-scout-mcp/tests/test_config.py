"""Tests for configuration management."""

import pytest
import os
from pathlib import Path

from yaml_context_engineering.config import Config, CrawlingConfig, ExtractionConfig, OutputConfig


class TestConfig:
    """Test configuration class."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = Config()
        
        assert config.server_name == "yaml-context-engineering"
        assert config.server_version == "1.0.0"
        assert config.log_level == "INFO"
        
        # Test crawling defaults
        assert config.crawling.max_crawl_depth == 3
        assert config.crawling.crawl_delay_seconds == 1.0
        assert config.crawling.max_pages_per_domain == 100
        assert config.crawling.timeout_seconds == 30
        
        # Test extraction defaults
        assert config.extraction.context_granularity == "L1_L2"
        assert config.extraction.content_summarization == "detailed"
        assert config.extraction.language_detection is True
        assert config.extraction.extract_metadata is True
        
        # Test output defaults
        assert config.output.output_base_directory == Path("generated_contexts")
        assert config.output.create_index_files is True
    
    def test_config_from_env(self, monkeypatch):
        """Test configuration from environment variables."""
        # Set environment variables
        monkeypatch.setenv("MCP_SERVER_NAME", "test-server")
        monkeypatch.setenv("MCP_LOG_LEVEL", "DEBUG")
        monkeypatch.setenv("MCP_MAX_CRAWL_DEPTH", "5")
        monkeypatch.setenv("MCP_CRAWL_DELAY", "2.5")
        monkeypatch.setenv("MCP_MAX_PAGES_PER_DOMAIN", "200")
        monkeypatch.setenv("MCP_CONTEXT_GRANULARITY", "full_hierarchy")
        monkeypatch.setenv("MCP_CONTENT_SUMMARIZATION", "brief")
        monkeypatch.setenv("MCP_OUTPUT_DIRECTORY", "/tmp/test_output")
        
        config = Config.from_env()
        
        assert config.server_name == "test-server"
        assert config.log_level == "DEBUG"
        assert config.crawling.max_crawl_depth == 5
        assert config.crawling.crawl_delay_seconds == 2.5
        assert config.crawling.max_pages_per_domain == 200
        assert config.extraction.context_granularity == "full_hierarchy"
        assert config.extraction.content_summarization == "brief"
        assert config.output.output_base_directory == Path("/tmp/test_output")
    
    def test_config_validation_valid(self):
        """Test configuration validation with valid values."""
        config = Config()
        config.validate()  # Should not raise
        
        # Test edge cases
        config.extraction.context_granularity = "L1_only"
        config.extraction.content_summarization = "none"
        config.crawling.max_crawl_depth = 1
        config.crawling.crawl_delay_seconds = 0.5
        config.validate()  # Should not raise
    
    def test_config_validation_invalid_granularity(self):
        """Test configuration validation with invalid granularity."""
        config = Config()
        config.extraction.context_granularity = "invalid"
        
        with pytest.raises(ValueError, match="Invalid context_granularity"):
            config.validate()
    
    def test_config_validation_invalid_summarization(self):
        """Test configuration validation with invalid summarization."""
        config = Config()
        config.extraction.content_summarization = "invalid"
        
        with pytest.raises(ValueError, match="Invalid content_summarization"):
            config.validate()
    
    def test_config_validation_invalid_crawl_depth(self):
        """Test configuration validation with invalid crawl depth."""
        config = Config()
        
        # Too low
        config.crawling.max_crawl_depth = 0
        with pytest.raises(ValueError, match="max_crawl_depth must be between"):
            config.validate()
        
        # Too high
        config.crawling.max_crawl_depth = 11
        with pytest.raises(ValueError, match="max_crawl_depth must be between"):
            config.validate()
    
    def test_config_validation_invalid_crawl_delay(self):
        """Test configuration validation with invalid crawl delay."""
        config = Config()
        config.crawling.crawl_delay_seconds = 0.3
        
        with pytest.raises(ValueError, match="crawl_delay_seconds must be at least"):
            config.validate()


class TestCrawlingConfig:
    """Test crawling configuration."""
    
    def test_default_values(self):
        """Test default crawling configuration values."""
        config = CrawlingConfig()
        
        assert config.max_crawl_depth == 3
        assert config.target_domain_patterns == []
        assert config.crawl_delay_seconds == 1.0
        assert config.max_pages_per_domain == 100
        assert config.timeout_seconds == 30
        assert config.user_agent == "YAML-Context-Engineering-Agent/1.0"


class TestExtractionConfig:
    """Test extraction configuration."""
    
    def test_default_values(self):
        """Test default extraction configuration values."""
        config = ExtractionConfig()
        
        assert config.context_granularity == "L1_L2"
        assert config.content_summarization == "detailed"
        assert config.language_detection is True
        assert config.extract_metadata is True
        assert config.max_content_length == 100000


class TestOutputConfig:
    """Test output configuration."""
    
    def test_default_values(self):
        """Test default output configuration values."""
        config = OutputConfig()
        
        assert config.output_base_directory == Path("generated_contexts")
        assert config.yaml_template_path is None
        assert config.create_index_files is True
        assert config.prettify_output is True