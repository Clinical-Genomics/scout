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

from scout.constants import CHROMOSOMES, SV_TYPES

LOG = logging.getLogger(__name__)
CHROMOSOME_EDIT_OPTIONS = [(chrom, chrom) for chrom in CHROMOSOMES]
SUBCATEGORY_CHOICES = [("snv", "SNV"), ("indel", "INDEL")] + [
    (term, term.replace("_", " ").upper()) for term in SV_TYPES
]
CATEGORY_CHOICES = [
    (term, term.replace("_", " ").upper()) for term in ["snv", "sv", "cancer_snv", "cancer_sv"]
]


class ManagedVariantForm(FlaskForm):
    position = IntegerField("Start position", [validators.Optional()])
    end = IntegerField("End position", [validators.Optional()])
    cytoband_start = SelectField("Cytoband start", choices=[])
    cytoband_end = SelectField("Cytoband end", choices=[])
    description = TextField(label="Description")
    build = SelectField(
        "Genome build", [validators.Optional()], choices=[("37", "37"), ("38", "38")]
    )


class ManagedVariantsFilterForm(ManagedVariantForm):
    chromosome = SelectField("Chromosome", [validators.Optional()], choices=[])

    category = SelectMultipleField("Category", choices=CATEGORY_CHOICES)
    sub_category = SelectMultipleField("Kind", choices=SUBCATEGORY_CHOICES)

    filter_variants = SubmitField(label="Filter variants")
    export = SubmitField(label="Filter and export")


class ManagedVariantEditForm(ManagedVariantForm):
    chromosome = SelectField("Chromosome", [validators.Optional()], choices=CHROMOSOME_EDIT_OPTIONS)

    reference = TextField(label="Ref")
    alternative = TextField(label="Alt")

    category = SelectField("Category", choices=CATEGORY_CHOICES)
    sub_category = SelectField("Kind", choices=SUBCATEGORY_CHOICES)


class ManagedVariantAddForm(ManagedVariantEditForm):
    add_variant = SubmitField(label="Add")
    cancel = SubmitField(label="Cancel")


class ManagedVariantModifyForm(ManagedVariantEditForm):
    modify_variant = SubmitField(label="Save")
    cancel = SubmitField(label="Cancel")
