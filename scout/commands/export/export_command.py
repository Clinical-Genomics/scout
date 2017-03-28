#!/usr/bin/env python
# encoding: utf-8
"""
export.py

Export objects from a scout database

Created by Måns Magnusson on 2016-05-11.
Copyright (c) 2016 ScoutTeam__. All rights reserved.

"""

import logging
import json
import datetime

import click

from scout.export.gene import export_genes
from scout.export.transcript import export_transcripts
from scout.export.variant import export_causatives
from scout.export.panel import export_panels

logger = logging.getLogger(__name__)


@click.command('omim', short_help='Export a omim gene panel')
@click.option('-v', '--version',
            type=float,
            help="Choose what version number should be used"
)
@click.option('-b', '--build',
            default='37',
            type=click.Choice(['37','38']),
            help="Choose what genome build to use"
)
@click.option('--to-json',
            is_flag=True,
            help="Output to json"
)
@click.option('-o', '--outfile',
            type=click.File('w'),
            help="Specify path to a file where result should be stored"
)
@click.pass_context
def omim(context, version, build, to_json, outfile):
    """Export the omim gene panel to a .bed like format.
    """
    version = version or 1.0
    logger.info("Running scout export omim")
    adapter = context.obj['adapter']
    
    if not to_json:
        # print the headers
        click.echo("##panel_id=OMIM-aut")
        click.echo("##institute=cust002")
        click.echo("##version={0}".format(version))
        click.echo("##date={0}".format(datetime.date.today()))
        click.echo("##display_name=OMIM")
        click.echo("##contact=daniel.nilsson@clinicalgenomics.se")
        click.echo("#hgnc_id\thgnc_symbol")
    
    nr_omim = 0
    all_genes = adapter.all_genes(build=str(build))
    nr_genes = all_genes.count()
    
    json_genes = []
    for gene in all_genes:
        keep = False
        # A omim gene is recognized by having phenotypes
        if gene.get('phenotypes'):
            gene.pop('_id')
            for phenotype in gene['phenotypes']:
                if phenotype['status'] in ['established', 'provisional']:
                    keep = True
        if keep:
            nr_omim += 1
            if to_json:
                json_genes.append(gene)
            else:
                click.echo("{0}\t{1}".format(gene['hgnc_id'], gene['hgnc_symbol']))
    
    if to_json:
        if outfile:
            json.dump(json_genes, outfile, sort_keys=True, indent=4)
        else:
            print(json.dumps(json_genes, sort_keys=True, indent=4))
        
    
    logger.info("Nr of genes in total: %s" % nr_genes)
    logger.info("Nr of omim genes: %s" % nr_omim)
    logger.info("Nr of genes outside mim panel: %s" % (nr_genes - nr_omim))


@click.command('panel', short_help='Export gene panels')
@click.argument('panel',
                nargs=-1,
                metavar='<panel_name>'
)
@click.pass_context
def panel(context, panel):
    """Export gene panels to .bed like format.
    
        Specify any number of panels on the command line
    """
    logger.info("Running scout export panel")
    adapter = context.obj['adapter']
    
    if not panel:
        logger.warning("Please provide at least one gene panel")
        context.abort()

    logger.info("Exporting panels: {}".format(', '.join(panel)))
    export_panels(adapter, panel)

@click.command('genes', short_help='Export genes')
@click.pass_context
def genes(context):
    """Export all genes to .bed like format"""
    logger.info("Running scout export genes")
    adapter = context.obj['adapter']
    
    header = ["#Chrom\tStart\tEnd\tHgncSymbol\tHgncID"]

    for line in header:
        print(line)

    for gene in export_genes(adapter):
        print(gene)

@click.command('transcripts', short_help='Export transcripts')
@click.pass_context
def transcripts(context):
    """Export all transcripts to .bed like format"""
    logger.info("Running scout export transcripts")
    adapter = context.obj['adapter']
    
    header = ["#Chrom\tStart\tEnd\tTranscript\tRefSeq\tHgncSymbol\tHgncID"]

    for line in header:
        print(line)

    for transcript in export_transcripts(adapter):
        print(transcript)

@click.command('variants', short_help='Export variants')
@click.option('-c', '--collaborator')
@click.pass_context
def variants(context, collaborator):
    """Export causatives for a collaborator in .vcf format"""
    logger.info("Running scout export variants")
    adapter = context.obj['adapter']
    
    header = ["#Chrom\tStart\tEnd\tTranscript\tRefSeq\tHgncSymbol\tHgncID"]

    if not collaborator:
        click.echo("Please provide a collaborator to export variants")
        context.abort()

    header = [
        "##fileformat=VCFv4.2",
        "#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO"
    ]

    for line in header:
        print(line)

    for variant in export_causatives(adapter, collaborator):
        print(variant)

@click.command('hpo_genes', short_help='Export hpo gene list')
@click.argument('hpo_term',nargs=-1)
@click.pass_context
def hpo_genes(context, hpo_term):
    """Export a list of genes base on hpo terms"""
    logger.info("Running scout export hpo_genes")
    adapter = context.obj['adapter']
    
    header = ["#Gene_id\tCount"]

    if not hpo_term:
        click.echo("Please use at least one hpo term")
        context.abort()

    for line in header:
        print(line)

    for term in adapter.generate_hpo_gene_list(*hpo_term):
        print("{0}\t{1}".format(term[0], term[1]))



@click.group()
@click.pass_context
def export(ctx):
    """
    Export objects from the mongo database.
    """
    logger.info("Running scout export")

export.add_command(panel)
export.add_command(genes)
export.add_command(transcripts)
export.add_command(variants)
export.add_command(hpo_genes)
export.add_command(omim)

