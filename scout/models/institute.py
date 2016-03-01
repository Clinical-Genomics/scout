# -*- coding: utf-8 -*-
"""

"main concept of MongoDB is embed whenever possible"
Ref: http://stackoverflow.com/questions/4655610#comment5129510_4656431
"""
from __future__ import absolute_import
from datetime import datetime

from mongoengine import (DateTimeField, Document, EmailField, IntField,
                         ListField, ReferenceField, StringField)


class Institute(Document):

  """Represents an institute linked to multiple collaborating users."""

  meta = {'strict': False}

  internal_id = StringField(primary_key=True, required=True)
  display_name = StringField(required=True)
  sanger_recipients = ListField(EmailField())
  created_at = DateTimeField(default=datetime.now)
  updated_at = DateTimeField(default=datetime.now)

  coverage_cutoff = IntField(default=10)

  def __unicode__(self):
    return self.display_name

  def __repr__(self):
    return "Institute(internal_id={0}, display_name={1}, "\
           "sanger_recipients={2}, created_at={3})".format(
             self.internal_id, self.display_name, self.sanger_recipients,
             self.created_at
             )
