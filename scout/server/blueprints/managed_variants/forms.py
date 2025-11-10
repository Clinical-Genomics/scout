# -*- coding: utf-8 -*-
import logging
import re

from flask_wtf import FlaskForm
from wtforms import (
    IntegerField,
    SelectField,
    SelectMultipleField,
    StringField,
    SubmitField,
    ValidationError,
    validators,
)
from wtforms.widgets import NumberInput

from scout.constants import CHROMOSOMES, SV_TYPES
from scout.utils.vcf import (
    is_symbolic_alt,
    validate_bnd_alt,
    validate_snv_alt,
    validate_symbolic_alt,
)

LOG = logging.getLogger(__name__)
CHROMOSOME_EDIT_OPTIONS = [(chrom, chrom) for chrom in CHROMOSOMES]
SUBCATEGORY_CHOICES = [("snv", "SNV"), ("indel", "INDEL")] + [
    (term, term.replace("_", " ").upper()) for term in SV_TYPES
]
CATEGORY_CHOICES = [
    (term, term.replace("_", " ").upper()) for term in ["snv", "sv", "cancer_snv", "cancer_sv"]
]


class ManagedVariantForm(FlaskForm):
    position = IntegerField(
        "Start position",
        [
            validators.Optional(),
            validators.NumberRange(min=0, message="Start position must be 1 or greater."),
        ],
        widget=NumberInput(min=1),
    )
    end = IntegerField(
        "End position",
        [
            validators.Optional(),
            validators.NumberRange(min=0, message="End position must be 1 or greater."),
        ],
        widget=NumberInput(min=1),
    )
    description = StringField(label="Description")
    build = SelectField(
        "Genome build", [validators.Optional()], choices=[("37", "37"), ("38", "38")]
    )


class ManagedVariantsFilterForm(ManagedVariantForm):
    chromosome = SelectField("Chromosome", [validators.Optional()], choices=[])

    category = SelectMultipleField("Category", choices=CATEGORY_CHOICES)
    sub_category = SelectMultipleField("Kind", choices=SUBCATEGORY_CHOICES)

    cytoband_start = SelectField("Cytoband start", choices=[])
    cytoband_end = SelectField("Cytoband end", choices=[])

    filter_variants = SubmitField(label="Filter variants")
    export = SubmitField(label="Filter and export")


def check_alternative(form, field):
    ref = form.reference.data
    alt = field.data
    category = form.category.data
    sub_category = form.sub_category.data

    print(f"Validating {category} variant {ref} {alt}")

    if ref == alt and ref != "N":
        raise ValidationError("The ref and alt are identical")

    if ref.endswith(alt):
        raise ValidationError(
            "The variant is not normalised - it has extra nucleotides on the right side"
        )

    if len(ref) > 1 and len(alt) > 1 and (ref.startswith(alt) or alt.startswith(ref)):
        raise ValidationError(
            "The variant is not normalised - it has extra nucleotides on the left side"
        )

    alt_validator = None

    match sub_category.upper():
        case "SNV" | "INDEL":
            alt_validator = validate_snv_alt
        case "BND":
            alt_validator = validate_bnd_alt

    if is_symbolic_alt(alt):
        alt_validator = validate_symbolic_alt

    if alt_validator:
        status, msg = alt_validator(alt)
        if not status:
            raise ValidationError(msg)
        return True


class ManagedVariantEditForm(ManagedVariantForm):

    chromosome = SelectField("Chromosome", [validators.Optional()], choices=CHROMOSOME_EDIT_OPTIONS)

    position = IntegerField(
        "Start position",
        [
            validators.InputRequired(),
            validators.NumberRange(min=0, message="Start position must be 1 or greater."),
        ],
        widget=NumberInput(min=1),
    )

    reference = StringField(
        label="Ref",
        validators=[
            validators.Regexp(r"^[ACGTN]+$", message="Invalid reference base"),
        ],
    )
    alternative = StringField(
        label="Alt",
        validators=[
            validators.InputRequired(),
            check_alternative,
        ],
    )

    category = SelectField("Category", choices=CATEGORY_CHOICES)
    sub_category = SelectField("Kind", choices=SUBCATEGORY_CHOICES)


class ManagedVariantAddForm(ManagedVariantEditForm):
    add_variant = SubmitField(label="Add")
    cancel = SubmitField(label="Cancel")


class ManagedVariantModifyForm(ManagedVariantEditForm):
    modify_variant = SubmitField(label="Save")
    cancel = SubmitField(label="Cancel")
