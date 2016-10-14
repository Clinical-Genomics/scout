# -*- coding: utf-8 -*-
from __future__ import absolute_import

from .setup_objects import setup_compound, setup_variant


def test_compound():
  """
  Test the compound class
  """
  compound = setup_compound()
  
  assert compound.variant == setup_variant()
  assert compound.display_name == '1_132_A_C'
  assert compound.combined_score == 13
  