# -*- coding: utf-8 -*-
import decimal
import logging

from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import (
    BooleanField,
    DecimalField,
    Field,
    HiddenField,
    IntegerField,
    SelectField,
    SelectMultipleField,
    StringField,
    SubmitField,
    validators,
)
from wtforms.widgets import NumberInput, TextInput

from scout.constants import (
    CALLERS,
    CLINICAL_FILTER_BASE,
    CLINICAL_FILTER_BASE_CANCER,
    CLINICAL_FILTER_BASE_MEI,
    CLINICAL_FILTER_BASE_OUTLIER,
    CLINICAL_FILTER_BASE_SV,
    CLINSIG_MAP,
    FEATURE_TYPES,
    GENETIC_MODELS,
    ONC_CLNSIG,
    OUTLIER_TYPES,
    SO_TERMS,
    SPIDEX_LEVELS,
    SV_TYPES,
    VARIANT_GENOTYPES,
)

LOG = logging.getLogger(__name__)

CLINSIG_OPTIONS = list(CLINSIG_MAP.items())
ONC_CLNSIG_OPTIONS = [(term.lower().replace(" ", "_"), term) for term in ONC_CLNSIG]
FUNC_ANNOTATIONS = [(term, term.replace("_", " ")) for term in SO_TERMS]
REGION_ANNOTATIONS = [(term, term.replace("_", " ")) for term in FEATURE_TYPES]
SV_TYPE_CHOICES = [(term, term.replace("_", " ").upper()) for term in SV_TYPES]
OUTLIER_TYPE_CHOICES = [(term, term.replace("_", " ").upper()) for term in OUTLIER_TYPES]
SPIDEX_CHOICES = [(term, term.replace("_", " ")) for term in SPIDEX_LEVELS]
FUSION_CALLER_CHOICES = [(term.get("id"), term.get("name")) for term in CALLERS.get("fusion")]


class NonValidatingSelectMultipleField(SelectMultipleField):
    """Necessary to skip validation of dynamic multiple selects in form"""

    def pre_validate(self, _form):
        pass


class NonValidatingSelectField(SelectField):
    """Necessary to skip validation of dynamic selects in form"""

    def pre_validate(self, _form):
        pass


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


class BetterDecimalField(DecimalField):
    """
    Very similar to WTForms DecimalField, except handles ',' and '.'.
    """

    def process_formdata(self, valuelist):
        if not valuelist:
            return

        raw_decimal = valuelist[0]
        if type(raw_decimal) is str:
            raw_decimal = valuelist[0].replace(",", ".")
        try:
            self.data = decimal.Decimal(raw_decimal)
        except (decimal.InvalidOperation, ValueError):
            self.data = None
            raise ValueError(self.gettext("Not a valid decimal value"))


