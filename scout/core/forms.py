# -*- coding: utf-8 -*-
"""

"main concept of MongoDB is embed whenever possible"
Ref: http://stackoverflow.com/questions/4655610#comment5129510_4656431
"""
from __future__ import absolute_import, unicode_literals
from flask_wtf import Form
from wtforms import (DecimalField as _DecimalField, Field,
                     SelectMultipleField)
from wtforms.widgets import TextInput

from ..models.variant import GENETIC_MODELS, SO_TERMS, FEATURE_TYPES
from .._compat import text_type

REGION_ANNOTATIONS = [(term, term.replace('_', ' ')) for term in FEATURE_TYPES]
FUNC_ANNOTATIONS = [(term, term.replace('_', ' ')) for term in SO_TERMS]


def process_filters_form(form):
  # process HGNC symbols to list
  if form.hgnc_symbols.data:
    form.hgnc_symbols.data = [x.strip() for x in
                              form.hgnc_symbols.data[0].split(',')
                              if x]
  else:
    form.hgnc_symbols.data = []

  # correct decimal fields
  for field_name in ['thousand_genomes_frequency', 'exac_frequency']:
    field = getattr(form, field_name)

    if field.data:
      field.data = float(field.data)


class DecimalField(_DecimalField):
  """Modify regular DecimalField to better handle text input from user.

  Based on: http://stackoverflow.com/questions/15366452
  """
  def _value(self):
    try:
      # check whether you have a 'number'
      float(self.data)
      return super(DecimalField, self)._value()

    except (TypeError, ValueError):
      # self.data is 'None', 'asdf' ...
      return text_type(self.data) if self.data else ''


class ListField(Field):
  widget = TextInput()

  def _value(self):
    if self.data:
      return ', '.join(self.data)

    else:
      return ''

  def process_formdata(self, valuelist):
    if valuelist:
      self.data = [x.strip() for x in valuelist[0].split(',')]

    else:
      self.data = []


class FiltersForm(Form):
  # choices populated dynamically
  gene_lists = SelectMultipleField(choices=[])
  hgnc_symbols = ListField()

  thousand_genomes_frequency = DecimalField('1000 Genomes')
  exac_frequency = DecimalField('ExAC')

  region_annotations = SelectMultipleField(choices=REGION_ANNOTATIONS)
  functional_annotations = SelectMultipleField(choices=FUNC_ANNOTATIONS)
  genetic_models = SelectMultipleField(choices=GENETIC_MODELS)


def init_filters_form(get_args):
  """Initialize the filters form with GET request data.

  This is to get around some inconsistencies in the way the WTForms
  seems to handle GET request arguments. I suppose that it's difficult
  to reason about what is supposed to be a list and what is not.
  """
  # initialize the normal way to get lists inserted correctly
  form = FiltersForm(**get_args)

  for field_name in ['thousand_genomes_frequency', 'exac_frequency']:
    field = getattr(form, field_name)

    if field.data:
      field.data = field.data[0] if field.data[0] else None

  return form
