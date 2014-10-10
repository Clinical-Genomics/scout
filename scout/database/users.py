# -*- coding: utf-8 -*-
"""

"main concept of MongoDB is embed whenever possible"
Ref: http://stackoverflow.com/questions/4655610#comment5129510_4656431
"""
from __future__ import absolute_import, unicode_literals
from datetime import datetime

from ..extensions import db


# define mongoengine documents
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
    return query_role in [role.name for role in self.roles]

  # required for Flask-Admin interface
  def __unicode__(self):
    return self.name


class Role(db.Document):
  name = db.StringField(required=True)
  created_at = db.DateTimeField(default=datetime.now)

  def __unicode__(self):
    return self.name


class Institute(db.Document):
  name = db.StringField(required=True)

  sanger_email = db.ListField(db.EmailField())

  def __unicode__(self):
    return self.name
