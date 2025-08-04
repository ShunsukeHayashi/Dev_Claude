"""Tests for quality analyzer."""

import pytest
from pathlib import Path
import tempfile
import asyncio

from yaml_context_engineering.quality_analyzer import (
    QualityAnalyzer, QualityMetrics, QualityIssue, QualityReport
)


@pytest.fixture
def analyzer():
    """Create a quality analyzer instance."""
    return QualityAnalyzer()


@pytest.fixture
def sample_good_content():
    """Sample well-structured content."""
    return """---
title: "API Documentation"
source_url: "https://api.example.com/docs"
extraction_timestamp: "2025-08-04T10:00:00Z"
extracted_by: "test-agent"
hierarchy_levels: ["L1", "L2", "L3"]
language: "en"
extraction_confidence: 0.95
---

# API Documentation

This is a comprehensive API documentation with examples.

## Table of Contents

- [Authentication](#authentication)
- [Endpoints](#endpoints)
- [Error Handling](#error-handling)

## Authentication

All API requests require authentication using Bearer tokens.

### Getting a Token

To obtain an authentication token:

```python
import requests

response = requests.post('https://api.example.com/auth/token', 
    json={'username': 'user', 'password': 'pass'})
token = response.json()['token']
```

## Endpoints

### GET /users

Retrieve a list of users.

**Request:**
```bash
curl -H "Authorization: Bearer TOKEN" https://api.example.com/users
```

**Response:**
```json
{
  "users": [
    {"id": 1, "name": "John Doe"},
    {"id": 2, "name": "Jane Smith"}
  ]
}
```

### POST /users

Create a new user.

## Error Handling

The API uses standard HTTP status codes:

- `200` - Success
- `400` - Bad Request
- `401` - Unauthorized
- `500` - Server Error

## Summary

This API provides a simple interface for user management with secure authentication.
"""


@pytest.fixture
def sample_poor_content():
    """Sample poorly structured content."""
    return """---
title: "Bad Documentation"
source_url: "invalid-url"
---

## Missing H1

Content without proper structure.

### Empty Section

## Another Section

Very short.

```
code without language
```

### Broken Link

See [this section](#nonexistent).
"""


@pytest.mark.asyncio
async def test_quality_metrics_calculation():
    """Test quality metrics calculation."""
    metrics = QualityMetrics(
        completeness_score=80,
        consistency_score=75,
        accuracy_score=90,
        usability_score=85
    )
    
    overall = metrics.calculate_overall()
    assert overall == 82.5
    assert metrics.overall_score == 82.5


@pytest.mark.asyncio
async def test_analyze_good_content(analyzer, sample_good_content):
    """Test analyzing well-structured content."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(sample_good_content)
        f.flush()
        
        report = await analyzer.analyze_file(Path(f.name))
        
        # Check high scores
        assert report.metrics.overall_score >= 80
        assert report.metrics.completeness_score >= 85
        assert report.metrics.consistency_score >= 90
        assert report.metrics.accuracy_score >= 90
        assert report.metrics.usability_score >= 80
        
        # Check for strengths
        assert len(report.strengths) > 0
        
        # Should have minimal issues
        critical_issues = [i for i in report.issues if i.severity == "critical"]
        assert len(critical_issues) == 0
        
        # Clean up
        Path(f.name).unlink()


@pytest.mark.asyncio
async def test_analyze_poor_content(analyzer, sample_poor_content):
    """Test analyzing poorly structured content."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(sample_poor_content)
        f.flush()
        
        report = await analyzer.analyze_file(Path(f.name))
        
        # Check low scores
        assert report.metrics.overall_score < 70
        assert report.metrics.completeness_score < 80
        
        # Should have multiple issues
        assert len(report.issues) > 5
        
        # Check for specific issues
        issue_descriptions = [i.description for i in report.issues]
        assert any("No top-level (L1) headings" in desc for desc in issue_descriptions)
        assert any("Invalid source URL" in desc for desc in issue_descriptions)
        assert any("code blocks without language" in desc for desc in issue_descriptions)
        assert any("broken internal links" in desc for desc in issue_descriptions)
        
        # Should have improvement recommendations
        assert len(report.improvements) > 0
        
        # Clean up
        Path(f.name).unlink()


@pytest.mark.asyncio
async def test_empty_content_handling(analyzer):
    """Test handling of empty content."""
    empty_content = """---
title: "Empty"
---

"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(empty_content)
        f.flush()
        
        report = await analyzer.analyze_file(Path(f.name))
        
        # Should have very low completeness score
        assert report.metrics.completeness_score < 50
        
        # Should flag content as too short
        issue_descriptions = [i.description for i in report.issues]
        assert any("Content too short" in desc for desc in issue_descriptions)
        
        # Clean up
        Path(f.name).unlink()


@pytest.mark.asyncio
async def test_metadata_validation(analyzer):
    """Test metadata validation."""
    content_with_bad_metadata = """---
title: "Test"
source_url: "not-a-valid-url"
extraction_timestamp: "invalid-timestamp"
extraction_confidence: 2.5
hierarchy_levels: ["L1", "L2"]
---

# Test Document

## Section 1

Content here.

### Subsection

