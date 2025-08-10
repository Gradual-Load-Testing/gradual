# Stress Testing Framework

General Python Stress Testing Framework

## Quick Installation

```bash
# Clone the repository
git clone https://github.com/Gradual-Load-Testing/Gradual.git
cd gradual

# Set up virtual environment and install dependencies
make setup

# Alternatively, install directly
pip install -e ".[dev,bokeh,websockets,notebook]"


# Optional: Install authentication dependencies
pip install -e ".[auth]"      # Install all authentication methods
pip install -e ".[kerberos]"  # Install only Kerberos authentication
```

## Building the Package

```bash
# Build the package
make build

# Or manually
python -m build
```

## Usage Examples

### Basic Example

### Using Command Line Interface

```bash
# Run a stress test using a YAML configuration
stress-run --test_config examples/api_test.yaml --request_config examples/requests.yaml

# Start the monitoring dashboard
stress-dashboard --mode websocket  # or --mode bokeh
```

## Development Guide

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/Gradual-Load-Testing/Gradual.git
cd gradual

# Install development dependencies
make setup

# Only for the first time
pre-commit install

# Run tests
make test

# Format code
make format

# Run linting
make lint
```

### Project Structure

```text
gradual/
├── benchmarks/       # Benchmark configurations
├── docs/             # Documentation
├── examples/         # Example scenarios and usage
├── notebooks/        # Jupyter notebooks for development
├── results/          # Test results output directory
├── src/              # Source code
│   └── gradual/
├── tests/            # Test suite
├── .gitignore        # Git ignore file
├── LICENSE           # License file
├── Makefile          # Build and development commands
├── pyproject.toml    # Project configuration
├── README.md         # This file
├── requirements.txt  # Dependencies
└── setup.py          # Setup script
```

### Adding Dependencies

When adding new packages to the project, update the following files:

1. **pyproject.toml**: Add the package to the appropriate section:

   ```toml
   # For core dependencies
   [project]

   dependencies = [
       # Existing dependencies...
       "new-package>=1.0.0",
   ]


   # For optional dependencies
   [project.optional-dependencies]
   auth = [
       "requests_kerberos>=0.14.0",  # For Kerberos authentication
       "requests_ntlm>=1.2.0",       # For NTLM authentication
       "requests_oauthlib>=1.3.1",   # For OAuth authentication
   ]
   kerberos = [
       "requests_kerberos>=0.14.0",  # For Kerberos authentication only
   ]
   ```

2. **requirements.txt**: Add core dependencies with version constraints.


   ```text
   new-package>=1.0.0
   ```


3. After updating these files, install the dependencies:


   ```bash
   # Activate the virtual environment if not already activated
   source .venv/bin/activate  # On Unix/MacOS
   # OR
   .venv\Scripts\activate  # On Windows

   # Install core dependencies
   pip install -e .

   # Install optional dependencies
   pip install -e ".[auth]"      # For all authentication methods
   pip install -e ".[kerberos]"  # For Kerberos authentication only

   ```

4. If the package is only needed for development, testing, or documentation:
   - Add it to the appropriate section in `pyproject.toml`:

     ```toml
     [project.optional-dependencies]
     dev = [
         # Existing dev dependencies...
         "new-dev-package>=1.0.0",
     ]
     ```

   - Install it with:

     ```bash
     pip install -e ".[dev]"  # For dev dependencies
     # OR
     pip install -e ".[docs]"  # For documentation dependencies
     ```

5. Update build and CI configurations if necessary (e.g., `.github/workflows/python-package.yml`).

6. Commit your changes to version control:

   ```bash
   git add pyproject.toml requirements.txt
   git commit -m "Add new-package dependency"
   ```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
