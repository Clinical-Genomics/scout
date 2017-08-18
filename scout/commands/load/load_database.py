#!/usr/bin/env python
# encoding: utf-8
"""
wipe_and_load.py

Script to clean the database and reload it with new data.

Created by Måns Magnusson on 2015-01-14.
Copyright (c) 2015 __MoonsoInc__. All rights reserved.

"""
import logging

import click

from .case import case as case_command

from .institute import institute as institute_command
from .hpo import hpo as hpo_command
from .genes import genes as genes_command
from .panel import panel as panel_command
from .research import research as research_command
from .disease import diseases as disease_command
from .variants import variants as variants_command

from scout.load.all import load_region

log = logging.getLogger(__name__)

@click.command('region', short_help='Load variants from region')
@click.option('--hgnc-id', type=int,
              help="Use a existing hgnc id to define the region",)
@click.option('--case-id', required=True, help="Id of case")
@click.option('-c', '--chromosome')
@click.option('-s', '--start', type=int)
@click.option('-e', '--end', type=int)
@click.pass_context
def region(context, hgnc_id, case_id, chromosome, start, end):
    """Load all variants in a region to a existing case"""
    adapter = context.obj['adapter']
    load_region(
        adapter=adapter, case_id=case_id, hgnc_id=hgnc_id, chrom=chromosome, start=start, end=end
    )


@click.command('user', short_help='Load a user')
@click.option('-i', '--institute-id', required=True,)
@click.option('-u', '--user-name', required=True)
@click.option('-m', '--user-mail', required=True)
@click.pass_context
def user(context, institute_id, user_name, user_mail):
    """Add a user to the database."""
    adapter = context.obj['adapter']

    institute = adapter.institute(institute_id=institute_name)

    if not institute:
        log.info("Institute {0} does not exist".format(institute_id))
        context.abort()

    user_info = dict(email=user_mail, name=user_name, roles=['admin'], institutes=[institute_id])
    adapter.add_user(user_info)

@click.group()
@click.pass_context
def load(context):
    """Load the Scout database."""
    pass


@load.command()
@click.argument('case_id')
@click.argument('report_path', type=click.Path(exists=True))
@click.pass_context
def report(context, case_id, report_path):
    """Add delivery report to an existing case."""
    adapter = context.obj['adapter']
    customer, family = case_id.split('-', 1)
    existing_case = adapter.case(customer, family)
    if existing_case is None:
        click.echo("ERROR: no case found!")
        context.abort()
    existing_case.delivery_report = report_path
    existing_case.save()
    click.echo("saved report to case!")


load.add_command(case_command)
load.add_command(institute_command)
load.add_command(genes_command)
load.add_command(region)
load.add_command(hpo_command)
load.add_command(panel_command)
load.add_command(user)
load.add_command(research_command)
load.add_command(disease_command)
load.add_command(variants_command)
