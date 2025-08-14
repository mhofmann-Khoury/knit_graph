"""
    Configuration file for the Sphinx documentation builder.
    =============================================================================
    SPHINX DOCUMENTATION CONFIGURATION
    =============================================================================
    This file configures how Sphinx generates documentation from your Python code.
    For the full list of built-in configuration values, see:
    https://www.sphinx-doc.org/en/master/usage/configuration.html
"""

import os
import sys
from datetime import datetime
from importlib.metadata import PackageNotFoundError, version

# =============================================================================
# PATH SETUP
# =============================================================================
# Add the project root and source directory to Python path so Sphinx can import your modules

# Path to your source code (adjust if not using src/ layout)
sys.path.insert(0, os.path.abspath('..'))  # Project root
sys.path.insert(0, os.path.abspath('../src'))  # Source directory
sys.path.insert(0, os.path.abspath('.'))  # Docs directory

# =============================================================================
# PROJECT INFORMATION
# =============================================================================

project = 'knit-graphs'
copyright = f'{datetime.now().year}, Megan Hofmann'
author = 'Megan Hofmann'

try:
    # Get version from installed package metadata
    # This reads from pyproject.toml when the package is installed
    version = version("knit-graphs")
except PackageNotFoundError:
    # Package is not installed (e.g., during development)
    # This happens when running from source without installation
    version = "0.0.0+dev"

release = version

# =============================================================================
# GENERAL CONFIGURATION
# =============================================================================

# Extensions to enable (these add functionality to Sphinx)
extensions = [
    # Core Sphinx extensions
    'sphinx.ext.autodoc',  # Generate docs from docstrings
    'sphinx.ext.autosummary',  # Generate summary tables automatically
    'sphinx.ext.viewcode',  # Add [source] links to documentation
    'sphinx.ext.napoleon',  # Support Google/NumPy docstring styles
    'sphinx.ext.intersphinx',  # Link to other project docs (e.g., Python docs)
    'sphinx.ext.githubpages',  # Publish to GitHub Pages (.nojekyll file)
    'sphinx.ext.todo',  # Support TODO items in docs
    'sphinx.ext.coverage',  # Check documentation coverage
    'sphinx.ext.doctest',  # Test code snippets in documentation

    # Third-party extensions (these need to be installed)
    'sphinx_autodoc_typehints',  # Better type hint rendering
    'myst_parser',  # Support for Markdown files (optional)
]

# =============================================================================
# SOURCE FILE CONFIGURATION
# =============================================================================

# File extensions that Sphinx will process
source_suffix = {
    '.rst': None,  # RestructuredText (default)
    '.md': 'myst_parser',  # Markdown (requires myst_parser extension)
}

# The master toctree document (main page)
master_doc = 'index'

# Files and directories to exclude from processing
exclude_patterns = [
    '_build',  # Build output directory
    'Thumbs.db',  # Windows thumbnail cache
    '.DS_Store',  # macOS metadata
    '**.ipynb_checkpoints',  # Jupyter notebook checkpoints
]

# =============================================================================
# HTML OUTPUT CONFIGURATION
# =============================================================================

# The theme to use for HTML pages
html_theme = 'sphinx_rtd_theme'  # Read the Docs theme (clean, professional)

# Directories containing static files (CSS, JS, images)
html_static_path = ['_static']


# Theme-specific options
html_theme_options = {
    'logo_only': False,  # Show project name with logo
    'display_version': True,  # Show version in sidebar
    'prev_next_buttons_location': 'bottom',  # Navigation button placement
    'style_external_links': True,  # Style external links differently
    'vcs_pageview_mode': '',  # Version control integration
    'style_nav_header_background': '#2980B9',  # Header background color

    # Table of contents options
    'collapse_navigation': True,  # Collapse subsections in nav
    'sticky_navigation': True,  # Keep navigation visible on scroll
    'navigation_depth': 4,  # Maximum navigation depth
    'includehidden': True,  # Include hidden toctrees
    'titles_only': False,  # Show subsection titles in nav
}

# Additional HTML options
html_title = f'{project} Documentation'  # Browser window title
html_short_title = project  # Short title for navigation


# html_logo = '_static/logo.png'
# html_favicon = '_static/favicon.ico'

# Show "Edit on GitHub" links (requires proper URL)
# html_context = {
#     'github_user': 'your-username',
#     'github_repo': 'your-repo-name',
#     'github_version': 'main',
#     'doc_path': 'docs',
# }

# =============================================================================
# AUTODOC CONFIGURATION
# =============================================================================
# Controls how automatic documentation is generated from Python code

# Default options for all autodoc directives
autodoc_default_options = {
    'members': True,  # Include all members
    'member-order': 'bysource',  # Order members as they appear in source
    'special-members': '__init__',  # Include __init__ methods
    'undoc-members': True,  # Include members without docstrings
    'exclude-members': '__weakref__',  # Exclude certain members
    'show-inheritance': True,  # Show class inheritance
    'inherited-members': True,  # Include inherited methods
}

# How to display class signatures
autodoc_class_signature = "mixed"  # Show __init__ parameters with class

# Order of members in documentation
autodoc_member_order = 'bysource'  # bysource, alphabetical, or groupwise

# Mock imports for modules that might not be available during doc building
# Add any modules that cause import errors during doc building
autodoc_mock_imports = [
    # 'numpy',
    # 'pandas',
    # 'some_optional_dependency',
]

# =============================================================================
# AUTOSUMMARY CONFIGURATION
# =============================================================================
# Controls automatic generation of summary tables

