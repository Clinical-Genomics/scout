# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from .setup_objects import setup_gt_call


def test_gt_call():
  """
  Test the GTCall class
  """
  gt_call = setup_gt_call()
  
  assert gt_call.sample_id == '1'
  assert gt_call.display_name == '1'
  assert gt_call.genotype_call == '0/1'
  assert gt_call.allele_depths == [10,12]
  assert gt_call.read_depth == 22
  assert gt_call.genotype_quality == 55
  