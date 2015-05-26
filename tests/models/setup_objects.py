# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from scout.models import *

def setup_institute(**kwargs):
  """
  Setup a Institute object
  """
  institute = Institute(
    internal_id = kwargs.get('internal_id', 'internal_institute'),
    display_name = kwargs.get('display_name', 'institute0'),
    sanger_recipients = kwargs.get('sanger_recipients', ['john@doe.com']),
  )
  return institute


def setup_user(**kwargs):
  """
  Setup a User object
  """
  user = User(
    email = kwargs.get('email', 'john@doe.com'),
    name = kwargs.get('name', 'John Doe'),
    location = kwargs.get('location', 'se'),
    institutes = kwargs.get('institutes', [setup_institute()]),
    roles = kwargs.get('roles', ['admin']),
  )
  return user

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

def setup_phenotype_term(**kwargs):
  """
  Setup an Phenotype term object
  """
  
  term = PhenotypeTerm(
    phenotype_id=kwargs.get('hpo_id', "1234"), 
    feature=kwargs.get('feature', "NOC1"),
    disease_models=kwargs.get('disease_models', ["AD"])
  )
  return term


def setup_case(**kwargs):
  """
  Setup a Case object
  """
  case = Case(
    case_id = kwargs.get('case_id', "Institute0_1"),
    display_name = kwargs.get('display_name', "1"),
    owner = kwargs.get('owner', "Institute0"),
    collaborators = kwargs.get('collaborators', ['Institute1']),
    assignee = kwargs.get('assignee', setup_user()),
    individuals = kwargs.get('individuals', [setup_individual()]),
    suspects = kwargs.get('suspects', [setup_variant()]),
    causative = kwargs.get('causative', setup_variant()),
    synopsis=kwargs.get('synopsis', "This is a synopsis"),
    status=kwargs.get('status', "inactive"),
    is_research=kwargs.get('is_research', False),
    default_gene_lists = kwargs.get('default_gene_lists', ['List_1']),
    clinical_gene_lists = kwargs.get('clinical_gene_lists', [setup_gene_list()]),
    research_gene_lists = kwargs.get('research_gene_lists', [setup_gene_list()]),
    genome_build = kwargs.get('genome_build', "GRCh"),
    genome_version = kwargs.get('genome_version', 38),
    gender_check = kwargs.get('gender_check', 'confirm'),
    phenotype_terms = kwargs.get('phenotype_terms', [setup_phenotype_term()]),
    madeline_info = kwargs.get('madeline_info', "XML text"),
    vcf_file = kwargs.get('vcf_file', "path/to/variants.vcf")
    coverage_report = kwargs.get('coverage_report', b"coverage info")
  )
  
  return case


#
# def setup_case():
#   """Setup a Case object"""
#   case_id = "Institute0_1"
#   display_name = "1"
#   owner = "Institute0"
#   collaborators = ['Institute1']
#   # assignee = ReferenceField('User')
#   assignee = None
#   # individuals = ListField(EmbeddedDocumentField(Individual))
#   individuals = []
#
#   created_at = datetime.now
#   updated_at = datetime.now
#   # suspects = ListField(ReferenceField('Variant'))
#   suspects = []
#   # causative = ReferenceField('Variant')
#   causative = None
#   synopsis = "This is a synopsis"
#
#   status = 'inactive'
#   is_research = False
#
#   default_gene_lists = ['List_1']
#   # clinical_gene_lists = ListField(EmbeddedDocumentField(GeneList))
#   # research_gene_lists = ListField(EmbeddedDocumentField(GeneList))
#
#   genome_build = "GRCh"
#   genome_version = 38
#
#   # analysis_date =
#
#   # gender_check = StringField(choices=['unconfirmed', 'confirm', 'deviation'],
#   #                            default='unconfirmed')
#   # phenotype_terms = ListField(EmbeddedDocumentField(PhenotypeTerm))
#
#   # madeline_info = StringField()
#   # vcf_file = StringField()
#
#   # coverage_report_path = BinaryField()
#   case = Case(case_id=case_id, display_name=display_name, owner=owner,
#   collaborators=collaborators, assignee=assignee, individuals = individuals,
#   created_at=created_at, updated_at=updated_at, suspects=suspects,
#   causative = causative, synopsis=synopsis, status=status,
#   is_research=is_research
#   )
#   return case
#
#
# def setup_event(**kwargs):
#   """
#   Setup an Event object object
#   """
#   event = Event(
#     institute = kwargs.get('variant', None),
#     case_id = StringField(required=True)
#     # All events will have url links
#     link = StringField()
#     # All events has to have a category
#     category = StringField(choices=('case', 'variant'), required=True)
#
#     # All events will have an author
#     author = ReferenceField('User', required=True)
#     # Subject is the string that will be displayed after 'display_info'
#     subject = StringField(required=True) # case 23 or 1_2343_A_C
#
#     verb = StringField(choices=VERBS)
#     level = StringField(choices=('global', 'specific'), default='specific')
#
#     # An event can belong to a variant
#     variant_id = StringField()
#     # This is the content of a comment
#     content = StringField()
#
#     # timestamps
#     created_at = DateTimeField(default=datetime.now)
#     updated_at = DateTimeField(default=datetime.now)
#
#     variant = kwargs.get('variant', None),
#     display_name = kwargs.get('display_name', '1_132_A_C'),
#     combined_score = kwargs.get('combined_score', '13'),
#   )
#
#   return compound
