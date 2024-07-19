# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import json
import os
import sys

sys.path.insert(0, os.path.abspath("../../config_modules_vmware/"))
sys.path.insert(0, os.path.abspath("../../"))
sys.path.insert(0, os.path.abspath("../../config_modules_vmware/controllers/"))
from config_modules_vmware.services.mapper import mapper_utils
from config_modules_vmware.controllers.base_controller import BaseController

project = "config_modules"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ["sphinx.ext.autodoc", "sphinx.ext.viewcode", "sphinx_markdown_builder", "sphinx.ext.napoleon"]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
language = "en"
add_module_names = False

# -- Options for autodoc extension ----------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#configuration

autodoc_typehints = "description"
autodoc_default_options = {"member-order": "bysource", "exclude-members": "metadata"}
autodoc_default_flags = ["members", "undoc-members"]

napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True


def docstring_processor_add_metadata(app, what, name, obj, options, lines):
    prefix = "config_modules_vmware.controllers."
    code_block_text = "Controller Metadata\n````json\n"
    if what == "class":
        class_ref = mapper_utils.get_class(prefix + name)
        if isinstance(class_ref, BaseController) or not hasattr(class_ref, "metadata"):
            return
        lines.append(
            code_block_text + json.dumps(class_ref.metadata.to_dict(always_include_defaults=True), indent=2) + "\n````"
        )


def setup(app):
    app.connect("autodoc-process-docstring", docstring_processor_add_metadata)
