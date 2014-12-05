# -*- coding: utf-8 -*-
"""

"main concept of MongoDB is embed whenever possible"
Ref: http://stackoverflow.com/questions/4655610#comment5129510_4656431
"""
from __future__ import absolute_import, unicode_literals
from flask_wtf import Form
from wtforms import FloatField, SelectField, SelectMultipleField, StringField

from ..models.variant import GENETIC_MODELS

REGION_ANNOTATIONS = (
  ('exonic', 'exonic'),
  ('intronic', 'intronic'),
  ('downstream', 'downstream'),
  ('intergenic', 'intergenic'),
  ('ncRNA_exonic', 'ncRNA_exonic'),
  ('ncRNA_intronic', 'ncRNA_intronic'),
  ('ncRNA_splicing', 'ncRNA_splicing'),
  ('ncRNA_UTR3', 'ncRNA_UTR3'),
  ('ncRNA_UTR5', 'ncRNA_UTR5'),
  ('splicing', 'splicing'),
  ('upstream', 'upstream'),
  ('UTR3', 'UTR3'),
  ('UTR5', 'UTR5')
)

FUNC_ANNOTATIONS = (
  ('-', '-'),
  ('frameshift deletion', 'frameshift deletion'),
  ('frameshift insertion', 'frameshift insertion'),
  ('frameshift substitution', 'frameshift substitution'),
  ('nonframeshift deletion', 'nonframeshift deletion'),
  ('nonframeshift insertion', 'nonframeshift insertion'),
  ('nonframeshift substitution', 'nonframeshift substitution'),
  ('nonsynonymous SNV', 'nonsynonymous SNV'),
  ('stopgain SNV', 'stopgain SNV'),
  ('stoploss SNV', 'stoploss SNV'),
  ('synonymous SNV', 'synonymous SNV'),
  ('unknown', 'unknown'),
)


class FiltersForm(Form):
  gene_list = SelectField()  # dynamic select field
  hgnc_symbol = StringField()

  thousand_genomes_frequency = FloatField('1000 Genomes')
  exac_frequency = FloatField('ExAC')
  local_frequency = FloatField('Local')

  region_annotations = SelectMultipleField(choices=REGION_ANNOTATIONS)
  functional_annotations = SelectMultipleField(choices=FUNC_ANNOTATIONS)
  genetic_models = SelectMultipleField(choices=GENETIC_MODELS)
