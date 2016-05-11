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
@click.option('-i', '--institute', default=None)
@click.option('-t', '--variant-type', default='causative')
@click.option('-f', '--format', default='vcf')
@click.option('-c', '--collaborator')
@click.pass_context
def export(ctx, institute, variant_type, collaborator, format):
    """
    Export variants from the mongo database.
    """
    logger.info("Running scout export")

    adapter = ctx.obj['adapter']
    cases = adapter.cases(
        collaborator=collaborator
    )

    for case in cases:
        if case.causatives:
            logger.debug("Found causatives for case {0}".format(case.case_id))
            for variant in case.causatives:
                print(variant.variant_id)
