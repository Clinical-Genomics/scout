# -*- coding: utf-8 -*-
"""

"main concept of MongoDB is embed whenever possible"
Ref: http://stackoverflow.com/questions/4655610#comment5129510_4656431
"""
from __future__ import absolute_import, unicode_literals
from datetime import datetime

from ..extensions import db

class User(db.Document):
  email = db.EmailField(required=True, unique=True)
  name = db.StringField(max_length=40, required=True)
  created_at = db.DateTimeField(default=datetime.now)
  accessed_at = db.DateTimeField()
  location = db.StringField()
  institutes = db.ListField(db.ReferenceField('Institute'))
  roles = db.ListField(db.StringField())

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
    return query_role in self.roles

  # required for Flask-Admin interface
  def __unicode__(self):
    return self.name

