# -*- coding: utf-8 -*-
"""
scout.models.event
~~~~~~~~~~~~~~~~~~

Define a combined embedded document to specify activity events and
comments. The idea of this model is to be embedded under the model
to which it belongs.

The Event model is designed to cover a range of user generated events.

Case:
  - Comments
    - tags, content, (title,) user, timestamp
  - Changed status
    - user, timestamp, delta
    - Auto "active" when first user checks out variants
  - Updated synopsis
    - timestamp, user, content
  - Pinning and unpinning a variant
  - Assignments and un-assignments
  - Sanger sequencing orders
  - Analysis updates ("analysis was rerun 13 days ago")
  - Archivals?

Variant:
  - Comments
  - Sanger sequencing orders
  - Pinning?
  - Archivals?
"""
from __future__ import absolute_import, unicode_literals
from datetime import datetime

from mongoengine import (DateTimeField, EmbeddedDocument, ListField,
                         ReferenceField, StringField)


class Event(EmbeddedDocument):
  """Embedded model for defining a general user generated event."""
  title = StringField()
  content = StringField()
  link = StringField()

  # metadata
  author = ReferenceField('User')      # George
  verb = StringField()                 # commented on
  subject = StringField()              # case 23
  action = StringField()
  tags = ListField(StringField())

  # timestamps
  created_at = DateTimeField(default=datetime.now)
  updated_at = DateTimeField(default=datetime.now)

  def is_edited(self):
    """Find out if the event has been edited."""
    return self.created_at == self.updated_at
