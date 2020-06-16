# -*- coding: utf-8 -*-
import logging

from flask_wtf import FlaskForm
from wtforms import (
    IntegerField,
    SelectField,
    SelectMultipleField,
    SubmitField,
    TextField,
    validators,
)

from scout.constants import (
    SV_TYPES,
    CHROMOSOMES,
)

LOG = logging.getLogger(__name__)
CHROMOSOME_OPTIONS = [("", "All")] + [(chrom, chrom) for chrom in CHROMOSOMES]
SV_TYPE_CHOICES = [(term, term.replace("_", " ").upper()) for term in SV_TYPES]
CATEGORY_CHOICES = [
    (term, term.replace("_", " ").upper()) for term in ["snv", "str", "sv", "cancer", "cancer_sv"]
]


class ManagedVariantsFilterForm(FlaskForm):
    chrom = SelectField("Chromosome", [validators.Optional()], choices=[])
    start = IntegerField("Start position", [validators.Optional()])
    end = IntegerField("End position", [validators.Optional()])
    cytoband_start = SelectField("Cytoband start", choices=[])
    cytoband_end = SelectField("Cytoband end", choices=[])

    category = SelectMultipleField("Category", choices=CATEGORY_CHOICES)
    subcategory = SelectMultipleField("Kind", choices=SV_TYPE_CHOICES)

    description = TextField(label="Description")
    filter_variants = SubmitField(label="Filter variants")
    export = SubmitField(label="Filter and export")
