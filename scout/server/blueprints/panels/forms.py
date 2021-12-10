"""Code for panel gene form"""
from flask_wtf import FlaskForm
from wtforms import BooleanField, SelectMultipleField, StringField

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
