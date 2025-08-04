# Claude Code Local Testing Environment

## Overview

This directory contains test scripts and utilities for validating the Claude Code integration with the YAML Context Engineering Agent.

## Test Scripts

### 1. `test-slash-commands.sh`
Tests all slash commands implementation:
- `/extract-context` - URL and file extraction
- `/setup-project` - Project initialization
- `/generate-agent` - Agent generation

**Usage:**
```bash
./test-slash-commands.sh
```

### 2. `test-subagents.sh`
Tests all sub-agent functionality:
- Context Extractor (general purpose)
- API Documentation Specialist
- Tutorial Specialist
- Knowledge Base Specialist
- Quality Analyzer

**Usage:**
```bash
./test-subagents.sh
```

### 3. `test-integration.sh`
Comprehensive integration test that validates:
- Project structure
- Configuration files
- MCP server components
- Claude Code hooks
- LDD system
- Sub-agent configurations

**Usage:**
```bash
./test-integration.sh
```

### 4. `test-hooks.sh`
Located in `.claude/hooks/`, tests all hook scripts:
- Pre-tool-use hooks
- Post-tool-use hooks
- Notification hooks

**Usage:**
```bash
../.claude/hooks/test-hooks.sh
```

## Testing Workflow

### 1. Initial Setup Validation
```bash
# Run integration test first
./test-integration.sh

# This checks:
# - All directories exist
# - Configuration files are in place
# - Python environment is ready
# - Hooks are executable
```

### 2. Component Testing
```bash
# Test individual components
./test-slash-commands.sh  # Slash commands
./test-subagents.sh      # Sub-agents
../.claude/hooks/test-hooks.sh  # Hooks
```

### 3. Manual Testing with Claude Code

#### Testing Slash Commands
In Claude Code, try:
```
/extract-context https://docs.example.com
/setup-project my-new-project
/generate-agent api-docs
```

#### Testing Sub-Agents
Using the Task tool:
```
Task agent=api-docs-specialist "Extract API documentation from https://api.example.com/docs"
Task agent=tutorial-specialist "Process tutorial from ./tutorial.md"
Task agent=quality-analyzer "Analyze ./generated_contexts/example.md"
```

#### Testing Hooks
Hooks should trigger automatically when using tools:
```bash
# This should trigger pre-tool-use-bash hook
ls -la

# This should trigger pre/post write hooks
echo "test" > test.txt
```

## Expected Test Results

### Successful Integration Test
```
✅ Project structure: Complete
✅ Configuration files: Present
✅ MCP server: Configured
✅ Claude Code hooks: Executable
✅ Sub-agents: Registered
✅ LDD system: Initialized
```

### Common Issues and Solutions

#### 1. Python Module Not Found
**Issue:** `MCP server module not in Python path`
**Solution:**
```bash
cd mcp-server
pip install -e .
```

#### 2. Missing config.yaml
**Issue:** `config.yaml (missing)`
**Solution:** Already created during Phase 2-4

#### 3. Hook Permission Denied
**Issue:** `Permission denied` when running hooks
**Solution:**
```bash
chmod +x .claude/hooks/*.sh
```

#### 4. Log Directory Missing
**Issue:** Hook logs not created
**Solution:**
```bash
mkdir -p ~/.claude/logs
mkdir -p .claude/logs
```

## Test Data

### Sample URLs for Testing
```
https://docs.python.org/3/tutorial/
https://api.github.com/
https://nodejs.org/docs/latest/api/
```

### Sample Content Files
Create test files in `test-data/`:
```bash
mkdir -p test-data
echo "# Sample Tutorial" > test-data/tutorial.md
echo '{"api": "v1"}' > test-data/api.json
```

## Debugging

### Check Hook Logs
```bash
# Global logs
tail -f ~/.claude/logs/execution.log

# Project logs
tail -f .claude/logs/*.log
```

### Verify MCP Server
```bash
cd mcp-server
python -m yaml_context_engineering.main --help
```

### Test Individual Tools
```python
# Test MCP tools directly
from yaml_context_engineering.tools import web_content_fetcher
result = web_content_fetcher.fetch_content(["https://example.com"])
print(result)
```

## Performance Testing

### Load Test
```bash
# Test with multiple URLs
time ./test-slash-commands.sh

# Monitor resource usage
top -pid $(pgrep -f yaml_context_engineering)
```

### Memory Usage
```bash
# Check memory consumption
ps aux | grep yaml_context_engineering
```

## Continuous Testing

### Pre-commit Hook
Add to `.git/hooks/pre-commit`:
```bash
#!/bin/bash
./test-claude-code/test-integration.sh
```

### GitHub Actions
See `.github/workflows/` for automated testing

## Next Steps

After successful local testing:

1. **Deploy to Production**
   - Update API keys
   - Configure production URLs
   - Set appropriate log levels

2. **Monitor Performance**
   - Track extraction success rates
   - Monitor response times
   - Analyze quality scores

3. **Iterate and Improve**
   - Collect user feedback
   - Enhance agent prompts
   - Add new specialized agents

## Support

For issues or questions:
- Check logs in `.claude/logs/`
- Review hook outputs
- Consult main README.md
- Open GitHub issue