# -*- coding: utf-8 -*-
from scout.constants import SAMPLE_SOURCE
from flask import get_template_attribute


def test_update_individuals_table(app, case_obj, institute_obj):
    # GIVEN an initialized app
    with app.test_client() as client:

        # WHEN collecting the individuals_table jinja macro
        macro = get_template_attribute("cases/individuals_table.html", "individuals_table")

        # and passing to it the required parameters
        html = macro(case_obj, institute_obj, SAMPLE_SOURCE)

        # THEN the macro should contain the expected html code
        assert '<div class="panel-heading">Individuals</div>' in html