More content.
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(content_with_bad_metadata)
        f.flush()
        
        report = await analyzer.analyze_file(Path(f.name))
        
        # Should have metadata issues
        metadata_issues = [i for i in report.issues if i.category == "metadata"]
        assert len(metadata_issues) >= 3
        
        # Check for specific validation errors
        issue_descriptions = [i.description for i in metadata_issues]
        assert any("Invalid source URL" in desc for desc in issue_descriptions)
        assert any("Invalid timestamp format" in desc for desc in issue_descriptions)
        assert any("Invalid extraction confidence" in desc for desc in issue_descriptions)
        
        # Clean up
        Path(f.name).unlink()


@pytest.mark.asyncio
async def test_hierarchy_consistency(analyzer):
    """Test heading hierarchy validation."""
    content_with_bad_hierarchy = """---
title: "Bad Hierarchy"
hierarchy_levels: ["L1", "L2"]
---

### L3 without L1 or L2

Content here.

#### L4 without proper parents

More content.
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(content_with_bad_hierarchy)
        f.flush()
        
        report = await analyzer.analyze_file(Path(f.name))
        
        # Should have low consistency score
        assert report.metrics.consistency_score < 80
        
        # Should have hierarchy issues
        structure_issues = [i for i in report.issues if i.category == "structure"]
        assert len(structure_issues) > 0
        
        # Check metadata mismatch
        metadata_issues = [i for i in report.issues if i.category == "metadata"]
        assert any("hierarchy levels" in i.description.lower() for i in metadata_issues)
        
        # Clean up
        Path(f.name).unlink()


@pytest.mark.asyncio
async def test_analyze_directory(analyzer):
    """Test analyzing multiple files in a directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        
        # Create test files
        good_file = tmpdir_path / "good.md"
        good_file.write_text("""---
title: "Good File"
source_url: "https://example.com"
extraction_timestamp: "2025-08-04T10:00:00Z"
extracted_by: "test"
hierarchy_levels: ["L1"]
---

# Good File

Content here.
""")
        
        poor_file = tmpdir_path / "poor.md"
        poor_file.write_text("""---
title: "Poor File"
---

Short content.
""")
        
        # Skip special files
        special_file = tmpdir_path / "@memory-bank.md"
        special_file.write_text("Special file content")
        
        # Analyze directory
        reports = await analyzer.analyze_directory(tmpdir_path)
        
        # Should have 2 reports (excluding special file)
        assert len(reports) == 2
        
        # Check individual reports
        assert str(good_file) in reports
        assert str(poor_file) in reports
        
        # Good file should have higher score
        assert reports[str(good_file)].metrics.overall_score > reports[str(poor_file)].metrics.overall_score


@pytest.mark.asyncio
async def test_summary_report_generation(analyzer):
    """Test summary report generation."""
    # Create mock reports
    reports = {
        "file1.md": QualityReport(
            file_path="file1.md",
            metrics=QualityMetrics(
                completeness_score=90,
                consistency_score=85,
                accuracy_score=95,
                usability_score=88,
                overall_score=89.5
            ),
            issues=[
                QualityIssue("low", "formatting", "Minor issue", recommendation="Fix it")
            ]
        ),
        "file2.md": QualityReport(
            file_path="file2.md",
            metrics=QualityMetrics(
                completeness_score=60,
                consistency_score=55,
                accuracy_score=70,
                usability_score=50,
                overall_score=58.75
            ),
            issues=[
                QualityIssue("high", "content", "Major issue", recommendation="Fix urgently"),
                QualityIssue("critical", "structure", "Critical issue", recommendation="Immediate fix")
            ]
        )
    }
    
    summary = analyzer.generate_summary_report(reports)
    
    # Check summary contains expected sections
    assert "Quality Analysis Summary Report" in summary
    assert "Files Analyzed: 2" in summary
    assert "Average Overall Score:" in summary
    assert "Issues Summary" in summary
    assert "Top Performing Files" in summary
    assert "Files Needing Attention" in summary
    
    # Check issue counts
    assert "Critical: 1" in summary
    assert "High: 1" in summary
    assert "Low: 1" in summary


@pytest.mark.asyncio
async def test_quality_improvements_detection(analyzer):
    """Test detection of improvement opportunities."""
    content_needing_improvements = """---
title: "Needs Improvement"
source_url: "https://example.com"
extraction_timestamp: "2025-08-04T10:00:00Z"
extracted_by: "test"
hierarchy_levels: ["L1", "L2"]
---

# Document

## Long Section

This is a very long section with multiple paragraphs that could benefit from better organization and structure to improve readability.

## Code Section

```
print("No language specified")
```

## Links Section

See [broken link](#missing).
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(content_needing_improvements)
        f.flush()
        
        report = await analyzer.analyze_file(Path(f.name))
        
        # Should have usability improvements
        assert any("table of contents" in imp.lower() for imp in report.improvements)
        assert any("example" in imp.lower() for imp in report.improvements)
        
        # Should have specific issues
        assert any("code blocks without language" in i.description for i in report.issues)
        assert any("broken internal links" in i.description for i in report.issues)
        
        # Clean up
        Path(f.name).unlink()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])