# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from scout.models import Event

class Event(Document):
  """Embedded model for defining a general user generated event."""
  # an event will allways belong to a institute and a case
  institute = ReferenceField('Institute', required=True)
  case_id = StringField(required=True)
  # All events will have url links
  link = StringField()
  # All events has to have a category
  category = StringField(choices=('case', 'variant'), required=True)
                             
  # All events will have an author
  author = ReferenceField('User', required=True)
  # Subject is the string that will be displayed after 'display_info'
  subject = StringField(required=True) # case 23 or 1_2343_A_C
  
  verb = StringField(choices=VERBS)
  level = StringField(choices=('global', 'specific'), default='specific')

  # An event can belong to a variant
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
    display_info = {
      "assign" : "was assigned to",
      "unassign" : "was unassigned from",
      "status" : "updated the status for",
      "comment" : "commented on",
      "synopsis" : "updated synopsis for",
      "pin" : "pinned variant",
      "unpin" : "removed pinned variant",
      "sanger" : "ordered sanger sequencing for",
      "archive" : "archived",
      "open_research" : "opened research mode for",
    }
    
    return display_info.get(self.verb, "")
  
  @property
  def is_edited(self):
    """
    Find out if the event has been edited.
    """
    return self.created_at == self.updated_at


def setup_event(**kwargs):
  """
  Setup an Event object object
  """
  event = Event(
    institute = kwargs.get('variant', None),
    case_id = StringField(required=True)
    # All events will have url links
    link = StringField()
    # All events has to have a category
    category = StringField(choices=('case', 'variant'), required=True)
                             
    # All events will have an author
    author = ReferenceField('User', required=True)
    # Subject is the string that will be displayed after 'display_info'
    subject = StringField(required=True) # case 23 or 1_2343_A_C
  
    verb = StringField(choices=VERBS)
    level = StringField(choices=('global', 'specific'), default='specific')

    # An event can belong to a variant
    variant_id = StringField()
    # This is the content of a comment
    content = StringField()
  
    # timestamps
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)
    
    variant = kwargs.get('variant', None),
    display_name = kwargs.get('display_name', '1_132_A_C'),
    combined_score = kwargs.get('combined_score', '13'),
  )

  return compound
  
def test_event():
  """
  Test the Event class
  """
  compound = setup_compound()
  
  assert compound.variant == None
  assert compound.display_name == '1_132_A_C'
  assert compound.combined_score == 13
  