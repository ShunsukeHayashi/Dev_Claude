"""LLM-based structure extraction tool for YAML Context Engineering."""

import re
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
import json

from ..config import Config
from ..utils.logging import get_logger


@dataclass
class HeadingNode:
    """Represents a heading in the document structure."""
    level: int
    text: str
    content: str = ""
    children: List["HeadingNode"] = field(default_factory=list)
    line_number: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "level": self.level,
            "text": self.text,
            "content": self.content,
            "children": [child.to_dict() for child in self.children],
            "line_number": self.line_number
        }


class LLMStructureExtractor:
    """Tool for extracting hierarchical structure from text content."""
    
    def __init__(self, config: Config):
        """Initialize the structure extractor.
        
        Args:
            config: Server configuration
        """
        self.config = config
        self.logger = get_logger(__name__)
        
        # Heading patterns for different formats
        self.heading_patterns = {
            "markdown": re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE),
            "html": re.compile(r"<h([1-6]).*?>(.*?)</h[1-6]>", re.IGNORECASE | re.DOTALL),
            "rst": re.compile(r"^(.+)\n([=\-~`#\"^+*]{3,})$", re.MULTILINE),
            "asciidoc": re.compile(r"^(={1,6})\s+(.+)$", re.MULTILINE)
        }
    
    def _detect_format(self, content: str) -> str:
        """Detect the format of the content.
        
        Args:
            content: Text content
            
        Returns:
            Detected format type
        """
        # Check for HTML tags
        if re.search(r"<h[1-6].*?>", content, re.IGNORECASE):
            return "html"
        
        # Check for Markdown headers
        if re.search(r"^#{1,6}\s+", content, re.MULTILINE):
            return "markdown"
        
        # Check for reStructuredText
        if re.search(r"^.+\n[=\-~`#\"^+*]{3,}$", content, re.MULTILINE):
            return "rst"
        
        # Check for AsciiDoc
        if re.search(r"^={1,6}\s+", content, re.MULTILINE):
            return "asciidoc"
        
        # Default to markdown
        return "markdown"
    
    def _extract_markdown_headings(self, content: str) -> List[Tuple[int, str, int]]:
        """Extract headings from Markdown content.
        
        Args:
            content: Markdown content
            
        Returns:
            List of (level, text, line_number) tuples
        """
        headings = []
        lines = content.split("\n")
        
        for i, line in enumerate(lines):
            match = self.heading_patterns["markdown"].match(line)
            if match:
                level = len(match.group(1))
                text = match.group(2).strip()
                headings.append((level, text, i + 1))
        
        return headings
    
    def _extract_html_headings(self, content: str) -> List[Tuple[int, str, int]]:
        """Extract headings from HTML content.
        
        Args:
            content: HTML content
            
        Returns:
            List of (level, text, line_number) tuples
        """
        headings = []
        
        for match in self.heading_patterns["html"].finditer(content):
            level = int(match.group(1))
            text = re.sub(r"<.*?>", "", match.group(2)).strip()
            # Approximate line number
            line_number = content[:match.start()].count("\n") + 1
            headings.append((level, text, line_number))
        
        return headings
    
    def _build_hierarchy(self, headings: List[Tuple[int, str, int]], content_lines: List[str]) -> List[HeadingNode]:
        """Build hierarchical structure from flat heading list.
        
        Args:
            headings: List of (level, text, line_number) tuples
            content_lines: Original content lines
            
        Returns:
            List of root heading nodes
        """
        if not headings:
            return []
        
        root_nodes = []
        stack = []  # Stack of (level, node) tuples
        
        for i, (level, text, line_num) in enumerate(headings):
            # Extract content between this heading and the next
            start_line = line_num
            if i + 1 < len(headings):
                end_line = headings[i + 1][2] - 1
            else:
                end_line = len(content_lines)
            
            # Get content, excluding the heading line itself
            content = "\n".join(content_lines[start_line:end_line]).strip()
            
            node = HeadingNode(level=level, text=text, content=content, line_number=line_num)
            
            # Find parent node
            while stack and stack[-1][0] >= level:
                stack.pop()
            
            if stack:
                # Add as child to parent
                stack[-1][1].children.append(node)
            else:
                # Add as root node
                root_nodes.append(node)
            
            stack.append((level, node))
        
        return root_nodes
    
    def _filter_by_granularity(self, nodes: List[HeadingNode], granularity: str) -> List[HeadingNode]:
        """Filter nodes based on granularity setting.
        
        Args:
            nodes: List of heading nodes
            granularity: Granularity level
            
        Returns:
            Filtered list of nodes
        """
        max_level = {
            "L1_only": 1,
            "L1_L2": 2,
            "L1_L2_L3": 3,
            "full_hierarchy": 6
        }.get(granularity, 6)
        
        def filter_node(node: HeadingNode) -> Optional[HeadingNode]:
            if node.level > max_level:
                return None
            
            filtered_children = []
            for child in node.children:
                filtered_child = filter_node(child)
                if filtered_child:
                    filtered_children.append(filtered_child)
            
            return HeadingNode(
                level=node.level,
                text=node.text,
                content=node.content,
                children=filtered_children,
                line_number=node.line_number
            )
        
        return [filter_node(node) for node in nodes if filter_node(node)]
    
    def _summarize_content(self, content: str, level: str) -> str:
        """Summarize content based on summarization level.
        
        Args:
            content: Content to summarize
            level: Summarization level
            
        Returns:
            Summarized content
        """
        if level == "none":
            return ""
        elif level == "brief":
            # Return first paragraph or 200 characters
            paragraphs = content.split("\n\n")
            if paragraphs:
                return paragraphs[0][:200] + "..." if len(paragraphs[0]) > 200 else paragraphs[0]
            return content[:200] + "..." if len(content) > 200 else content
        elif level == "detailed":
            # Return first 500 characters or 2 paragraphs
            paragraphs = content.split("\n\n")
            if len(paragraphs) >= 2:
                return "\n\n".join(paragraphs[:2])
            return content[:500] + "..." if len(content) > 500 else content
        else:  # full
            return content
    
    async def extract(
        self,
        content: str,
        target_schema: Optional[Dict[str, Any]] = None,
        extraction_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Extract hierarchical structure from content.
        
        Args:
            content: Text content to analyze
            target_schema: Optional target structure schema
            extraction_config: Optional extraction configuration
            
        Returns:
            Extracted structure with metadata
        """
        self.logger.info("Extracting structure from content", 
                        content_length=len(content))
        
        # Merge extraction config with defaults
        config = {
            "granularity": self.config.extraction.context_granularity,
            "summarization": self.config.extraction.content_summarization,
            **(extraction_config or {})
        }
        
        # Detect content format
        format_type = self._detect_format(content)
        self.logger.debug(f"Detected format: {format_type}")
        
        # Extract headings based on format
        if format_type == "markdown":
            headings = self._extract_markdown_headings(content)
        elif format_type == "html":
            headings = self._extract_html_headings(content)
        else:
            # Fallback to markdown
            headings = self._extract_markdown_headings(content)
        
        # Build hierarchy
        content_lines = content.split("\n")
        hierarchy = self._build_hierarchy(headings, content_lines)
        
        # Filter by granularity
        filtered_hierarchy = self._filter_by_granularity(hierarchy, config["granularity"])
        
        # Calculate extraction confidence
        total_headings = len(headings)
        confidence = min(1.0, total_headings / 10.0) if total_headings > 0 else 0.0
        
        # Extract entities (simplified version)
        entities = self._extract_entities(content)
        
        result = {
            "structured_headings": [node.to_dict() for node in filtered_hierarchy],
            "content_summary": self._summarize_content(content, config["summarization"]),
            "extracted_entities": entities,
            "confidence_score": confidence,
            "format_detected": format_type,
            "total_headings": total_headings,
            "hierarchy_levels": list(set(h[0] for h in headings)) if headings else []
        }
        
        self.logger.info("Structure extraction completed", 
                        total_headings=total_headings,
                        confidence=confidence)
        
        return result
    
    def _extract_entities(self, content: str) -> Dict[str, List[str]]:
        """Extract named entities from content.
        
        Args:
            content: Text content
            
        Returns:
            Dictionary of entity types and values
        """
        entities = {
            "urls": [],
            "emails": [],
            "code_blocks": [],
            "key_terms": []
        }
        
        # Extract URLs
        url_pattern = re.compile(r"https?://[^\s<>\"{}|\\^`\[\]]+")
        entities["urls"] = list(set(url_pattern.findall(content)))
        
        # Extract emails
        email_pattern = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")
        entities["emails"] = list(set(email_pattern.findall(content)))
        
        # Extract code blocks (markdown style)
        code_pattern = re.compile(r"```[\s\S]*?```", re.MULTILINE)
        entities["code_blocks"] = [match.group() for match in code_pattern.finditer(content)]
        
        # Extract key terms (simplified - look for capitalized multi-word phrases)
        term_pattern = re.compile(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b")
        potential_terms = term_pattern.findall(content)
        # Filter common phrases
        entities["key_terms"] = [term for term in set(potential_terms) 
                               if len(term.split()) <= 4 and term.count(" ") <= 3]
        
        return entities