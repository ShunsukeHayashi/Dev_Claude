# YAML Context Engineering MCP Server API Documentation

## Overview

The YAML Context Engineering MCP Server provides a comprehensive set of tools for extracting hierarchical context from various sources and generating structured YAML documentation.

## MCP Tools

### 1. web_content_fetcher

Fetches web page content from specified URLs.

**Parameters:**
- `urls` (array of strings, required): List of URLs to fetch
- `timeout` (integer, optional): Timeout in seconds (default: 30)

**Returns:**
```json
[
  {
    "url": "string",
    "status_code": "integer",
    "content": "string (markdown)",
    "title": "string",
    "meta_description": "string",
    "language": "string",
    "extracted_urls": ["array of strings"],
    "content_type": "string",
    "success": "boolean",
    "error": "string (if failed)"
  }
]
```

**Example:**
```json
{
  "tool": "web_content_fetcher",
  "params": {
    "urls": ["https://docs.example.com/api", "https://example.com/guide"],
    "timeout": 60
  }
}
```

### 2. llm_structure_extractor

Extracts hierarchical heading structure from text content.

**Parameters:**
- `content` (string, required): Text content to analyze
- `target_schema` (object, optional): Target structure schema
- `extraction_config` (object, optional): Extraction configuration
  - `granularity` (string): "L1_only", "L1_L2", "L1_L2_L3", "full_hierarchy"
  - `summarization` (string): "none", "brief", "detailed", "full"

**Returns:**
```json
{
  "structured_headings": [
    {
      "level": "integer",
      "text": "string",
      "content": "string",
      "children": ["array of heading objects"],
      "line_number": "integer"
    }
  ],
  "content_summary": "string",
  "extracted_entities": {
    "urls": ["array"],
    "emails": ["array"],
    "code_blocks": ["array"],
    "key_terms": ["array"]
  },
  "confidence_score": "float",
  "format_detected": "string",
  "total_headings": "integer",
  "hierarchy_levels": ["array of integers"]
}
```

**Example:**
```json
{
  "tool": "llm_structure_extractor",
  "params": {
    "content": "# Main Title\n\nContent...\n\n## Section 1\n\nMore content...",
    "extraction_config": {
      "granularity": "L1_L2",
      "summarization": "detailed"
    }
  }
}
```

### 3. url_discovery_engine

Discovers and prioritizes URLs from content.

**Parameters:**
- `content` (string, required): Content to search for URLs
- `base_domain` (string, required): Base domain for context
- `filters` (array of strings, optional): URL filter patterns (regex)

**Returns:**
```json
[
  {
    "url": "string",
    "priority_score": "float (0.0-1.0)",
    "relation_type": "string (internal|subdomain|external)",
    "estimated_content_value": "string (high|medium|low|unknown)",
    "context_snippet": "string"
  }
]
```

**Example:**
```json
{
  "tool": "url_discovery_engine",
  "params": {
    "content": "Check our API docs at https://docs.example.com/api...",
    "base_domain": "example.com",
    "filters": ["api", "docs"]
  }
}
```

### 4. file_system_manager

Manages file system operations for context storage.

**Parameters:**
- `action` (string, required): Action to perform
  - "create_directory": Create directory structure
  - "write_file": Write content to file
  - "sanitize_path": Sanitize path components
  - "generate_index": Generate index file
- `path` (string, optional): Path for the operation
- `content` (string/object, optional): Content for write operations

**Returns:**
```json
{
  "success": "boolean",
  "action": "string",
  "path": "string (absolute path)",
  "message": "string",
  "error": "string (if failed)"
}
```

**Examples:**

#### Create Directory
```json
{
  "tool": "file_system_manager",
  "params": {
    "action": "create_directory",
    "path": "project/docs",
    "content": {
      "api": {},
      "guides": {}
    }
  }
}
```

#### Write Context File
```json
{
  "tool": "file_system_manager",
  "params": {
    "action": "write_file",
    "path": "contexts/api-doc.md",
    "content": {
      "title": "API Documentation",
      "source_url": "https://example.com/api",
      "language": "en",
      "body": "# API Documentation\n\nContent here..."
    }
  }
}
```

## Configuration

The server can be configured through environment variables:

```bash
# Server settings
MCP_SERVER_NAME=yaml-context-engineering
MCP_LOG_LEVEL=INFO

# Crawling settings
MCP_MAX_CRAWL_DEPTH=3
MCP_CRAWL_DELAY=1.0
MCP_MAX_PAGES_PER_DOMAIN=100
MCP_TIMEOUT_SECONDS=30

# Extraction settings
MCP_CONTEXT_GRANULARITY=L1_L2
MCP_CONTENT_SUMMARIZATION=detailed

# Output settings
MCP_OUTPUT_DIRECTORY=generated_contexts
```

## Output Format

Generated context files follow this YAML frontmatter structure:

```yaml
---
title: "Extracted Content Title"
source_url: "https://source.url"
last_updated: "2025-01-15T10:30:00Z"
content_type: "documentation"
language: "ja"
extraction_confidence: 0.95
agent_version: "1.0.0"
extracted_by: "YAML Context Engineering Agent"
extraction_timestamp: "2025-08-03T12:00:00Z"
hierarchy_levels: ["L1", "L2", "L3"]
related_sources: 
  - "https://related1.url"
  - "https://related2.url"
tags: 
  - "tag1"
  - "tag2"
---

# Content

Hierarchically organized markdown content...
```

## Error Handling

All tools return error information in a consistent format:

```json
{
  "error": "Error message",
  "tool": "tool_name",
  "success": false
}
```

Common error scenarios:
- Invalid URL format
- Network timeouts
- Invalid configuration
- File system permissions
- Content parsing failures

## Best Practices

1. **URL Fetching**
   - Batch URLs for efficiency
   - Set appropriate timeouts
   - Handle rate limiting

2. **Structure Extraction**
   - Choose appropriate granularity
   - Use summarization for large content
   - Check confidence scores

3. **URL Discovery**
   - Provide accurate base domain
   - Use filters to reduce noise
   - Review priority scores

4. **File Management**
   - Sanitize paths for safety
   - Generate indexes for navigation
   - Use consistent naming conventions

## Example Workflow

```python
# 1. Fetch web content
urls = ["https://docs.example.com/api", "https://docs.example.com/guide"]
fetch_result = web_content_fetcher(urls=urls, timeout=60)

# 2. Extract structure from each page
for page in fetch_result:
    if page["success"]:
        structure = llm_structure_extractor(
            content=page["content"],
            extraction_config={"granularity": "L1_L2"}
        )
        
        # 3. Discover related URLs
        urls = url_discovery_engine(
            content=page["content"],
            base_domain="example.com"
        )
        
        # 4. Save structured content
        file_system_manager(
            action="write_file",
            path=f"contexts/{page['title']}.md",
            content={
                "title": page["title"],
                "source_url": page["url"],
                "body": generate_markdown(structure)
            }
        )

# 5. Generate index
file_system_manager(action="generate_index")
```