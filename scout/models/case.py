# -*- coding: utf-8 -*-
"""

"main concept of MongoDB is embed whenever possible"
Ref: http://stackoverflow.com/questions/4655610#comment5129510_4656431
"""
from __future__ import absolute_import, unicode_literals
from datetime import datetime
import itertools

from query_phenomizer import query
from mongoengine import (DateTimeField, Document, EmbeddedDocument,
                         EmbeddedDocumentField, IntField, ListField,
                         ReferenceField, FloatField, StringField,
                         BooleanField)

from .event import Event


class Individual(EmbeddedDocument):
  """Represents an individual (sample) in a case (family)."""
  display_name = StringField()
  sex = StringField()
  phenotype = IntField()
  father = StringField()
  mother = StringField()
  individual_id = StringField()
  capture_kits = ListField(StringField())
  bam_file = StringField()

  @property
  def sex_human(self):
    """Transform sex string into human readable form."""
    # pythonic switch statement
    return {'1': 'male', '2': 'female'}.get(self.sex, 'unknown')

  @property
  def phenotype_human(self):
    """Transform phenotype integer into human readable form."""
    # pythonic switch statement
    terms = {-9: 'missing', 0: 'missing', 1: 'unaffected', 2: 'affected'}
    return terms.get(self.phenotype, 'undefined')

  def __unicode__(self):
    return self.display_name
  
  def __repr__(self):
    return "Individual(individual_id={0}, display_name={1})".format(
      self.individual_id, self.display_name
    )


class PhenotypeTerm(EmbeddedDocument):
  hpo_id = StringField()
  feature = StringField()
  
  def __repr__(self):
    return "PhenotypeTerm(hpo_id={0}, feature={1})".format(
      self.hpo_id, self.feature
    )


class GeneList(EmbeddedDocument):
  list_id = StringField(required=True)
  version = FloatField(required=True)
  date = StringField(required=True)
  display_name = StringField()
  
  def __repr__(self):
    return "GeneList(list_id={0}, version={1}, date={2}, display_name={3})".format(
      self.list_id, self.version, self.date, self.display_name
    )


class Case(Document):
  """Represents a case (family) of individuals (samples)."""
  # This is the md5 string id for the family:
  case_id = StringField(primary_key=True, required=True)
  # This is the string that will be shown in scout:
  display_name = StringField(required=True)
  # This is the owner of the case
  owner = StringField(required=True)
  # These are the names of all the collaborators that are allowed to view the
  # case, including the owner
  collaborators = ListField(StringField)
  assignee = ReferenceField('User')
  individuals = ListField(EmbeddedDocumentField(Individual))
  created_at = DateTimeField(default=datetime.now)
  updated_at = DateTimeField(default=datetime.now)
  last_updated = DateTimeField()
  suspects = ListField(ReferenceField('Variant'))
  causative = ReferenceField('Variant')
  synopsis = StringField(default='')
  status = StringField(default='inactive',
                       choices=['inactive', 'active', 'archived', 'solved'])
  is_research = BooleanField()
  events = ListField(EmbeddedDocumentField(Event))
  comments = ListField(EmbeddedDocumentField(Event))

  # This decides which gene lists that should be shown when the case is opened
  default_gene_lists = ListField(StringField())
  clinical_gene_lists = ListField(EmbeddedDocumentField(GeneList))
  research_gene_lists = ListField(EmbeddedDocumentField(GeneList))

  genome_build = StringField()
  genome_version = FloatField()

  analysis_date = StringField()

  gender_check = StringField(choices=['unconfirmed', 'confirm', 'deviation'],
                             default='unconfirmed')
  phenotype_terms = ListField(EmbeddedDocumentField(PhenotypeTerm))
  # madeline info is a full xml file
  madeline_info = StringField()
  vcf_file = StringField()

  coverage_report_path = StringField()

  @property
  def hpo_genes(self):
    """
    Return the list of HGNC symbols that match annotated HPO terms.

    Returns:
      query_result : A list of dictionaries on the form:
        {
            'p_value': float,
            'gene_id': str,
            'omim_id': int,
            'orphanet_id': int,
            'decipher_id': int,
            'any_id': int,
            'mode_of_inheritance':str,
            'description': str,
            'raw_line': str
        }
    """
    hpo_terms = [hpo_term.hpo_id for hpo_term in self.phenotype_terms]

    # skip querying Phenomizer unless at least one HPO terms exists
    if hpo_terms:
      try:
        return query(hpo_terms)
      except SystemExit:
        return {}
    else:
      return {}

  @property
  def hpo_gene_ids(self):
    """Parse out all HGNC symbols form the dynamic Phenomizer query."""
    return [term['gene_id'] for term in self.hpo_genes if term['gene_id']]

  @property
  def bam_files(self):
    """Aggregate all BAM files across all individuals."""
    return [individual.bam_file for individual in self.individuals
            if individual.bam_file]

  @property
  def all_gene_lists(self):
    """Yield all gene lists (both clinical and research)."""
    return itertools.chain(self.clinical_gene_lists, self.research_gene_lists)

  def __repr__(self):
    return "Case(case_id={0}, display_name={1}, owner={2})".format(
      self.case_id, self.display_name, self.owner
    )
  # def __unicode__(self):
  #   return self.display_name
