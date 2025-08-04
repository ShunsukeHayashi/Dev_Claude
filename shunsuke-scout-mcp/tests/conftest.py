"""Pytest configuration and fixtures."""

import pytest
from pathlib import Path
import tempfile
import shutil
from typing import Generator

from yaml_context_engineering.config import Config


@pytest.fixture
def test_config() -> Config:
    """Create test configuration."""
    config = Config()
    config.log_level = "DEBUG"
    config.crawling.timeout_seconds = 5
    config.crawling.max_crawl_depth = 2
    config.extraction.context_granularity = "L1_L2"
    return config


@pytest.fixture
def temp_output_dir() -> Generator[Path, None, None]:
    """Create temporary output directory."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_html_content() -> str:
    """Sample HTML content for testing."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Page</title>
        <meta name="description" content="This is a test page">
    </head>
    <body>
        <h1>Main Title</h1>
        <p>Introduction paragraph.</p>
        
        <h2>Section 1</h2>
        <p>Content for section 1.</p>
        
        <h3>Subsection 1.1</h3>
        <p>Content for subsection 1.1.</p>
        
        <h2>Section 2</h2>
        <p>Content for section 2.</p>
        
        <nav>
            <a href="/page1">Page 1</a>
            <a href="/page2">Page 2</a>
            <a href="https://example.com">External Link</a>
        </nav>
    </body>
    </html>
    """


@pytest.fixture
def sample_markdown_content() -> str:
    """Sample Markdown content for testing."""
    return """# Main Title

Introduction paragraph with some text.

## Section 1

Content for section 1 with [a link](https://example.com).

### Subsection 1.1

Content for subsection 1.1.

```python
def hello_world():
    print("Hello, world!")
```

## Section 2

Content for section 2.

- List item 1
- List item 2
- List item 3

### Subsection 2.1

More content here.
"""


@pytest.fixture
def expected_structure() -> list:
    """Expected structure for sample markdown."""
    return [
        {
            "level": 1,
            "text": "Main Title",
            "content": "Introduction paragraph with some text.",
            "children": [],
            "line_number": 1
        },
        {
            "level": 2,
            "text": "Section 1",
            "content": "Content for section 1 with [a link](https://example.com).",
            "children": [
                {
                    "level": 3,
                    "text": "Subsection 1.1",
                    "content": "Content for subsection 1.1.\n\n```python\ndef hello_world():\n    print(\"Hello, world!\")\n```",
                    "children": [],
                    "line_number": 9
                }
            ],
            "line_number": 5
        },
        {
            "level": 2,
            "text": "Section 2",
            "content": "Content for section 2.\n\n- List item 1\n- List item 2\n- List item 3",
            "children": [
                {
                    "level": 3,
                    "text": "Subsection 2.1",
                    "content": "More content here.",
                    "children": [],
                    "line_number": 25
                }
            ],
            "line_number": 17
        }
    ]