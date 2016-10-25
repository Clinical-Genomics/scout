#!/usr/bin/env python
# encoding: utf-8
"""
load_hpo.py


Created by Måns Magnusson on 2016-10-25.
Copyright (c) 2016 __MoonsoInc__. All rights reserved.
"""

from codecs import open
import gzip
import logging

import click

from scout.load import load_hpo_terms

logger = logging.getLogger(__name__)

@click.command()
@click.option('--hpo_terms',
                type=click.Path(exists=True),
                help="Path to hpo file",
                required=True
)
@click.pass_context
def hpo(ctx, hpo_terms):
    """
    Load the hpo terms to the mongo database.
    """
    logger.info("Loading hpo terms file from {0}".format(hpo_terms))
    if hpo_terms.endswith('.gz'):
        hpo_terms_handle = gzip.open(hpo_terms, 'r')
    else:
        hpo_terms_handle = open(hpo_terms, 'r')

    load_hpo_terms(
        adapter=ctx.obj['adapter'],
        hpo_lines=hpo_terms_handle, 
    )