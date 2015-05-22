# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from datetime import datetime

from scout.models import (Case, Individual, User)


def setup_case():
  """Setup a Case object"""
  case_id = "Institute0_1"
  display_name = "1"
  owner = "Institute0"
  collaborators = ['Institute1']
  # assignee = ReferenceField('User')
  assignee = None
  # individuals = ListField(EmbeddedDocumentField(Individual))
  individuals = []
  
  created_at = datetime.now
  updated_at = datetime.now
  # suspects = ListField(ReferenceField('Variant'))
  suspects = []
  # causative = ReferenceField('Variant')
  causative = None
  synopsis = "This is a synopsis"

  status = 'inactive'
  is_research = False

  default_gene_lists = ['List_1']
  # clinical_gene_lists = ListField(EmbeddedDocumentField(GeneList))
  # research_gene_lists = ListField(EmbeddedDocumentField(GeneList))

  genome_build = "GRCh"
  genome_version = 38

  # analysis_date = 

  # gender_check = StringField(choices=['unconfirmed', 'confirm', 'deviation'],
  #                            default='unconfirmed')
  # phenotype_terms = ListField(EmbeddedDocumentField(PhenotypeTerm))
  
  # madeline_info = StringField()
  # vcf_file = StringField()

  # coverage_report_path = BinaryField()
  case = Case(case_id=case_id, display_name=display_name, owner=owner, 
  collaborators=collaborators, assignee=assignee, individuals = individuals,
  created_at=created_at, updated_at=updated_at, suspects=suspects,
  causative = causative, synopsis=synopsis, status=status, 
  is_research=is_research
  )
  return case

def test_case():
  """Test the case class"""
  case = setup_case()
  assert case.case_id == "Institute0_1"