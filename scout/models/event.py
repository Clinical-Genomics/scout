# -*- coding: utf-8 -*-
"""
scout.models.event
~~~~~~~~~~~~~~~~~~

Define a document to specify activity events and comments both for variants and
cases.

Events are stored in its own collection

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

from __future__ import unicode_literals

from datetime import datetime

from mongoengine import (DateTimeField, Document, ReferenceField, StringField)

VERBS_MAP = {
  "assign": "was assigned to",
  "unassign": "was unassigned from",
  "status": "updated the status for",
  "comment": "commented on",
  "synopsis": "updated synopsis for",
  "pin": "pinned variant",
  "unpin": "removed pinned variant",
  "sanger": "ordered sanger sequencing for",
  "archive": "archived",
  "open_research": "opened research mode for",
  "mark_causative": "marked causative for",
  "unmark_causative": "unmarked causative for",
  "manual_rank": "updated manual rank for",
  "add_phenotype": "added HPO term for",
  "remove_phenotype": "removed HPO term for",
  "add_case": "added case",
  "update_case": "updated case",
  "check_case": "marked case as",
  "share": "shared case with",
  "unshare": "revoked access for",
  "rerun": "requested rerun of",
  "validate": "marked validation status for",
  "update_diagnosis": "updated diagnosis for",
}

VERBS = list(VERBS_MAP.keys())


class Event(Document):

  """Embedded model for defining a general user generated event."""

  meta = {'strict': False}

  # an event will allways belong to a institute and a case
  institute = ReferenceField('Institute', required=True)
  case = ReferenceField('Case', required=True)
  # All events will have url links
  link = StringField()
  # All events has to have a category
  category = StringField(choices=('case', 'variant'), required=True)

  # All events will have an author
  author = ReferenceField('User', required=True)
  # Subject is the string that will be displayed after 'display_info'
  subject = StringField(required=True) # case 23 or 1_2343_A_C

  verb = StringField(choices=VERBS)
  level = StringField(choices=('global', 'specific', 'internal'), default='specific')

  # An event can belong to a variant. This is the id that looks like 1_34253_A_C.
  variant_id = StringField()
  # This is the content of a comment
  content = StringField()

  # timestamps
  created_at = DateTimeField(default=datetime.now)
  updated_at = DateTimeField(default=datetime.now)

  @property
  def display_info(self):
    """
    Return the string that should be displayed based on the keyword
    """
    return VERBS_MAP.get(self.verb, "")

  @property
  def is_edited(self):
    """
    Find out if the event has been edited.
    """
    return self.created_at == self.updated_at
