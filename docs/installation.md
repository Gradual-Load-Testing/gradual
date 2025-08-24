# Installation Guide

This guide covers everything you need to install and set up Gradual for stress testing your applications and systems.

## Prerequisites

Before installing Gradual, ensure you have the following:

- **Python 3.9 or higher** - Gradual requires Python 3.9+ for modern language features
- **pip package manager** - For installing Python packages
- **Git** - For cloning the repository (if installing from source)
- **System dependencies** - May vary based on your operating system

## Installation Methods

### Method 1: Install from Source (Recommended for Development)

```bash
# Clone the repository
git clone https://github.com/Gradual-Load-Testing/gradual.git
cd gradual

# Install in development mode with core features
pip install -e ".[dev,bokeh,websockets]"
```

### Method 2: Install from PyPI (Coming Soon)

```bash
# Install the latest stable version
pip install gradual-load-testing

# Install with all optional dependencies
pip install gradual-load-testing[all]
```

### Method 3: Install in Virtual Environment (Recommended for Production)

```bash
# Create a virtual environment
python -m venv gradual-env

# Activate the virtual environment
# On Linux/macOS:
source gradual-env/bin/activate
# On Windows:
gradual-env\Scripts\activate

# Install Gradual
pip install -e ".[dev,bokeh,websockets]"
```

## Dependency Management

### Core Dependencies

The following dependencies are automatically installed with the core package:

- **gevent** – High-performance asynchronous I/O and concurrency
- **requests** – User-friendly HTTP client for Python

### Optional Dependencies

Install additional features by specifying extra dependencies:

```bash
# For kerb and oidc (coming soon) authentication support
pip install -e ".[auth]"

# For distributed testing across multiple machines
pip install -e ".[distributed]"

# For advanced metrics collection and analysis
pip install -e ".[metrics]"

# For all optional features
pip install -e ".[all]"
```

### Development Dependencies

For contributing to Gradual or running tests:

```bash
# Install development dependencies
pip install -e ".[dev]"

# This includes:
# - pytest for testing
# - black for code formatting
# - flake8 for linting
# - mypy for type checking
# - pre-commit for git hooks
```

## Platform-Specific Installation

### Linux (Ubuntu/Debian)

```bash
# Update package list
sudo apt update

# Install system dependencies
sudo apt install python3-pip python3-venv git

# Install Gradual
pip3 install -e ".[dev,bokeh,websockets]"
```

### Linux (CentOS/RHEL/Fedora)

```bash
# Install system dependencies
sudo yum install python3-pip python3-venv git
# or for newer versions:
sudo dnf install python3-pip python3-venv git

# Install Gradual
pip3 install -e ".[dev,bokeh,websockets]"
```

### macOS

```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python and Git
brew install python git

# Install Gradual
pip3 install -e ".[dev,bokeh,websockets]"
```

### Windows

```bash
# Install Python from https://python.org
# Install Git from https://git-scm.com

# Open Command Prompt or PowerShell
pip install -e ".[dev,bokeh,websockets]"
```

## Docker Installation

If you prefer using Docker:

```bash
# Pull the official image (when available)
docker pull gradual/gradual:latest

# Run a container
docker run -it --rm gradual/gradual:latest stress-run --help

# Mount your test configurations
docker run -it --rm -v $(pwd):/tests gradual/gradual:latest stress-run --test_config /tests/my_test.yaml --request_config /tests/requests.yaml
```

## Verification

After installation, verify that Gradual is working correctly:

```bash
# Check if stress-run command is available
stress-run --version

# Check if stress-dashboard command is available
stress-dashboard --version

# Run a simple test to verify functionality
stress-run --help
```

## Troubleshooting Installation

### Common Issues

#### Permission Errors

```bash
# Use --user flag to install in user directory
pip install --user -e ".[dev,bokeh,websockets]"

# Or use sudo (not recommended for production)
sudo pip install -e ".[dev,bokeh,websockets]"
```

#### Python Version Issues

```bash
# Check your Python version
python --version
python3 --version

# Use specific Python version
python3.9 -m pip install -e ".[dev,bokeh,websockets]"
```

#### Dependency Conflicts

```bash
# Create a fresh virtual environment
python -m venv fresh-env
source fresh-env/bin/activate  # Linux/macOS
# fresh-env\Scripts\activate  # Windows

# Install with --no-deps to avoid conflicts
pip install -e ".[dev,bokeh,websockets]" --no-deps
```

#### Network Issues

```bash
# Use alternative package index
pip install -e ".[dev,bokeh,websockets]" -i https://pypi.org/simple/

# Or use a mirror
pip install -e ".[dev,bokeh,websockets]" -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

## Next Steps

After successful installation:

1. **Read the [Getting Started Guide](getting_started.md)** to run your first test
2. **Explore the [User Guide](user_guide.md)** for detailed usage information
3. **Check out [Examples](examples.md)** for real-world use cases
4. **Join the community** for support and discussions

## Support

If you encounter installation issues:

- Check the [GitHub Issues](https://github.com/Gradual-Load-Testing/gradual/issues)
- Review the [Troubleshooting section](user_guide.md#troubleshooting)
- Join the [community discussions](https://github.com/Gradual-Load-Testing/gradual/discussions)
