# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField, validators

from scout.constants import CASE_SEARCH_TERMS
from scout.server.blueprints.institutes.forms import CaseFilterForm

CASE_SEARCH_KEY = [("", "")] + [
    (value["prefix"], value["label"]) for key, value in CASE_SEARCH_TERMS.items()
]


class NonValidatingSelectField(SelectField):
    """Necessary to skip validation of dynamic selects in form"""

    def pre_validate(self, form):
        pass


class DashboardFilterForm(CaseFilterForm):
    """Takes care of cases filtering on dashboard page"""

    search_institute = NonValidatingSelectField("Institute", choices=[])
