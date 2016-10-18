#!/usr/bin/env python
# encoding: utf-8
"""
load_hgnc.py

Script to clean the database and reload it with new data.

Created by Måns Magnusson on 2015-01-14.
Copyright (c) 2015 __MoonsoInc__. All rights reserved.

"""
from codecs import open
import gzip
import logging

import click

from scout.parse import parse_hgnc_genes

logger = logging.getLogger(__name__)


@click.command()
@click.argument('hgnc_file',
                type=click.Path(exists=True),
)
@click.pass_context
def hgnc(ctx, hgnc_file):
    """
    Load the hgnc aliases to the mongo database.
    """
    logger.info("Loading hgnc aliases from {0}".format(hgnc_file))
    if hgnc_file.endswith('.gz'):
        file_handle = gzip.open(hgnc_file, 'r')
    else:
        file_handle = open(hgnc_file, 'r')
    
    adapter = ctx.obj['adapter']
    
    for gene in read_hgnc_genes(file_handle):
        adapter.add_hgnc_alias(gene)

