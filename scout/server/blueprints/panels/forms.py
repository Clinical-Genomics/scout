# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import (BooleanField, TextField, SelectMultipleField)

from scout.constants import GENETIC_MODELS


class PanelGeneForm(FlaskForm):
    disease_associated_transcripts = SelectMultipleField('Disease transcripts', choices=[])
    reduced_penetrance = BooleanField()
    mosaicism = BooleanField()
    inheritance_models = SelectMultipleField(choices=GENETIC_MODELS)
    comment = TextField()
