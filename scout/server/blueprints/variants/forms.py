# -*- coding: utf-8 -*-
import decimal
import logging

from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    DecimalField,
    Field,
    TextField,
    SelectMultipleField,
    SelectField,
    HiddenField,
    StringField,
    IntegerField,
    SubmitField,
    validators,
)
from wtforms.widgets import TextInput
from flask_wtf.file import FileField

from scout.constants import (
    CLINSIG_MAP,
    FEATURE_TYPES,
    GENETIC_MODELS,
    SO_TERMS,
    SPIDEX_LEVELS,
    SV_TYPES,
)

LOG = logging.getLogger(__name__)

CLINSIG_OPTIONS = list(CLINSIG_MAP.items())
FUNC_ANNOTATIONS = [(term, term.replace("_", " ")) for term in SO_TERMS]
REGION_ANNOTATIONS = [(term, term.replace("_", " ")) for term in FEATURE_TYPES]
SV_TYPE_CHOICES = [(term, term.replace("_", " ").upper()) for term in SV_TYPES]
SPIDEX_CHOICES = [(term, term.replace("_", " ")) for term in SPIDEX_LEVELS]


class TagListField(Field):
    widget = TextInput()

    def _value(self):
        if self.data:
            return ", ".join(self.data)
        else:
            return ""

    def process_formdata(self, valuelist):
        if valuelist:
            self.data = [x.strip() for x in valuelist[0].split(",") if x.strip()]
        else:
            self.data = []


class BetterDecimalField(DecimalField):
    """
    Very similar to WTForms DecimalField, except handles ',' and '.'.
    """

    def process_formdata(self, valuelist):
        if valuelist:
            raw_decimal = valuelist[0].replace(",", ".")
            try:
                self.data = decimal.Decimal(raw_decimal)
            except (decimal.InvalidOperation, ValueError):
                self.data = None
                raise ValueError(self.gettext("Not a valid decimal value"))


class VariantFiltersForm(FlaskForm):
    variant_type = HiddenField(default="clinical")

    gene_panels = SelectMultipleField(choices=[])
    hgnc_symbols = TagListField("HGNC Symbols/Ids (case sensitive)")

    region_annotations = SelectMultipleField(choices=REGION_ANNOTATIONS)
    functional_annotations = SelectMultipleField(choices=FUNC_ANNOTATIONS)
    genetic_models = SelectMultipleField(choices=GENETIC_MODELS)

    cadd_score = BetterDecimalField("CADD", places=2)
    cadd_inclusive = BooleanField("CADD inclusive")
    clinsig = SelectMultipleField("CLINSIG", choices=CLINSIG_OPTIONS)

    gnomad_frequency = BetterDecimalField("gnomadAF", places=2)

    filters = SelectField(choices=[])
    filter_display_name = StringField(default="")
    save_filter = SubmitField(label="Save filter")
    load_filter = SubmitField(label="Load filter")
    delete_filter = SubmitField(label="Delete filter")


class FiltersForm(VariantFiltersForm):
    """Base FiltersForm for SNVs - extends VariantFiltersForm."""

    symbol_file = FileField("Symbol File")

    clinsig_confident_always_returned = BooleanField("CLINSIG Confident")
    spidex_human = SelectMultipleField("SPIDEX", choices=SPIDEX_CHOICES)

    chrom = TextField("Chromosome", [validators.Optional()])
    start = IntegerField("Start position", [validators.Optional(), IntegerField])
    end = IntegerField("End position", [validators.Optional(), IntegerField])
    local_obs = IntegerField("Local obs. (archive)")

    filter_variants = SubmitField(label="Filter variants")
    clinical_filter = SubmitField(label="Clinical filter")
    export = SubmitField(label="Filter and export")


class CancerFiltersForm(VariantFiltersForm):
    """Base filters for CancerFiltersForm - extends VariantsFiltersForm"""

    depth = IntegerField("Depth >")
    alt_count = IntegerField("Min alt count >")
    control_frequency = BetterDecimalField("Control freq. <", places=2)
    mvl_tag = BooleanField("In Managed Variant List")


class StrFiltersForm(FlaskForm):
    """docstring for StrFiltersForm"""

    variant_type = HiddenField(default="clinical")

    chrom = TextField("Chromosome")
    gene_panels = SelectMultipleField(choices=[])
    repids = TagListField()


class SvFiltersForm(VariantFiltersForm):
    """Extends FiltersForm for structural variants"""

    size = TextField("Length")
    size_shorter = BooleanField("Length shorter than")
    svtype = SelectMultipleField("SVType", choices=SV_TYPE_CHOICES)

    decipher = BooleanField("Decipher")
    clingen_ngi = IntegerField("ClinGen NGI obs")
    swegen = IntegerField("SweGen obs")

    chrom = TextField("Chromosome", [validators.Optional()])
    start = IntegerField("Start position", [validators.Optional(), IntegerField])
    end = IntegerField("End position", [validators.Optional(), IntegerField])

    filter_variants = SubmitField(label="Filter variants")
    clinical_filter = SubmitField(label="Clinical filter")
    export = SubmitField(label="Filter and export")
