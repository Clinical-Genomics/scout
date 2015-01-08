# -*- coding: utf-8 -*-
"""

"main concept of MongoDB is embed whenever possible"
Ref: http://stackoverflow.com/questions/4655610#comment5129510_4656431
"""
from __future__ import absolute_import, unicode_literals
from flask_wtf import Form
from wtforms import FloatField, SelectField, SelectMultipleField, StringField

from ..models.variant import GENETIC_MODELS, SO_TERMS, FEATURE_TYPES

REGION_ANNOTATIONS = [(term, term.replace('_', ' ')) for term in FEATURE_TYPES]
FUNC_ANNOTATIONS = [(term, term.replace('_', ' ')) for term in SO_TERMS]


class FiltersForm(Form):
  gene_list = SelectField()  # dynamic select field
  hgnc_symbol = StringField()

  thousand_genomes_frequency = FloatField('1000 Genomes')
  exac_frequency = FloatField('ExAC')
  local_frequency = FloatField('Local')

  region_annotations = SelectMultipleField(choices=REGION_ANNOTATIONS)
  functional_annotations = SelectMultipleField(choices=FUNC_ANNOTATIONS)
  genetic_models = SelectMultipleField(choices=GENETIC_MODELS)


def init_filters_form(get_args, gene_lists=None):
  """Initialize the filters form with GET request data.

  This is to get around some inconsistencies in the way the WTForms
  seems to handle GET request arguments. I suppose that it's difficult
  to reason about what is supposed to be a list and what is not.
  """
  if gene_lists is None:
    gene_lists = []

  # initialize the normal way to get lists inserted correctly
  form = FiltersForm(**get_args)

  # add gene list options
  form.gene_list.choices = [(option, option) for option in gene_lists]

  if form.hgnc_symbol.data:
    form.hgnc_symbol.data = (form.hgnc_symbol.data[0]
                             if form.hgnc_symbol.data[0] != '' else None)

  for field_name in ['thousand_genomes_frequency', 'exac_frequency',
                     'local_frequency']:
    field = getattr(form, field_name)

    if field.data:
      field.data = float(field.data[0]) if field.data[0] else None

  return form