autosummary_generate = True  # Generate stub pages for autosummary
autosummary_imported_members = True  # Include imported members

# =============================================================================
# NAPOLEON CONFIGURATION (DOCSTRING STYLES)
# =============================================================================
# Configures support for Google and NumPy style docstrings

napoleon_google_docstring = True  # Parse Google-style docstrings
napoleon_numpy_docstring = True  # Parse NumPy-style docstrings
napoleon_include_init_with_doc = True  # Include __init__ docstring with class
napoleon_include_private_with_doc = False  # Don't document private members
napoleon_include_special_with_doc = True  # Document special methods (__str__, etc.)
napoleon_use_admonition_for_examples = False  # Style for Examples sections
napoleon_use_admonition_for_notes = False  # Style for Notes sections
napoleon_use_admonition_for_references = False  # Style for References sections
napoleon_use_ivar = False  # Use :ivar: for instance variables
napoleon_use_param = True  # Use :param: for parameters
napoleon_use_rtype = True  # Use :rtype: for return types
napoleon_preprocess_types = False  # Preprocess type annotations
napoleon_type_aliases = None  # Custom type aliases
napoleon_attr_annotations = True  # Include attribute annotations

# =============================================================================
# INTERSPHINX CONFIGURATION
# =============================================================================
# Links to external documentation

intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'numpy': ('https://numpy.org/doc/stable/', None),
    'pandas': ('https://pandas.pydata.org/pandas-docs/stable/', None),
    'matplotlib': ('https://matplotlib.org/stable/', None),
    'scipy': ('https://docs.scipy.org/doc/scipy/', None),
    'sklearn': ('https://scikit-learn.org/stable/', None),
    'typing': ('https://typing.readthedocs.io/en/latest/', None),
}

# =============================================================================
# TYPE HINTS CONFIGURATION
# =============================================================================
# Controls how type hints are displayed in documentation

typehints_fully_qualified = False  # Use short names for types
always_document_param_types = True  # Always show parameter types
typehints_document_rtype = True  # Document return types
typehints_use_rtype = True  # Use :rtype: directive for return types

# =============================================================================
# TODO EXTENSION CONFIGURATION
# =============================================================================

todo_include_todos = True  # Include TODO items in documentation
todo_emit_warnings = True  # Warn about TODO items during build

# =============================================================================
# COVERAGE EXTENSION CONFIGURATION
# =============================================================================
# Checks what's documented vs what's not

coverage_ignore_modules = [
    #  Add modules to ignore in coverage reports
]
coverage_ignore_functions = [
    #  Add functions to ignore in coverage reports
]
coverage_ignore_classes = [
    #  Add classes to ignore in coverage reports
]

# =============================================================================
# ADDITIONAL CUSTOMIZATION
# =============================================================================

# Control how module names are displayed
add_module_names = False  # Don't prepend module names to functions

# Show author information in output
show_authors = False  # Don't show author info by default

# Syntax highlighting style
pygments_style = 'sphinx'  # Code highlighting theme

# Language for content that doesn't specify a language
language = 'en'


# =============================================================================
# CUSTOM FUNCTIONS AND SETUP
# =============================================================================

def autodoc_skip_member(app, what, name, obj, skip, options):
    """
    Custom function to control which members are included in documentation.

    Args:
        app: The Sphinx application instance
        what: The type of the object (module, class, function, etc.)
        name: The fully qualified name of the object
        obj: The object itself
        skip: Boolean indicating if this member should be skipped
        options: The options given to the directive

    Returns:
        Boolean indicating whether to skip this member
    """
    # Add custom logic to skip certain members
    # Example: Skip private methods that start with underscore
    # if name.startswith('_') and not name.startswith('__'):
    #     return True

    return skip


def setup(app):
    """
    Custom Sphinx setup function.
    This function is called when Sphinx initializes and allows you to
    add custom functionality, connect to events, etc.

    Args:
        app: The Sphinx application instance
    """
    # Connect custom functions to Sphinx events
    app.connect('autodoc-skip-member', autodoc_skip_member)

    # Return extension metadata
    return {
        'version': version,
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }

# =============================================================================
# CHECKLIST FOR SPHINX SETUP
# =============================================================================
# When using this configuration:
#
# 1. BASIC SETUP:
#    - [ ] Update project, author, and copyright information
#    - [ ] Set correct version/release values
#    - [ ] Verify source code paths are correct
#    - [ ] Create docs/_static/ directory for custom files
#
# 2. CONTENT CREATION:
#    - [ ] Create docs/index.rst (main page)
#    - [ ] Create docs/installation.rst (installation guide)
#    - [ ] Create docs/usage.rst (usage examples)
#    - [ ] Create docs/api.rst (API reference)
#
# 3. CUSTOMIZATION:
#    - [ ] Choose and configure theme options
#    - [ ] Add logo and favicon to _static/
#    - [ ] Create custom CSS/JS if needed
#    - [ ] Configure intersphinx for your dependencies
#
# 4. TESTING:
#    - [ ] Run: poetry run sphinx-build docs/ docs/_build/html/
#    - [ ] Check output in docs/_build/html/index.html
#    - [ ] Fix any warnings or errors
#
# 5. GITHUB PAGES:
#    - [ ] Ensure githubpages extension is enabled
#    - [ ] Configure GitHub repository Pages settings
#    - [ ] Test deployment with GitHub Actions workflow
#
# COMMON COMMANDS:
#   poetry run sphinx-apidoc -o docs/source/api src/your_project_name/ --force --module-first       # Generate API docs
#   poetry run sphinx-build docs/source/ docs/build/html/ # Build documentation
