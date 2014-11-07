
# -*- coding: utf-8 -*-
"""

"main concept of MongoDB is embed whenever possible"
Ref: http://stackoverflow.com/questions/4655610#comment5129510_4656431
"""
from __future__ import absolute_import, unicode_literals
from datetime import datetime

from .extensions import db


class Whitelist(db.Document):
  email = db.EmailField(required=True, unique=True)
  created_at = db.DateTimeField(default=datetime.now)
  default_institute = db.ReferenceField('Institute')


class User(db.Document):
  email = db.EmailField(required=True, unique=True)
  name = db.StringField(max_length=40, required=True)
  created_at = db.DateTimeField(default=datetime.now)
  accessed_at = db.DateTimeField()
  location = db.StringField()
  institutes = db.ListField(db.ReferenceField('Institute'))
  roles = db.ListField(db.ReferenceField('Role'))

  # Flask-Login integration
  def is_authenticated(self):
    return True

  def is_active(self):
    return True

  def is_anonymous(self):
    return False

  def get_id(self):
    return str(self.id)

  def has_role(self, query_role):
    return query_role in {role.name for role in self.roles}

  # required for Flask-Admin interface
  def __unicode__(self):
    return self.name


class Role(db.Document):
  name = db.StringField(required=True, unique=True)
  created_at = db.DateTimeField(default=datetime.now)

  def __unicode__(self):
    return self.name


class Sample(db.EmbeddedDocument):
  name = db.StringField(required=True, unique=True)
  display_name = db.StringField()

  capture_kit = db.StringField()
  inheritance_model = db.ListField(db.StringField())
  phenotype = db.StringField()
  sex = db.StringField()

  def __unicode__(self):
    return self.name


class Case(db.EmbeddedDocument):
  name = db.StringField(required=True, unique=True)
  assignee = db.ReferenceField('User')
  samples = db.ListField(db.EmbeddedDocumentField(Sample))
  databases = db.ListField(db.StringField())
  created_at = db.DateTimeField(default=datetime.now)
  updated_at = db.DateTimeField(default=datetime.now)
  suspects = db.ListField(db.ReferenceField('Variant'))

  def __unicode__(self):
    return self.name


class Institute(db.Document):
  name = db.StringField(required=True, unique=True)
  display_name = db.StringField(required=True, unique=True)
  sanger_recipients = db.ListField(db.EmailField())
  cases = db.ListField(db.EmbeddedDocumentField(Case))
  created_at = db.DateTimeField(default=datetime.now)

  def __unicode__(self):
    return self.name


class VariantCommon(db.EmbeddedDocument):
  chrom = db.StringField()
  position = db.IntField()
  reference = db.StringField()
  alternative = db.StringField()
  rs_number = db.StringField()
  hgnc_symbol = db.StringField()
  gene_ids = db.DictField()
  thousand_genomes_frequency = db.FloatField()
  cadd_score = db.FloatField()

  def __unicode__(self):
    return "%s:%s" % (self.chrom, self.position)


class VariantCaseSpecific(db.EmbeddedDocument):
  rank_score = db.IntField()
  inheritance_models = db.ListField(db.StringField(choices=[
    'AR_hom', 'AR_compound', 'AR_hom_denovo', 'AD', 'AD_denovo', 'X', 'X_dn'
  ]))


class Variant(db.Document):
  md5_key = db.StringField(required=True, unique=True)
  common = db.EmbeddedDocumentField(VariantCommon)
  case_specifics = db.ListField(db.EmbeddedDocumentField(VariantCaseSpecific))

  def __unicode__(self):
    return self.md5_key
