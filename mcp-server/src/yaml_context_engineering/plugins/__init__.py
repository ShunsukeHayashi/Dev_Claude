"""Plugin system for YAML Context Engineering."""

from .base import Plugin, PluginMetadata, PluginType
from .manager import PluginManager
from .registry import PluginRegistry

__all__ = [
    "Plugin",
    "PluginMetadata", 
    "PluginType",
    "PluginManager",
    "PluginRegistry"
]