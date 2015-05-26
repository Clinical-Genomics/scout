# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from .setup_objects import setup_gene_list


def test_gene_list():
  """
  Test the Gene List class
  """
  gene_list = setup_gene_list()
  
  assert gene_list.list_id == "gene_list"
  assert gene_list.version == 1.0  
  assert gene_list.date == "20150522" 
  assert gene_list.display_name == "gene_list"