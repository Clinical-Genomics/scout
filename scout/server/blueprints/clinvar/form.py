import logging

from flask.ext.wtf.html5 import NumberInput
from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    RadioField,
    SelectField,
    SelectMultipleField,
    StringField,
    TextAreaField,
)
from wtforms.ext.dateutil.fields import DateField

LOG = logging.getLogger(__name__)


class NonValidatingSelectMultipleField(SelectMultipleField):
    """Necessary to skip validation of dynamic multiple selects in form"""

    def pre_validate(self, _form):
        pass


class ClinVarVariantForm(FlaskForm):
    """Contains the key/values to fill in to specify a single general variant in the ClinVar submssion creation page"""

    category = HiddenField()
    local_id = HiddenField()
    linking_id = HiddenField()
    chromosome = HiddenField()
    ref = HiddenField()
    alt = HiddenField()
    gene_symbols = HiddenField()
    inheritance_model = NonValidatingSelectMultipleField("Inheritance models", choices=[])
    clinsig = SelectField("Clinical Significance", choices=[])
    clinsig_comment = TextAreaField("Comment on clinical significance")
    clinsig_cit = TextAreaField("Clinical significance citations")
    eval_date = DateField("Date last evaluated")
    funct_conseq = SelectField(
        "Functional consequence (based on experimental evidence, leave blank if unsure)",
        choices=[],
    )
    funct_conseq_comment = TextAreaField("Comment on functional consequence")
    hpo_terms = NonValidatingSelectMultipleField("Variant-associated HPO terms", choices=[])
    omim_terms = NonValidatingSelectMultipleField("Variant-associated OMIM terms", choices=[])
    variant_condition_comment = TextAreaField("Additional comments describing condition")

    # Extra fields:
    assertion_method = StringField("Assertion method")
    assertion_method_cit = TextAreaField("Assertion method citation")
    drug_resp_cond = TextAreaField("Drug response condition(s)")


class ClinVarSNVariantForm(ClinVarVariantForm):
    """Inherits fields from the general ClinVar variant form and adds fields specific to SNVs"""

    start = HiddenField()
    stop = HiddenField()
    tx_hgvs = RadioField("Transcipt and HGVS", choices=[], validators=[validators.Optional()])
    dbsnp_ids = StringField("Variation identifiers (dbSNPs)")
    funct_conseq = SelectField(
        "Functional consequence (based on experimental evidence, leave blank if unsure)",
        choices=[],
    )


class ClinVarSVariantForm(ClinVarVariantForm):
    """Inherits fields from the general ClinVar variant form and adds fields specific to SVs"""

    funct_conseq = SelectField(
        "Functional consequence (based on experimental evidence, leave blank if unsure)",
        choices=[],
    )
    sv_type = SelectField("Type of structural variant", choices=[])
    copy_number = IntegerField("Copy number", widget=NumberInput())
    ref_copy_number = IntegerField("Reference copy number", widget=NumberInput())
    bp_1 = IntegerField("Breakpoint 1", widget=NumberInput())
    bp_2 = IntegerField("Breakpoint 2", widget=NumberInput())
    outer_start = IntegerField("Outer start", widget=NumberInput())
    inner_start = IntegerField("Inner start", widget=NumberInput())
    inner_stop = IntegerField("Inner stop", widget=NumberInput())
    outer_stop = IntegerField("Outer stop", widget=NumberInput())
    comments = TextAreaField("Comments on this variant")
