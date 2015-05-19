# -*- coding: utf-8 -*-
"""

"main concept of MongoDB is embed whenever possible"
Ref: http://stackoverflow.com/questions/4655610#comment5129510_4656431
"""
from __future__ import absolute_import, unicode_literals
from datetime import datetime
import itertools

from query_phenomizer import query
from mongoengine import (DateTimeField, Document, EmbeddedDocument,
                         EmbeddedDocumentField, IntField, ListField,
                         ReferenceField, FloatField, StringField,
                         BooleanField)

from .event import Event






  
  # def __unicode__(self):
  #   return self.display_name
