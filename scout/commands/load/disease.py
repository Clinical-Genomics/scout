#!/usr/bin/env python
# encoding: utf-8
"""
disease.py

Load the disease terms into the database

Created by Måns Magnusson on 2017-04-03.
Copyright (c) 2017 __MoonsoInc__. All rights reserved.
"""

import logging

import click

from scout.load.hpo import load_disease_terms
from scout.utils.handle import get_file_handle
from scout.resources import (hpo_phenotype_to_terms_path, genemap2_path)

logger = logging.getLogger(__name__)

@click.command('diseases', short_help='Load disease terms')
@click.pass_context
def diseases(ctx):
    """
    Load the disease terms to the mongo database.
    """
    adapter = ctx.obj['adapter']
    
    logger.info("Dropping Disease Terms")
    adapter.disease_term_collection.drop()
    logger.debug("Disease Terms dropped")
    
    logger.info("Loading disease info from file {0}".format(genemap2_path))
    logger.info("Loading hpo info from file {0}".format(hpo_phenotype_to_terms_path))
    
    disease_handle = get_file_handle(genemap2_path)
    hpo_handle = get_file_handle(hpo_phenotype_to_terms_path)

    alias_genes = adapter.genes_by_alias()
    
    load_disease_terms(
        adapter=adapter,
        genemap_lines=disease_handle, 
        genes=alias_genes,
        hpo_disease_lines=hpo_handle,
    )

    logger.info("Successfully loaded all hpo terms")
