# -*- coding: utf-8 -*-
from flask import get_template_attribute

from scout.constants import SAMPLE_SOURCE


def test_update_individuals_table(app, case_obj, institute_obj):
    # GIVEN an initialized app
    with app.test_client() as client:
        # WHEN collecting the individuals_table jinja macro
        macro = get_template_attribute("cases/individuals_table.html", "individuals_table")

        # and passing to it the required parameters
        html = macro(case_obj, institute_obj, SAMPLE_SOURCE)

        for ind in case_obj["individuals"]:
            # THEN the macro should contain the expected html code
            assert ind["display_name"] in html
