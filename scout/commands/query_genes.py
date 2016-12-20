#!/usr/bin/env python
# encoding: utf-8
"""
query_genes.py

Created by Måns Magnusson on 2016-11-07.
Copyright (c) 2016 __MoonsoInc__. All rights reserved.

"""
import logging
import click

logger = logging.getLogger(__name__)

@click.command('hgnc_query', short_help='Check if genes exist')
@click.option('--hgnc-symbol', '-s',
                help="A valid hgnc symbol",
)
@click.option('--hgnc-id', '-i',
                type=int,
                help="A valid hgnc id",
)
@click.pass_context
def hgnc_query(ctx, hgnc_symbol, hgnc_id):
    """
    Query the hgnc aliases
    """
    adapter = ctx.obj['adapter']
    results = []
    if hgnc_id:
        result = adapter.hgnc_gene(hgnc_id)
        if result:
            results.append(result)
    elif hgnc_symbol:
        result = adapter.hgnc_genes(hgnc_symbol)
        if result:
            results = result
    else:
        logger.warning("Please provide a hgnc symbol or hgnc id")
        ctx.abort()
    
    if not results:
        logger.info("No results found")
    
    else:
        for result in results:
            print(result)
    