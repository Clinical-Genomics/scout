# -*- coding: utf-8 -*-
"""

"main concept of MongoDB is embed whenever possible"
Ref: http://stackoverflow.com/questions/4655610#comment5129510_4656431
"""
from __future__ import absolute_import, unicode_literals
from datetime import datetime

from ..extensions import db


class VariantCommon(db.EmbeddedDocument):
  # Gene ids:
  hgnc_symbols = db.ListField(db.StringField())
  ensemble_gene_ids = db.ListField(db.StringField())
  # Frequencies:
  thousand_genomes_frequency = db.FloatField()
  exac_frequency = db.FloatField()
  # Predicted deleteriousness:
  cadd_score = db.FloatField()
  sift_predictions = db.ListField(db.StringField())
  polyphen_predictions = db.ListField(db.StringField())
  functional_annotation = db.ListField(db.StringField())
  region_annotation = db.ListField(db.StringField())

  def __unicode__(self):
    return "%s:%s" % (self.chrom, self.position)


class GTCall(db.EmbeddedDocument):
  sample = db.StringField()
  genotype_call = db.StringField()
  allele_depths = db.ListField(db.IntField())
  read_depth = db.IntField()
  genotype_quality = db.IntField()

  def __unicode__(self):
    return self.sample


class VariantCaseSpecific(db.EmbeddedDocument):
  rank_score = db.IntField()
  variant_rank = db.IntField()
  quality = db.FloatField()
  filters = db.ListField(db.StringField())
  samples = db.ListField(db.EmbeddedDocumentField(GTCall))
  genetic_models = db.ListField(db.StringField(choices=[
    'AR_hom', 'AR_compound', 'AR_hom_denovo', 'AD', 'AD_denovo', 'X', 'X_dn'
  ]))

  def __unicode__(self):
    return 'placeholder'


class Variant(db.Document):
  _id = db.StringField(primary_key=True)
  md5_key = db.StringField()
  display_name = db.StringField(required=True)
  chromosome = db.StringField(required=True)
  position = db.IntField(required=True)
  reference = db.StringField(required=True)
  alternatives = db.ListField(db.StringField(), required=True)
  db_snp_ids = db.ListField(db.StringField())
  common = db.EmbeddedDocumentField(VariantCommon)
  specific = db.MapField(db.EmbeddedDocumentField(VariantCaseSpecific))

  def __unicode__(self):
    return self.display_name
