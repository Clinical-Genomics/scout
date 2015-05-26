#!/usr/bin/env python
# encoding: utf-8
"""
mongo.py

This is the mongo adapter for scout, it is a communicator for quering and
updating the mongodatabase.
Implements BaseAdapter.

Created by Måns Magnusson on 2014-11-17.
Copyright (c) 2014 __MoonsoInc__. All rights reserved.

"""
from __future__ import (absolute_import, unicode_literals, print_function)

import sys
import os

import io
import json
import click
import logging
from mongoengine import connect, DoesNotExist, Q

from . import BaseAdapter
from .config_parser import ConfigParser
from scout.models import (Variant, Compound, Case, Event)

from pprint import pprint as pp

class MongoAdapter(BaseAdapter):
  """Adapter for cummunication between the scout server and a mongo database."""

  def init_app(self, app):
    config = getattr(app, 'config', {})

    # self.client = MongoClient(config.get('MONGODB_HOST', 'localhost'), config.get('MONGODB_PORT', 27017))
    # self.db = self.client[config.get('MONGODB_DB', 'variantDatabase')]
    host = config.get('MONGODB_HOST', 'localhost')
    port = config.get('MONGODB_PORT', 27017)
    database = config.get('MONGODB_DB', 'variantDatabase')
    username = config.get('MONGODB_USERNAME', None)
    password = config.get('MONGODB_PASSWORD', None)

    connect(database, host=host, port=port, username=username,
            password=password)

    # self.case_collection = self.db.case
    # self.variant_collection = self.db.variant

  def __init__(self, app=None):

    if app:
      self.init_app(app)
    
    self.logger = logging.getLogger(__name__)
    # combine path to the local development fixtures
    # self.config_object = ConfigParser(config_file)


  def cases(self, collaborator = None):
    if collaborator:
      return Case.objects(collaborators=collaborator).order_by('-updated_at')
    else:
      return Case.objects().order_by('-updated_at')

  def case(self, case_id):

    try:
      return Case.objects(case_id=case_id)
    except DoesNotExist:
      return None


  def build_query(self, case_id, query=None, variant_ids=None):
    """
    Build a mongo query based on what is found in the query.
    query looks like:
      {
         'genetic_models': list,
         'thousand_genomes_frequency': float,
         'exac_frequency': float,
         'functional_annotations': list,
         'hgnc_symbols': list,
         'region_annotations': list
       }

    Arguments:
      case_id     : A string that represents the case
      query       : A dictionary with querys for the database
      variant_ids : A list of md5 strings that represents variant ids

    Returns:
      mongo_query : A dictionary in the mongo query format

    """
    mongo_query = {}
    # We will allways use the case id when we query the database
    mongo_query['case_id'] = case_id
    mongo_query['variant_type'] = query.get('variant_type', 'clinical')
    if query:
      # We need to check if there is any query specified in the input query
      any_query = False
      mongo_query['$and'] = []

      if query['thousand_genomes_frequency']:
        try:
          mongo_query['$and'].append({'thousand_genomes_frequency':{
                                '$lt': float(query['thousand_genomes_frequency'])
                                                              }
                                                            }
                                                          )
          any_query = True
        except TypeError:
          pass

      if query['exac_frequency']:
        try:
          mongo_query['$and'].append({'exac_frequency':{
                                '$lt': float(query['exac_frequency'])
                                                            }
                                                          }
                                                        )
          any_query = True
        except TypeError:
          pass

      if query['genetic_models']:
        mongo_query['$and'].append({'genetic_models':
                                        {'$in': query['genetic_models']}
                                      }
                                    )
        any_query = True

      if query['hgnc_symbols']:
        mongo_query['$and'].append({'hgnc_symbols':
                                      {'$in': query['hgnc_symbols']}
                                    }
                                  )
        any_query = True

      if query['gene_lists']:
        mongo_query['$and'].append({'gene_lists':
                                      {'$in': query['gene_lists']}
                                    }
                                  )
        any_query = True


      if query['functional_annotations']:
          mongo_query['$and'].append({'genes.functional_annotation':
                                        {'$in': query['functional_annotations']}
                                        }
                                      )
          any_query = True

      if query['region_annotations']:
          mongo_query['$and'].append({'genes.region_annotation':
                                        {'$in': query['region_annotations']}
                                        }
                                      )
          any_query = True

      if variant_ids:
        mongo_query['$and'].append({'variant_id':
                                      {'$in': variant_ids}
                                    }
                                  )
        any_query = True


      if not any_query:
        del mongo_query['$and']

      return mongo_query

  def variants(self, case_id, query=None, variant_ids=None, nr_of_variants = 10, skip = 0):
    """
    Returns the number of variants specified in question for a specific case.
    If skip ≠ 0 skip the first n variants.

    Arguments:
      case_id : A string that represents the case
      query   : A dictionary with querys for the database

    Returns:
      A generator with the variants

    """
    if variant_ids:
      nr_of_variants = len(variant_ids)
    else:
      nr_of_variants = skip + nr_of_variants

    mongo_query = self.build_query(case_id, query, variant_ids)

    for variant in (Variant.objects(__raw__=mongo_query)
                           .order_by('variant_rank')
                           .skip(skip)
                           .limit(nr_of_variants)):
      yield variant

  def variant(self, document_id):
    """
    Returns the specified variant.

    Arguments:
      document_id : A md5 key that represents the variant

    Returns:
      variant_object: A odm variant object
    """

    try:
      return Variant.objects.get(document_id=document_id)
    except DoesNotExist:
      return None

  def next_variant(self, document_id):
    """
    Returns the next variant from the rank order.

    Arguments:
      document_id : A md5 key that represents the variant

    Returns:
      variant_object: A odm variant object
    """

    previous_variant = Variant.objects.get(document_id=document_id)
    rank = previous_variant.variant_rank or 0
    case_id = previous_variant.case_id
    variant_type = previous_variant.variant_type
    try:
      return Variant.objects.get(__raw__=({'$and':[
                                        {'case_id': case_id},
                                        {'variant_type': variant_type},
                                        {'variant_rank': rank+1}
                                        ]
                                      }
                                    )
                                  )
    except DoesNotExist:
      return None

  def previous_variant(self, document_id):
    """
    Returns the next variant from the rank order

    Arguments:
      document_id : A md5 key that represents the variant

    Returns:
      variant_object: A odm variant object

    """
    previous_variant = Variant.objects.get(document_id=document_id)
    rank = previous_variant.variant_rank or 0
    case_id = previous_variant.case_id
    variant_type = previous_variant.variant_type
    try:
      return Variant.objects.get(__raw__=({'$and':[
                                        {'case_id': case_id},
                                        {'variant_type': variant_type},
                                        {'variant_rank': rank - 1}
                                        ]
                                      }
                                    )
                                  )
    except DoesNotExist:
      return None

  def create_event(self, institute, case, user, link, category, verb, 
                  subject, level='specific', variant_id="", content=""):
    """
    Create an Event with the parameters given.
    
    Arguments:
      institute (Institute): A Institute object
      case (Case): A Case object
      user (User): A User object
      link (str): The url to be used in the event
      category (str): Case or Variant
      verb (str): What type of event
      subject (str): What is operated on
      level (str): 'specific' or 'global'. Default is 'specific'
      variant (Variant): A variant object
      content (str): The content of the comment
    
    """
    event = Event(
      institute=institute,
      case=case,
      author=user.to_dbref(),
      link=link,
      category=category,
      verb=verb,
      subject=subject,
      level=level,
      variant_id=variant_id,
      content=content
      )

    self.logger.debug("Saving Event")
    event.save()
    self.logger.debug("Event Saved")
    
    return

  def assign(self, institute, case, user, link):
    """
    Assign a user to a case.
    
    This function will create an Event to log that a person has been assigned
    to a case. Also the "assignee" on the case will be updated.
    
    Arguments:
      institute (Institute): A Institute object
      case (Case): Case object
      user (User): A User object
      link (str): The url to be used in the event
    """
    self.logger.info("Creating event for assigning {0} to {1}".format(
      user.name, case.display_name
    ))
    
    self.create_event(
      institute=institute,
      case=case,
      user=user,
      link=link,
      category='case',
      verb='assign',
      subject=case.display_name
    )
    self.logger.info("Updating {0} to be assigned with {1}".format(
      case.display_name, user.name
    ))
    case.assignee = user
    case.save()
    self.logger.debug("Case updated")
    
    return

  def unassign(self, institute, case, user, link):
    """
    Unassign a user from a case.
    
    This function will create an Event to log that a person has been unassigned
    from a case. Also the "assignee" on the case will be updated.
    
    Arguments:
      institute (Institute): A Institute object
      case (Case): A Case object
      user (User): A User object (Should this be a user id?)
      link (str): The url to be used in the event
    """
    self.logger.info("Creating event for unassigning {0} from {1}".format(
      user.display_name, case.display_name
    ))
    self.create_event(
      institute=institute,
      case=case,
      user=user,
      link=link,
      category='case',
      verb='unassign',
      subject=case.display_name
    )
    
    self.logger.info("Updating {0} to be unassigned with {1}".format(
      case.display_name, user.display_name
    ))
    case.assignee = None
    case.save()
    self.logger.debug("Case updated")
    
    return

  def update_status(self, institute, case, user, status, link):
    """
    Update the status of a case.
    
    This function will create an Event to log that a user have updated the
    status of a case. Also the status of the case will be updated.
    
    Arguments:
      institute (Institute): A Institute object
      case (Case): A Case object
      user (User): A User object
      status (str): The new status of the case
      link (str): The url to be used in the event
    
    """
    
    self.logger.info("Creating event for assigning {0} to {1}".format(
      user.display_name, case.display_name
    ))
    self.create_event(
      institute=institute,
      case=case,
      user=user,
      link=link,
      category='case',
      verb='status',
      subject=case.display_name
    )
    
    self.logger.info("Updating {0} to status {1}".format(
      case.display_name, status
    ))
    case.status = status
    case.save()
    self.logger.debug("Case updated")
    
    return
  
  def update_synopsis(self, institute, case, user, link, content=""):
    """
    Create an Event for updating the synopsis for a case.
    
    This function will create an Event and update the synopsis for a case.
    
    Arguments:
      institute (Institute): A Institute object
      case (Case): A Case object
      user (User): A User object
      link (str): The url to be used in the event
      content (str): The content for what should be added to the synopsis
      
    """
    self.logger.info("Creating event for updating the synopsis for case {0}".format(
      case.display_name
    ))
    
    self.create_event(
      institute=institute,
      case=case,
      user=user,
      link=link,
      category='case',
      verb='synopsis',
      subject=case.display_name,
      content=content
    )
    
    self.logger.info("Updating the synopsis for case {0}".format(
      case.display_name
    ))
    case.synopsis = content
    
    return

  def archive_case(self, institute, case, user, link):
    """
    Create an event for archiving a case.
    
    Arguments:
      institute (Institute): A Institute object
      case (Case): Case object
      user (User): A User object
      link (str): The url to be used in the event
      
    """
    self.logger.info("Creating event for archiving case {0}".format(
      case.display_name
    ))
    self.create_event(
      institute=institute,
      case=case,
      user=user,
      link=link,
      category='case',
      verb='archive',
      subject=case.display_name,
    )

    return

  def open_research(self, institute, case, user, link):
    """
    Create an event for opening the research list a case.
    
    Arguments:
      institute (Institute): A Institute object
      case (Case): Case object
      user (User): A User object
      link (str): The url to be used in the event
      
    """
    self.logger.info("Creating event for opening research for case"\
                    " {0}".format(case.display_name))
    self.create_event(
      institute=institute,
      case=case,
      user=user,
      link=link,
      category='case',
      verb='open_research',
      subject=case.display_name,
    )
    self.logger.info("Setting is_research to 'True' in case {0}".format(
      case.display_name
    ))
    case.is_research = True
    case.save()
    return


  def comment(self, institute, case, user, link, variant=None,
              content="", comment_level="specific"):
    """
    Add a comment to a variant or a case.
    
    This function will create an Event to log that a user have commented on
    a variant. If a variant id is given it will be a variant comment.
    A variant comment can be 'global' or specific. The global comments will be
    shown for this variation in all cases while the specific comments will only
    be shown for a specific case.
    
    Arguments:
      institute (Institute): A Institute object
      case (Case): A Case object
      user (User): A User object
      link (str): The url to be used in the event
      variant (Variant): A variant object
      content (str): The content of the comment
      comment_level (str): Any one of 'specific' or 'global'.
                           Default is 'specific'
    
    """
    if variant:
      self.logger.info("Creating event for a {0} comment on variant {1}".format(
        comment_level, variant.display_name
      )) 
      self.create_event(
        institute=institute,
        case=case,
        user=user,
        link=link,
        category='variant',
        verb='comment',
        level=comment_level,
        variant_id=variant.variant_id,
        subject=variant.display_name,
        content=content
      )

    else:
      self.logger.info("Creating event for a comment on case {0}".format(
        case.display_name
      )) 

      self.create_event(
        institute=institute,
        case=case,
        user=user,
        link=link,
        category='case',
        verb='comment',
        subject=case.display_name,
        content=content
      )
    
    return

  def pin_variant(self, institute, case, user, link, variant):
    """
    Create an event for pinning a variant.
    
    Arguments:
      institute (Institute): A Institute object
      case (Case): Case object
      user (User): A User object
      link (str): The url to be used in the event
      variant (Variant): A variant object
      
    """
    self.logger.info("Creating event for pinning variant {0}".format(
      variant.display_name
    ))
    self.create_event(
      institute=institute,
      case=case,
      user=user,
      link=link,
      category='variant',
      verb='pin',
      variant_id=variant.variant_id,
      subject=variant.display_name,
    )

    return

  def unpin_variant(self, institute, case, user, link, variant):
    """
    Create an event for unpinning a variant.
    
    Arguments:
      institute (Institute): A Institute object
      case (Case): Case object
      user (User): A User object
      link (str): The url to be used in the event
      variant (Variant): A variant object
      
    """
    self.logger.info("Creating event for unpinning variant {0}".format(
      variant.display_name
    ))
    self.create_event(
      institute=institute,
      case=case,
      user=user,
      link=link,
      category='variant',
      verb='unpin',
      variant_id=variant.variant_id,
      subject=variant.display_name,
    )

    return

  def order_sanger(self, institute, case, user, link, variant):
    """
    Create an event for order sanger for a variant.
    
    Arguments:
      institute (Institute): A Institute object
      case (Case): Case object
      user (User): A User object
      link (str): The url to be used in the event
      variant (Variant): A variant object
      
    """
    self.logger.info("Creating event for unpinning variant {0}".format(
      variant.display_name
    ))
    self.create_event(
      institute=institute,
      case=case,
      user=user,
      link=link,
      category='variant',
      verb='sanger',
      variant_id=variant.variant_id,
      subject=variant.display_name,
    )

    return

