#!/bin/bash

# Setup script for Gradual documentation
# This script installs dependencies and sets up the documentation environment

set -e

echo "🚀 Setting up Gradual documentation environment..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.9"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ Python $REQUIRED_VERSION or higher is required. Found: $PYTHON_VERSION"
    exit 1
fi

echo "✅ Python $PYTHON_VERSION found"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
else
    echo "📦 Using existing virtual environment..."
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip setuptools wheel

# Install documentation dependencies
echo "📚 Installing documentation dependencies..."
pip install -r requirements-docs.txt

# Install Gradual in development mode
echo "🔧 Installing Gradual in development mode..."
pip install -e ".[dev]"

# Verify installation
echo "✅ Verifying installation..."
python -c "import mkdocs; print(f'MkDocs version: {mkdocs.__version__}')"
python -c "import gradual; print('Gradual package imported successfully')"

echo ""
echo "🎉 Documentation environment setup complete!"
echo ""
echo "📖 Available commands:"
echo "  make docs        - Build the documentation"
echo "  make docs-serve  - Start local documentation server"
echo "  make docs-deploy - Deploy to GitHub Pages"
echo ""
echo "🔧 API Documentation Generation:"
echo "  python generate_api_docs.py  - Generate/update API documentation"
echo "  make docs-api               - Generate/update API documentation (Makefile target)"
echo "  # This script automatically discovers all modules in the gradual package"
echo "  # and generates corresponding API documentation files in docs/api/"
echo ""
echo "🌐 To view documentation locally:"
echo "  make docs-serve"
echo "  # Then open http://127.0.0.1:8000 in your browser"
echo ""
echo "📚 Documentation files are in the docs/ directory"
echo "   - index.md          - Main documentation page"
echo "   - user_guide.md     - User guide"
echo "   - dev_guide.md      - Development guide"
echo "   - api/              - API reference (auto-generated)"
echo "     - overview.md     - API overview and module listing"
echo "     - *.md            - Individual module documentation"
echo "   - examples.md       - Usage examples"
echo "   - contributing.md   - Contributing guide"
echo ""
echo "🔄 To keep API docs up-to-date:"
echo "  # Run this after making changes to the codebase"
echo "  python generate_api_docs.py"
echo "  # OR use the Makefile target:"
echo "  make docs-api"
echo "  make docs-serve      # View updated documentation"
