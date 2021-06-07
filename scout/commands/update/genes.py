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
    fetch_resource,
)

LOG = logging.getLogger(__name__)

MIM_RESOURCES = {
    "mim2genes": "mim2genes.txt",
    "genemap2": "genemap2.txt",
}
PHENOTYPE_TO_GENES_FILENAME = "phenotype_to_genes.txt"
HGNC_FILENAME = "hgnc.txt"
ENSEMBL_FILENAMES = {"37": "ensembl_transcripts_37.txt", "38": "ensembl_genes_38.txt"}
EXAC_FILENAME = "fordist_cleaned_exac_r03_march16_z_pli_rec_null_data.txt"


def fetch_downloaded_resource(downloads_folder, resource_filename):
    """Checks that a resource file exists on disk and returns its content as a list of lines

    Args:
        downloads_folder(str): Path to downloaded resources. Provided by user in the cli command
        resource_filename(str): Resource file name

    Returns:
        File.readlines(list): list of lines contained in the resource file
    """
    resource_path = os.path.join(downloads_folder, resource_filename)
    if os.path.isfile(resource_path) is False:
        LOG.error(f"Missing resource {resource_filename} in provided path.")
        raise click.Abort()
    return get_file_handle(resource_path).readlines()


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

    if build:
        builds = [build]
    else:
        builds = ["37", "38"]

    mim_files = {}  # OMIM resource files
    hpo_genes = []  # list of lines from HPO genes file
    ensembl_genes = []  # list of lines from Ensembl genes file
    exac_lines = []  # list of lines from the EXAC resource file

    if downloads_folder:
        # Fetch resources lines from provided download folder
        for resource_name, filename in MIM_RESOURCES.items():
            mim_files[resource_name] = fetch_downloaded_resource(downloads_folder, filename)
        hpo_genes = fetch_downloaded_resource(downloads_folder, PHENOTYPE_TO_GENES_FILENAME)
        hgnc_lines = fetch_downloaded_resource(downloads_folder, HGNC_FILENAME)
        exac_lines = fetch_downloaded_resource(downloads_folder, EXAC_FILENAME)

    else:
        # Download resources and return file lines from downloaded files
        hpo_genes = fetch_genes_to_hpo_to_disease()
        hgnc_lines = fetch_hgnc()
        exac_lines = fetch_exac_constraint()

        api_key = api_key or current_app.config.get("OMIM_API_KEY")
        if api_key:
            try:
                mim_files = fetch_mim_files(api_key, mim2genes=True, morbidmap=False, genemap2=True)
            except Exception as err:
                LOG.warning(err)
                raise click.Abort()

    # Check that mandatory resources were collected correcly
    for resource in hpo_genes, hgnc_lines, exac_lines:
        if not resource:
            LOG.error(
                f"A resource necessary to update genes collection is missing:{resource}. Please download all necessary files by running 'scout download everything' or make sure the missing file is downloadable from the internet."
            )
            raise click.Abort()

    LOG.warning("Dropping all gene information")
    adapter.drop_genes(build)
    LOG.info("Genes dropped")
    LOG.warning("Dropping all transcript information")
    adapter.drop_transcripts(build)
    LOG.info("transcripts dropped")

    for genome_build in builds:
        if downloads_folder:
            ensembl_genes = fetch_downloaded_resource(
                downloads_folder, ENSEMBL_FILENAMES[genome_build]
            )
        else:
            ensembl_genes = fetch_ensembl_genes(build=genome_build)
        # load the genes
        hgnc_genes = load_hgnc_genes(
            adapter=adapter,
            ensembl_lines=ensembl_genes,
            hgnc_lines=hgnc_lines,
            exac_lines=exac_lines,
            mim2gene_lines=mim_files.get("mim2genes"),
            genemap_lines=mim_files.get("genemap2"),
            hpo_lines=hpo_genes,
            build=genome_build,
        )

        ensembl_genes = {}
        for gene_obj in hgnc_genes:
            ensembl_id = gene_obj["ensembl_id"]
            ensembl_genes[ensembl_id] = gene_obj

        # Fetch the transcripts from ensembl
        ensembl_transcripts = fetch_ensembl_transcripts(build=genome_build)

        transcripts = load_transcripts(adapter, ensembl_transcripts, genome_build, ensembl_genes)

    adapter.update_indexes()

    LOG.info("Genes, transcripts and Exons loaded")
