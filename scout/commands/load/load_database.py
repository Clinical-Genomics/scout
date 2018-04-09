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
from .panel import panel as panel_command
from .research import research as research_command
from .variants import variants as variants_command

from scout.load.all import load_region

LOG = logging.getLogger(__name__)

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
@click.option('-i', '--institute-id', 
    required=True, 
    multiple=True
)
@click.option('-u', '--user-name', required=True)
@click.option('-m', '--user-mail', required=True)
@click.option('--admin', 
    is_flag=True,
    help="If user should be admin",
)
@click.pass_context
def user(context, institute_id, user_name, user_mail, admin):
    """Add a user to the database."""
    adapter = context.obj['adapter']
    
    institutes = []
    for institute in institute_id:
        institute_obj = adapter.institute(institute_id=institute)
        
        if not institute_obj:
            LOG.warning("Institute % does not exist", institute)
            context.abort()

        institutes.append(institute)
    
    roles = []
    if admin:
        LOG.info("User is admin")
        roles.append('admin')

    user_info = dict(email=user_mail, name=user_name, roles=roles, institutes=institutes)
    
    try:
        adapter.add_user(user_info)
    except Exception as err:
        LOG.warning(err)
        context.abort()

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
load.add_command(region)
load.add_command(panel_command)
load.add_command(user)
load.add_command(research_command)
load.add_command(variants_command)
