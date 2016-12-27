#!/usr/bin/env python
# encoding: utf-8
"""
wipe_and_load.py

Script to clean the database and reload it with new data.

Created by Måns Magnusson on 2015-01-14.
Copyright (c) 2015 __MoonsoInc__. All rights reserved.

"""
import logging
import datetime

import click
import yaml

from scout.exceptions import (IntegrityError, ConfigError)

from scout.models import (User, Whitelist)

from scout.commands.case import case as case_command
from scout.commands.load_institute import institute as institute_command
from scout.commands.load_hpo import hpo as hpo_command
from scout.commands.load_genes import genes as genes_command
from scout.commands.load_panel import panel as panel_command

from scout.load.all import load_region

logger = logging.getLogger(__name__)
    

@click.command('region', short_help='Load variants from region')
@click.option('--hgnc-id',
    type=int,
    help="Use a existing hgnc id to define the region",
)
@click.option('--institute-name',
    required = True,
    help = "Specify the institute that the case belongs to"
)
@click.option('--case-name',
    required = True,
    help = "Name of case"
)
@click.option('-c','--chromosome')
@click.option('-s','--start', type=int)
@click.option('-e','--end', type=int)
@click.pass_context
def region(context, hgnc_id, case_name, institute_name, chromosome, start, end):
    """Load all variants in a region to a existing case"""
    adapter = context.obj['adapter']
    
    try:
        load_region(
            adapter=adapter, 
            case_id=case_name, 
            owner=institute_name, 
            hgnc_id=hgnc_id, 
            chrom=chromosome, 
            start=start, 
            end=end)
    except Error as err:
        logger.warning(err)
        context.abort()

@click.command('user', short_help='Load a user')
@click.option('-i', '--institute-name',
    required = True,
)
@click.option('-u', '--user-name',
    default = 'Clark Kent',
)
@click.option('-m', '--user-mail',
    default = 'clark.kent@mail.com',
)
@click.pass_context
def user(context, institute_name, user_name, user_mail):
    """Add a user to the database"""
    adapter = context.obj['adapter']
    
    institute = adapter.institute(institute_id=institute_name)
    
    if not institute:
        logger.info("Institute {0} does not exist".format(institute_name))
        context.abort()

    Whitelist(email=user_mail).save()
    user = User(email=user_mail,
                name=user_name,
                roles=['admin'],
                institutes=[institute])
    user.save()
    

@click.group()
@click.pass_context
def load(context):
    """Load the Scout database."""
    pass
    
load.add_command(case_command)
load.add_command(institute_command)
load.add_command(genes_command)
load.add_command(region)
load.add_command(hpo_command)
load.add_command(panel_command)
load.add_command(user)
