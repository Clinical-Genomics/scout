#!/usr/bin/env python
# encoding: utf-8
"""
export.py

Export variants from a scout database

Created by Måns Magnusson on 2016-05-11.
Copyright (c) 2016 ScoutTeam__. All rights reserved.

"""

import logging

import click

logger = logging.getLogger(__name__)

@click.command()
@click.option('-t', '--variant-type', default='causative')
@click.option('-f', '--format', default='vcf')
@click.option('-c', '--collaborator', default=None)
@click.pass_context
def export(ctx, institute, variant_type, collaborator, format):
    """
    Export variants from the mongo database.
    """
    logger.info("Running scout export")
    
    # Store variants in a dictionary
    causative_variants = {}
    
    adapter = ctx.obj['adapter']
    cases = adapter.cases(
        collaborator=collaborator,
        has_causatives=True
    )

    for case_obj in cases:
        for variant_obj in case_obj.causatives:
            logger.debug("Found causative {0}".format(variant_obj.display_name))
            causative_variants[variant_obj.variant_id] == variant_obj
    
    
