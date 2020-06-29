# -*- coding: utf-8 -*-
import decimal

from flask_wtf import FlaskForm
from wtforms import (
    Field,
    TextField,
    SelectField,
    SelectMultipleField,
    IntegerField,
    SubmitField,
    BooleanField,
    validators,
)
from wtforms.widgets import TextInput

CASE_SEARCH_KEY = [
    "Case Name",
    "HPO term",
    "Search synopsis",
    "Gene panel",
    "Case status",
    "Phenotype group",
    "Patient cohort",
    "Similar case",
    "Similar phenotype",
    "Pinned gene",
    "Causative gene",
    "Assigned user",
]


class CaseFilterForm(FlaskForm):
    """Takes care of cases filtering in cases page"""

    search_type = SelectField("Search by", [validators.Optional()], choices=CASE_SEARCH_KEY)
    search_term = TextField("Search cases")
    search_limit = IntegerField("Limit", [validators.Optional()], default=100)
    hide_assigned = BooleanField("Hide assigned")
    hide_non_research = BooleanField("Hide non-research")
    search = SubmitField(label="Search")


# make a base class or other utility with this instead..
class TagListField(Field):
    widget = TextInput()

    def _value(self):
        if self.data:
            return ", ".join(self.data)

        return ""

    def process_formdata(self, valuelist):
        if valuelist:
            self.data = [x.strip() for x in valuelist[0].split(",") if x.strip()]
        else:
            self.data = []


class GeneVariantFiltersForm(FlaskForm):
    """Base FiltersForm for SNVs"""

    variant_type = SelectMultipleField(choices=[("clinical", "clinical"), ("research", "research")])
    hgnc_symbols = TagListField("HGNC Symbols/Ids (case sensitive)")
    filter_variants = SubmitField(label="Filter variants")
    rank_score = IntegerField()
    phenotype_terms = TagListField("HPO terms")
    phenotype_groups = TagListField("Phenotype groups")
    similar_case = TagListField("Phenotypically similar case")
    cohorts = TagListField("Cohorts")
