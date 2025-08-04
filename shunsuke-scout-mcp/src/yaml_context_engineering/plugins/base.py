"""Base classes for plugin system."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any, Optional, List, Callable
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class PluginType(Enum):
    """Types of plugins supported."""
    
    EXTRACTOR = "extractor"          # Content extraction plugins
    FORMATTER = "formatter"          # Output formatting plugins
    VALIDATOR = "validator"          # Content validation plugins
    ENHANCER = "enhancer"           # Content enhancement plugins
    ANALYZER = "analyzer"           # Analysis plugins
    INTEGRATION = "integration"     # Third-party integrations


@dataclass
class PluginMetadata:
    """Metadata for a plugin."""
    
    name: str
    version: str
    type: PluginType
    description: str
    author: str
    dependencies: List[str] = None
    config_schema: Dict[str, Any] = None
    enabled: bool = True
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.config_schema is None:
            self.config_schema = {}


class Plugin(ABC):
    """Base class for all plugins."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the plugin.
        
        Args:
            config: Plugin-specific configuration
        """
        self.config = config or {}
        self._metadata = None
        self._hooks = {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    @property
    @abstractmethod
    def metadata(self) -> PluginMetadata:
        """Return plugin metadata."""
        pass
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the plugin.
        
        This method is called when the plugin is loaded.
        Use it to set up resources, validate config, etc.
        """
        pass
    
    @abstractmethod
    async def shutdown(self) -> None:
        """Shutdown the plugin.
        
        This method is called when the plugin is unloaded.
        Use it to clean up resources.
        """
        pass
    
    def register_hook(self, hook_name: str, callback: Callable) -> None:
        """Register a hook callback.
        
        Args:
            hook_name: Name of the hook
            callback: Callback function
        """
        if hook_name not in self._hooks:
            self._hooks[hook_name] = []
        self._hooks[hook_name].append(callback)
        self.logger.debug(f"Registered hook: {hook_name}")
    
    async def trigger_hook(self, hook_name: str, *args, **kwargs) -> List[Any]:
        """Trigger all callbacks for a hook.
        
        Args:
            hook_name: Name of the hook
            *args: Positional arguments for callbacks
            **kwargs: Keyword arguments for callbacks
            
        Returns:
            List of results from callbacks
        """
        results = []
        if hook_name in self._hooks:
            for callback in self._hooks[hook_name]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        result = await callback(*args, **kwargs)
                    else:
                        result = callback(*args, **kwargs)
                    results.append(result)
                except Exception as e:
                    self.logger.error(f"Hook {hook_name} callback failed: {e}")
        return results
    
    def validate_config(self) -> bool:
        """Validate plugin configuration against schema.
        
        Returns:
            True if valid, False otherwise
        """
        # Basic implementation - can be overridden
        schema = self.metadata.config_schema
        if not schema:
            return True
        
        # Check required fields
        for field, field_schema in schema.items():
            if field_schema.get("required", False) and field not in self.config:
                self.logger.error(f"Missing required config field: {field}")
                return False
        
        return True


class ExtractorPlugin(Plugin):
    """Base class for content extraction plugins."""
    
    @abstractmethod
    async def can_extract(self, source: str) -> bool:
        """Check if this plugin can extract from the given source.
        
        Args:
            source: Source URL or identifier
            
        Returns:
            True if can extract, False otherwise
        """
        pass
    
    @abstractmethod
    async def extract(self, source: str, **kwargs) -> Dict[str, Any]:
        """Extract content from the source.
        
        Args:
            source: Source to extract from
            **kwargs: Additional extraction parameters
            
        Returns:
            Extracted content and metadata
        """
        pass


class FormatterPlugin(Plugin):
    """Base class for output formatting plugins."""
    
    @abstractmethod
    def get_supported_formats(self) -> List[str]:
        """Get list of supported output formats.
        
        Returns:
            List of format identifiers (e.g., ["yaml", "json", "xml"])
        """
        pass
    
    @abstractmethod
    async def format(self, content: Dict[str, Any], format: str, **kwargs) -> str:
        """Format content to the specified format.
        
        Args:
            content: Content to format
            format: Target format
            **kwargs: Additional formatting options
            
        Returns:
            Formatted content as string
        """
        pass


class ValidatorPlugin(Plugin):
    """Base class for content validation plugins."""
    
    @abstractmethod
    async def validate(self, content: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Validate content.
        
        Args:
            content: Content to validate
            **kwargs: Additional validation parameters
            
        Returns:
            Validation result with errors and warnings
        """
        pass


class EnhancerPlugin(Plugin):
    """Base class for content enhancement plugins."""
    
    @abstractmethod
    async def enhance(self, content: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Enhance content.
        
        Args:
            content: Content to enhance
            **kwargs: Additional enhancement parameters
            
        Returns:
            Enhanced content
        """
        pass


class AnalyzerPlugin(Plugin):
    """Base class for analysis plugins."""
    
    @abstractmethod
    async def analyze(self, content: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Analyze content.
        
        Args:
            content: Content to analyze
            **kwargs: Additional analysis parameters
            
        Returns:
            Analysis results
        """
        pass


class IntegrationPlugin(Plugin):
    """Base class for third-party integration plugins."""
    
    @abstractmethod
    async def connect(self) -> bool:
        """Connect to the third-party service.
        
        Returns:
            True if connected successfully
        """
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from the third-party service."""
        pass
    
    @abstractmethod
    async def sync(self, content: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Sync content with the third-party service.
        
        Args:
            content: Content to sync
            **kwargs: Additional sync parameters
            
        Returns:
            Sync result
        """
        pass


# Hook definitions
class Hooks:
    """Standard hooks that plugins can register for."""
    
    # Content processing hooks
    PRE_EXTRACT = "pre_extract"
    POST_EXTRACT = "post_extract"
    PRE_FORMAT = "pre_format"
    POST_FORMAT = "post_format"
    
    # File system hooks
    PRE_WRITE = "pre_write"
    POST_WRITE = "post_write"
    PRE_READ = "pre_read"
    POST_READ = "post_read"
    
    # Analysis hooks
    PRE_ANALYZE = "pre_analyze"
    POST_ANALYZE = "post_analyze"
    
    # Server lifecycle hooks
    SERVER_START = "server_start"
    SERVER_STOP = "server_stop"
    PLUGIN_LOADED = "plugin_loaded"
    PLUGIN_UNLOADED = "plugin_unloaded"


import asyncio