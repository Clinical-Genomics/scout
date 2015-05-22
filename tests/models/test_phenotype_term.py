# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from scout.models import PhenotypeTerm

def setup_phenotype(**kwargs):
  """
  Setup an Phenotype term object
  """
  phenotype_id = kwargs.get('hpo_id', "1234")
  feature = kwargs.get('feature', "NOC1")
  disease_models = kwargs.get('disease_models', ["AD"])

  term = PhenotypeTerm(
    phenotype_id=phenotype_id, 
    feature=feature,
    disease_models=disease_models
  )
  return term
  
def test_phenotype_term():
  """
  Test the PhenotypeTerm class
  """
  term = setup_phenotype()
  
  assert term.phenotype_id == "1234"
  assert term.feature == "NOC1"
  assert term.disease_models == ["AD"]
  assert term.omim_link == "http://www.omim.org/entry/1234"
