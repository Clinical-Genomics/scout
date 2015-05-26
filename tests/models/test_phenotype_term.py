# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from .setup_objects import setup_phenotype_term


def test_phenotype_term():
  """
  Test the PhenotypeTerm class
  """
  term = setup_phenotype_term()
  
  assert term.phenotype_id == "1234"
  assert term.feature == "NOC1"
  assert term.disease_models == ["AD"]
  assert term.omim_link == "http://www.omim.org/entry/1234"
