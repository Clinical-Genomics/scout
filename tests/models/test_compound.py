# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from scout.models import Compound, Variant


def setup_compound(**kwargs):
  """
  Setup an Compound object object
  """
  compound = Compound(
    variant = kwargs.get('variant', None),
    display_name = kwargs.get('display_name', '1_132_A_C'),
    combined_score = kwargs.get('combined_score', '13'),
  )

  return compound
  
def test_compound():
  """
  Test the compound class
  """
  compound = setup_compound()
  
  assert compound.variant == None
  assert compound.display_name == '1_132_A_C'
  assert compound.combined_score == 13
  