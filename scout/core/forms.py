# -*- coding: utf-8 -*-
"""

"main concept of MongoDB is embed whenever possible"
Ref: http://stackoverflow.com/questions/4655610#comment5129510_4656431
"""
from __future__ import absolute_import, unicode_literals
from flask_wtf import Form
from flask_wtf.file import FileField
from wtforms import (DecimalField as _DecimalField, Field,
                     SelectMultipleField, RadioField, DateField)
from wtforms import widgets

from ..models.variant import GENETIC_MODELS, SO_TERMS, FEATURE_TYPES
from .._compat import text_type

REGION_ANNOTATIONS = [(term, term.replace('_', ' ')) for term in FEATURE_TYPES]
FUNC_ANNOTATIONS = [(term, term.replace('_', ' ')) for term in SO_TERMS]


def process_filters_form(form):
  """Make some necessary corrections to the form data.

  This should ideally be handled with ``form.validate_on_submit`` but
  this will have to do in the mean time.
  """
  # make sure HGNC symbols are handled correctly
  if len(form.hgnc_symbols.data) == 1:
    if ',' in form.hgnc_symbols.data[0]:
      form.hgnc_symbols.data = [x.strip() for x in
                                form.hgnc_symbols.data[0].split(',')
                                if x]

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
  widget = widgets.TextInput()

  def _value(self):
    if self.data:
      return ', '.join(self.data)

    else:
      return ''


class MultiCheckboxField(SelectMultipleField):
  """A multiple-select, except displays a list of checkboxes.

  Iterating the field will produce subfields, allowing custom rendering
  of the enclosed checkbox fields.
  """
  widget = widgets.ListWidget(prefix_label=False)
  option_widget = widgets.CheckboxInput()


class FiltersForm(Form):
  # choices populated dynamically
  gene_lists = MultiCheckboxField(choices=[])
  hgnc_symbols = ListField()

  thousand_genomes_frequency = DecimalField('1000 Genomes', places=None)
  exac_frequency = DecimalField('ExAC', places=None)

  region_annotations = MultiCheckboxField(choices=REGION_ANNOTATIONS)
  functional_annotations = MultiCheckboxField(choices=FUNC_ANNOTATIONS)
  genetic_models = MultiCheckboxField(choices=GENETIC_MODELS)


class GeneListUpload(Form):
  gene_list = FileField('Dynamic gene list upload')


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

  form.gene_lists.data = [gene_list for gene_list
                          in (form.gene_lists.data or [])
                          if gene_list]
  return form
