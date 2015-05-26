# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from .setup_objects import (setup_event, setup_institute, setup_user, setup_case)


def test_event():
  """
  Test the Event class
  """
  subject = "X_2343_G_C"
  verb = "comment"
  event = setup_event(
    subject = subject,
    verb = verb,
    variant_id = subject
  )
  
  assert event.institute == setup_institute()
  assert event.case == setup_case()
  assert event.link == "an/url"
  assert event.category == "variant"
  assert event.author.name == setup_user().name
  assert event.subject == subject
  assert event.verb == verb
  assert event.level == "specific"
  assert event.variant_id == subject
  assert event.content == "This is a comment"
  
  assert event.is_edited == False
  assert event.display_info == "commented on"
  
  
  