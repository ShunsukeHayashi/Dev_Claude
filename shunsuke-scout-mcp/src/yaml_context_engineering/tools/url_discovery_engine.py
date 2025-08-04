"""URL discovery engine for YAML Context Engineering."""

import re
from typing import List, Dict, Any, Set
from urllib.parse import urlparse, urljoin
from collections import defaultdict

import validators

from ..config import Config
from ..utils.logging import get_logger


class URLDiscoveryEngine:
    """Tool for discovering and prioritizing URLs from content."""
    
    def __init__(self, config: Config):
        """Initialize the URL discovery engine.
        
        Args:
            config: Server configuration
        """
        self.config = config
        self.logger = get_logger(__name__)
        
        # URL extraction patterns
        self.url_patterns = [
            # Standard URLs
            re.compile(r'https?://[^\s<>"\'{}\|\\^`\[\]]+'),
            # Markdown links
            re.compile(r'\[([^\]]+)\]\((https?://[^)]+)\)'),
            # HTML links
            re.compile(r'<a[^>]+href=["\']?(https?://[^"\'>\s]+)["\']?[^>]*>'),
            # Plain domain references
            re.compile(r'\b(?:www\.)?([a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)+)(?:/[^\s]*)?')
        ]
        
        # Priority keywords for URL scoring
        self.priority_keywords = {
            "high": ["api", "documentation", "docs", "reference", "guide", "tutorial", "manual"],
            "medium": ["example", "sample", "demo", "overview", "introduction", "getting-started"],
            "low": ["blog", "news", "about", "contact", "privacy", "terms"]
        }
    
    def _extract_urls(self, content: str, base_domain: str) -> Set[str]:
        """Extract all URLs from content.
        
        Args:
            content: Text content
            base_domain: Base domain for resolving relative URLs
            
        Returns:
            Set of unique URLs
        """
        urls = set()
        base_url = f"https://{base_domain}" if not base_domain.startswith("http") else base_domain
        
        # Extract with different patterns
        for pattern in self.url_patterns:
            matches = pattern.findall(content)
            for match in matches:
                if isinstance(match, tuple):
                    # For patterns that capture groups
                    url = match[1] if len(match) > 1 else match[0]
                else:
                    url = match
                
                # Handle plain domain references
                if not url.startswith(("http://", "https://")):
                    if validators.domain(url.split("/")[0]):
                        url = f"https://{url}"
                    else:
                        # Might be a relative path
                        url = urljoin(base_url, url)
                
                # Validate and add
                if validators.url(url):
                    urls.add(url)
        
        return urls
    
    def _calculate_priority_score(self, url: str, context: str = "") -> float:
        """Calculate priority score for a URL.
        
        Args:
            url: URL to score
            context: Optional context where URL was found
            
        Returns:
            Priority score (0.0 to 1.0)
        """
        score = 0.5  # Base score
        url_lower = url.lower()
        context_lower = context.lower() if context else ""
        
        # Check URL path for keywords
        for priority, keywords in self.priority_keywords.items():
            for keyword in keywords:
                if keyword in url_lower:
                    if priority == "high":
                        score += 0.3
                    elif priority == "medium":
                        score += 0.2
                    else:
                        score -= 0.1
        
        # Check context for relevance
        if context:
            # URLs in headings or near important keywords get higher scores
            if any(keyword in context_lower for keyword in ["important", "required", "must", "essential"]):
                score += 0.2
        
        # Penalize certain URL patterns
        if any(pattern in url_lower for pattern in ["#", "?page=", "login", "signin", "register"]):
            score -= 0.2
        
        # Prefer documentation subdirectories
        if any(path in url_lower for path in ["/docs/", "/api/", "/reference/", "/guide/"]):
            score += 0.2
        
        # Normalize score
        return max(0.0, min(1.0, score))
    
    def _determine_relation_type(self, url: str, base_domain: str) -> str:
        """Determine the relation type of URL to base domain.
        
        Args:
            url: URL to check
            base_domain: Base domain
            
        Returns:
            Relation type
        """
        parsed_url = urlparse(url)
        parsed_base = urlparse(base_domain if base_domain.startswith("http") else f"https://{base_domain}")
        
        if parsed_url.netloc == parsed_base.netloc:
            return "internal"
        elif parsed_url.netloc.endswith(f".{parsed_base.netloc}"):
            return "subdomain"
        elif parsed_base.netloc.endswith(f".{parsed_url.netloc}"):
            return "parent_domain"
        else:
            return "external"
    
    def _estimate_content_value(self, url: str) -> str:
        """Estimate the content value of a URL.
        
        Args:
            url: URL to evaluate
            
        Returns:
            Estimated content value category
        """
        url_lower = url.lower()
        
        # High value patterns
        if any(pattern in url_lower for pattern in [
            "/api", "/docs", "/documentation", "/reference", "/spec",
            "/tutorial", "/guide", "/manual", "/quickstart"
        ]):
            return "high"
        
        # Medium value patterns
        if any(pattern in url_lower for pattern in [
            "/example", "/sample", "/demo", "/overview", "/about",
            "/introduction", "/features", "/faq"
        ]):
            return "medium"
        
        # Low value patterns
        if any(pattern in url_lower for pattern in [
            "/blog", "/news", "/press", "/contact", "/privacy",
            "/terms", "/legal", "/careers", "/jobs"
        ]):
            return "low"
        
        return "unknown"
    
    async def discover(
        self,
        content: str,
        base_domain: str,
        filters: List[str] = None
    ) -> List[Dict[str, Any]]:
        """Discover and prioritize URLs from content.
        
        Args:
            content: Content to search for URLs
            base_domain: Base domain for context
            filters: Optional URL filter patterns
            
        Returns:
            List of discovered URLs with metadata
        """
        self.logger.info(f"Discovering URLs from content", 
                        content_length=len(content),
                        base_domain=base_domain)
        
        # Extract all URLs
        urls = self._extract_urls(content, base_domain)
        
        # Apply filters if provided
        if filters:
            filtered_urls = set()
            for url in urls:
                if any(re.search(pattern, url) for pattern in filters):
                    filtered_urls.add(url)
            urls = filtered_urls
        
        # Apply domain pattern restrictions from config
        if self.config.crawling.target_domain_patterns:
            domain_filtered = set()
            for url in urls:
                if any(re.search(pattern, url) for pattern in self.config.crawling.target_domain_patterns):
                    domain_filtered.add(url)
            urls = domain_filtered
        
        # Score and analyze each URL
        url_data = []
        for url in urls:
            # Find context around URL in content
            context = ""
            url_index = content.find(url)
            if url_index != -1:
                # Get 100 characters before and after
                start = max(0, url_index - 100)
                end = min(len(content), url_index + len(url) + 100)
                context = content[start:end]
            
            url_info = {
                "url": url,
                "priority_score": self._calculate_priority_score(url, context),
                "relation_type": self._determine_relation_type(url, base_domain),
                "estimated_content_value": self._estimate_content_value(url),
                "context_snippet": context.strip() if context else ""
            }
            url_data.append(url_info)
        
        # Sort by priority score
        url_data.sort(key=lambda x: x["priority_score"], reverse=True)
        
        # Group by relation type for reporting
        by_relation = defaultdict(int)
        for item in url_data:
            by_relation[item["relation_type"]] += 1
        
        self.logger.info(f"Discovered {len(url_data)} URLs",
                        by_relation=dict(by_relation))
        
        return url_data