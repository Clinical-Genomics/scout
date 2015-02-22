# -*- coding: utf-8 -*-
"""

"main concept of MongoDB is embed whenever possible"
Ref: http://stackoverflow.com/questions/4655610#comment5129510_4656431
"""
from __future__ import absolute_import, unicode_literals
from datetime import datetime

from mongoengine import (Document, DateTimeField, EmailField, ListField,
                         ReferenceField)


class Whitelist(Document):
  email = EmailField(required=True, unique=True)
  created_at = DateTimeField(default=datetime.now)
  institutes = ListField(ReferenceField('Institute'))
