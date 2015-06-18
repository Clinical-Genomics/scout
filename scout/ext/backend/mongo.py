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
import json
import click
import logging
from mongoengine import connect, DoesNotExist, Q

from . import BaseAdapter
from .config_parser import ConfigParser
from scout.models import (Variant, Case, Event, Institute, PhenotypeTerm)

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

    self.logger = logging.getLogger(__name__)

    if app:
      self.logger.info("Initializing app")
      self.init_app(app)

    self.logger = logging.getLogger(__name__)
    # combine path to the local development fixtures
    # self.config_object = ConfigParser(config_file)

  def institute(self, institute_id):
    """Fetch an Institute from the  database."""
    return Institute.objects.get(internal_id=institute_id)

  def cases(self, collaborator=None):
    self.logger.info("Fetch all cases")
    if collaborator:
      self.logger.info("Use collaborator {0}".format(collaborator))
      return Case.objects(collaborators=collaborator).order_by('-updated_at')
    else:
      return Case.objects().order_by('-updated_at')

  def case(self, institute_id, case_id):
    self.logger.info("Fetch case {0}".format(case_id))
    try:
      return Case.objects.get(owner=institute_id, display_name=case_id)
    except DoesNotExist:
      self.logger.warning("Could not find case {0}".format(case_id))
      return None

  def events(self, institute, case=None, variant_id=None, level=None,
             comments=False):
    """Fetch events from the database.

    Args:
      case (Case, optional): case object
      variant_id (str, optional): global variant id
      level (str, optional): restrict comments to 'specific' or 'global'
      comments (bool, optional): restrict events to include only comments

    Returns:
      list: filtered query returning matching events
    """
    # add basic filters
    filters = [Q(institute=institute)]

    if variant_id:
      # restrict to only variant events
      filters.append(Q(category='variant'))
      filters.append(Q(variant_id=variant_id))

      if level:
        # filter on specific/global (implicit: only comments)
        filters.append(Q(level=level))

        if level != 'global':
          # restrict to case
          filters.append(Q(case=case))
      else:
        # return both global and specific comments for the variant
        filters.append(Q(case=case) | Q(level='global'))

    else:
      # restrict to case events
      filters.append(Q(category='case'))

      if case:
        # restrict to case only
        filters.append(Q(case=case))

    if comments:
      # restrict events to only comments
      filters.append(Q(verb='comment'))

    query = reduce(lambda old_filter, next_filter: old_filter & next_filter, filters)
    return Event.objects.filter(query)

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
    self.logger.info("Fetching next variant for {0}".format(
      previous_variant.display_name
      ))
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
    self.logger.info("Fetching previous variant for {0}".format(
      previous_variant.display_name
      ))
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

  def update_dynamic_gene_list(self, case, gene_list):
    """
    Update the dynamic gene list for a case

    Arguments:
      case (Case): The case that should be updated
      gene_list (list): The list of genes that should be added

    """
    self.logger.info("Updating the dynamic gene list for case %s", case.display_name)
    case.dynamic_gene_list = gene_list
    case.save()
    self.logger.debug("Case updated")

    return

  def delete_event(self, event_id):
    """
    Delete a event

    Arguments:
      event_id (str): The database key for the event
    """
    self.logger.info("Deleting event{0}".format(
      event_id
      ))
    Event.objects(id=event_id).delete()
    self.logger.debug("Event {0} deleted".format(
      event_id
      ))

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
    case.assignee = user.to_dbref()
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
    self.logger.info("Creating event for updating status of {0} to {1}".format(
      case.display_name, status
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

    self.logger.info("Updating {0} to status {1}".format(case.display_name, status))
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
    case.save()
    self.logger.debug("Case updated")

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

    self.logger.info("Change status for case {0} to 'archived'".format(
      case.display_name
    ))
    case.status = 'archived'
    case.save()
    self.logger.debug("Case updated")

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
    self.logger.debug("Case updated")

    return

  def add_phenotype(self, institute, case, user, link, phenotype_id):
    """Add a new HPO phenotype to a case."""
    phenotype_term = PhenotypeTerm(phenotype_id=phenotype_id)
    self.logger.info("Adding new HPO term to case %s", case.display_name)
    # append the new HPO term (ID)
    case.phenotype_terms.append(phenotype_term)

    case.save()
    self.logger.debug("Case updated")

    self.logger.info("Creating event for adding phenotype term for case %s",
                     case.display_name)
    self.create_event(institute=institute, case=case, user=user, link=link,
                      category='case', verb='add_phenotype',
                      subject=case.display_name,)

    return

  def remove_phenotype(self, institute, case, user, link, phenotype_id):
    """Remove an existing HPO phenotype from a case."""
    self.logger.info("Removing HPO term from case %s", case.display_name)

    # remove the new HPO term (ID)
    for phenotype in case.phenotype_terms:
      if phenotype.phenotype_id == phenotype_id:
        case.phenotype_terms.remove(phenotype)
        break

    case.save()
    self.logger.debug("Case updated")

    self.logger.info("Creating event for removing phenotype term from case %s",
                     case.display_name)
    self.create_event(institute=institute, case=case, user=user, link=link,
                      category='case', verb='remove_phenotype',
                      subject=case.display_name)

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

    # add variant to list of pinned references in the case model
    case.suspects.append(variant)
    case.save()

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

    # remove variant from list of references in the case model
    case.suspects.remove(variant)
    case.save()

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
    self.logger.info("Creating event for ordering sanger for variant {0}".format(
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

    self.logger.info("Creating event for ordering sanger for case {0}".format(
      case.display_name
    ))
    self.create_event(
      institute=institute,
      case=case,
      user=user,
      link=link,
      category='case',
      verb='sanger',
      variant_id=variant.variant_id,
      subject=variant.display_name,
    )

    return

  def mark_causative(self, institute, case, user, link, variant):
    """
    Create an event for marking a variant causative.

    Arguments:
      institute (Institute): A Institute object
      case (Case): Case object
      user (User): A User object
      link (str): The url to be used in the event
      variant (Variant): A variant object

    """
    # mark the variant as causative in the case model
    case.causative = variant

    # mark the case as solved
    case.status = 'solved'

    # persist changes
    case.save()

    self.logger.info("Creating case event for marking {0} causative"
                     .format(variant.display_name))
    self.create_event(
      institute=institute,
      case=case,
      user=user,
      link=link,
      category='case',
      verb='mark_causative',
      variant_id=variant.variant_id,
      subject=variant.display_name,
    )

    self.logger.info("Creating variant event for marking {0} causative"
                     .format(case.display_name))
    self.create_event(
      institute=institute,
      case=case,
      user=user,
      link=link,
      category='variant',
      verb='mark_causative',
      variant_id=variant.variant_id,
      subject=variant.display_name,
    )

    return

  def unmark_causative(self, institute, case, user, link, variant):
    """
    Create an event for unmarking a variant causative.

    Arguments:
      institute (Institute): A Institute object
      case (Case): Case object
      user (User): A User object
      link (str): The url to be used in the event
      variant (Variant): A variant object

    """
    # remove the variant as causative in the case model
    case.causative = None

    # mark the case as active again
    case.status = 'active'

    # persist changes
    case.save()

    self.logger.info("Creating events for unmarking variant {0} causative"
                     .format(variant.display_name))
    self.create_event(
      institute=institute,
      case=case,
      user=user,
      link=link,
      category='case',
      verb='unmark_causative',
      variant_id=variant.variant_id,
      subject=variant.display_name,
    )

    self.create_event(
      institute=institute,
      case=case,
      user=user,
      link=link,
      category='variant',
      verb='unmark_causative',
      variant_id=variant.variant_id,
      subject=variant.display_name,
    )

    return

  def update_manual_rank(self, institute, case, user, link, variant, manual_rank):
    """
    Create an event for updating the manual rank of a variant.
    This function will create a event and update the manual rank of the variant.

    Arguments:
      institute (Institute): A Institute object
      case (Case): Case object
      user (User): A User object
      link (str): The url to be used in the event
      variant (Variant): A variant object
      manual_rank (int): The new manual rank

    """
    self.logger.info("Creating event for updating the manual rank for variant"\
      " {0}".format(variant.display_name))

    self.create_event(
      institute=institute,
      case=case,
      user=user,
      link=link,
      category='variant',
      verb='manual_rank',
      variant_id=variant.variant_id,
      subject=variant.display_name,
    )
    self.logger.info("Setting manual rank to {0} for variant {1}".format(
      manual_rank, variant.display_name
    ))
    variant.manual_rank = manual_rank
    variant.save()
    self.logger.debug("Variant updated")


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
