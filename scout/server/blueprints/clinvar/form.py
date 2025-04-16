import logging
from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    DateField,
    HiddenField,
    IntegerField,
    RadioField,
    SelectField,
    SelectMultipleField,
    StringField,
    TextAreaField,
    validators,
    widgets,
)

from scout.constants import (
    AFFECTED_STATUS,
    ALLELE_OF_ORIGIN,
    ASSERTION_METHOD_GERMLINE,
    ASSERTION_METHOD_GERMLINE_CIT,
    ASSERTION_METHOD_ONCOGENIC_ID,
    CLINVAR_API_ASSERTION_METHOD_CIT_DB_OPTIONS,
    CLINVAR_ASSERTION_METHOD_CIT_DB_OPTIONS,
    CLINVAR_INHERITANCE_MODELS,
    CLINVAR_SV_TYPES,
    COLLECTION_METHOD,
    CONDITION_PREFIX,
    GERMLINE_CLASSIF_TERMS,
    MULTIPLE_CONDITION_EXPLANATION,
)

LOG = logging.getLogger(__name__)


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class BaseClinVarVariantForm(FlaskForm):
    """Contains form fields common to all classes of ClinVar variant Submission Forms."""

    assertion_method_cit_db = SelectField("Assertion method citation type", choices=[])
    assertion_method_cit_id = StringField("Assertion method citation id")
    category = HiddenField()
    last_evaluated = DateField("Date evaluated", default=datetime.now())
    record_status = HiddenField(default="novel")


class ClinVarVariantForm(BaseClinVarVariantForm):
    """Contains the key/values to fill in to specify a single general variant in the ClinVar submssion creation page"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.assertion_method_cit_db.choices = [
            (item, item) for item in CLINVAR_ASSERTION_METHOD_CIT_DB_OPTIONS
        ]
        self.assertion_method_cit_db.data = "PMID"
        self.assertion_method_cit_id.data = ASSERTION_METHOD_GERMLINE_CIT.split(":")[1]

    assertion_method = StringField("Assertion method", default=ASSERTION_METHOD_GERMLINE)

    # Variant-specific fields
    case_id = HiddenField()
    local_id = HiddenField()
    linking_id = HiddenField()
    ref = HiddenField()
    alt = HiddenField()
    gene_symbol = StringField("Gene symbols, comma-separated")
    inheritance_mode = SelectField(
        "Inheritance model",
        choices=[("", "-")] + [(item, item) for item in CLINVAR_INHERITANCE_MODELS],
    )
    clinsig = SelectField(
        "Germline classification", choices=[(item, item) for item in GERMLINE_CLASSIF_TERMS[:5]]
    )
    clinsig_comment = TextAreaField("Comment on classification")
    clinsig_cit = TextAreaField("Clinical significance citations (with identifier)")
    hpo_terms = MultiCheckboxField("Case-associated HPO terms", choices=[])
    omim_terms = MultiCheckboxField("Case-associated OMIM terms", choices=[])
    orpha_terms = MultiCheckboxField("Case-associated Orphanet terms", choices=[])
    condition_comment = TextAreaField("Additional comments describing condition")
    condition_type = SelectField(
        "Condition ID type", choices=[(key, key) for key, value in CONDITION_PREFIX.items()]
    )
    conditions = SelectMultipleField("Condition ID value, without prefix")
    multiple_condition_explanation = SelectField(
        "Explanation for multiple conditions",
        choices=[(item, item) for item in MULTIPLE_CONDITION_EXPLANATION],
    )


class SNVariantForm(ClinVarVariantForm):
    """Inherits fields from the general ClinVar variant form and adds fields specific to SNVs"""

    chromosome = HiddenField()
    start = HiddenField()
    stop = HiddenField()
    tx_hgvs = RadioField("Transcipts and HGVS", choices=[], validators=[validators.Optional()])
    variations_ids = StringField("Variation identifiers (dbSNPs)")


class SVariantForm(ClinVarVariantForm):
    """Inherits fields from the general ClinVar variant form and adds fields specific to SVs"""

    funct_conseq = SelectField(
        "Functional consequence (based on experimental evidence, leave blank if unsure)",
        choices=[],
    )
    var_type = SelectField(
        "Type of structural variant", choices=[(item, item) for item in CLINVAR_SV_TYPES]
    )
    ncopy = IntegerField("Copy number")
    ref_copy = IntegerField("Reference copy number")
    chromosome = StringField("Chromosome")
    end_chromosome = StringField("End chromosome")
    breakpoint1 = IntegerField("Breakpoint 1")
    breakpoint2 = IntegerField("Breakpoint 2")
    outer_start = IntegerField("Outer start")
    inner_start = IntegerField("Inner start")
    inner_stop = IntegerField("Inner stop")
    outer_stop = IntegerField("Outer stop")
    comments = TextAreaField("Comments on this variant")


class CaseDataForm(FlaskForm):
    """Contains the key/values to fill in to specify a case individual (or sample) in the ClinVar submssion creation page
    Schema available here: https://github.com/Clinical-Genomics/preClinVar/blob/718905521590196dc84fd576bc43d9fac418b97a/preClinVar/resources/submission_schema.json#L288
    """

    include_ind = BooleanField("Include individual")
    individual_id = StringField("Individual ID")
    linking_id = HiddenField()
    affected_status = SelectField(
        "Affected Status", choices=[(item, item) for item in AFFECTED_STATUS]
    )
    allele_of_origin = SelectField(
        "Allele of origin", choices=[(item, item) for item in ALLELE_OF_ORIGIN]
    )
    collection_method = SelectField(
        "Collection method",
        default="clinical testing",
        choices=[(item, item) for item in COLLECTION_METHOD],
    )


### Cancer variant - related forms


class CancerSNVariantForm(BaseClinVarVariantForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.assertion_method_cit_id.data = "25741868"  # Richards 2015
        self.assertion_method_cit_db.choices = [
            (item, item) for item in CLINVAR_API_ASSERTION_METHOD_CIT_DB_OPTIONS
        ]
        self.assertion_method_cit_db.data = "PubMed"
