# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from .setup_objects import setup_user, setup_institute

def test_user():
  """
  Test the User class
  """
  user = setup_user()
  
  assert user.email == 'john@doe.com'
  assert user.name == 'John Doe'
  assert user.location == 'se'
  assert user.roles == ['admin']
  assert user.institutes == [setup_institute()]
  assert user.first_name == 'John'
  assert user.display_name == 'John Doe'
  
  assert user.is_authenticated() == True
  assert user.is_active() == True
  assert user.is_anonymous() == False
  assert user.get_id() == str(user.id)
  assert user.has_role('admin') == True
  assert user.has_role('user') == False
  

