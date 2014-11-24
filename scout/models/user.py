# -*- coding: utf-8 -*-
"""

"main concept of MongoDB is embed whenever possible"
Ref: http://stackoverflow.com/questions/4655610#comment5129510_4656431
"""
from __future__ import absolute_import, unicode_literals
from datetime import datetime

from mongoengine import *

class User(Document):
  email = EmailField(required=True, unique=True)
  name = StringField(max_length=40, required=True)
  created_at = DateTimeField(default=datetime.now)
  accessed_at = DateTimeField()
  location = StringField()
  institutes = ListField(ReferenceField('Institute'))
  roles = ListField(StringField())

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

  def belongs_to(self, institute_id):
    return institute_id in self.institutes

  # required for Flask-Admin interface
  def __unicode__(self):
    return self.name

