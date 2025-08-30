# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "HE Retail Analytics"
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
    "sphinx_sitemap",
    "sphinxext.opengraph",
    "sphinx_design"
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

html_extra_path = ["_extra"]






# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# conf.py
html_theme = "furo"
html_theme_options = {"navigation_with_keys": True,
                      "source_repository": "https://github.com/SamHarrison1999/he-retail-analytics/",
                      "source_branch": "main",
                      "source_directory": "docs/source/",
}

html_baseurl = "https://samharrison1999.github.io/he-retail-analytics/"

# sitemap (needs html_baseurl set, which you already have)
sitemap_url_scheme = "{link}"

# OpenGraph (social cards)
ogp_site_url = html_baseurl
ogp_site_name = project
ogp_image = "_static/logo.svg"  # adjust if you prefer a PNG
ogp_description = "Homomorphic encryption for retail analytics — code, experiments, and docs."

linkcheck_timeout = 10
linkcheck_retries = 2
linkcheck_anchors = False
linkcheck_ignore = [r"https?://localhost[:/].*", r"https?://127\.0\.0\.1[:/].*"]