class VariantFiltersForm(FlaskForm):
    variant_type = HiddenField(default="clinical")

    gene_panels = NonValidatingSelectMultipleField(choices=[])
    gene_panels_exclude = BooleanField("Exclude genes")
    hgnc_symbols = TagListField("HGNC Symbols/Ids (case sensitive)")

    region_annotations = SelectMultipleField(choices=REGION_ANNOTATIONS)
    functional_annotations = SelectMultipleField(choices=FUNC_ANNOTATIONS)
    genetic_models = SelectMultipleField(choices=GENETIC_MODELS)
    genotypes = NonValidatingSelectField(choices=VARIANT_GENOTYPES)

    cadd_score = BetterDecimalField("CADD", validators=[validators.Optional()])
    revel = BetterDecimalField("REVEL", validators=[validators.Optional()])

    compound_rank_score = IntegerField("Compound rank score")
    compound_follow_filter = BooleanField("Compounds follow filter")
    cadd_inclusive = BooleanField("CADD inclusive")
    clinsig = NonValidatingSelectMultipleField("ClinVar significance", choices=CLINSIG_OPTIONS)
    clinsig_exclude = BooleanField("Exclude")
    clinvar_tag = BooleanField("ClinVar hits only")
    prioritise_clinvar = BooleanField("Prioritise ClinVar")

    gnomad_frequency = BetterDecimalField("gnomadAF", validators=[validators.Optional()])
    local_obs_old = IntegerField("Local obs. (archive)", validators=[validators.Optional()])

    filters = NonValidatingSelectField(choices=[], validators=[validators.Optional()])
    filter_display_name = StringField(default="")
    save_filter = SubmitField(label="Save filter")
    load_filter = SubmitField(label="Load filter")
    lock_filter = SubmitField(label="Lock filter")
    delete_filter = SubmitField(label="Delete filter")
    audit_filter = SubmitField(label="Audit filter")

    chrom_pos = StringField(
        "Chromosome position",
        [validators.Optional()],
        render_kw={"placeholder": "<chr>:<start pos>-<end pos>[optional +/-<span>]"},
    )

    chrom = NonValidatingSelectMultipleField("Chromosome", choices=[], default="")
    start = IntegerField(
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
    cytoband_start = NonValidatingSelectField("Cytoband start", choices=[])
    cytoband_end = NonValidatingSelectField("Cytoband end", choices=[])

    size_selector = NonValidatingSelectField(
        "Variant size in bp", choices=[("$gte", ">="), ("$lt", "<")]
    )
    size = IntegerField(
        "",
        [
            validators.Optional(),
            validators.NumberRange(min=0, message="Number of bases must be 1 or greater."),
        ],
        widget=NumberInput(min=1),
    )

    hide_dismissed = BooleanField("Hide dismissed", default=False)
    filter_variants = SubmitField(label="Filter variants")
    export = SubmitField(label="Filter and export")

    show_unaffected = BooleanField("Include variants present only in unaffected", default=True)
    show_soft_filtered = BooleanField(f"Include soft-filtered variants", default=False)
    institute_soft_filters = HiddenField()


class FiltersForm(VariantFiltersForm):
    """Base FiltersForm for SNVs - extends VariantFiltersForm."""

    symbol_file = FileField("Symbol File")

    clinvar_trusted_revstat = BooleanField("CLINSIG Confident")
    spidex_human = SelectMultipleField("SPIDEX", choices=SPIDEX_CHOICES)

    clinical_filter = SubmitField(label="Clinical filter")

    # polymorphic constant base for clinical filter
    clinical_filter_base = CLINICAL_FILTER_BASE


class CancerFiltersForm(VariantFiltersForm):
    """Base filters for CancerFiltersForm - extends VariantsFiltersForm"""

    depth = IntegerField("Depth >", validators=[validators.Optional()])
    alt_count = IntegerField("Min alt count", validators=[validators.Optional()])
    control_frequency = BetterDecimalField("Normal alt AF <", validators=[validators.Optional()])
    tumor_frequency = BetterDecimalField("Tumor alt AF >", validators=[validators.Optional()])
    cosmic_tag = BooleanField("Cosmic hits")
    clinsig_onc = NonValidatingSelectMultipleField(
        "ClinVar oncogenicity", choices=ONC_CLNSIG_OPTIONS
    )
    clinsig_onc_exclude = BooleanField("Exclude")
    mvl_tag = BooleanField("Managed Variants hits")
    local_obs_cancer_somatic_old = IntegerField(
        "Local somatic obs. (archive)", validators=[validators.Optional()]
    )
    local_obs_cancer_germline_old = IntegerField(
        "Local germline obs. (archive)", validators=[validators.Optional()]
    )
    # polymorphic constant base for clinical filter
    clinical_filter_base = CLINICAL_FILTER_BASE_CANCER


class MeiFiltersForm(VariantFiltersForm):
    """FiltersForm for Mobile Element Insertion variants"""

    mei_name = StringField("Element")
    clinical_filter = SubmitField(label="Clinical filter")
    swegen_freq = BetterDecimalField("SweGen(Max) AF", validators=[validators.Optional()])

    # polymorphic constant base for clinical filter
    clinical_filter_base = CLINICAL_FILTER_BASE_MEI


class StrFiltersForm(VariantFiltersForm):
    """FiltersForm for Short Tandem Repeat variants. So far only VariantFiltersForm"""


class SvFiltersForm(VariantFiltersForm):
    """Extends FiltersForm for structural variants"""

    svtype = SelectMultipleField("SVType", choices=SV_TYPE_CHOICES)
    decipher = BooleanField("Decipher")
    clingen_ngi = IntegerField("ClinGen NGI obs")
    swegen = IntegerField("SweGen obs")
    clinical_filter = SubmitField(label="Clinical filter")

    local_obs_cancer_somatic_old = IntegerField(
        "Local somatic obs. (archive)", validators=[validators.Optional()]
    )
    local_obs_cancer_germline_old = IntegerField(
        "Local germline obs. (archive)", validators=[validators.Optional()]
    )

    # polymorphic constant base for clinical filter
    clinical_filter_base = CLINICAL_FILTER_BASE_SV


class CancerSvFiltersForm(SvFiltersForm):
    """Extends SvFiltersForm for cancer structural variants"""

    depth = IntegerField("Depth >", validators=[validators.Optional()])
    alt_count = IntegerField("Min alt count", validators=[validators.Optional()])
    somatic_score = IntegerField("Somatic score", validators=[validators.Optional()])


class FusionFiltersForm(VariantFiltersForm):
    """Extends FiltersForm for fusion variants"""

    decipher = BooleanField("Decipher")
    clinical_filter = SubmitField(label="Clinical filter")
    fusion_score = BetterDecimalField("Fusion score >=", validators=[validators.Optional()])
    ffpm = BetterDecimalField("FFPM >=", validators=[validators.Optional()])
    junction_reads = IntegerField("Junction reads >=", validators=[validators.Optional()])
    split_reads = IntegerField("Split reads >=", validators=[validators.Optional()])
    fusion_caller = SelectMultipleField("Fusion Caller", choices=FUSION_CALLER_CHOICES, default=[])


class OutlierFiltersForm(FlaskForm):
    variant_type = HiddenField(default="clinical")

    gene_panels = NonValidatingSelectMultipleField(choices=[])
    gene_panels_exclude = BooleanField("Exclude genes")
    hgnc_symbols = TagListField("HGNC Symbols/Ids (case sensitive)")

    svtype = SelectMultipleField("Type", choices=OUTLIER_TYPE_CHOICES)

    filters = NonValidatingSelectField(choices=[], validators=[validators.Optional()])
    filter_display_name = StringField(default="")
    save_filter = SubmitField(label="Save filter")
    load_filter = SubmitField(label="Load filter")
    lock_filter = SubmitField(label="Lock filter")
    delete_filter = SubmitField(label="Delete filter")
    audit_filter = SubmitField(label="Audit filter")
    clinical_filter = SubmitField(label="Clinical filter")

    chrom_pos = StringField(
        "Chromosome position",
        [validators.Optional()],
        render_kw={"placeholder": "<chr>:<start pos>-<end pos>[optional +/-<span>]"},
    )

    chrom = NonValidatingSelectMultipleField("Chromosome", choices=[], default="")
    start = IntegerField(
        "Start position",
        [
            validators.Optional(),
            validators.NumberRange(min=1, message="Start position must be 0 or greater."),
        ],
        widget=NumberInput(min=1),
    )
    end = IntegerField(
        "End position",
        [
            validators.Optional(),
            validators.NumberRange(min=1, message="End position must be 0 or greater."),
        ],
        widget=NumberInput(min=1),
    )
    cytoband_start = NonValidatingSelectField("Cytoband start", choices=[])
    cytoband_end = NonValidatingSelectField("Cytoband end", choices=[])

    filter_variants = SubmitField(label="Filter variants")
    export = SubmitField(label="Filter and export")

    clinical_filter_base = CLINICAL_FILTER_BASE_OUTLIER

    show_unaffected = BooleanField("Include variants present only in unaffected", default=False)

    sort_by = NonValidatingSelectField(
        choices=[
            ("", "Sort by"),
            ("p_value", "Sort by P-value"),
            ("delta_psi", "Sort by Δψ"),
            ("psi_value", "Sort by ψ value"),
            ("zscore", "Sort by zscore"),
            ("l2fc", "Sort by l2fc"),
        ],
        validators=[validators.Optional()],
    )
    sort_order = NonValidatingSelectField(
        choices=[("", "Sort order"), ("asc", "asc"), ("desc", "desc")],
        validators=[validators.Optional()],
    )


FILTERSFORMCLASS = {
    "snv": FiltersForm,
    "str": StrFiltersForm,
    "sv": SvFiltersForm,
    "cancer_sv": CancerSvFiltersForm,
    "cancer": CancerFiltersForm,
    "mei": MeiFiltersForm,
    "fusion": FusionFiltersForm,
    "outlier": OutlierFiltersForm,
}
