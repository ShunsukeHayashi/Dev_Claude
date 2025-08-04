# Claude Code Sub-Agents Documentation

## Overview

This directory contains specialized sub-agents for the YAML Context Engineering Agent project. Each agent is optimized for specific types of content extraction and processing.

## Available Sub-Agents

### 1. Context Extractor (General Purpose)
- **File**: `context-extractor.md`
- **Purpose**: General hierarchical content extraction from any source
- **Best For**: 
  - Mixed content types
  - Initial exploration
  - General documentation
  - Unknown content structures

### 2. Quality Analyzer
- **File**: `quality-analyzer.md`
- **Purpose**: Assess and improve extracted content quality
- **Best For**:
  - Post-extraction validation
  - Quality scoring
  - Improvement recommendations
  - Content consistency checks

### 3. API Documentation Specialist
- **File**: `api-docs-specialist.md`
- **Purpose**: Extract and structure API documentation
- **Best For**:
  - REST APIs
  - GraphQL schemas
  - OpenAPI/Swagger docs
  - SDK documentation
- **Special Features**:
  - Endpoint grouping
  - Authentication extraction
  - Code sample processing
  - Rate limit documentation

### 4. Tutorial Specialist
- **File**: `tutorial-specialist.md`
- **Purpose**: Process tutorials, guides, and learning materials
- **Best For**:
  - Step-by-step guides
  - How-to articles
  - Getting started docs
  - Workshop materials
- **Special Features**:
  - Learning path mapping
  - Prerequisite extraction
  - Exercise identification
  - Progress tracking

### 5. Knowledge Base Specialist
- **File**: `knowledge-base-specialist.md`
- **Purpose**: Extract KB articles, FAQs, and troubleshooting guides
- **Best For**:
  - Support documentation
  - FAQ sections
  - Troubleshooting guides
  - Configuration references
- **Special Features**:
  - Problem-solution mapping
  - Search optimization
  - Category extraction
  - Related article linking

## Using Sub-Agents

### Via Claude Code

```bash
# Use the Task tool to invoke a sub-agent
Task agent=api-docs-specialist "Extract API documentation from https://api.example.com/docs"

# Quality check after extraction
Task agent=quality-analyzer "Analyze the extracted content in generated_contexts/api_example_com.md"
```

### Via Slash Commands

The `/generate-agent` command can create custom agents based on these templates:

```bash
/generate-agent api-docs
/generate-agent tutorial
/generate-agent custom "Legal document analyzer"
```

## Agent Selection Guide

Choose the right agent based on your content:

| Content Type | Recommended Agent | Why |
|-------------|-------------------|-----|
| API Reference | api-docs-specialist | Optimized for endpoint extraction |
| Learning Materials | tutorial-specialist | Handles step-by-step structures |
| Support Docs | knowledge-base-specialist | FAQ and troubleshooting focus |
| Mixed/Unknown | context-extractor | General purpose, adaptive |
| Quality Check | quality-analyzer | Post-processing validation |

## Creating Custom Agents

To create a new specialized agent:

1. **Copy a template**:
   ```bash
   cp context-extractor.md custom-agent.md
   ```

2. **Customize the system prompt**:
   - Define specific expertise
   - List extraction priorities
   - Specify output format

3. **Update extraction strategy**:
   - Add domain-specific patterns
   - Define quality criteria
   - Include specialized tools

4. **Register in settings.json**:
   ```json
   "custom-agent": {
     "file": "agents/custom-agent.md",
     "enabled": true,
     "description": "Your custom description"
   }
   ```

## Agent Architecture

Each agent follows this structure:

```markdown
# Agent Name

## Name
{agent-identifier}

## Description
{Brief description}

## System Prompt
{Detailed instructions and expertise}

## Tools Available
{List of allowed tools}

## Extraction Strategy
{Step-by-step approach}

## Output Format
{Expected YAML frontmatter and content structure}

## Quality Criteria
{Validation rules}

## Best Practices
{Guidelines for optimal results}
```

## Performance Tips

1. **Use specialized agents** for better accuracy
2. **Chain agents** for complex workflows:
   - Extract with specialist
   - Validate with quality-analyzer
   - Enhance with context-extractor

3. **Monitor logs** in `.claude/logs/subagent.log`

4. **Test agents** before production use:
   ```bash
   Task agent=tutorial-specialist "Test with sample content"
   ```

## Troubleshooting

### Agent not found
- Check file exists in `.claude/agents/`
- Verify registration in `settings.json`
- Ensure proper file permissions

### Poor extraction quality
- Use quality-analyzer for assessment
- Choose more specialized agent
- Adjust system prompt if needed

### Performance issues
- Check log files for errors
- Reduce extraction scope
- Use appropriate granularity level

## Future Agents (Planned)

- **technical-spec-specialist**: Technical specifications and RFCs
- **changelog-specialist**: Version history and release notes
- **code-docs-specialist**: Code documentation and comments
- **data-schema-specialist**: Database schemas and data models

## Contributing

To contribute a new agent:
1. Follow the agent template structure
2. Include comprehensive documentation
3. Add usage examples
4. Test with diverse content
5. Submit PR with example outputs