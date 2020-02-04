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

event = dict(
    # an event will always belong to a institute and a case
    institute=str,  # Institute _id, required
    case=str,  # case_id, required
    link=str,  # url link, required
    # All events has to have a category
    category=str,  # choices = ('case', 'variant', 'panel'), required
    # All events will have an author
    user_id=str,  # user email, required
    user_name=str,  # user name
    # Subject is the string that will be displayed after 'display_info'
    subject=str,  # case 23 or 1_2343_A_C, required
    verb=str,  # choices=VERBS
    level=str,  # choices=('global', 'specific', 'internal'), default='specific'
    # An event can belong to a variant. This is the id that looks like 1_34253_A_C.
    variant_id=str,  # A variant id
    panel_name=str,  # A gene panel
    # This is the content of a comment
    content=str,
    # timestamps
    created_at=datetime,  # default=datetime.now
    updated_at=datetime,  # default=datetime.now
)
