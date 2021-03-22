# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
sys.path.insert(0, os.path.abspath('..'))

# -- Options for Napoleon Extension --------------------------------------------

# Parse Google style docstrings.
# See http://google.github.io/styleguide/pyguide.html
napoleon_google_docstring = True

# Parse NumPy style docstrings.
# See https://github.com/numpy/numpy/blob/master/doc/HOWTO_DOCUMENT.rst.txt
napoleon_numpy_docstring = True

# If True, use Sphinx :param: directive for function parameters:
#     :param arg1: Description of arg1.
#     :type arg1: type
# If False, output function parameters using the :parameters: field:
#     :parameters: **arg1** (*type*) -- Description of arg1.
napoleon_use_param = True

# If True, use Sphinx :rtype: directive for the return type:
#     :returns: Description of return value.
#     :rtype: type
# If False, output the return type inline with the return description:
#     :returns: *type* -- Description of return value.
napoleon_use_rtype = True


# -- Project information -----------------------------------------------------

project = 'City Scanner API'
copyright = '2021, Vasco Xu'
author = 'Vasco Xu'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.napoleon',
    'sphinxcontrib.autohttp.flask',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'


# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']
