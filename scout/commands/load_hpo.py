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

from scout.load import load_hpo

from .utils import get_file_handle

logger = logging.getLogger(__name__)

@click.command()
@click.option('--hpo-terms',
                type=click.Path(exists=True),
                help="Path to hpo file",
                required=True
)
@click.option('--hpo-disease',
                type=click.Path(exists=True),
                help="Path to file with hpo diseases",
                required=True
)
@click.pass_context
def hpo(ctx, hpo_terms, hpo_disease):
    """
    Load the hpo terms to the mongo database.
    """
    logger.info("Loading hpo terms from file {0}".format(hpo_terms))
    logger.info("Loading hpo disease terms from file {0}".format(hpo_disease))
    
    hpo_terms_handle = get_file_handle(hpo_terms)
    hpo_disease_handle = get_file_handle(hpo_disease)
    
    load_hpo(
        adapter=ctx.obj['adapter'],
        hpo_lines=hpo_terms_handle, 
        disease_lines=hpo_disease_handle, 
    )
    
    logger.info("Successfully loaded all hpo terms")
