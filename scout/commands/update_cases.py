#!/usr/bin/env python
# encoding: utf-8
"""
update_cases.py

Update cases with information from a old instance

Created by Måns Magnusson on 2016-05-11.
Copyright (c) 2016 ScoutTeam__. All rights reserved.

"""
import logging

import click
import yaml

from scout.models import Variant, Event
from scout.models.phenotype_term import PhenotypeTerm

logger = logging.getLogger(__name__)


def update_variants(adapter, case_obj, old_variants):
    """Update new variants with old information."""
    for variant in old_variants:
        new_variant = Variant.objects(variant_id=variant['variant_id']).first()
        if new_variant is None:
            logger.warning("missing variant: %s", variant['variant_id'])
            continue
        if variant.get('manual_rank'):
            new_variant.manual_rank = variant['manual_rank']
        if variant.get('sanger_ordered') is True:
            new_variant.sanger_ordered = True
            if new_variant not in case_obj.suspects:
                new_variant.suspects.append(new_variant)
        yield new_variant


def update_events(adapter, case_obj, old_events):
    """Update old events (comments) for a new case."""
    for event in old_events:
        if not event.get('content'):
            logger.debug("skipping event with no content: %s", event['verb'])
            continue
        user_obj = adapter.user(event['author'])
        if user_obj is None:
            logger.warn("unable to find user: %s", event['author'])
            continue
        institute = adapter.institute(case_obj.owner)
        new_event = Event(case=case_obj, institute=institute, link=event['link'],
                          category=event['category'], author=user_obj,
                          subject=event['subject'], verb=event['verb'],
                          level=event['level'], content=event['content'],
                          created_at=event['created_at'])
        if event['variant_id']:
            new_event.variant_id = event['variant_id']
        yield new_event


def update_case(adapter, case_obj, exported_data):
    """docstring for update_case"""
    case_id = case_obj.case_id

    # Update the collaborators
    if exported_data['collaborators']:
        collaborators = set([coll for coll in case_obj.collaborators] +
                            exported_data['collaborators'])
        logger.info("Set collaborators to %s ", ', '.join(collaborators))
        case_obj.collaborators = list(collaborators)

    # Set assignee
    if case_obj.assignee is None:
        if exported_data['assignee']:
            mail = exported_data['assignee']
            user_obj = adapter.user(email=mail)
            if user_obj:
                logger.info("Assigning user %s", mail)
                case_obj.assignee = user_obj
            else:
                logger.info("Could not find user user %s", mail)

    # Add the old suspects
    if exported_data['suspects']:
        existing_suspects = case_obj.suspects
        for suspect in exported_data['suspects']:
            variant_obj = Variant.objects.get(variant_id=suspect, case_id=case_id)
            if variant_obj:
                logger.info("Adding suspect %s", variant_obj.display_name)
                existing_suspects.append(variant_obj)
            else:
                logger.info("Could not find suspect %s in database", suspect)
        case_obj.suspects = existing_suspects

    # Add the old suspects
    if exported_data['causatives']:
        existing_causatives = case_obj.causatives
        for causative in exported_data['causatives']:
            variant_obj = Variant.objects.get(variant_id=causative, case_id=case_id)
            if variant_obj:
                logger.info("Adding causative %s", variant_obj.display_name)
                existing_causatives.append(variant_obj)
            else:
                logger.info("Could not find causative %s in database", causative)
        case_obj.causatives = existing_causatives

    # Update the synopsis
    if exported_data['synopsis']:
        if not case_obj.synopsis:
            logger.info("Updating synopsis")
            case_obj.synopsis = exported_data['synopsis']

    # Update the phenotype terms
    # If the case is phenotyped, skip to add the terms
    phenotype_terms = exported_data['phenotype_terms']
    if phenotype_terms:
        logger.info("Updating phenotype terms")
        existing_terms = case_obj.phenotype_terms
        if len(existing_terms) == 0:
            for term in phenotype_terms:
                hpo_obj = adapter.hpo_term(term)
                if hpo_obj:
                    new_term = PhenotypeTerm(phenotype_id=term,
                                             feature=hpo_obj.description)
                    logger.info("Adding term %s", term)
                    existing_terms.append(new_term)
                else:
                    logger.info("Could not find term %s", term)
            case_obj.phenotype_terms = existing_terms
        else:
            logger.info("Case was already phenotyped")

    # Update the phenotype groups
    # If the case has a phenotype group, skip to add the groups
    phenotype_groups = exported_data['phenotype_groups']
    if phenotype_groups:
        logger.info("Updating phenotype groups")
        existing_groups = case_obj.phenotype_groups
        if len(existing_groups) == 0:
            for term in phenotype_groups:
                hpo_obj = adapter.hpo_term(term)
                if hpo_obj:
                    new_term = PhenotypeTerm(phenotype_id=term,
                                             feature=hpo_obj.description)
                    logger.info("Adding term %s", term)
                    existing_groups.append(new_term)
                else:
                    logger.info("Could not find term %s", term)
            case_obj.phenotype_groups = existing_groups
        else:
            logger.info("Case already had phenotype groups")

    logger.info("Saving case")
    case_obj.save()


@click.command('update_cases', short_help='Update cases')
@click.argument('exported_cases', type=click.File('r'))
@click.pass_context
def update_cases(context, exported_cases):
    """Update all information that was manually annotated from a old instance

        Takes a yaml file
    """
    logger.info("Running scout update cases")

    exported_data = yaml.load(exported_cases)

    adapter = context.obj['adapter']

    for case_obj in adapter.cases():
        if not case_obj.is_migrated:
            case_id = case_obj.case_id
            if case_id in exported_data:
                logger.info("Updating case: %s" % case_id)
                exported_info = exported_data[case_id]
                update_case(adapter, case_obj, exported_info)
                if exported_info.get('variants'):
                    new_variants = update_variants(adapter, case_obj,
                                                   exported_info['variants'])
                    for new_variant in new_variants:
                        new_variant.save()
                if exported_info.get('events'):
                    new_events = update_events(adapter, case_obj,
                                               exported_info['events'])
                    for new_event in new_events:
                        new_event.save()
            case_obj.is_migrated = True
            case_obj.save()
