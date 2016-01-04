#!/usr/bin/env python
# encoding: utf-8
"""
delete_case.py

Script to delete a case and all of its variants from the database.

Created by Måns Magnusson on 2015-04-07.
Copyright (c) 2015 ScoutTeam__. All rights reserved.

"""
from __future__ import print_function
import logging

import click


logger = logging.getLogger(__name__)


@click.command()
@click.option('-c', '--case_id', default=None)
@click.option('-o', '--owner', default=None)
@click.pass_context
def delete_case(ctx, case_id, owner):
    """
    Delete a case and all of its variants from the mongo database.
    """
    logger.info("Running delete_case")

    if not case_id:
        logger.warning("Please specify the id of the case that should be "
                       "deleted with flag '-c/--case_id'.")
        ctx.abort()

    if not owner:
        logger.warning("Please specify the owner of the case that should be "
                       "deleted with flag '-o/--owner'.")
        ctx.abort()

    adapter = ctx.obj['adapter']
    logger.info("Delete case {0}".format(case_id))
    case = adapter.delete_case(
        institute_id=owner,
        case_id=case_id)

    if case:
        logger.info("Delete the clinical variants for case {0}".format(
            case.case_id))
        adapter.delete_variants(case_id=case.case_id, variant_type='clinical')
        logger.info("Delete the research variants for case {0}".format(
            case.case_id))
        adapter.delete_variants(case_id=case.case_id, variant_type='research')
