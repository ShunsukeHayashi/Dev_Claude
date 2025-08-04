"""Web content fetching tool for YAML Context Engineering."""

import asyncio
import re
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, urlparse

import aiohttp
from bs4 import BeautifulSoup
import html2text
from langdetect import detect
import validators
from tenacity import retry, stop_after_attempt, wait_exponential

from ..config import Config
from ..utils.logging import get_logger


class WebContentFetcher:
    """Tool for fetching web content from URLs."""
    
    def __init__(self, config: Config):
        """Initialize the web content fetcher.
        
        Args:
            config: Server configuration
        """
        self.config = config
        self.logger = get_logger(__name__)
        self.html_converter = html2text.HTML2Text()
        self.html_converter.ignore_links = False
        self.html_converter.ignore_images = True
        self.html_converter.body_width = 0  # No line wrapping
        
        # Session for connection pooling
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=self.config.crawling.timeout_seconds)
            headers = {"User-Agent": self.config.crawling.user_agent}
            self._session = aiohttp.ClientSession(
                timeout=timeout,
                headers=headers
            )
        return self._session
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def _fetch_single_url(self, url: str) -> Dict[str, Any]:
        """Fetch content from a single URL with retry logic.
        
        Args:
            url: URL to fetch
            
        Returns:
            Dictionary with fetched content and metadata
        """
        session = await self._get_session()
        
        try:
            async with session.get(url) as response:
                response.raise_for_status()
                
                # Get content
                content_type = response.headers.get("Content-Type", "")
                if "text/html" in content_type:
                    html_content = await response.text()
                    soup = BeautifulSoup(html_content, "lxml")
                    
                    # Extract metadata
                    title = soup.find("title")
                    title_text = title.string if title else ""
                    
                    meta_description = soup.find("meta", attrs={"name": "description"})
                    description = meta_description.get("content", "") if meta_description else ""
                    
                    # Convert to markdown
                    markdown_content = self.html_converter.handle(html_content)
                    
                    # Detect language
                    try:
                        language = detect(markdown_content[:1000])
                    except:
                        language = "unknown"
                    
                    # Extract URLs
                    extracted_urls = self._extract_urls(soup, url)
                    
                    return {
                        "url": str(response.url),
                        "status_code": response.status,
                        "content": markdown_content,
                        "title": title_text,
                        "meta_description": description,
                        "language": language,
                        "extracted_urls": extracted_urls,
                        "content_type": content_type,
                        "success": True
                    }
                else:
                    # Non-HTML content
                    text_content = await response.text()
                    return {
                        "url": str(response.url),
                        "status_code": response.status,
                        "content": text_content,
                        "title": "",
                        "meta_description": "",
                        "language": "unknown",
                        "extracted_urls": [],
                        "content_type": content_type,
                        "success": True
                    }
                    
        except aiohttp.ClientError as e:
            self.logger.error(f"Failed to fetch URL: {url}", error=str(e))
            return {
                "url": url,
                "status_code": 0,
                "content": "",
                "error": str(e),
                "success": False
            }
    
    def _extract_urls(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract URLs from HTML content.
        
        Args:
            soup: BeautifulSoup object
            base_url: Base URL for resolving relative URLs
            
        Returns:
            List of extracted URLs
        """
        urls = []
        
        # Extract from links
        for link in soup.find_all("a", href=True):
            href = link["href"]
            absolute_url = urljoin(base_url, href)
            
            # Validate URL
            if validators.url(absolute_url):
                urls.append(absolute_url)
        
        # Extract from navigation elements
        for nav in soup.find_all(["nav", "aside"]):
            for link in nav.find_all("a", href=True):
                href = link["href"]
                absolute_url = urljoin(base_url, href)
                if validators.url(absolute_url) and absolute_url not in urls:
                    urls.append(absolute_url)
        
        return urls
    
    async def fetch(self, urls: List[str], timeout: int = 30) -> List[Dict[str, Any]]:
        """Fetch content from multiple URLs.
        
        Args:
            urls: List of URLs to fetch
            timeout: Timeout in seconds
            
        Returns:
            List of results for each URL
        """
        self.logger.info(f"Fetching {len(urls)} URLs", urls=urls)
        
        # Update timeout if different from config
        if timeout != self.config.crawling.timeout_seconds:
            self.config.crawling.timeout_seconds = timeout
        
        # Validate URLs
        valid_urls = []
        results = []
        
        for url in urls:
            if validators.url(url):
                valid_urls.append(url)
            else:
                self.logger.warning(f"Invalid URL: {url}")
                results.append({
                    "url": url,
                    "error": "Invalid URL format",
                    "success": False
                })
        
        # Fetch valid URLs concurrently
        if valid_urls:
            tasks = [self._fetch_single_url(url) for url in valid_urls]
            fetch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in fetch_results:
                if isinstance(result, Exception):
                    results.append({
                        "error": str(result),
                        "success": False
                    })
                else:
                    results.append(result)
        
        self.logger.info(f"Fetched {len(results)} URLs successfully")
        return results
    
    async def close(self) -> None:
        """Close the session."""
        if self._session and not self._session.closed:
            await self._session.close()