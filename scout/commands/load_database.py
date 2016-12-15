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

from scout.commands.case import case as case_command
from scout.commands.load_institute import institute as institute_command
from scout.commands.load_hpo import hpo as hpo_command
from scout.commands.load_genes import genes as genes_command
from scout.commands.load_panel import panel as panel_command

logger = logging.getLogger(__name__)
    

@click.command()
@click.pass_context
def region(context):
    """Load all variants in a region to a existing case"""
    pass

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
