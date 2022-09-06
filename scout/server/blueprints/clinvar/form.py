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
)
from wtforms.ext.dateutil.fields import DateField

LOG = logging.getLogger(__name__)


class ClinVarVariantForm(FlaskForm):
    """Contains the key/values to fill in to specify a single general variant in the ClinVar submssion creation page"""

    category = HiddenField()
    local_id = HiddenField()
    linking_id = HiddenField()
    chromosome = HiddenField()
    ref = HiddenField()
    alt = HiddenField()
    gene_symbols = HiddenField()
    inheritance_models = SelectMultipleField("Inheritance models", choices=[])
    clinsig = SelectField("Clinical Significance", choices=[])
    clinsig_comment = TextAreaField("Comment on clinical significance")
    clinsig_cit = TextAreaField("Clinical significance citations")
    eval_date = DateField("Date last evaluated")
    funct_conseq_comment = TextAreaField("Comment on functional consequence")
    hpo_terms = SelectMultipleField("Variant-associated HPO terms", choices=[])
    omim_terms = SelectMultipleField("Variant-associated OMIM terms", choices=[])
    variant_condition_comment = TextAreaField("Additional comments describing condition")

    # Extra fields:
    assertion_method = StringField("Assertion method")
    assertion_method_cit = TextAreaField("Assertion method citation")
    drug_resp_cond = TextAreaField("Drug response condition(s)")

    submit_btn = SubmitField("Add to submission")


class SNVariantForm(ClinVarVariantForm):
    """Inherits fields from the general ClinVar variant form and adds fields specific to SNVs"""

    start = HiddenField()
    stop = HiddenField()
    tx_hgvs = RadioField("Transcipt and HGVS", choices=[], validators=[validators.Optional()])
    dbsnp_ids = StringField("Variation identifiers (dbSNPs)")
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
    sv_type = SelectField("Type of structural variant", choices=[])
    copy_number = IntegerField("Copy number")
    ref_copy_number = IntegerField("Reference copy number")
    bp_1 = IntegerField("Breakpoint 1")
    bp_2 = IntegerField("Breakpoint 2")
    outer_start = IntegerField("Outer start")
    inner_start = IntegerField("Inner start")
    inner_stop = IntegerField("Inner stop")
    outer_stop = IntegerField("Outer stop")
    comments = TextAreaField("Comments on this variant")
