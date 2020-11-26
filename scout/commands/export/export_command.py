#!/usr/bin/env python
# encoding: utf-8
"""
export.py

Export objects from a scout database

Created by Måns Magnusson on 2016-05-11.
Copyright (c) 2016 ScoutTeam__. All rights reserved.

"""

import logging

import click

from .case import cases
from .database import database
from .exon import exons
from .gene import genes
from .hpo import hpo_genes
from .mitochondrial_report import mt_report
from .panel import panel_cmd
from .transcript import transcripts
from .variant import variants, verified

LOG = logging.getLogger(__name__)


@click.group()
def export():
    """
    Export objects from the mongo database.
    """
    LOG.info("Running scout export")
    pass


export.add_command(panel_cmd)
export.add_command(genes)
export.add_command(transcripts)
export.add_command(exons)
export.add_command(variants)
export.add_command(verified)
export.add_command(hpo_genes)
export.add_command(cases)
export.add_command(mt_report)
export.add_command(database)
