# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import (BooleanField, DecimalField, Field, SelectField,
                     SelectMultipleField)
from wtforms.widgets import TextInput

from scout.constants import CLINSIG_MAP, FEATURE_TYPES, GENETIC_MODELS, SO_TERMS

CLINSIG_OPTIONS  = list(CLINSIG_MAP.items())
FUNC_ANNOTATIONS = [(term, term.replace('_', ' ')) for term in SO_TERMS]
REGION_ANNOTATIONS = [(term, term.replace('_', ' ')) for term in FEATURE_TYPES]


class TagListField(Field):
    widget = TextInput()

    def _value(self):
        if self.data:
            return ', '.join(self.data)
        else:
            return ''

    def process_formdata(self, valuelist):
        if valuelist:
            self.data = [x.strip() for x in valuelist[0].split(',') if x.strip()]
        else:
            self.data = []


class FiltersForm(FlaskForm):
    gene_panels = SelectMultipleField(choices=[])
    hgnc_symbols = TagListField()

    region_annotations = SelectMultipleField(choices=REGION_ANNOTATIONS)
    functional_annotations = SelectMultipleField(choices=FUNC_ANNOTATIONS)
    genetic_models = SelectMultipleField(choices=GENETIC_MODELS)

    cadd_score = DecimalField('CADD', places=2)
    cadd_inclusive = BooleanField()
    clinsig = SelectMultipleField('CLINSIG', choices=CLINSIG_OPTIONS)

    thousand_genomes_frequency = DecimalField('1000 Genomes', places=2)
    exac_frequency = DecimalField('ExAC', places=2)
