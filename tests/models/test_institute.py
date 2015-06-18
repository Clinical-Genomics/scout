# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from .setup_objects import setup_institute


def test_institute():
  """
  Test the Institute class
  """
  institute = setup_institute()
  
  assert institute.internal_id == 'internal_institute'
  assert institute.display_name == 'institute0'
  assert institute.sanger_recipients == ['john@doe.com']
  

