# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import (BooleanField, TextField, SelectMultipleField, TextField)

from scout.constants import INHERITANCE_MODELS


class PanelGeneForm(FlaskForm):
    disease_associated_transcripts = SelectMultipleField('Disease transcripts', choices=[])
    reduced_penetrance = BooleanField()
    mosaicism = BooleanField()
    database_entry_version = TextField()
    inheritance_models = SelectMultipleField(choices=INHERITANCE_MODELS)
    custom_inheritance_models = TextField('Other inheritance models (comma separated)')
    comment = TextField()
