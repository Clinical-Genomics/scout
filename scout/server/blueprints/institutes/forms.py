# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    DecimalField,
    Field,
    IntegerField,
    SelectField,
    SelectMultipleField,
    StringField,
    SubmitField,
    validators,
)
from wtforms.widgets import PasswordInput, TextInput

from scout.constants import PHENOTYPE_GROUPS
from scout.models.case import STATUS

CATEGORY_CHOICES = [("snv", "SNV"), ("sv", "SV")]


class NonValidatingSelectField(SelectField):
    """Necessary to skip validation of dynamic selects in form"""

    def pre_validate(self, form):
        pass


class NonValidatingSelectMultipleField(SelectMultipleField):
    """Necessary to skip validation of dynamic multiple selects in form"""

    def pre_validate(self, form):
        pass


class InstituteForm(FlaskForm):
    """Institute-specific settings"""

    hpo_tuples = []
    for key in PHENOTYPE_GROUPS.keys():
        option_name = " ".join(
            [
                key,
                ",",
                PHENOTYPE_GROUPS[key]["name"],
                "(",
                PHENOTYPE_GROUPS[key]["abbr"],
                ")",
            ]
        )
        hpo_tuples.append((option_name, option_name))

    display_name = StringField(
        "Institute display name",
        validators=[validators.InputRequired(), validators.Length(min=2, max=100)],
    )
    sanger_emails = NonValidatingSelectMultipleField(
        "Sanger recipients", validators=[validators.Optional()]
    )
    coverage_cutoff = IntegerField(
        "Coverage cutoff",
        validators=[validators.Optional(), validators.NumberRange(min=1)],
    )
    frequency_cutoff = DecimalField(
        "Frequency cutoff",
        validators=[
            validators.Optional(),
            validators.NumberRange(min=0, message="Number must be positive"),
        ],
    )

    pheno_group = StringField("New phenotype group", validators=[validators.Optional()])
    pheno_abbrev = StringField("Abbreviation", validators=[validators.Optional()])

    gene_panels = NonValidatingSelectMultipleField(
        "Gene panels available for variants filtering",
        validators=[validators.Optional()],
    )

    gene_panels_matching = NonValidatingSelectMultipleField(
        "Gene panels available for other variants matching (managed and causatives variants)",
        validators=[validators.Optional()],
    )

    pheno_groups = NonValidatingSelectMultipleField("Custom phenotype groups", choices=hpo_tuples)
    cohorts = NonValidatingSelectMultipleField(
        "Available patient cohorts", validators=[validators.Optional()]
    )

    institutes = NonValidatingSelectMultipleField("Institutes to share cases with", choices=[])

    loqusdb_id = NonValidatingSelectField("LoqusDB id", choices=[])

    alamut_key = StringField("Alamut API key", validators=[validators.Optional()])

    alamut_institution = StringField("Alamut Institution ID", validators=[validators.Optional()])

    check_show_all_vars = BooleanField("Preselect 'Include variants only present in unaffected'")

    soft_filters = NonValidatingSelectMultipleField(
        "Default soft filters", validators=[validators.Optional()]
    )

    clinvar_key = StringField("API key", widget=PasswordInput(hide_value=False))

    clinvar_emails = NonValidatingSelectMultipleField(
        "ClinVar submitters",
        validators=[
            validators.Optional(),
        ],
        choices=[],
    )

    show_all_cases_status = NonValidatingSelectMultipleField(
        "Always display all cases from the following categories",
        choices=[(status, status) for status in STATUS],
    )

    submit_btn = SubmitField("Save settings")


class BeaconDatasetForm(FlaskForm):
    """A form that allows admins to create a new Beacon dataset for the institute with a controlled dictionary"""

    beacon_dataset = NonValidatingSelectField("Select dataset to be created")
    beacon_submit_btn = SubmitField("Create dataset")


# make a base class or other utility with this instead..
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


class GeneVariantFiltersForm(FlaskForm):
    """Base FiltersForm for SNVs"""

    variant_type = SelectMultipleField(choices=[("clinical", "clinical"), ("research", "research")])
    category = SelectMultipleField(choices=CATEGORY_CHOICES)
    hgnc_symbols = TagListField(
        "HGNC Symbols (comma-separated, case sensitive)",
        validators=[validators.InputRequired()],
    )
    institute = SelectMultipleField(choices=[])
    rank_score = IntegerField(default=15)
    phenotype_terms = TagListField("HPO terms (comma-separated)")
    phenotype_groups = TagListField("Phenotype groups")
    similar_case = TagListField("Phenotypically similar case")
    cohorts = TagListField("Cohorts")
    filter_variants = SubmitField(label="Filter variants")
    filter_export_variants = SubmitField(label="Filter and export variants")


class CaseFilterForm(FlaskForm):
    """Takes care of cases filtering on cases page"""

    case = StringField("Case or Individual name", [validators.Optional()])
    exact_pheno = StringField("HPO terms, comma-separated", [validators.Optional()])
    exact_dia = StringField("Disease terms, comma-separated", [validators.Optional()])
    synopsis = StringField("Synopsis", [validators.Optional()])
    panel = StringField("Gene panel name", [validators.Optional()])
    status = StringField("Case status", [validators.Optional()])
    tags = StringField("Case tag", [validators.Optional()])
    track = StringField("Case track", [validators.Optional()])
    pheno_group = StringField("Phenotype group", [validators.Optional()])
    cohort = StringField("Cohort", [validators.Optional()])
    similar_case = StringField("Similar case", [validators.Optional()])
    similar_pheno = StringField("Similar phenotype", [validators.Optional()])
    pinned = StringField("Pinned gene", [validators.Optional()])
    causative = StringField("Causative gene", [validators.Optional()])
    user = StringField("Assigned user", [validators.Optional()])
    search_limit = IntegerField("Limit", [validators.Optional()], default=100)
    advanced_search = BooleanField("Advanced search options")
    skip_assigned = BooleanField("Hide assigned")
    is_research = BooleanField("Research only")
    clinvar_submitted = BooleanField("Has ClinVar submissions")
    has_rna = BooleanField("Has RNA-seq data")
    validation_ordered = BooleanField("Validation pending")
    search = SubmitField(label="Search")
    export = SubmitField(label="Filter and export")
