# -*- coding: utf-8 -*-
from flask import get_template_attribute

from scout.server.blueprints.variants.forms import FiltersForm


def test_modal_prompt_filter_name(app):
    # GIVEN an initialized app
    with app.test_client() as client:
        # WHILE collection a specific jinja macro
        macro = get_template_attribute("variants/utils.html", "modal_prompt_filter_name")
        # and passing to it the required parameters
        # Including a case without HPO phenotype or diagnosis (OMIM terms) assigned
        form = FiltersForm()
        html = macro(form)
        # THEN a string from the modal can be found in the output
        assert "Please name" in html
