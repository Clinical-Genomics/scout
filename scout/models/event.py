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

from ..extensions import db


class Event(db.EmbeddedDocument):
  title = db.StringField()
  content = db.StringField()
  link = db.URLField()

  # metadata
  author = db.ReferenceField('User')
  verb = db.StringField()
  action = db.StringField()
  category = db.StringField()
  tags = db.ListField(db.StringField())

  # timestamps
  created_at = db.DateTimeField(default=datetime.now)
  updated_at = db.DateTimeField(default=datetime.now)

  def is_edited(self):
    """Find out if the event has been edited."""
    return self.created_at == self.updated_at
