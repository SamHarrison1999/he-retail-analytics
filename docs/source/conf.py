# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'HE Retail Thesis'
copyright = '2025, Sam Harrison'
author = 'Sam Harrison'
release = '0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "myst_parser",
    "sphinx.ext.graphviz",   # built-in, no pip install
    "sphinx_copybutton",
    "sphinxcontrib.mermaid",
]

# Let Sphinx read Markdown files
myst_enable_extensions = ["colon_fence", "deflist", "html_admonition", "html_image"]
source_suffix = {".rst": "restructuredtext", ".md": "markdown"}

# Graphviz output as SVG (crisper)
graphviz_output_format = "svg"
# Optional: pin the dot executable if needed
# graphviz_dot = "/usr/bin/dot"


templates_path = ['_templates']
exclude_patterns = []

html_logo = "_static/logo.svg"
html_favicon = "_static/favicon.ico"




# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# conf.py
html_theme = "furo"
html_theme_options = {"navigation_with_keys": True}

