# -*- coding: utf-8 -*-
"""

"main concept of MongoDB is embed whenever possible"
Ref: http://stackoverflow.com/questions/4655610#comment5129510_4656431
"""
from __future__ import absolute_import, unicode_literals
from datetime import datetime

from ..extensions import db

class Individual(db.EmbeddedDocument):
  display_name = db.StringField()
  sex = db.StringField()
  phenotype = db.IntField()
  father = db.StringField()
  mother = db.StringField()
  individual_id = db.StringField()
  capture_kit = db.ListField(db.StringField())

  @property
  def sex_human(self):
    """Transform sex string into human readable form."""
    # pythonic switch statement
    return {
      '1': 'male',
      '2': 'female'
    }.get(self.sex, 'unknown')

  @property
  def phenotype_human(self):
    """Transform phenotype integer into human readable form."""
    # pythonic switch statement
    return {
      -9: 'missing',
       0: 'missing',
       1: 'unaffected',
       2: 'affected'
    }.get(self.phenotype, 'undefined')

  def __unicode__(self):
    return self.individual_id


class Case(db.Document):
  # This is the md5 string id for the family:
  case_id = db.StringField(primary_key=True, required=True)
  display_name = db.StringField(required=True)
  assignee = db.ReferenceField('User')
  individuals = db.ListField(db.EmbeddedDocumentField(Individual))
  databases = db.ListField(db.StringField())
  created_at = db.DateTimeField(default=datetime.now)
  updated_at = db.DateTimeField(default=datetime.now)
  last_updated = db.DateTimeField()
  suspects = db.ListField(db.ReferenceField('Variant'))
  synopsis = db.StringField(default='')
  status = db.StringField(default = 'inactive', choices=[
    'inactive', 'active', 'research', 'archived', 'solved'
  ])
  

  def __unicode__(self):
    return self.display_name

