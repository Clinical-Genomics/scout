# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from .setup_objects import setup_variant
from scout.ext.backend.utils import generate_md5_key


def test_variant():
  """
  Test the variant class
  """
  variant = setup_variant()
  
  assert variant.document_id == 'institute_genelist_caseid_variantid'
  assert variant.variant_id == generate_md5_key('1_132_A_C'.split('_'))
  assert variant.manual_rank == 5
  assert variant.manual_rank_level == 'high'
  
  
  
  
  
