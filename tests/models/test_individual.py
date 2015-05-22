# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from scout.models import Individual

def setup_individual(individual_id='A', display_name='A', sex='1', 
                    phenotype=1, father='C', mother='B', 
                    capture_kits=['Nimblegen'], bam_file='path/to/bam'):
  """
  Setup an Individual object with the given parameters
  """
  individual = Individual(
                  individual_id = individual_id,
                  display_name = display_name,
                  sex = sex,
                  phenotype = phenotype,
                  father = father,
                  mother = mother,
                  capture_kits = capture_kits,
                  bam_file = bam_file
                  )
  return individual
  
def test_individual():
  """docstring for test_individual"""
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
