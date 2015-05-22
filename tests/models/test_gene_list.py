# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from scout.models import GeneList

def setup_gene_list(**kwargs):
  """
  Setup an Phenotype term object
  """
  list_id = kwargs.get('list_id', "gene_list")
  version = kwargs.get('version', 1.0)
  date = kwargs.get('date', "20150522")
  display_name = kwargs.get('display_name', "gene_list")
  
  gene_list = GeneList(
    list_id=list_id,
    version=version,
    date=date,
    display_name=display_name
  )
  return gene_list
  
def test_gene_list():
  """
  Test the Gene List class
  """
  gene_list = setup_gene_list()
  assert gene_list.list_id == "gene_list"
  assert gene_list.version == 1.0  
  assert gene_list.date == "20150522" 
  assert gene_list.display_name == "gene_list"