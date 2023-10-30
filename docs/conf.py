"""Sphinx configuration."""
project = "Boss Bus"
author = "Jim Dickinson"
project_copyright = "2023, Jim Dickinson"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx_click",
    "myst_parser",
]
autodoc_typehints = "description"
html_theme = "furo"
