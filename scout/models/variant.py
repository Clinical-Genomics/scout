# -*- coding: utf-8 -*-
"""

"main concept of MongoDB is embed whenever possible"
Ref: http://stackoverflow.com/questions/4655610#comment5129510_4656431
"""
from __future__ import absolute_import, unicode_literals

from mongoengine import *


class VariantCommon(EmbeddedDocument):
  # Gene ids:
  hgnc_symbols = ListField(StringField())
  ensemble_gene_ids = ListField(StringField())
  # Frequencies:
  thousand_genomes_frequency = FloatField()
  exac_frequency = FloatField()
  # Predicted deleteriousness:
  cadd_score = FloatField()
  sift_predictions = ListField(StringField())
  polyphen_predictions = ListField(StringField())
  functional_annotation = ListField(StringField())
  region_annotation = ListField(StringField())

  def __unicode__(self):
    return "%s:%s" % (self.chrom, self.position)


class GTCall(EmbeddedDocument):
  sample = StringField()
  genotype_call = StringField()
  allele_depths = ListField(IntField())
  read_depth = IntField()
  genotype_quality = IntField()

  def __unicode__(self):
    return self.sample


class VariantCaseSpecific(EmbeddedDocument):
  rank_score = FloatField()
  variant_rank = IntField()
  quality = FloatField()
  filters = ListField(StringField())
  samples = ListField(EmbeddedDocumentField(GTCall))
  genetic_models = ListField(StringField(choices=[
    'AR_hom', 'AR_comp', 'AR_comp_dn', 'AR_hom_dn', 'AD', 'AD_dn', 'XR', 'XR_dn', 'XD', 'XD_dn'
  ]))

  def __unicode__(self):
    return 'placeholder'


class Variant(Document):
  variant_id = StringField(primary_key=True)
  display_name = StringField(required=True)
  chromosome = StringField(required=True)
  position = IntField(required=True)
  reference = StringField(required=True)
  alternatives = ListField(StringField(), required=True)
  db_snp_ids = ListField(StringField())
  common = EmbeddedDocumentField(VariantCommon)
  specific = MapField(EmbeddedDocumentField(VariantCaseSpecific))

  def __unicode__(self):
    return self.display_name
