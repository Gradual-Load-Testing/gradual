#!/usr/bin/env python3
"""
Automatic API Documentation Generator

This script automatically discovers all modules in the gradual package
and generates the corresponding API documentation files.
"""

import os
import importlib
import pkgutil
from pathlib import Path


def discover_modules(package_name):
    """Discover all modules in a package recursively."""
    try:
        package = importlib.import_module(package_name)
        package_path = Path(package.__file__).parent

        modules = []

        # Get all Python files in the package
        for item in pkgutil.iter_modules([str(package_path)]):
            if not item.name.startswith("_"):
                modules.append(f"{package_name}.{item.name}")

        # Recursively check subdirectories
        for item in os.listdir(package_path):
            item_path = package_path / item
            if item_path.is_dir() and not item.startswith("_"):
                init_file = item_path / "__init__.py"
                if init_file.exists():
                    sub_package = f"{package_name}.{item}"
                    sub_modules = discover_modules(sub_package)
                    modules.extend(sub_modules)

        return modules
    except ImportError:
        return []


def generate_api_file(module_name, output_dir):
    """Generate an API documentation file for a module."""
    filename = f"{module_name.split('.')[-1]}.md"
    filepath = output_dir / filename

    content = f"""# {module_name.split('.')[-1].title()}

This page contains the API documentation for the `{module_name}` module.

::: {module_name}
    options:
        show_source: true
        show_root_heading: true
        show_signature_annotations: true
        show_category_heading: true
        heading_level: 2
        members_order: source
        docstring_style: google
        filters: ["!^_"]
        preload_modules: [{module_name}]
        merge_init_into_class: true
        show_submodules: true
        show_if_no_docstring: true
"""

    with open(filepath, "w") as f:
        f.write(content)

    return filename


def main():
    """Main function to generate all API documentation."""
    package_name = "gradual"
    docs_dir = Path("docs/api")

    # Create docs directory if it doesn't exist
    docs_dir.mkdir(parents=True, exist_ok=True)

    # Discover all modules
    print(f"Discovering modules in {package_name}...")
    modules = discover_modules(package_name)

    if not modules:
        print(f"No modules found in {package_name}")
        return

    print(f"Found {len(modules)} modules:")
    for module in modules:
        print(f"  - {module}")

    # Generate documentation files
    print("\nGenerating API documentation files...")
    generated_files = []

    for module in modules:
        filename = generate_api_file(module, docs_dir)
        generated_files.append(filename)
        print(f"  ✓ Generated {filename}")

    # Generate overview file
    overview_content = f"""# API Reference

This page provides comprehensive API documentation for the {package_name} package.

## Available Modules

The following modules are automatically discovered and documented:

"""

    for module in modules:
        module_short = module.split(".")[-1]
        overview_content += (
            f"- [{module_short.title()}]({module_short}.md) - `{module}`\n"
        )

    overview_content += """

## Automatic Discovery

This documentation is automatically generated using a Python script that:
1. Discovers all modules in the package
2. Generates individual documentation files for each module
3. Uses mkdocstrings to extract documentation from docstrings
4. Updates automatically when you run the script

To regenerate all API documentation, run:
```bash
python generate_api_docs.py
```
"""

    overview_file = docs_dir / "overview.md"
    with open(overview_file, "w") as f:
        f.write(overview_content)

    print(f"\n✓ Generated overview.md")
    print(f"\nTotal files generated: {len(generated_files) + 1}")
    print(f"Run 'mkdocs build' to build the documentation")


if __name__ == "__main__":
    main()
