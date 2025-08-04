"""File system management tool for YAML Context Engineering."""

import os
import re
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

import aiofiles
import yaml
from ruamel.yaml import YAML

from ..config import Config
from ..utils.logging import get_logger


class FileSystemManager:
    """Tool for managing file system operations."""
    
    def __init__(self, config: Config):
        """Initialize the file system manager.
        
        Args:
            config: Server configuration
        """
        self.config = config
        self.logger = get_logger(__name__)
        self.ruamel_yaml = YAML()
        self.ruamel_yaml.preserve_quotes = True
        self.ruamel_yaml.width = 4096  # Prevent line wrapping
    
    def _sanitize_path_component(self, component: str) -> str:
        """Sanitize a path component for safe file system usage.
        
        Args:
            component: Path component to sanitize
            
        Returns:
            Sanitized path component
        """
        # Remove or replace invalid characters
        sanitized = re.sub(r'[<>:"|?*\x00-\x1f]', '_', component)
        
        # Remove leading/trailing dots and spaces
        sanitized = sanitized.strip('. ')
        
        # Replace multiple underscores with single
        sanitized = re.sub(r'_+', '_', sanitized)
        
        # Limit length
        if len(sanitized) > 255:
            sanitized = sanitized[:255]
        
        # Ensure not empty
        if not sanitized:
            sanitized = "unnamed"
        
        return sanitized
    
    async def _create_directory_structure(self, base_path: Path, structure: Dict[str, Any]) -> None:
        """Create directory structure recursively.
        
        Args:
            base_path: Base path for creation
            structure: Directory structure definition
        """
        base_path.mkdir(parents=True, exist_ok=True)
        
        for name, content in structure.items():
            if isinstance(content, dict):
                # Subdirectory
                subdir = base_path / self._sanitize_path_component(name)
                await self._create_directory_structure(subdir, content)
            else:
                # File placeholder
                file_path = base_path / self._sanitize_path_component(name)
                if not file_path.exists():
                    file_path.touch()
    
    async def _write_context_file(self, file_path: Path, content: Dict[str, Any]) -> None:
        """Write a context file with YAML frontmatter.
        
        Args:
            file_path: Path to write to
            content: Content dictionary with metadata and body
        """
        # Ensure parent directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Prepare frontmatter
        frontmatter = {
            "title": str(content.get("title", "Untitled")),
            "source_url": str(content.get("source_url", "")),
            "last_updated": content.get("last_updated", datetime.utcnow().isoformat() + "Z"),
            "content_type": content.get("content_type", "documentation"),
            "language": content.get("language", "ja"),
            "extraction_confidence": content.get("extraction_confidence", 0.0),
            "agent_version": self.config.server_version,
            "extracted_by": "YAML Context Engineering Agent",
            "extraction_timestamp": datetime.utcnow().isoformat() + "Z",
            "hierarchy_levels": content.get("hierarchy_levels", []),
            "related_sources": content.get("related_sources", []),
            "tags": content.get("tags", [])
        }
        
        # Build file content
        file_content = "---\n"
        
        # Use ruamel.yaml for better formatting
        import io
        stream = io.StringIO()
        self.ruamel_yaml.dump(frontmatter, stream)
        file_content += stream.getvalue()
        
        file_content += "---\n\n"
        file_content += content.get("body", "")
        
        # Write file
        async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
            await f.write(file_content)
        
        self.logger.info(f"Written context file: {file_path}")
    
    async def _generate_index_file(self, directory: Path) -> None:
        """Generate an index file for a directory of context files.
        
        Args:
            directory: Directory to index
        """
        index_content = f"# Context Index\n\n"
        index_content += f"Generated: {datetime.utcnow().isoformat()}Z\n\n"
        
        # Collect all .md files
        md_files = []
        for file_path in directory.rglob("*.md"):
            if file_path.name != "index.md":
                md_files.append(file_path)
        
        # Sort by path
        md_files.sort()
        
        # Group by directory
        current_dir = None
        for file_path in md_files:
            rel_path = file_path.relative_to(directory)
            dir_path = rel_path.parent
            
            if dir_path != current_dir:
                current_dir = dir_path
                if str(dir_path) != ".":
                    index_content += f"\n## {dir_path}\n\n"
            
            # Read frontmatter to get title
            try:
                async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                    content = await f.read()
                
                # Extract title from frontmatter
                if content.startswith("---"):
                    yaml_end = content.find("---", 3)
                    if yaml_end != -1:
                        yaml_content = content[3:yaml_end]
                        metadata = yaml.safe_load(yaml_content)
                        title = metadata.get("title", file_path.stem)
                    else:
                        title = file_path.stem
                else:
                    title = file_path.stem
                
                # Add to index
                index_content += f"- [{title}]({rel_path.as_posix()})\n"
                
            except Exception as e:
                self.logger.warning(f"Failed to read file for index: {file_path}", error=str(e))
                index_content += f"- [{file_path.stem}]({rel_path.as_posix()})\n"
        
        # Write index file
        index_path = directory / "index.md"
        async with aiofiles.open(index_path, 'w', encoding='utf-8') as f:
            await f.write(index_content)
        
        self.logger.info(f"Generated index file: {index_path}")
    
    async def execute(
        self,
        action: str,
        path: Optional[str] = None,
        content: Optional[Any] = None
    ) -> Dict[str, Any]:
        """Execute file system operation.
        
        Args:
            action: Action to perform
            path: Path for the operation
            content: Content for write operations
            
        Returns:
            Operation result
        """
        self.logger.info(f"Executing file system action: {action}", path=path)
        
        try:
            if action == "create_directory":
                if not path:
                    raise ValueError("Path required for create_directory")
                
                # Create directory structure
                base_path = self.config.output.output_base_directory / path
                
                if isinstance(content, dict):
                    # Create complex structure
                    await self._create_directory_structure(base_path, content)
                else:
                    # Simple directory
                    base_path.mkdir(parents=True, exist_ok=True)
                
                return {
                    "success": True,
                    "action": action,
                    "path": str(base_path),
                    "message": "Directory structure created"
                }
            
            elif action == "write_file":
                if not path or content is None:
                    raise ValueError("Path and content required for write_file")
                
                file_path = self.config.output.output_base_directory / path
                
                if isinstance(content, dict) and "body" in content:
                    # Context file with metadata
                    await self._write_context_file(file_path, content)
                else:
                    # Simple file write
                    file_path.parent.mkdir(parents=True, exist_ok=True)
                    async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
                        if isinstance(content, dict):
                            await f.write(yaml.dump(content, default_flow_style=False))
                        else:
                            await f.write(str(content))
                
                return {
                    "success": True,
                    "action": action,
                    "path": str(file_path),
                    "message": "File written successfully"
                }
            
            elif action == "sanitize_path":
                if not path:
                    raise ValueError("Path required for sanitize_path")
                
                # Sanitize each component
                path_obj = Path(path)
                sanitized_parts = [self._sanitize_path_component(part) for part in path_obj.parts]
                sanitized_path = Path(*sanitized_parts)
                
                return {
                    "success": True,
                    "action": action,
                    "original_path": path,
                    "sanitized_path": str(sanitized_path),
                    "message": "Path sanitized"
                }
            
            elif action == "generate_index":
                # Generate index for output directory or specified path
                index_path = self.config.output.output_base_directory
                if path:
                    index_path = index_path / path
                
                await self._generate_index_file(index_path)
                
                return {
                    "success": True,
                    "action": action,
                    "path": str(index_path / "index.md"),
                    "message": "Index generated successfully"
                }
            
            else:
                raise ValueError(f"Unknown action: {action}")
                
        except Exception as e:
            self.logger.error(f"File system operation failed: {action}", error=str(e))
            return {
                "success": False,
                "action": action,
                "error": str(e),
                "message": f"Operation failed: {str(e)}"
            }