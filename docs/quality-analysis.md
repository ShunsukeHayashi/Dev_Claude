# Quality Analysis System Documentation

## Overview

The Quality Analysis System is a comprehensive tool for evaluating the quality of extracted context files in the YAML Context Engineering Agent. It provides detailed metrics, identifies issues, and suggests improvements.

## Features

### 1. Quality Metrics

The system evaluates content across four key dimensions:

- **Completeness Score (0-100)**: Measures if all expected content and metadata are present
- **Consistency Score (0-100)**: Evaluates structural consistency and formatting uniformity
- **Accuracy Score (0-100)**: Validates metadata correctness and content accuracy
- **Usability Score (0-100)**: Assesses readability, navigation, and user-friendliness

### 2. Issue Detection

Issues are categorized by:

#### Severity Levels
- **Critical**: Prevents proper usage (missing content, broken structure)
- **High**: Significantly impacts quality (major inconsistencies)
- **Medium**: Noticeable issues (minor structural problems)
- **Low**: Minor improvements (formatting, style)

#### Categories
- **Structure**: Heading hierarchy, section organization
- **Content**: Missing sections, empty content, broken links
- **Metadata**: Invalid fields, format errors, missing required data
- **Formatting**: Inconsistent styles, code block issues

### 3. Improvement Suggestions

The system provides:
- Prioritized action items
- Specific recommendations for each issue
- Quick wins for immediate improvements
- Long-term enhancement strategies

## Usage

### Command Line Interface

```bash
# Analyze a single file
yaml-context quality -f generated_contexts/example.md

# Analyze all files in a directory
yaml-context quality -d generated_contexts/

# Filter by severity
yaml-context quality -f file.md --severity high

# Save report to file
yaml-context quality -d generated_contexts/ -o quality-report.md
```

### MCP Tool Usage

In Claude Code:
```
mcp__yaml-context-engineering__quality_analyzer action="analyze_file" file_path="example.md"
mcp__yaml-context-engineering__quality_analyzer action="analyze_directory" directory_path="generated_contexts"
mcp__yaml-context-engineering__quality_analyzer action="suggest_improvements" file_path="example.md"
mcp__yaml-context-engineering__quality_analyzer action="compare_files" file_paths=["file1.md", "file2.md"]
```

### Programmatic Usage

```python
from yaml_context_engineering.quality_analyzer import QualityAnalyzer

analyzer = QualityAnalyzer()

# Analyze single file
report = await analyzer.analyze_file(Path("example.md"))
print(f"Overall Score: {report.metrics.overall_score}/100")

# Analyze directory
reports = await analyzer.analyze_directory(Path("generated_contexts"))
summary = analyzer.generate_summary_report(reports)
```

## Quality Criteria

### Completeness Requirements
- Required metadata fields present
- Minimum content length (100 words)
- Proper heading hierarchy starting with L1
- No empty sections

### Consistency Standards
- Sequential heading hierarchy (no skipped levels)
- Uniform list markers
- Consistent code fence styles
- Matching declared vs actual hierarchy levels

### Accuracy Validation
- Valid ISO timestamp formats
- Proper URL formats
- Correct language detection
- Valid confidence scores (0-1)

### Usability Features
- Table of contents for long documents
- Language-specified code blocks
- Working internal links
- Examples and summaries
- Reasonable sentence length

## Report Format

### Individual File Report
```yaml
timestamp: "2025-08-04T12:00:00Z"
scores:
  overall: 85.5
  completeness: 90
  consistency: 85
  accuracy: 88
  usability: 82
issues:
  - severity: "medium"
    category: "structure"
    description: "Inconsistent L3 heading usage"
    recommendation: "Standardize subsection headings"
improvements:
  - "Add table of contents"
  - "Include more examples"
strengths:
  - "Comprehensive metadata"
  - "Clear structure"
confidence: 0.92
```

### Directory Summary Report
```markdown
# Quality Analysis Summary Report

## Overview
- Files Analyzed: 25
- Average Overall Score: 78.3/100

## Average Scores by Category
- Completeness: 82.1/100
- Consistency: 76.5/100
- Accuracy: 79.8/100
- Usability: 74.9/100

## Issues Summary
- Critical: 2
- High: 8
- Medium: 15
- Low: 32

## Top Performing Files
- api_docs.md: 92.3/100
- tutorial.md: 89.7/100

## Files Needing Attention
- legacy_doc.md: 45.2/100
- incomplete.md: 52.8/100
```

## Best Practices

### For High Quality Scores

1. **Complete Metadata**
   ```yaml
   ---
   title: "Comprehensive Title"
   source_url: "https://valid.url"
   extraction_timestamp: "2025-08-04T10:00:00Z"
   extracted_by: "agent-name"
   hierarchy_levels: ["L1", "L2", "L3"]
   language: "en"
   extraction_confidence: 0.95
   ---
   ```

2. **Proper Structure**
   ```markdown
   # Main Title (L1)
   
   ## Table of Contents
   
   ## Section 1 (L2)
   
   ### Subsection 1.1 (L3)
   ```

3. **Quality Content**
   - Include examples
   - Add summaries
   - Use proper code blocks with language
   - Ensure adequate content length

4. **Navigation Aids**
   - Table of contents for documents > 5 sections
   - Internal links with valid anchors
   - Clear section organization

## Integration with LDD

Quality analysis results are automatically logged to the LDD system:

```yaml
task_name: "Quality Analysis"
status: "Completed"
metrics:
  files_analyzed: 25
  average_score: 78.3
  issues_found: 57
insights:
  - "Common issue: Missing language in code blocks"
  - "Improvement area: Add more examples"
```

## Troubleshooting

### Common Issues

1. **File Not Found**
   - Ensure file path is relative to output directory
   - Check file permissions

2. **Invalid YAML Frontmatter**
   - Validate YAML syntax
   - Ensure proper delimiter (---)

3. **Slow Analysis**
   - Large files may take longer
   - Consider analyzing in batches

### Debug Mode

Enable verbose logging:
```bash
yaml-context quality -f file.md --verbose
```

## Future Enhancements

- Machine learning-based quality prediction
- Custom quality rules configuration
- Integration with CI/CD pipelines
- Real-time quality monitoring
- Automated quality improvement suggestions