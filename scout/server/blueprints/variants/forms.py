# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import (BooleanField, DecimalField, Field, TextField, SelectMultipleField,
                     HiddenField)
from wtforms.widgets import TextInput

from scout.constants import CLINSIG_MAP, FEATURE_TYPES, GENETIC_MODELS, SO_TERMS, SV_TYPES

CLINSIG_OPTIONS = list(CLINSIG_MAP.items())
FUNC_ANNOTATIONS = [(term, term.replace('_', ' ')) for term in SO_TERMS]
REGION_ANNOTATIONS = [(term, term.replace('_', ' ')) for term in FEATURE_TYPES]
SV_TYPE_CHOICES = [(term, term.replace('_', ' ').upper()) for term in SV_TYPES]


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
    variant_type = HiddenField()
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


class SvFiltersForm(FlaskForm):
    gene_panels = SelectMultipleField(choices=[])
    hgnc_symbols = TagListField()

    region_annotations = SelectMultipleField(choices=REGION_ANNOTATIONS)
    functional_annotations = SelectMultipleField(choices=FUNC_ANNOTATIONS)
    genetic_models = SelectMultipleField(choices=GENETIC_MODELS)

    cadd_score = DecimalField('CADD', places=2)
    cadd_inclusive = BooleanField()
    clinsig = SelectMultipleField('CLINSIG', choices=CLINSIG_OPTIONS)

    chrom = TextField('Chromosome')
    size = TextField('Length')
    size_inclusive = BooleanField('Length inclusive')
    svtype = SelectMultipleField('SVType', choices=SV_TYPE_CHOICES)

    thousand_genomes_frequency = DecimalField('1000 Genomes', places=2)
