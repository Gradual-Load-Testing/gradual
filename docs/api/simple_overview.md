# Simple API Reference

This is the simplest approach - just document the main package and let mkdocstrings automatically discover all submodules.

## All-in-One Documentation

::: gradual
    options:
        show_source: true
        show_root_heading: true
        show_signature_annotations: true
        show_category_heading: true
        heading_level: 2
        members_order: source
        docstring_style: google
        filters: ["!^_"]
        # These options enable automatic discovery
        show_submodules: true
        show_submodules_full: true
        merge_init_into_class: true
        show_if_no_docstring: true
        # Auto-discover all modules
        preload_modules: [gradual]
