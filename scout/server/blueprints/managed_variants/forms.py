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


class ManagedVariantForm(FlaskForm):
    chromosome = SelectField("Chromosome", [validators.Optional()], choices=[])
    position = IntegerField("Start position", [validators.Optional()])
    end = IntegerField("End position", [validators.Optional()])
    cytoband_start = SelectField("Cytoband start", choices=[])
    cytoband_end = SelectField("Cytoband end", choices=[])

    description = TextField(label="Description")


class ManagedVariantsFilterForm(ManagedVariantForm):
    category = SelectMultipleField("Category", choices=CATEGORY_CHOICES)
    subcategory = SelectMultipleField("Kind", choices=SV_TYPE_CHOICES)

    filter_variants = SubmitField(label="Filter variants")
    export = SubmitField(label="Filter and export")


class ManagedVariantsAddForm(ManagedVariantForm):
    reference = TextField(label="Ref")
    alternative = TextField(label="Alt")

    category = SelectField("Category", choices=CATEGORY_CHOICES)
    subcategory = SelectField("Kind", choices=SV_TYPE_CHOICES)

    add_variant = SubmitField(label="Add")
    cancel = SubmitField(label="Cancel")


class ManagedVariantsModifyForm(ManagedVariantForm):
    reference = TextField(label="Ref")
    alternative = TextField(label="Alt")

    category = SelectField("Category", choices=CATEGORY_CHOICES)
    subcategory = SelectField("Kind", choices=SV_TYPE_CHOICES)

    modify_variant = SubmitField(label="Save")
    cancel = SubmitField(label="Cancel")
