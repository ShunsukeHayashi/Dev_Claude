# Contributing to YAML Context Engineering Agent

Thank you for your interest in contributing to the YAML Context Engineering Agent! This document provides guidelines and instructions for contributing.

## 🤝 Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct:
- Be respectful and inclusive
- Welcome newcomers and help them get started
- Focus on constructive criticism
- Respect differing viewpoints and experiences

## 🚀 Getting Started

1. **Fork the repository**
   ```bash
   gh repo fork yaml-context-engineering/agent
   ```

2. **Clone your fork**
   ```bash
   git clone https://github.com/YOUR_USERNAME/yaml-context-engineering-agent.git
   cd yaml-context-engineering-agent
   ```

3. **Set up development environment**
   ```bash
   # Python environment
   cd mcp-server
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e ".[dev]"
   
   # Install pre-commit hooks
   pre-commit install
   ```

4. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

## 📝 Development Workflow

### 1. Planning
- Check existing issues and PRs
- Discuss major changes in an issue first
- Follow the project's architecture patterns

### 2. Implementation
- Write clean, documented code
- Follow existing code style
- Add tests for new functionality
- Update documentation as needed

### 3. Testing
```bash
# Run all tests
./test-claude-code/test-integration.sh

# Run specific tests
cd mcp-server
pytest tests/test_your_feature.py

# Check code quality
ruff check .
black --check .
mypy .
```

### 4. Commit Guidelines
We follow conventional commits:
```
type(scope): subject

body

footer
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test additions/changes
- `chore`: Maintenance tasks

Example:
```bash
git commit -m "feat(mcp-server): Add caching for web content fetcher"
```

### 5. Pull Request
1. Push your branch
   ```bash
   git push origin feature/your-feature-name
   ```

2. Create PR with:
   - Clear title following commit convention
   - Description of changes
   - Link to related issues
   - Screenshots if applicable

3. PR template:
   ```markdown
   ## Description
   Brief description of changes
   
   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Breaking change
   - [ ] Documentation update
   
   ## Testing
   - [ ] Unit tests pass
   - [ ] Integration tests pass
   - [ ] Manual testing completed
   
   ## Checklist
   - [ ] Code follows project style
   - [ ] Self-review completed
   - [ ] Documentation updated
   - [ ] Tests added/updated
   ```

## 🏗️ Architecture Guidelines

### MCP Server Development
- Keep tools focused and single-purpose
- Use async/await for I/O operations
- Implement proper error handling
- Add comprehensive logging

### Claude Code Integration
- Follow slash command patterns
- Keep sub-agents specialized
- Test hooks thoroughly
- Document all configurations

### GitHub Actions
- Keep workflows modular
- Use job dependencies wisely
- Cache dependencies
- Add proper error handling

## 🧪 Testing Requirements

### Unit Tests
- Minimum 80% coverage for new code
- Test edge cases and error conditions
- Use appropriate mocks and fixtures

### Integration Tests
- Test tool interactions
- Verify Claude Code integration
- Check workflow automation

### Documentation Tests
- Verify examples work
- Check for broken links
- Validate configuration samples

## 📚 Documentation

### Code Documentation
- Add docstrings to all public functions
- Include type hints
- Provide usage examples

### User Documentation
- Update relevant .md files
- Add examples for new features
- Include troubleshooting tips

### API Documentation
- Document new MCP tools
- Update parameter descriptions
- Include response examples

## 🐛 Reporting Issues

### Bug Reports
Include:
- Clear description
- Steps to reproduce
- Expected vs actual behavior
- Environment details
- Error messages/logs

### Feature Requests
Include:
- Use case description
- Proposed solution
- Alternative approaches
- Potential impacts

## 🎯 Areas for Contribution

### High Priority
- Performance optimization
- Additional sub-agents
- Test coverage improvement
- Documentation enhancement

### Good First Issues
- Documentation updates
- Simple bug fixes
- Test additions
- Code style improvements

### Advanced
- New MCP tools
- Complex integrations
- Architecture improvements
- Plugin system development

## 📋 Review Process

1. **Automated Checks**
   - CI/CD pipeline must pass
   - Code quality checks
   - Security scanning

2. **Claude Review**
   - Automatic PR review
   - Suggestions and feedback

3. **Human Review**
   - Architecture alignment
   - Code quality
   - Documentation completeness

## 🏆 Recognition

Contributors are recognized in:
- CONTRIBUTORS.md file
- Release notes
- Project documentation

## 💬 Communication

- **Issues**: Bug reports and features
- **Discussions**: General questions
- **PR Comments**: Code-specific discussion

## 📜 License

By contributing, you agree that your contributions will be licensed under the project's MIT License.

---

Thank you for contributing to YAML Context Engineering Agent! 🎉