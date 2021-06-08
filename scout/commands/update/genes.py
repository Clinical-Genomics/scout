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

from scout.load import load_hgnc_genes, load_transcripts
from scout.server.extensions import store
from scout.utils.handle import get_file_handle
from scout.utils.scout_requests import (
    fetch_ensembl_genes,
    fetch_ensembl_transcripts,
    fetch_exac_constraint,
    fetch_genes_to_hpo_to_disease,
    fetch_hgnc,
    fetch_mim_files,
)

LOG = logging.getLogger(__name__)

DOWNLOADED_RESOURCES = {
    "mim2genes": "mim2genes.txt",
    "genemap2": "genemap2.txt",
    "hpo_genes": "genes_to_phenotype.txt",
    "hgnc_lines": "hgnc.txt",
    "exac_lines": "fordist_cleaned_exac_r03_march16_z_pli_rec_null_data.txt",
    "ensembl_genes_37": "ensembl_genes_37.txt",
    "ensembl_genes_38": "ensembl_genes_38.txt",
    "ensembl_transcripts_37": "ensembl_transcripts_37.txt",
    "ensembl_transcripts_38": "ensembl_transcripts_38.txt",
}


def fetch_downloaded_resource(downloads_folder, resource_name, resource_filename, builds):
    """Checks that a resource file exists on disk and has valid data. Return its content as a list of lines
    Args:
        downloads_folder(str): Path to downloaded resources. Provided by user in the cli command
        resource_filename(str): Resource file name

    Returns:
        resource_lines(list) or None: list of lines contained in the resource file
    """
    resource_path = os.path.join(downloads_folder, resource_filename)
    resource_exists = os.path.isfile(resource_path)

    # If the resource is manadatory make sure it exists and contains data (OMIM data is NOT mandatory)
    if resource_name in ["hpo_genes", "hgnc_lines", "exac_lines"] and resource_exists is False:
        LOG.error(f"Missing resource {resource_filename} in provided path.")
        raise click.Abort()

    # Check that the available genes and transcripts file correspond to the required genome build
    for build in builds:
        if resource_name.endswith(build) and resource_exists is False:
            LOG.error(
                f"Updating genes for genome build '{build}' requires a resource '{resource_filename}' that is currenly missing in provided path."
            )
            raise click.Abort()

    if resource_exists:
        resource_lines = get_file_handle(resource_path).readlines()
        if not resource_lines:
            LOG.error(f"Resource file '{resource_filename}' doesn't contain valid data.")
            raise click.Abort()
        return resource_lines


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
    resources = {}

    # If resources have been previosly doenloaded, read those file and return their linesFetch resources from folder containing previously-downloaded resource files
    if downloads_folder:
        api_key = None
        for resname, filename in DOWNLOADED_RESOURCES.items():
            resources[resname] = fetch_downloaded_resource(
                downloads_folder, resname, filename, builds
            )

    else:  # Download resource files and return their lines
        api_key = api_key or current_app.config.get("OMIM_API_KEY")

    LOG.warning("Dropping all gene information")
    adapter.drop_genes(build)
    LOG.warning("Dropping all transcript information")
    adapter.drop_transcripts(build)

    # Load genes and transcripts info
    for build in builds:
        ensembl_gene_res = (
            resources.get("ensembl_genes_37")
            if build == "37"
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
            build=build,
        )

        ensembl_genes_dict = {}
        for gene_obj in hgnc_genes:
            ensembl_id = gene_obj["ensembl_id"]
            ensembl_genes_dict[ensembl_id] = gene_obj

        # Load the transcripts
        ensembl_tx_res = (
            resources.get("ensembl_transcripts_37")
            if build == "37"
            else resources.get("ensembl_transcripts_38")
        )  # It will be none if everything needs to be downloaded

        load_transcripts(adapter, ensembl_tx_res, build, ensembl_genes_dict)

    adapter.update_indexes()

    LOG.info("Genes and transcripts loaded")
