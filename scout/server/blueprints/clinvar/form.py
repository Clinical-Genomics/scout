import logging

from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    HiddenField,
    IntegerField,
    RadioField,
    SelectField,
    SelectMultipleField,
    StringField,
    SubmitField,
    TextAreaField,
    validators,
    widgets,
)
from wtforms.ext.dateutil.fields import DateField

from scout.constants import (
    AFFECTED_STATUS,
    ALLELE_OF_ORIGIN,
    ASSERTION_METHOD,
    ASSERTION_METHOD_CIT,
    CLINVAR_INHERITANCE_MODELS,
    CLNSIG_TERMS,
    SV_TYPES,
)

LOG = logging.getLogger(__name__)


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class ClinVarVariantForm(FlaskForm):
    """Contains the key/values to fill in to specify a single general variant in the ClinVar submssion creation page"""

    # Variant-specific fields
    category = HiddenField()
    local_id = HiddenField()
    linking_id = HiddenField()
    chromosome = HiddenField()
    ref = HiddenField()
    alt = HiddenField()
    gene_symbols = StringField("Gene symbols")
    inheritance_models = SelectField(
        "Inheritance models", choices=[(model, model) for model in CLINVAR_INHERITANCE_MODELS]
    )
    clinsig = SelectField("Clinical Significance", choices=[(term, term) for term in CLNSIG_TERMS])
    clinsig_comment = TextAreaField("Comment on clinical significance")
    clinsig_cit = TextAreaField("Clinical significance citations (with identifier)")
    eval_date = DateField("Date last evaluated")
    hpo_terms = MultiCheckboxField("Variant-associated HPO terms", choices=[])
    omim_terms = MultiCheckboxField("Variant-associated OMIM terms", choices=[])
    variant_condition_comment = TextAreaField("Additional comments describing condition")

    # Extra fields:
    assertion_method = StringField("Assertion method", default=ASSERTION_METHOD)
    assertion_method_cit = TextAreaField("Assertion method citation", default=ASSERTION_METHOD_CIT)

    submit_btn = SubmitField("Add variant to submission")


class SNVariantForm(ClinVarVariantForm):
    """Inherits fields from the general ClinVar variant form and adds fields specific to SNVs"""

    start = HiddenField()
    stop = HiddenField()
    tx_hgvs = RadioField("Transcipts and HGVS", choices=[], validators=[validators.Optional()])
    dbsnp_id = StringField("Variation identifiers (dbSNPs)")
    funct_conseq = SelectField(
        "Functional consequence (based on experimental evidence, leave blank if unsure)",
        choices=[],
    )


class SVariantForm(ClinVarVariantForm):
    """Inherits fields from the general ClinVar variant form and adds fields specific to SVs"""

    funct_conseq = SelectField(
        "Functional consequence (based on experimental evidence, leave blank if unsure)",
        choices=[],
    )
    sv_type = SelectField("Type of structural variant", choices=[(type, type) for type in SV_TYPES])
    copy_number = IntegerField("Copy number")
    ref_copy_number = IntegerField("Reference copy number")
    bp_1 = IntegerField("Breakpoint 1")
    bp_2 = IntegerField("Breakpoint 2")
    outer_start = IntegerField("Outer start")
    inner_start = IntegerField("Inner start")
    inner_stop = IntegerField("Inner stop")
    outer_stop = IntegerField("Outer stop")
    comments = TextAreaField("Comments on this variant")


class CaseDataForm(FlaskForm):
    """Contains the key/values to fill in to specify a case individual (or sample) in the ClinVar submssion creation page"""

    affected_status = BooleanField(
        "Affected Status", choices=[(status, status) for status in AFFECTED_STATUS]
    )