@click.command()
@click.option('-i','--institute',
                default='CMMS'
)
@click.option('-c' ,'--case',
                default='1'
)
@click.option('--thousand_g',
                default=100.0
)
@click.option('--exac',
                default=100.0
)
@click.option('--hgnc_id',
                multiple=True
)
def cli(institute, case, thousand_g, exac, hgnc_id):
    """Test the vcf class."""
    import hashlib

    def generate_md5_key(list_of_arguments):
      """Generate an md5-key from a list of arguments"""
      h = hashlib.md5()
      h.update(' '.join(list_of_arguments))
      return h.hexdigest()


    print('Institute: %s, Case: %s' % (institute, case))
    my_mongo = MongoAdapter(app='hej')

    hgnc_question = []
    for hgnc_symbol in hgnc_id:
      hgnc_question.append(hgnc_symbol)

    query = {
            'genetic_models':None,
            'thousand_genomes_frequency':None,
            'exac_frequency':None,
            'hgnc_symbols': ['ACTN4'],
            'functional_annotations' : None,
            'region_annotations' : None
          }
# ['missense_variant']
# ['exonic']
    ### FOR DEVELOPMENT ###

    case_id = '_'.join([institute, case])
    print(case_id)
    my_case = my_mongo.case(case_id)

    print('Case found:')
    pp(json.loads(my_case.to_json()))
    print('')
    pp(query)

    print('Query:')
    pp(query)
    print('')
    variant_count = 0

    numbers_matched = 0
    for variant in my_mongo.variants(case_id, query):
      pp(json.loads(variant.to_json()))
      print('')
      numbers_matched += 1
    print('Number of variants: %s' % (numbers_matched))

if __name__ == '__main__':
    cli()
