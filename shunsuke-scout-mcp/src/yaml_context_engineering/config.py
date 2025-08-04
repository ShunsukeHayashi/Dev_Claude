"""Configuration management for YAML Context Engineering MCP Server."""

import os
from dataclasses import dataclass, field
from typing import List, Optional
from pathlib import Path


@dataclass
class CrawlingConfig:
    """Configuration for web crawling."""
    
    max_crawl_depth: int = 3
    target_domain_patterns: List[str] = field(default_factory=list)
    crawl_delay_seconds: float = 1.0
    max_pages_per_domain: int = 100
    timeout_seconds: int = 30
    user_agent: str = "YAML-Context-Engineering-Agent/1.0"


@dataclass
class ExtractionConfig:
    """Configuration for content extraction."""
    
    context_granularity: str = "L1_L2"  # L1_only, L1_L2, L1_L2_L3, full_hierarchy
    content_summarization: str = "detailed"  # none, brief, detailed, full
    language_detection: bool = True
    extract_metadata: bool = True
    max_content_length: int = 100000


@dataclass
class OutputConfig:
    """Configuration for output generation."""
    
    output_base_directory: Path = field(default_factory=lambda: Path("generated_contexts"))
    yaml_template_path: Optional[Path] = None
    create_index_files: bool = True
    prettify_output: bool = True


@dataclass
class Config:
    """Main configuration class."""
    
    server_name: str = "shunsuke-scout-mcp"
    server_version: str = "1.0.0"
    log_level: str = "INFO"
    
    crawling: CrawlingConfig = field(default_factory=CrawlingConfig)
    extraction: ExtractionConfig = field(default_factory=ExtractionConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
    
    @classmethod
    def from_env(cls) -> "Config":
        """Create configuration from environment variables."""
        config = cls()
        
        # Server settings
        config.server_name = os.getenv("MCP_SERVER_NAME", config.server_name)
        config.log_level = os.getenv("MCP_LOG_LEVEL", config.log_level)
        
        # Crawling settings
        if max_depth := os.getenv("MCP_MAX_CRAWL_DEPTH"):
            config.crawling.max_crawl_depth = int(max_depth)
        if delay := os.getenv("MCP_CRAWL_DELAY"):
            config.crawling.crawl_delay_seconds = float(delay)
        if max_pages := os.getenv("MCP_MAX_PAGES_PER_DOMAIN"):
            config.crawling.max_pages_per_domain = int(max_pages)
        
        # Extraction settings
        if granularity := os.getenv("MCP_CONTEXT_GRANULARITY"):
            config.extraction.context_granularity = granularity
        if summarization := os.getenv("MCP_CONTENT_SUMMARIZATION"):
            config.extraction.content_summarization = summarization
        
        # Output settings
        if output_dir := os.getenv("MCP_OUTPUT_DIRECTORY"):
            config.output.output_base_directory = Path(output_dir)
        
        return config
    
    def validate(self) -> None:
        """Validate configuration values."""
        # Validate context granularity
        valid_granularities = ["L1_only", "L1_L2", "L1_L2_L3", "full_hierarchy"]
        if self.extraction.context_granularity not in valid_granularities:
            raise ValueError(f"Invalid context_granularity: {self.extraction.context_granularity}")
        
        # Validate content summarization
        valid_summarizations = ["none", "brief", "detailed", "full"]
        if self.extraction.content_summarization not in valid_summarizations:
            raise ValueError(f"Invalid content_summarization: {self.extraction.content_summarization}")
        
        # Validate crawl depth
        if not 1 <= self.crawling.max_crawl_depth <= 10:
            raise ValueError(f"max_crawl_depth must be between 1 and 10")
        
        # Validate crawl delay
        if self.crawling.crawl_delay_seconds < 0.5:
            raise ValueError(f"crawl_delay_seconds must be at least 0.5")