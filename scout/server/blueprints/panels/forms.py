"""Code for panel gene form"""

from flask_wtf import FlaskForm
from wtforms import BooleanField, SelectMultipleField, StringField, SubmitField
from wtforms.validators import DataRequired, Regexp

from scout.constants import GENE_PANELS_INHERITANCE_MODELS


class PanelGeneForm(FlaskForm):
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
        "Search", render_kw={"value": "searchGeneSubmit", "class": "btn btn-secondary"}
    )
