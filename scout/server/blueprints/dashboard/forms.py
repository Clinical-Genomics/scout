# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField, validators

from scout.constants import CASE_SEARCH_TERMS

CASE_SEARCH_KEY = [("", "")] + [
    (value["prefix"], value["label"]) for key, value in CASE_SEARCH_TERMS.items()
]


class NonValidatingSelectField(SelectField):
    """Necessary to skip validation of dynamic selects in form"""

    def pre_validate(self, form):
        pass


class DashboardFilterForm(FlaskForm):
    """Takes care of cases filtering in cases page"""

    search_type = NonValidatingSelectField(
        "Search by", [validators.Optional()], choices=CASE_SEARCH_KEY
    )
    search_institute = NonValidatingSelectField("Institute", choices=[])
    search_term = StringField("Search term")
    search = SubmitField(label="Search")
