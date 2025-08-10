# Contributing to Gradual

Thank you for your interest in contributing to the Gradual stress testing framework! This guide will help you get started with contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contribution Workflow](#contribution-workflow)
- [Code Standards](#code-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Release Process](#release-process)
- [Community](#community)

## Code of Conduct

This project adheres to a Code of Conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

### Our Standards

- **Be respectful** and inclusive
- **Be collaborative** and open to feedback
- **Be constructive** in criticism and suggestions
- **Be professional** in all interactions

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Git
- Basic understanding of Python development
- Familiarity with stress testing concepts (helpful but not required)

### Areas to Contribute

We welcome contributions in many areas:

- **Core Framework**: Protocol handlers, assertions, data providers
- **Documentation**: User guides, API reference, examples
- **Testing**: Unit tests, integration tests, performance benchmarks
- **Examples**: Test configurations, use cases, tutorials
- **Bug Fixes**: Issue resolution, performance improvements
- **Features**: New protocols, reporting capabilities, integrations

### Good First Issues

Look for issues labeled with:
- `good first issue` - Beginner-friendly
- `help wanted` - General help needed
- `documentation` - Documentation improvements
- `bug` - Bug fixes

## Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/YOUR_USERNAME/gradual.git
cd gradual

# Add the upstream remote
git remote add upstream https://github.com/Gradual-Load-Testing/gradual.git
```

### 2. Environment Setup

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### 3. Verify Setup

```bash
# Run tests to ensure everything works
make test

# Run linting
make lint

# Run type checking
make typecheck
```

## Contribution Workflow

### 1. Create a Feature Branch

```bash
# Update your main branch
git checkout main
git pull upstream main

# Create a new feature branch
git checkout -b feature/your-feature-name
```

### 2. Make Your Changes

- Write your code following the [Code Standards](#code-standards)
- Add tests for new functionality
- Update documentation as needed
- Ensure all tests pass

### 3. Commit Your Changes

```bash
# Stage your changes
git add .

# Commit with a descriptive message
git commit -m "feat: add custom protocol handler support

- Implement BaseProtocolHandler interface
- Add TCP protocol support
- Include comprehensive tests
- Update documentation"
```

### 4. Push and Create Pull Request

```bash
# Push your branch
git push origin feature/your-feature-name

# Create a Pull Request on GitHub
# Fill out the PR template with details about your changes
```

### 5. Code Review

- Address any feedback from reviewers
- Make requested changes
- Ensure CI checks pass
- Maintainers will merge when ready

## Code Standards

### Python Style Guide

We follow PEP 8 with some modifications:

- **Line Length**: 88 characters (Black default)
- **Import Sorting**: isort with Black profile
- **Type Hints**: Required for public APIs
- **Docstrings**: Google-style docstrings

### Code Formatting

```bash
# Format code with Black
make format
# or
black src/ tests/

# Sort imports
make sort-imports
# or
isort src/ tests/
```

### Linting and Type Checking

```bash
# Run all quality checks
make quality

# Run specific checks
make lint      # flake8
make typecheck # mypy
make test      # pytest
```

### Pre-commit Hooks

The project uses pre-commit hooks to ensure code quality:

```bash
# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

## Testing Guidelines

### Test Structure

```python
import pytest
from gradual.base import BaseProtocolHandler

class TestCustomProtocolHandler:
    """Test the custom protocol handler implementation."""
    
    def test_initialization(self):
        """Test handler initialization with config."""
        config = {"timeout": 30}
        handler = CustomProtocolHandler(config)
        assert handler.config == config
    
    def test_execute_request_success(self):
        """Test successful request execution."""
        handler = CustomProtocolHandler({})
        result = handler.execute_request({"message": "test"})
        assert result["status"] == "success"
    
    def test_execute_request_failure(self):
        """Test request execution failure."""
        handler = CustomProtocolHandler({})
        result = handler.execute_request({})
        assert result["status"] == "error"
```

### Test Requirements

- **Coverage**: Aim for >90% code coverage
- **Naming**: Use descriptive test names and docstrings
- **Isolation**: Tests should be independent and repeatable
- **Mocking**: Mock external dependencies appropriately
- **Fixtures**: Use pytest fixtures for common setup

### Running Tests

```bash
# Run all tests
make test

# Run specific test files
pytest tests/test_protocols.py

# Run with coverage
pytest --cov=src/gradual --cov-report=html

# Run performance tests
pytest tests/benchmarks/ -m "not slow"
```

## Documentation

### Code Documentation

- **Docstrings**: Use Google-style docstrings for all public methods
- **Type Hints**: Include type hints for function parameters and return values
- **Examples**: Provide usage examples in docstrings
- **Exceptions**: Document all exceptions that may be raised

Example:

```python
def execute_test_scenario(self, scenario: dict, user_data: dict) -> dict:
    """Execute a test scenario with user data.
    
    Args:
        scenario: Scenario configuration dictionary containing
                 steps, assertions, and metadata.
        user_data: User-specific data for the scenario execution.
        
    Returns:
        Dictionary containing execution results including
        status, response time, and any extracted data.
        
    Raises:
        ScenarioExecutionError: If scenario execution fails due to
                               configuration or runtime errors.
        ValidationError: If response validation fails for any
                        assertion in the scenario.
        
    Example:
        >>> scenario = {"steps": [{"request": {"method": "GET"}}]}
        >>> user_data = {"user_id": "123"}
        >>> result = runner.execute_test_scenario(scenario, user_data)
        >>> print(result["status"])
        'success'
    """
    pass
```

### API Documentation

- **Completeness**: Document all public APIs
- **Examples**: Include usage examples
- **Breaking Changes**: Document any breaking changes
- **Migration Guides**: Provide migration paths for major changes

### User Documentation

- **Clarity**: Write clear, concise instructions
- **Examples**: Provide real-world examples
- **Troubleshooting**: Include common issues and solutions
- **Screenshots**: Add visual aids where helpful

## Pull Request Guidelines

### PR Title and Description

```markdown
## Description
Brief description of what this PR accomplishes.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed
- [ ] Documentation updated

## Checklist
- [ ] Code follows the style guidelines
- [ ] Self-review of code completed
- [ ] Code is commented, particularly in hard-to-understand areas
- [ ] Corresponding changes to documentation made
- [ ] Changes generate no new warnings
- [ ] Tests added that prove fix is effective or feature works
- [ ] New and existing unit tests pass locally
- [ ] AI assistance (e.g., Cursor, ChatGPT, Claude) was used in making these changes (please specify tools in the PR description)
```

### Review Process

1. **Automated Checks**: Ensure CI checks pass
2. **Code Review**: Address reviewer feedback
3. **Testing**: Verify functionality works as expected
4. **Documentation**: Update relevant documentation
5. **Merge**: Maintainers will merge when ready

## Release Process

### Version Management

We use semantic versioning (MAJOR.MINOR.PATCH):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Checklist

- [ ] All tests pass
- [ ] Documentation is up to date
- [ ] Changelog is updated
- [ ] Version is bumped in `pyproject.toml`
- [ ] Release notes are written
- [ ] GitHub release is created
- [ ] PyPI package is published (maintainers only)

### Creating a Release

```bash
# Update version
# Edit pyproject.toml

# Build package
make build

# Test installation
pip install dist/*.whl

# Create git tag
git tag v1.0.0
git push origin v1.0.0

# Publish to PyPI (maintainers only)
make publish
```

## Community

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: Questions and general discussion
- **GitHub Pull Requests**: Code contributions
- **Email**: Direct contact with maintainers

### Getting Help

- **Documentation**: Start with the user guide and API reference
- **Examples**: Check the examples directory for usage patterns
- **Issues**: Search existing issues for similar problems
- **Discussions**: Ask questions in GitHub Discussions

### Recognition

Contributors are recognized in several ways:

- **Contributors List**: GitHub automatically tracks contributors
- **Release Notes**: Contributors are credited in release notes
- **Documentation**: Contributors are listed in documentation
- **Community**: Active contributors are invited to join the maintainer team

## Code of Conduct Enforcement

### Reporting Issues

If you experience or witness unacceptable behavior:

1. **Document**: Record the incident with details
2. **Report**: Contact project maintainers privately
3. **Escalate**: If needed, escalate to GitHub support

### Enforcement Actions

Maintainers may take actions including:

- **Warning**: Private or public warning
- **Temporary Ban**: Temporary restriction from participation
- **Permanent Ban**: Permanent removal from the project

## Next Steps

1. **Read the Documentation**: Familiarize yourself with the project
2. **Join Discussions**: Participate in GitHub Discussions
3. **Pick an Issue**: Start with a good first issue
4. **Make a Contribution**: Submit your first pull request
5. **Stay Engaged**: Continue contributing and helping others

Thank you for contributing to Gradual! Your contributions help make stress testing more accessible and powerful for everyone.
