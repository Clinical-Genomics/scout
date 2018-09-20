# -*- coding: utf-8 -*-
import decimal

from flask_wtf import FlaskForm
from wtforms import (BooleanField, DecimalField, Field, TextField, SelectMultipleField,
                     HiddenField, IntegerField)
from wtforms.widgets import TextInput

from scout.constants import (CLINSIG_MAP, FEATURE_TYPES, GENETIC_MODELS, SO_TERMS,
                             SPIDEX_LEVELS, SV_TYPES)

CLINSIG_OPTIONS = list(CLINSIG_MAP.items())
FUNC_ANNOTATIONS = [(term, term.replace('_', ' ')) for term in SO_TERMS]
REGION_ANNOTATIONS = [(term, term.replace('_', ' ')) for term in FEATURE_TYPES]
SV_TYPE_CHOICES = [(term, term.replace('_', ' ').upper()) for term in SV_TYPES]
SPIDEX_CHOICES = [(term, term.replace('_', ' ')) for term in SPIDEX_LEVELS]

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


class BetterDecimalField(DecimalField):
    """
    Very similar to WTForms DecimalField, except handles ',' and '.'.
    """

    def process_formdata(self, valuelist):
        if valuelist:
            raw_decimal = valuelist[0].replace(',', '.')
            try:
                self.data = decimal.Decimal(raw_decimal)
            except (decimal.InvalidOperation, ValueError):
                self.data = None
                raise ValueError(self.gettext('Not a valid decimal value'))


class FiltersForm(FlaskForm):
    variant_type = HiddenField(default='clinical')
    gene_panels = SelectMultipleField(choices=[])
    hgnc_symbols = TagListField('HGNC Symbols/Ids (case sensitive)')

    region_annotations = SelectMultipleField(choices=REGION_ANNOTATIONS)
    functional_annotations = SelectMultipleField(choices=FUNC_ANNOTATIONS)
    genetic_models = SelectMultipleField(choices=GENETIC_MODELS)

    cadd_score = BetterDecimalField('CADD', places=2)
    cadd_inclusive = BooleanField('CADD inclusive')
    clinsig = SelectMultipleField('CLINSIG', choices=CLINSIG_OPTIONS)
    clinsig_confident_always_returned = BooleanField('All CLINSIG confident')
    spidex_human = SelectMultipleField('SPIDEX', choices=SPIDEX_CHOICES)

    thousand_genomes_frequency = BetterDecimalField('1000 Genomes', places=2)
    exac_frequency = BetterDecimalField('ExAC', places=2)
    chrom = TextField('Chromosome')
    local_obs = IntegerField('Local obs. (archive)')


class CancerFiltersForm(FiltersForm):
    """docstring for CancerFiltersForm"""
    depth = IntegerField('Depth >')
    alt_count = IntegerField('Min alt count >')
    control_frequency = BetterDecimalField('Control freq. <', places=2)
    mvl_tag = BooleanField('In Managed Variant List')

class StrFiltersForm(FlaskForm):
    """docstring for CancerFiltersForm"""
    variant_type = HiddenField(default='clinical')

    chrom = TextField('Chromosome')
    gene_panels = SelectMultipleField(choices=[])
    repids = TagListField()

class SvFiltersForm(FlaskForm):
    gene_panels = SelectMultipleField(choices=[])
    hgnc_symbols = TagListField()

    region_annotations = SelectMultipleField(choices=REGION_ANNOTATIONS)
    functional_annotations = SelectMultipleField(choices=FUNC_ANNOTATIONS)
    genetic_models = SelectMultipleField(choices=GENETIC_MODELS)

    cadd_score = BetterDecimalField('CADD', places=2)
    cadd_inclusive = BooleanField('CADD inclusive')
    clinsig = SelectMultipleField('CLINSIG', choices=CLINSIG_OPTIONS)
    clinsig_confident_always_returned = BooleanField('All CLINSIG confident')

    chrom = TextField('Chromosome')
    size = TextField('Length')
    size_inclusive = BooleanField('Length inclusive')
    svtype = SelectMultipleField('SVType', choices=SV_TYPE_CHOICES)

    thousand_genomes_frequency = BetterDecimalField('1000 Genomes', places=2)
    clingen_ngi = IntegerField('ClinGen NGI obs')
