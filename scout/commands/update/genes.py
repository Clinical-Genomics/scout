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

"""
import logging
import os
import tempfile

import click
from flask.cli import current_app, with_appcontext

from scout.commands.download.ensembl import ensembl as ensembl_cmd
from scout.commands.download.exac import exac as exac_cmd
from scout.commands.download.hgnc import hgnc as hgnc_cmd
from scout.commands.download.hpo import hpo as hpo_cmd
from scout.commands.download.omim import omim as omim_cmd
from scout.constants import UPDATE_GENES_RESOURCES
from scout.load import load_hgnc_genes, load_transcripts
from scout.server.extensions import store
from scout.utils.handle import get_file_handle

LOG = logging.getLogger(__name__)


def download_resources(download_dir, api_key, builds):
    """Download necessary files to update gene definitions in a temporary directory

    Args:
        download_dir(str): path to downloaded resources. Provided by user in the cli command
        api_key(str): API key for downloading OMIM resources
        builds(list): a list containing both genome builds or one genome build ['37', '38']
    """
    ctx = click.get_current_context()
    if not api_key:
        LOG.warning("No OMIM API key provided. Please note that some information will be missing.")
    else:
        # Download OMIM files
        ctx.invoke(omim_cmd, out_dir=download_dir, api_key=api_key)

    # Download HPO definitions
    ctx.invoke(hpo_cmd, out_dir=download_dir)
    # Download Exac genes
    ctx.invoke(exac_cmd, out_dir=download_dir)
    # Download HGNC genes
    ctx.invoke(hgnc_cmd, out_dir=download_dir)
    # Download Ensembl genes
    for build in builds:
        ctx.invoke(
            ensembl_cmd,
            out_dir=download_dir,
            skip_tx=False,
            exons=False,
            build=build,
        )


def fetch_downloaded_resources(resources, downloads_folder, builds):
    """Checks that a resource file exists on disk and has valid data. Return its content as a list of lines
    Args:
        resources(dict): Dictionary containing resource files' lines
        downloads_folder(str): Path to downloaded resources. Provided by user in the cli command
        builds(list): a list containing both genome builds or one genome build ['37', '38']

    """

    for resname, filenames in UPDATE_GENES_RESOURCES.items():
        for filename in filenames:
            resource_path = os.path.join(downloads_folder, filename)
            resource_exists = os.path.isfile(resource_path)
            if resource_exists:
                resources[resname] = get_file_handle(resource_path).readlines()

        # If the resource is mandatory, make sure it exists and contains data (OMIM data is NOT mandatory)
        if resname in ["hpo_genes", "hgnc_lines", "exac_lines"] and not resources.get(resname):
            LOG.error(f"Missing resource {resname} in downloads path.")
            raise click.Abort()

        # Check that the available genes and transcripts file correspond to the required genome build
        for build in builds:
            if resname.endswith(build) and resources.get(resname) is False:
                LOG.error(
                    f"Updating genes for genome build '{build}' requires a resource '{resname}' that is currenly missing in provided path."
                )
                raise click.Abort()

        # Check that resource lines contain actual data
        if resname not in resources:
            continue
        if "<!DOCTYPE html>" in resources[resname][0] or "<!DOCTYPE html>" in resources[resname][1]:
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
    "--api-key",
    help="Specify the OMIM downloads api key. Only if downloads_folder is not provided",
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

    # If required resources are missing, download them to a temporary directory
    if downloads_folder is None:
        with tempfile.TemporaryDirectory() as tempdir:
            try:
                download_resources(tempdir, api_key, builds)
            except Exception as ex:
                LOG.error(ex)
            fetch_downloaded_resources(resources, tempdir, builds)
    else:  # If resources have been previosly downloaded, read those file and return their lines
        fetch_downloaded_resources(resources, downloads_folder, builds)

    # Load genes and transcripts info
    for genome_build in builds:
        LOG.warning("Dropping all gene information")
        adapter.drop_genes(genome_build)
        LOG.warning("Dropping all transcript information")
        adapter.drop_transcripts(genome_build)

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

    LOG.info("Genes and transcripts loaded")
