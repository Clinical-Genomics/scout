# -*- coding: utf-8 -*-
from flask import get_template_attribute
from scout.server.blueprints.variants.forms import FiltersForm


def test_modal_causative(app, case_obj, institute_obj, variant_obj):

    # GIVEN an initialized app
    with app.test_client() as client:

        # WHILE collection a specific jinja macro
        macro = get_template_attribute("variants/utils.html", "modal_causative")
        # and passing to it the required parameters
        # Including a case without HPO phenotype or diagnosis (OMIM terms) assigned
        html = macro(case_obj, institute_obj, variant_obj)

        # THEN the macro should contain the expected warning message
        assert "Assign at least an OMIM diagnosis or a HPO phenotype term" in html

        # WHEN the case contains one or more phenotype terms:
        case_obj["phenotype_terms"] = {
            "phenotype_id": "HPO:0002637",
            "feature": "Cerebral ischemia",
        }
        # and/or OMIM diagnoses
        case_obj["diagnosis_phenotypes"] = [616833]

        # THEN the macro should allow to assign partial causatives
        html = macro(case_obj, institute_obj, variant_obj)
        assert "Assign at least an OMIM diagnosis or a HPO phenotype term" not in html


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
