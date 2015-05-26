# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from scout.models import GTCall


def setup_gt_call(**kwargs):
  """
  Setup an GTCall object object
  """
  gt_call = GTCall(
    sample_id = kwargs.get('sample_id', '1'),
    display_name = kwargs.get('display_name', '1'),
    genotype_call = kwargs.get('genotype_call', '0/1'),
    allele_depths = kwargs.get('allele_depths', [10,12]),
    read_depth = kwargs.get('read_depth', 22),
    genotype_quality = kwargs.get('genotype_quality', 55),
  )

  return gt_call
  
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
  