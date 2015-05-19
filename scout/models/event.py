# -*- coding: utf-8 -*-
"""
scout.models.event
~~~~~~~~~~~~~~~~~~

Define a document to specify activity events and comments both for variants and
cases.

The frontend will use the user + verb + link to display the activity.

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
  - Pinning
  - Archivals

"""
from __future__ import absolute_import, unicode_literals
from datetime import datetime

from mongoengine import (DateTimeField, EmbeddedDocument, ListField,
                         ReferenceField, StringField)

VERBS = (
  "assign",
  "unassign",
  "status",
  "comment",
  "synopsis",
  "pin",
  "unpin",
  "sanger",
  "archive",
)

class Event(EmbeddedDocument):
  """Embedded model for defining a general user generated event."""
  title = StringField()
  content = StringField()
  link = StringField()
  # an event will allways belong to a institute and a case
  institute = ReferenceField('Institute', required=True)
  case_id = StringField(required=True)
  # An event can belong to a variant
  variant_id = StringField()
  
  category = StringField(required=True,
                             choices=('case', 'variant'))
  
  level = StringField(choices=('global', 'specific'), default='specific')

  # metadata

  author = ReferenceField('User') # George
  verb = StringField(choices=VERBS)
  
  # What about these two? subject and action...
  subject = StringField() # case 23
  action = StringField()
  
  tags = ListField(StringField())
  institute = ReferenceField('Institute')

  # timestamps
  created_at = DateTimeField(default=datetime.now)
  updated_at = DateTimeField(default=datetime.now)
  
  def get_display_info(self):
    """
    Return the string that should be displayed based on the keyword
    """
    display_info = {
      "assign" : "was assigned to",
      "unassign" : "was unassigned from",
      "status" : "updated the status for",
      "comment" : "commented on",
      "synopsis" : "updated synopsis for",
      "pin" : "pinned variant",
      "unpin" : "removed pinned variant",
      "sanger" : "ordered sanger sequencing for",
      "archove" : "archived",
      "open_research" : "opened research mode for",
      "open_research" : "opened research mode for",
    }
    
    return display_info[self.verb]
  
  def is_edited(self):
    """
    Find out if the event has been edited.
    """
    return self.created_at == self.updated_at
