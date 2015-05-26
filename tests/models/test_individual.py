# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from .setup_objects import setup_individual
  
def test_individual():
  """
  Test the Individual class
  """
  
  individual = setup_individual()
  
  assert individual.individual_id == 'A'
  assert individual.display_name == 'A'
  assert individual.sex == '1'
  assert individual.phenotype == 1
  assert individual.father == 'C'
  assert individual.mother == 'B'
  assert individual.capture_kits == ['Nimblegen']
  assert individual.bam_file == 'path/to/bam'
  assert individual.bam_file == 'path/to/bam'
  assert individual.sex_human == 'male'  
  assert individual.phenotype_human == 'unaffected'
