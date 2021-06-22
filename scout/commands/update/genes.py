#!/usr/bin/env python
# encoding: utf-8
"""
update/genes.py

Build a file with genes that are based on hgnc format.
Parses ftp://ftp.ebi.ac.uk/pub/databases/genenames/new/tsv/hgnc_complete_set.txt,
ftp.broadinstitute.org/pub/ExAC_release/release0.3/functional_gene_constraint/
and a biomart dump from ensembl with
'Gene ID' 'Chromosome' 'Gene Start' 'Gene End' 'HGNC symbol'

The hgnc file will determine which genes that are added and most of the meta information.
The ensembl gene file will add coordinates and the exac file will add pLi scores.

Created by Måns Magnusson on 2015-01-14.
Copyright (c) 2015 __MoonsoInc__. All rights reserved.

"""
import logging
import os

import click
from flask.cli import current_app, with_appcontext

from scout.commands.download.omim import omim
from scout.constants import UPDATE_GENES_RESOURCES
from scout.load import load_hgnc_genes, load_transcripts
from scout.server.extensions import store
from scout.utils.handle import get_file_handle

LOG = logging.getLogger(__name__)


def fetch_downloaded_resources(resources, downloads_folder, builds):
    """Checks that a resource file exists on disk and has valid data. Return its content as a list of lines
    Args:
        downloads_folder(str): Path to downloaded resources. Provided by user in the cli command
        resource_filename(str): Resource file name

    Returns:
        resource_lines(list) or None: list of lines contained in the resource file
    """

    for resname, filenames in DOWNLOADED_RESOURCES.items():
        for filename in filenames:
            resource_path = os.path.join(downloads_folder, filename)
            resource_exists = os.path.isfile(resource_path)
            if resource_exists:
                resources[resname] = get_file_handle(resource_path).readlines()

        # If the resource is manadatory make sure it exists and contains data (OMIM data is NOT mandatory)
        if resname in ["hpo_genes", "hgnc_lines", "exac_lines"] and not resources[resname]:
            LOG.error(f"Missing resource {resname} in provided path.")
            raise click.Abort()

        # Check that the available genes and transcripts file correspond to the required genome build
        for build in builds:
            if resname.endswith(build) and resources.get(resname) is False:
                LOG.error(
                    f"Updating genes for genome build '{build}' requires a resource '{resname}' that is currenly missing in provided path."
                )
                raise click.Abort()

        # Check that resource lines contain actual data
        if resources.get(resname) and "<!DOCTYPE html>" in resources[resname][0]:
            LOG.error(f"Resource file '{resname}' doesn't contain valid data.")
            raise click.Abort()


@click.command("genes", short_help="Update all genes")
@click.option(
    "--build",
    type=click.Choice(["37", "38"]),
    help="What genome build should be used. If no choice update 37 and 38.",
)
@click.option(
    "-f",
    "--downloads_folder",
    type=click.Path(exists=True, dir_okay=True, readable=True),
    help="specify path to folder where files necessary to update genes are pre-downloaded",
)
@click.option(
    "--api-key", help="Specify the OMIM downloads api key. Only if downloads_folder is not provided"
)
@with_appcontext
def genes(build, downloads_folder, api_key):
    """
    Load the hgnc aliases to the mongo database.
    """
    LOG.info("Running scout update genes")
    adapter = store
    builds = [build] if build else ["37", "38"]
    api_key = api_key or current_app.config.get("OMIM_API_KEY")
    resources = {}

    # If resources have been previosly doenloaded, read those file and return their linesFetch resources from folder containing previously-downloaded resource files
    if downloads_folder:
        api_key = None
        fetch_downloaded_resources(resources, downloads_folder, builds)

    LOG.warning("Dropping all gene information")
    adapter.drop_genes(build)
    LOG.warning("Dropping all transcript information")
    adapter.drop_transcripts(build)

    # Load genes and transcripts info
    for genome_build in builds:
        ensembl_gene_res = (
            resources.get("ensembl_genes_37")
            if genome_build == "37"
            else resources.get("ensembl_genes_38")
        )  # It will be none if everything needs to be downloaded

        # Load the genes
        hgnc_genes = load_hgnc_genes(
            adapter=adapter,
            ensembl_lines=ensembl_gene_res,
            hgnc_lines=resources.get("hgnc_lines"),
            exac_lines=resources.get("exac_lines"),
            mim2gene_lines=resources.get("mim2genes"),
            genemap_lines=resources.get("genemap2"),
            hpo_lines=resources.get("hpo_genes"),
            build=genome_build,
            omim_api_key=api_key,
        )

        ensembl_genes_dict = {}
        for gene_obj in hgnc_genes:
            ensembl_id = gene_obj["ensembl_id"]
            ensembl_genes_dict[ensembl_id] = gene_obj

        # Load the transcripts
        ensembl_tx_res = (
            resources.get("ensembl_transcripts_37")
            if genome_build == "37"
            else resources.get("ensembl_transcripts_38")
        )  # It will be none if everything needs to be downloaded

        load_transcripts(adapter, ensembl_tx_res, genome_build, ensembl_genes_dict)

    adapter.update_indexes()

    LOG.info("Genes and transcripts loaded")
