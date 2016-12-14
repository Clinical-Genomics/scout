#!/usr/bin/env python
# encoding: utf-8
"""
export.py

Export variants from a scout database

Created by Måns Magnusson on 2016-05-11.
Copyright (c) 2016 ScoutTeam__. All rights reserved.

"""

import logging

import click

from scout.export.gene import export_genes
from scout.export.transcript import export_transcripts
from scout.export.variant import export_causatives
from scout.export.panel import export_panels

logger = logging.getLogger(__name__)


@click.command()
@click.option('-c', '--collaborator')
@click.option('--genes',
                is_flag=True,
                help="Export all genes from the database"
)
@click.option('--gene-file',
              type=click.Path(exists=True),
              help="Return the genes on correct format based on hgnc ids in "\
                   "infile"
)
@click.option('--transcripts',
                is_flag=True,
                help="Export all refseq transcripts from the database"
)
@click.option('--panel',
                multiple=True,
                help="Export gene panels to .bed format"
)
@click.pass_context
def export(ctx, collaborator, genes, transcripts, gene_file, panel):
    """
    Export variants from the mongo database.
    """
    logger.info("Running scout export")
    adapter = ctx.obj['adapter']

    header = []
    function = []

    if panel:
        logger.info("Exporting panels: {}".format(', '.join(panel)))
        export_panels(adapter, panel)
    elif genes:
        header = ["#Chrom\tStart\tEnd\tHgncSymbol\tHgncID"]
        function = export_genes(adapter)

    elif transcripts:
        header = ["#Chrom\tStart\tEnd\tTranscript\tRefSeq\tHgncSymbol\tHgncID"]
        function = export_transcripts(adapter)

    else:
        if not collaborator:
            click.echo("Please provide a collaborator to export variants")
            ctx.abort()

        header = [
            "##fileformat=VCFv4.2",
            "#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO"
        ]

        function = export_causatives(adapter, collaborator)

    for line in header:
        print(line)

    for obj in function:
        print(obj)
