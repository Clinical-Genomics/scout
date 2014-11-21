# -*- coding: utf-8 -*-
"""

"main concept of MongoDB is embed whenever possible"
Ref: http://stackoverflow.com/questions/4655610#comment5129510_4656431
"""
from __future__ import absolute_import, unicode_literals
from datetime import datetime

from ..extensions import db

class Institute(db.Document):
  internal_id = db.StringField(primary_key=True, required=True)
  display_name = db.StringField(required=True)
  sanger_recipients = db.ListField(db.EmailField())
  cases = db.ListField(db.ReferenceField('Case'))
  created_at = db.DateTimeField(default=datetime.now)

  def count_cases(self):
    return len(self.cases)

  def __unicode__(self):
    return self.display_name
