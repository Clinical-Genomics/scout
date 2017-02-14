#!/usr/bin/env python
# encoding: utf-8
"""
export_cases.py

Script to export information from all cases in a scout instance to yaml

Created by Måns Magnusson on 2015-04-07.
Copyright (c) 2015 ScoutTeam__. All rights reserved.

"""
from __future__ import print_function
import logging

from mongoengine import Q

import click
import yaml
from scout.models import (Variant, Event, Case, User)

logger = logging.getLogger(__name__)

"""
case_id: cust003-16028

variants:
    - variant_id: 6a3a87223576594ec2bca7a474d0d0af
      manual_rank: 2
      sanger_ordered: yes

events:
    - link: /cust003/16028
      category: case
      author: robin.andeer@scilifelab.se
      subject: case 16028
      content: "We are happy!"
      created_at: 2015-01-03
      (level: specific)
      (variant_id: 6a3a87223576594ec2bca7a474d0d0af)
"""


def interacted_variants(case_id):
    """This is really the only valuable information on variant level."""
    interactions = Q(manual_rank__exists=True) | Q(sanger_ordered__exists=True)
    query = Variant.objects(Q(case_id=case_id) & interactions)
    for variant in query:
        yield {
            'variant_id': variant.variant_id,
            'manual_rank': variant.manual_rank,
            'sanger_ordered': variant.sanger_ordered,
        }


def case_events(case_id):
    """Get information about events related to a case."""
    for event in Event.objects(case=case_id):
        yield {
            'link': event.link,
            'category': event.category,
            'author': event.author.email,
            'subject': event.subject,
            'verb': event.verb,
            'content': event.content,
            'created_at': event.created_at,
            'level': event.level,
            'variant_id': event.variant_id if event.variant_id else None,
        }


def case_stuff(case_id, info={}):
    """Get all information possible for a case"""
    case_obj = Case.objects.get(case_id=case_id)

    info['collaborators'] = [institute for institute in case_obj.collaborators]
    if case_obj.assignee:
        info['assignee'] = case_obj.assignee.email
    else:
        info['assignee'] = None
    # These will be a list of variant ids
    info['suspects'] = []
    info['causatives'] = []
    for variant in case_obj.suspects:
        info['suspects'].append(variant.variant_id)
    for variant in case_obj.causatives:
        info['causatives'].append(variant.variant_id)

    info['synopsis'] = case_obj.synopsis

    # list of strings with phenptype terms
    info['phenotype_terms'] = []

    # list of strings with phenptype terms
    info['phenotype_groups'] = []

    for term in case_obj.phenotype_terms:
        info['phenotype_terms'].append(term.phenotype_id)

    for term in case_obj.phenotype_groups:
        info['phenotype_groups'].append(term.phenotype_id)

    return info


def export_case(customer_id, family_id):
    """Export information about a case."""
    case_id = '_'.join([customer_id, family_id])
    case_info = {'case_id': '-'.join([customer_id, family_id])}
    case_info['variants'] = list(interacted_variants(case_id))
    case_info['events'] = list(case_events(case_id))

    case_stuff(case_id, case_info)

    return case_info


@click.command()
@click.pass_context
def export_cases(ctx):
    """
    Export all cases in the database to yaml
    """
    logger.info("Running export_cases")
    for index, case_obj in enumerate(Case.objects.limit(10000)):
        logger.info("case no. %s", index)
        customer_id = case_obj.owner
        family_id = case_obj.display_name
        case_info = export_case(customer_id, family_id)
        print(yaml.safe_dump(case_info))
