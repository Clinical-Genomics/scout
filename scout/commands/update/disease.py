#!/usr/bin/env python
# encoding: utf-8
"""
update/disease.py

Update the disease terms in database

Created by Måns Magnusson on 2017-04-03.
Copyright (c) 2017 __MoonsoInc__. All rights reserved.
"""

import logging
import os

import click
from flask.cli import current_app, with_appcontext

from scout.constants import UPDATE_DISEASES_RESOURCES
from scout.load.hpo import load_disease_terms
from scout.server.extensions import store
from scout.utils.handle import get_file_handle
from scout.utils.scout_requests import (
    fetch_hpo_terms,
    fetch_hpo_to_genes_to_disease,
    fetch_mim_files,
)

LOG = logging.getLogger(__name__)


def _check_resources(resources):
    """Check that resource lines file contain valid data

    Args:
        resources(dict): resource names as keys and resource file lines as values
    """
    for resname, lines in resources.items():
        if not lines or lines[0].startswith("#") is False:
            LOG.error(f"Resource file '{resname}' doesn't contain valid data.")
            raise click.Abort()


def _fetch_downloaded_resources(resources, downloads_folder):
    """Populate resource lines if a resource exists in downloads folder

    Args:
        resources(dict):
        downloads_folder(str): path to downloaded files or demo version of these files

    """
    for resname, filenames in UPDATE_DISEASES_RESOURCES.items():
        for filename in filenames:
            resource_path = os.path.join(downloads_folder, filename)
            resource_exists = os.path.isfile(resource_path)
            if resource_exists:
                resources[resname] = get_file_handle(resource_path).readlines()
        if resname not in resources:
            LOG.error(f"Resource file '{resname}' was not found in provided downloads folder.")
            raise click.Abort()


@click.command("diseases", short_help="Update disease terms")
@click.option(
    "-f",
    "--downloads-folder",
    type=click.Path(exists=True, dir_okay=True, readable=True),
    help="specify path to folder where files necessary to update diseases are pre-downloaded",
)
@click.option(
    "--api-key",
    help="Download resources using an OMIM api key (required only if downloads folder is NOT specified)",
)
@with_appcontext
def diseases(downloads_folder, api_key):
    """
    Update disease terms in mongo database. Use pre-downloaded resource files (phenotype_to_genes and genemap2) or download them from OMIM.
    Both options require using a valid omim api key.
    """
    adapter = store
    api_key = api_key or current_app.config.get("OMIM_API_KEY")
    resources = {}

    if downloads_folder:
        api_key = None
        # Fetch required resource lines after making sure that are present in downloads folder and that contain valid data
        _fetch_downloaded_resources(resources, downloads_folder)
    else:
        # Download resources
        if not api_key:
            LOG.warning("Please provide a omim api key to load the omim gene panel")
            raise click.Abort()

        try:
            mim_files = fetch_mim_files(api_key, genemap2=True)
            resources["genemap_lines"] = mim_files["genemap2"]
            resources["hpo_gene_lines"] = fetch_hpo_to_genes_to_disease()

        except Exception as err:
            LOG.warning(err)
            raise click.Abort()

    _check_resources(resources)

    LOG.info("Dropping DiseaseTerms")
    adapter.disease_term_collection.drop()
    LOG.debug("DiseaseTerms dropped")

    load_disease_terms(
        adapter=adapter,
        genemap_lines=resources["genemap_lines"],
        hpo_disease_lines=resources["hpo_gene_lines"],
    )

    LOG.info("Successfully loaded all disease terms")
