"""Code for panel gene form"""

from flask_wtf import FlaskForm
from wtforms import BooleanField, SelectField, SelectMultipleField, StringField, SubmitField
from wtforms.validators import DataRequired, Optional, Regexp, ValidationError

from scout.constants import GENE_PANELS_INHERITANCE_MODELS


class PanelGeneForm(FlaskForm):
    def __init__(self, store, *args, **kwargs):
        """Initialize the form with a store instance for database access"""
        super().__init__(*args, **kwargs)
        self.store = store

    disease_associated_transcripts = SelectMultipleField("Disease transcripts", choices=[])
    reduced_penetrance = BooleanField()
    mosaicism = BooleanField()
    database_entry_version = StringField()

    inheritance_models = SelectMultipleField(
        "Manual inheritance (pre-set terms)", choices=GENE_PANELS_INHERITANCE_MODELS
    )
    custom_inheritance_models = StringField(
        "Manual inheritance (free text terms)",
    )
    comment = StringField()
    proxy_region = StringField("Region proxy ID", render_kw={"placeholder": "ISCA-1234"})

    def validate_proxy_region(self, region_field):
        """Ensure the supplied proxy region exists in the regions collection."""
        if not region_field.data:
            return

        region_id = region_field.data.strip()
        region = self.store.region_collection.find_one(
            {"isca_id": region_id},
            {"_id": 1},
        )

        if region is None:
            raise ValidationError(f"Region '{region_id}' was not found.")


class GeneSearchForm(FlaskForm):
    """Form for searching genes within panels using an autocomplete-enabled input."""

    searchGene = StringField(
        "Search Gene in Panels",
        validators=[
            DataRequired(),
            Regexp(
                r"^[0-9]+\s*\|\s*.*",
                message="Must contain a numeric HGNC id, a pipe (|), and a description",
            ),
        ],
        render_kw={
            "class": "form-control typeahead_gene mb-1",
            "autocomplete": "off",
            "placeholder": "Search Gene in Panels",
            "data-provide": "typeahead",
        },
    )

    submit = SubmitField(
        "Search",
        render_kw={
            "label": "Search gene",
            "class": "btn btn-secondary",
        },
    )


class PanelFilterForm(FlaskForm):
    """Contains form items used to filter panels by institute and panel name."""

    searchName = StringField(
        "Search panels..",
        validators=[Optional()],
        render_kw={"class": "search form-control w-auto"},
    )

    instituteFilter = SelectField(
        "Institute",
        choices=[],
        validate_choice=False,
        validators=[Optional()],
        render_kw={"class": "form-select w-auto", "name": "institute"},
    )

    submit = SubmitField("Search", render_kw={"class": "btn btn-primary"})
