#!/usr/bin/env python
# encoding: utf-8
"""
load_hpo.py


Created by Måns Magnusson on 2016-10-25.
Copyright (c) 2016 __MoonsoInc__. All rights reserved.
"""

import logging

import click

from scout.load.hpo import load_hpo_terms
from scout.utils.handle import get_file_handle
from scout.resources import hpoterms_path

logger = logging.getLogger(__name__)

@click.command('hpo', short_help='Load hpo terms')
@click.option('--hpo-terms',
                type=click.Path(exists=True),
                help="Path to hpo file",
                default=hpoterms_path
)
@click.pass_context
def hpo(ctx, hpo_terms):
    """
    Load the hpo terms to the mongo database.
    """
    adapter = ctx.obj['adapter']
    
    logger.info("Dropping HpoTerms")
    adapter.hpo_term_collection.drop()
    logger.debug("HpoTerms dropped")
    
    logger.info("Loading hpo terms from file {0}".format(hpo_terms))
    
    hpo_terms_handle = get_file_handle(hpo_terms)

    alias_genes = adapter.genes_by_alias()
    
    load_hpo_terms(
        adapter=adapter,
        hpo_lines=hpo_terms_handle, 
        genes=alias_genes, 
    )

    logger.info("Successfully loaded all hpo terms")
